from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import numpy as np
import polars as pl
import pytest

from predlab.core.hashing import AppendOnlyLedger
from predlab.racing import strategies as banc
from predlab.racing.features import load_finished
from predlab.racing.store.raw import RawStore

from .conftest import fixture_bytes
from .synthetic_db import make_db
from .test_carnet import OFF, _participants, _programme, _record


def _world(tmp: Path, boost: float) -> pl.DataFrame:
    db = make_db(tmp / "racing.duckdb", days=240, races_per_day=8, mudder_boost=boost, seed=11)
    frame = banc.walk_forward_model(load_finished(db, "PLAT"), 1000.0, min_races=200)
    # Dividends as the PMU would pay them: winners at ~85 % of their odds, placed at a
    # third of that (floor 1.1). Every race pays both kinds.
    won = frame.filter(pl.col("won")).select(
        "race_id",
        pl.lit("SIMPLE_GAGNANT").alias("bet_type"),
        "number",
        (pl.col("odds") * 0.85).alias("per_euro"),
    )
    placed = frame.filter(pl.col("placed")).select(
        "race_id",
        pl.lit("SIMPLE_PLACE").alias("bet_type"),
        "number",
        pl.max_horizontal(pl.col("odds") * 0.85 / 3, pl.lit(1.1)).alias("per_euro"),
    )
    return banc.with_returns(frame, pl.concat([won, placed]))


SPLIT = date(2024, 5, 31)


def test_the_bench_finds_and_confirms_a_planted_edge(tmp_path: Path) -> None:
    frame = _world(tmp_path, boost=2.0)
    cands = banc.explore(frame.filter(pl.col("day") <= SPLIT), "PLAT", min_bets=100, max_size=2)
    assert cands, "an edge the market ignores must show up in exploration"
    verdicts = banc.confirm(cands, frame.filter(pl.col("day") > SPLIT))
    # Simple gagnant only: the synthetic placé dividends are a crude approximation.
    confirmed = [
        c
        for c, v in zip(cands, verdicts, strict=True)
        if v["verdict"] == "confirmée" and c["bet"] == "SG"
    ]
    assert confirmed, "and survive out of sample"
    thirds = [
        (date(2024, 1, 1), date(2024, 3, 31)),
        (date(2024, 4, 1), date(2024, 6, 30)),
        (date(2024, 7, 1), date(2024, 12, 31)),
    ]
    steady = banc.explore(frame, "PLAT", periods=thirds, min_bets=100, max_size=1)
    assert all(len(c["periods"]) == 3 and all(p["roi"] > 0 for p in c["periods"]) for c in steady)
    on_going = [c for c in confirmed if {"going_lean", "going_cat"} & set(c["criteria"])]
    assert len(on_going) >= 0.8 * len(confirmed), "what survives is the planted liking"


def test_the_bench_confirms_almost_nothing_in_a_world_without_edge(tmp_path: Path) -> None:
    frame = _world(tmp_path, boost=0.0)
    cands = banc.explore(frame.filter(pl.col("day") <= SPLIT), "PLAT", min_bets=100, max_size=2)
    verdicts = banc.confirm(cands, frame.filter(pl.col("day") > SPLIT))
    assert (
        sum(
            v["verdict"] == "confirmée"
            for c, v in zip(cands, verdicts, strict=True)
            if c["bet"] == "SG"
        )
        <= 1
    )


def test_panel_update_is_idempotent_and_keeps_references(tmp_path: Path) -> None:
    frame = _world(tmp_path, boost=1.2)
    frame = frame.with_columns(
        # Shift the synthetic calendar so both windows exist: exploration up to 2024-12-31.
        (pl.col("day") + pl.duration(days=200)).alias("day")
    )
    panel = banc.Panel(tmp_path / "banc" / "panel.json")
    now = datetime(2026, 9, 30, 2, tzinfo=UTC)
    added = banc.update_panel(panel, frame, "PLAT", now, max_size=2, min_bets=100)
    assert any(s["reference"] for s in added)
    assert panel.gauge["PLAT"]["tested"] >= panel.gauge["PLAT"]["confirmed"]
    assert {s["origin"] for s in added} <= {
        "vérifiée sur 2025-2026",
        "régulière chaque année",
        "référence",
    }
    assert banc.update_panel(panel, frame, "PLAT", now, max_size=2, min_bets=100) == [], (
        "same data, nothing new"
    )
    panel.save()
    again = banc.Panel.load(panel.path)
    assert {s["id"] for s in again.strategies} == panel.ids()


def test_live_tickets_are_frozen_at_the_horizon_and_settled(tmp_path: Path) -> None:
    store = RawStore(tmp_path / "raw")
    ledger = AppendOnlyLedger(tmp_path / "banc" / "ledger.jsonl")
    _record(store, _programme(), "programme/2026-09-28", "programme", OFF - timedelta(hours=3))
    _record(
        store,
        _participants(),
        "participants/2026-09-28/R2C1",
        "participants",
        OFF - timedelta(minutes=8),
    )
    panel = banc.Panel(tmp_path / "panel.json")
    fav = {
        "id": "fav",
        "discipline": "PLAT",
        "bet": "SG",
        "criteria": {"odds_band": "Favori"},
        "eliminated_at": None,
    }
    long = {
        "id": "long",
        "discipline": "PLAT",
        "bet": "SP",
        "criteria": {"odds_band": "Outsider"},
        "eliminated_at": None,
    }
    panel.strategies = [fav, long]

    def frame_for(race, card, runners):
        odds = np.array([s.odds for s in card.starters])
        order = odds.argsort().argsort()
        return pl.DataFrame(
            {
                "number": [s.number for s in card.starters],
                "odds_band": [
                    "Favori" if r == 0 else "Outsider" if r == 3 else "Autre" for r in order
                ],
            }
        )

    rep = banc.run_banc(store, ledger, panel, now=OFF - timedelta(minutes=5), frame_for=frame_for)
    assert rep.frozen == ["2026-09-28/R2C1"] and rep.tickets == 2
    (rec,) = ledger.records()
    assert sorted(map(tuple, rec["tickets"])) == [("fav", "SG", 4), ("long", "SP", 3)]

    later = OFF + timedelta(hours=1)
    _record(store, _programme(final=True), "programme/2026-09-28", "programme", later)
    _record(
        store,
        fixture_bytes("rapports_2026-09-28_R2C1_full.json"),
        "rapports/2026-09-28/R2C1",
        "rapports",
        later,
    )
    rep = banc.run_banc(store, ledger, panel, now=later, frame_for=frame_for)
    assert rep.settled == ["2026-09-28/R2C1"]
    stats, meta = banc.live_stats(ledger)
    assert stats["fav"]["returned"] == pytest.approx(7.6), "no. 4 won: SG pays 7.60"
    assert stats["long"]["returned"] == 0.0, "no. 3 finished 3rd of 4: placé pays 2 places"
    assert meta["days"]["2026-09-28"]["tickets"] == 2
    ledger.verify()


def test_status_rules() -> None:
    s = {"id": "x", "eliminated_at": None}
    win = {"bets": 400, "low": 0.02, "high": 0.3}
    assert banc.status(s, win) == "gagnante"
    assert banc.status(s, {"bets": 100, "low": 0.1, "high": 0.4}) == "en test", "too few"
    panel = banc.Panel(Path("unused"), [dict(s)])
    now = datetime(2026, 10, 1, tzinfo=UTC)
    gone = banc.apply_eliminations(panel, {"x": {"bets": 150, "high": -0.08}}, now)
    assert gone == ["x"] and banc.status(panel.strategies[0], win) == "éliminée"
