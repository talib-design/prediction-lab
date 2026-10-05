from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path

import polars as pl
import pytest

from predlab.core.hashing import AppendOnlyLedger
from predlab.racing import arena, lab
from predlab.racing import strategies as banc
from predlab.racing.champion import Champion, Window
from predlab.racing.features import MODEL_FEATURES, load_finished
from predlab.registry.hypotheses import HypothesisRegistry, Origin, Status

from .synthetic_db import make_db

NOW = datetime(2026, 10, 5, 2, tzinfo=UTC)
WINDOW = Window(
    since=date(2024, 1, 1),
    train_end=date(2024, 6, 30),
    validation_end=date(2024, 12, 31),
    test_end=date(2025, 2, 28),
    vault_start=date(2025, 3, 1),
    vault_min_races=100,
)
LEAK = lab.Candidate(
    "leak",
    "Fuite du résultat (contrôle)",
    "Contrôle du protocole : connaît le gagnant.",
    ("PLAT",),
    Origin.HUMAN,
    expr=lambda: (pl.col("position") == 1).cast(pl.Float64),
)


@pytest.fixture(scope="module")
def frame(tmp_path_factory: pytest.TempPathFactory) -> pl.DataFrame:
    db = make_db(tmp_path_factory.mktemp("arena") / "r.duckdb", days=450, races_per_day=6, seed=5)
    f = load_finished(db, "PLAT")
    won = f.filter(pl.col("won")).select(
        "race_id",
        pl.lit("SIMPLE_GAGNANT").alias("bet_type"),
        "number",
        (pl.col("odds") * 0.85).alias("per_euro"),
    )
    placed = f.filter(pl.col("placed")).select(
        "race_id",
        pl.lit("SIMPLE_PLACE").alias("bet_type"),
        "number",
        pl.max_horizontal(pl.col("odds") * 0.85 / 3, pl.lit(1.1)).alias("per_euro"),
    )
    return banc.with_returns(f, pl.concat([won, placed]))


@pytest.fixture
def with_leak(monkeypatch: pytest.MonkeyPatch) -> None:
    cands = (*lab.CANDIDATES, LEAK)
    monkeypatch.setattr(lab, "CANDIDATES", cands)
    monkeypatch.setattr(lab, "BY_ID", {c.id: c for c in cands})


def test_champion_store(tmp_path: Path) -> None:
    champ = Champion.load(tmp_path, "PLAT")
    assert champ.current["version"] == 1 and champ.features == MODEL_FEATURES
    assert champ.previous is None and champ.vault_start(WINDOW) == date(2025, 3, 1)
    champ.record_attempt("x", (date(2025, 3, 1), date(2025, 3, 20)), {}, False, NOW)
    assert champ.vault_start(WINDOW) == date(2025, 3, 21), "each attempt consumes the vault"
    champ.promote(
        features=(*MODEL_FEATURES, "c_x"),
        tau=1.0,
        origin="test",
        evidence={},
        now=NOW,
        params_before={"features": list(MODEL_FEATURES)},
    )
    champ.admit_rule("value105")
    champ.save()
    again = Champion.load(tmp_path, "PLAT")
    assert again.current["version"] == 2 and again.features[-1] == "c_x"
    assert again.previous is not None and again.previous["frozen_params"]
    assert again.rules == ["value105"]


def test_waits_for_the_extended_history(tmp_path: Path) -> None:
    reg = HypothesisRegistry(AppendOnlyLedger(tmp_path / "h.jsonl"))
    added = arena.register(reg, "PLAT", tmp_path)
    assert added and all(k.endswith(":obj1") for k in added)
    assert not any(k.startswith("drift:") for k in added), "the live test keeps its protocol"
    lines, promo = arena.run(reg, None, tmp_path, "PLAT", WINDOW, ready=False, now=NOW)
    assert promo is None and len(lines) == len(added)
    assert all(h.status == Status.TESTING for h in reg.current())
    assert arena.run(reg, None, tmp_path, "PLAT", WINDOW, ready=False, now=NOW)[0] == [], (
        "the waiting note is not rewritten"
    )


def test_a_real_edge_passes_both_filters_and_the_vault(
    frame: pl.DataFrame, tmp_path: Path, with_leak: None
) -> None:
    reg = HypothesisRegistry(AppendOnlyLedger(tmp_path / "h.jsonl"))
    arena.register(reg, "PLAT", tmp_path)
    df = lab.add_candidates(frame, "PLAT")
    lines, promo = arena.run(reg, df, tmp_path, "PLAT", WINDOW, ready=True, max_tests=20, now=NOW)
    by = {h.experiment: h for h in reg.current()}
    assert by["leak:PLAT:obj1"].status == Status.SUPPORTED
    assert promo is not None and promo["features"][-1] == "c_leak", lines
    res = lab.results(tmp_path)["leak:PLAT:obj1"]
    assert res["money"]["roi_challenger"] > res["money"]["roi_favourite"]
    champ = Champion.load(tmp_path, "PLAT")
    assert champ.data["attempts"][-1]["passed"] and champ.data["vault_used_until"]
    rule = by["value105:PLAT:obj1"]
    assert rule.status == Status.TESTING and "fraîches" in (rule.forward_result or "")


def test_calibration_and_rule_evaluations(frame: pl.DataFrame, tmp_path: Path) -> None:
    champ = Champion.load(tmp_path, "PLAT")
    parts = arena.split(frame, WINDOW, WINDOW.vault_start)
    cal = arena.evaluate_calibration(parts, champ)
    assert 0.5 <= cal["tau"] <= 1.5 and "difference" in cal
    n, res = arena.evaluate_rule(frame, champ, WINDOW, date(2025, 3, 1), 100)
    assert n >= 100 and res is not None and res["bets"] >= 0
    status, _ = arena.verdict("rule", res)
    assert status in (Status.SUPPORTED, Status.REJECTED)
    later = replace(WINDOW, vault_min_races=10_000)
    assert arena.evaluate_rule(frame, champ, later, date(2025, 3, 1), 10_000)[1] is None


def test_history_is_ready_only_when_every_year_is_filled(tmp_path: Path) -> None:
    from predlab.racing.champion import history_ready

    db = make_db(tmp_path / "r.duckdb", days=30, races_per_day=2, start=date(2024, 3, 1))
    assert not history_ready(db, "PLAT"), "2024 only"
    assert not history_ready(tmp_path / "absent.duckdb", "PLAT")
    from predlab.racing.champion import history_coverage, races_since

    cov = history_coverage(db, "PLAT")
    assert cov["reference_2024"] == 60 and cov["years"]["2023"] == 0 and not cov["ready"]
    assert races_since(db, "PLAT", date(2024, 3, 21)) == 20


def test_the_value_rule_does_not_wait_for_the_extended_history(
    frame: pl.DataFrame, tmp_path: Path
) -> None:
    reg = HypothesisRegistry(AppendOnlyLedger(tmp_path / "h.jsonl"))
    arena.register(reg, "PLAT", tmp_path)
    df = lab.add_candidates(frame, "PLAT")
    arena.run(reg, df, tmp_path, "PLAT", WINDOW, ready=False, now=NOW, rule_window=WINDOW)
    by = {h.experiment: h for h in reg.current()}
    assert "fraîches" in (by["value105:PLAT:obj1"].forward_result or "")
    assert "historique 2020" in (by["logq2:PLAT:obj1"].forward_result or "")
