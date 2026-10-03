from __future__ import annotations

from datetime import UTC, date, datetime

import polars as pl
from fastapi.testclient import TestClient

from predlab.api.app import create_app
from predlab.core.paths import Paths
from predlab.racing import replay

from .test_api import lab  # noqa: F401  (fixture)


def _frame() -> pl.DataFrame:
    # Race A: the model agrees with the favourite (no. 1), who wins.
    # Race B: the model picks no. 3 (not the favourite no. 2); no. 3 wins.
    # Race C (next day): no model yet for this race, so it is not counted at all.
    rows = [
        ("A", date(2025, 1, 1), 1, 2.0, 0.50, 1.8, 1.2),
        ("A", date(2025, 1, 1), 2, 4.0, 0.30, 0.0, 1.5),
        ("A", date(2025, 1, 1), 3, 8.0, 0.20, 0.0, 0.0),
        ("B", date(2025, 1, 1), 1, 6.0, 0.10, 0.0, 0.0),
        ("B", date(2025, 1, 1), 2, 1.5, 0.35, 0.0, 1.1),
        ("B", date(2025, 1, 1), 3, 5.0, 0.55, 4.5, 2.0),
        ("C", date(2025, 1, 2), 1, 2.0, None, 1.9, 1.1),
        ("C", date(2025, 1, 2), 2, 3.0, None, 0.0, 1.3),
    ]
    return pl.DataFrame(
        rows,
        schema={
            "race_id": pl.Utf8,
            "day": pl.Date,
            "number": pl.Int64,
            "odds": pl.Float64,
            "p_model": pl.Float64,
            "ret_SG": pl.Float64,
            "ret_SP": pl.Float64,
        },
        orient="row",
    )


def test_picks_compare_favourite_and_model_on_the_same_races() -> None:
    per = replay.picks(_frame())
    assert per["race_id"].to_list() == ["A", "B"], "race without a model is left out"
    assert per["fav_number"].to_list() == [1, 2] and per["mod_number"].to_list() == [1, 3]
    series = {(s["bet"], s["pick"]): s["points"] for s in replay.daily(per)}
    (fav,) = series[("SG", "favori")]
    (mod,) = series[("SG", "modèle")]
    assert fav["races"] == mod["races"] == 2
    assert fav["net"] == round(1.8 - 2, 2) and mod["net"] == round(1.8 + 4.5 - 2, 2)
    s = replay.summary(per)
    assert s["differ"] == 1 and s["differ_share"] == 0.5
    assert s["when_they_differ"]["SG"] == {"races": 1, "favori_net": -1.0, "modèle_net": 3.5}


def test_report_keeps_only_the_latest_replay(tmp_path) -> None:
    runs = tmp_path / "runs"
    for h in (1, 2):
        rep = replay.build_report(_frame(), "PLAT", datetime(2026, 10, 3, h, tzinfo=UTC))
        replay.write_report(rep, runs)
    assert [p.name for p in runs.iterdir()] == ["replay_PLAT_20261003T020000Z"]


def test_replay_endpoint_filters_and_merges(lab: Paths) -> None:  # noqa: F811
    client = TestClient(create_app(lab))
    empty = client.get("/api/replay").json()
    assert empty["report"] is None and empty["available"] == []
    frame = _frame().with_columns(
        pl.when(pl.col("race_id") == "B")
        .then(date(2025, 1, 2))
        .otherwise(pl.col("day"))
        .alias("day")
    )
    replay.write_report(replay.build_report(frame, "PLAT"), lab.runs)
    body = client.get("/api/replay", params={"discipline": "PLAT"}).json()
    assert body["available"] == ["PLAT"] and body["report"]["summary"]["races"] == 2
    sg_mod = next(s for s in body["report"]["series"] if s["bet"] == "SG" and s["pick"] == "modèle")
    assert [p["day"] for p in sg_mod["points"]] == ["2025-01-01", "2025-01-02"]
    later = client.get("/api/replay", params={"discipline": "ALL", "since": "2025-01-02"}).json()
    pts = next(s for s in later["report"]["series"] if s["bet"] == "SG" and s["pick"] == "modèle")[
        "points"
    ]
    assert len(pts) == 1 and pts[0]["cum"] == pts[0]["net"] == 3.5, "totals restart at since"
    assert client.get("/api/replay", params={"discipline": "LOTO"}).status_code == 404
