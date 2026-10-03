from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np
import polars as pl
import pytest

from predlab.core.hashing import AppendOnlyLedger
from predlab.racing import lab
from predlab.racing.features import load_finished
from predlab.registry.hypotheses import HypothesisRegistry, Status

from .synthetic_db import make_db

NOW = datetime(2026, 10, 4, 2, tzinfo=UTC)


@pytest.fixture(scope="module")
def world(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, pl.DataFrame]:
    tmp = tmp_path_factory.mktemp("lab")
    # 2024-01-02 → 2025-03-27: train 2024 H1, validation 2024 H2, test 2025 (≈ 500 races).
    db = make_db(tmp / "racing.duckdb", days=450, races_per_day=6, seed=3)
    return db, load_finished(db, "PLAT")


def _parts(frame: pl.DataFrame) -> dict[str, pl.DataFrame]:
    return {
        "train": frame.filter(pl.col("day") <= date(2024, 6, 30)),
        "validation": frame.filter(
            (pl.col("day") > date(2024, 6, 30)) & (pl.col("day") <= date(2024, 12, 31))
        ),
        "test": frame.filter(pl.col("day") > date(2024, 12, 31)),
    }


def test_the_rule_sees_a_real_signal_and_refuses_noise(world) -> None:
    _, frame = world
    rng = np.random.default_rng(0)
    df = frame.with_columns(
        # A leak of the result: any honest procedure must call this a gain.
        (pl.col("position") == 1).cast(pl.Float64).alias("c_leak"),
        pl.Series("c_noise", rng.normal(size=frame.height)),
    )
    leak = lab.compare(_parts(df), "c_leak", lab.LAMBDAS)
    assert lab.verdict(leak, need_every_year=True)[0] == Status.SUPPORTED
    noise = lab.compare(_parts(df), "c_noise", lab.LAMBDAS)
    assert lab.verdict(noise, need_every_year=True)[0] != Status.SUPPORTED
    assert noise["level"] == 0.99 and set(noise["by_year"]) == {"2025"}


def test_verdict_rules() -> None:
    def res(d, lo, hi, years=(-0.01,)):
        return {
            "difference": d,
            "ci_low": lo,
            "ci_high": hi,
            "by_year": {str(2025 + i): {"difference": y} for i, y in enumerate(years)},
        }

    assert lab.verdict(res(-0.01, -0.02, -0.001), True)[0] == Status.SUPPORTED
    assert lab.verdict(res(-0.01, -0.02, -0.001, (-0.02, 0.01)), True)[0] == Status.INCONCLUSIVE
    assert lab.verdict(res(-0.01, -0.02, -0.001, (-0.02, 0.01)), False)[0] == Status.SUPPORTED
    assert lab.verdict(res(0.01, 0.001, 0.02), True)[0] == Status.REJECTED
    status, text = lab.verdict(res(0.0001, -0.0005, 0.0007), True)
    assert status == Status.INCONCLUSIVE and "Aucun gain mesurable" in text


def test_registration_comes_first_then_each_test_runs_once(world, tmp_path: Path) -> None:
    db, frame = world
    reg = HypothesisRegistry(AppendOnlyLedger(tmp_path / "hypotheses.jsonl"))
    added = lab.register(reg, "PLAT")
    plat = [c for c in lab.CANDIDATES if "PLAT" in c.disciplines]
    assert sorted(added) == sorted(lab.key(c, "PLAT") for c in plat)
    assert all(
        h.status == Status.PROPOSED and "Règle fixée" in h.description for h in reg.current()
    )
    assert lab.register(reg, "PLAT") == [], "idempotent"

    lines = lab.run_pending(reg, frame, db, tmp_path / "lab", "PLAT", max_tests=20, now=NOW)
    by = {h.experiment: h for h in reg.current()}
    drift = by["drift:PLAT"]
    assert drift.status == Status.TESTING and "0/1000" in (drift.forward_result or "")
    history = [lab.key(c, "PLAT") for c in plat if c.source == "history"]
    assert all(by[k].status not in (Status.PROPOSED, Status.TESTING) for k in history)
    assert set(lab.results(tmp_path / "lab")) == set(history)
    assert len(lines) == len(history) + 1
    again = lab.run_pending(reg, frame, db, tmp_path / "lab", "PLAT", max_tests=20, now=NOW)
    assert again == [], "nothing is retested, the waiting note is not rewritten"
    reg.verify()


def test_trot_candidates_wait_for_their_history(world, tmp_path: Path) -> None:
    db, _ = world
    reg = HypothesisRegistry(AppendOnlyLedger(tmp_path / "h.jsonl"))
    lab.register(reg, "ATTELE")
    empty = load_finished(db, "ATTELE")
    assert empty.is_empty()
    lab.run_pending(reg, empty, db, tmp_path / "lab", "ATTELE", now=NOW)
    statuses = {h.experiment: h.status for h in reg.current()}
    assert statuses["deferre4:ATTELE"] == Status.PROPOSED


def test_drift_is_the_change_in_normalised_probability() -> None:
    frame = pl.DataFrame(
        {
            "race_id": ["A", "A", "B", "B"],
            "number": [1, 2, 1, 2],
            "log_q": [np.log(0.6), np.log(0.4), np.log(0.5), np.log(0.5)],
        }
    )
    early = pl.DataFrame(
        {"race_id": ["A", "A", "B"], "number": [1, 2, 1], "odds_early": [2.0, 2.0, 3.0]}
    )
    out = lab.with_drift(frame, early)
    assert out["race_id"].unique().to_list() == ["A"], "race B lacks an early quote: dropped"
    assert out["c_drift"].to_list() == pytest.approx([np.log(0.6 / 0.5), np.log(0.4 / 0.5)])


def test_favourites_study_and_its_single_verdict(world, tmp_path: Path) -> None:
    _, frame = world
    df = frame.with_columns(
        pl.when(pl.col("won")).then(pl.col("odds") * 0.85).otherwise(0.0).alias("ret_SG"),
        pl.when(pl.col("placed")).then(1.1).otherwise(0.0).alias("ret_SP"),
    )
    reg = HypothesisRegistry(AppendOnlyLedger(tmp_path / "h.jsonl"))
    rep = lab.study_favourites(reg, df, tmp_path / "lab", "PLAT")
    total = rep["bands"][-1]
    assert total["band"] == "Tous les favoris" and total["races"] == frame["race_id"].n_unique()
    assert sum(b["races"] for b in rep["bands"][:-1]) == total["races"]
    assert (tmp_path / "lab" / "favourites_PLAT.json").exists()
    (h,) = reg.current()
    assert h.experiment == "favoris_lt_1.5:PLAT"
    first = h.status
    lab.study_favourites(reg, df, tmp_path / "lab", "PLAT")
    assert reg.current()[0].status == first and len(reg.history()) <= 2, "settled once"


def test_lab_endpoint(tmp_path: Path) -> None:
    from fastapi.testclient import TestClient

    from predlab.api.app import create_app
    from predlab.core.paths import Paths

    paths = Paths(tmp_path)
    paths.ensure()
    client = TestClient(create_app(paths))
    assert client.get("/api/lab").json()["experiments"] == []
    reg = HypothesisRegistry(AppendOnlyLedger(paths.hypotheses))
    lab.register(reg, "PLAT")
    body = client.get("/api/lab").json()
    drift = next(e for e in body["experiments"] if e["candidate"] == "drift")
    assert drift["status"] == "PROPOSED" and drift["source"] == "live" and drift["registered_at"]
    assert body["catalogue"] == len(lab.CANDIDATES)
