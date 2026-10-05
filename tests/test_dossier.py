from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import polars as pl

from predlab.core.hashing import AppendOnlyLedger
from predlab.core.paths import Paths
from predlab.racing import dossier, replay
from predlab.racing import strategies as banc
from predlab.racing.features import load_finished

from .synthetic_db import make_db

NOW = datetime(2026, 10, 11, 7, tzinfo=UTC)  # a Sunday morning, Paris day 2026-10-11


def _paths(tmp_path: Path) -> Paths:
    paths = Paths(tmp_path)
    paths.ensure()
    make_db(paths.database, days=200, races_per_day=6, seed=11)
    f = load_finished(paths.database, "PLAT")
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
        pl.lit(1.2).alias("per_euro"),
    )
    frame = banc.with_returns(f, pl.concat([won, placed]))
    rng = np.random.default_rng(0)
    frame = frame.with_columns(
        (pl.col("market_p") * pl.Series(np.exp(rng.normal(0, 0.3, frame.height)))).alias("p_model")
    )
    replay.write_picks(replay.picks(frame), "PLAT", paths.normalized)
    return paths


def _carnet(paths: Paths) -> None:
    ledger = AppendOnlyLedger(paths.carnet)
    for i, (fav, mod, rf, rm) in enumerate(((1, 1, 3.0, 3.0), (2, 5, 0.0, 9.0))):
        day = (NOW - timedelta(days=2 + i)).date().isoformat()
        rid = f"{day}/R1C{i + 1}"
        tickets = [
            {"strategy": "SG favori", "bet_type": "SIMPLE_GAGNANT", "numbers": [fav], "stake": 1.0},
            {"strategy": "SP favori", "bet_type": "SIMPLE_PLACE", "numbers": [fav], "stake": 1.0},
            {
                "strategy": "SG top marche_plus",
                "bet_type": "SIMPLE_GAGNANT",
                "numbers": [mod],
                "stake": 1.0,
            },
            {
                "strategy": "SP top marche_plus",
                "bet_type": "SIMPLE_PLACE",
                "numbers": [mod],
                "stake": 1.0,
            },
        ]
        ledger.append(
            {
                "kind": "freeze",
                "race_id": rid,
                "day": day,
                "discipline": "PLAT",
                "venue": "NULLE-PART",
                "off_time": f"{day}T14:00:00+00:00",
                "frozen_at": f"{day}T13:35:00+00:00",
                "odds_as_of": f"{day}T13:35:00+00:00",
                "alpha": 1.0,
                "tickets": tickets,
            }
        )
        ledger.append(
            {
                "kind": "settle",
                "race_id": rid,
                "settled_at": f"{day}T16:00:00+00:00",
                "finish_order": [[mod], [fav]],
                "returns": [rf, 1.1, rm, 2.0],
            }
        )


def test_the_dossier_holds_the_facts_the_critic_reads(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    _carnet(paths)
    rep = dossier.build(paths, NOW)
    assert rep["day"] == "2026-10-11"
    c = rep["carnet"]["PLAT"]
    assert c["all"]["races"] == 2 and c["week"]["races"] == 2
    assert c["all"]["favori"]["net"] == round(3.0 + 1.1 + 0.0 + 1.1 - 4, 2)
    assert c["all"]["modèle"]["net"] == round(3.0 + 2.0 + 9.0 + 2.0 - 4, 2)
    (diff,) = c["week_differ"]
    assert diff["favori"] == [2] and diff["modèle"] == [5] and diff["arrivée"] == [5, 2]

    h = rep["history"]["PLAT"]
    assert h["races"] > 1000 and 0 < h["differ"] < h["races"]
    assert h["low"] <= h["model_minus_favourite"] <= h["high"]
    for name, rows in h["segments"].items():
        assert sum(r["races"] for r in rows) == h["races"], name
    assert "terrain" in h["segments"], "flat racing has a going segment"
    odds = {r["segment"] for r in h["segments"]["cote du favori"]}
    assert odds <= {"< 1,5", "1,5 – 2", "2 – 3", "3 – 5", "≥ 5", "inconnu"}
    assert all(0 <= r["observed"] <= 1 for r in h["calibration"])

    js, md = dossier.write(rep, paths.lab)
    text = md.read_text(encoding="utf-8")
    assert js.exists() and "# Dossier de la semaine — 2026-10-11" in text
    assert "Courses de la semaine où les choix diffèrent" in text
    assert "Calibration du choix du modèle" in text


def test_the_dossier_works_without_history_or_carnet(tmp_path: Path) -> None:
    paths = Paths(tmp_path)
    paths.ensure()
    rep = dossier.build(paths, NOW)
    assert rep["carnet"] == {"week": ["2026-10-04", "2026-10-10"]} and rep["history"] == {}
    assert "# Dossier" in dossier.to_markdown(rep)
