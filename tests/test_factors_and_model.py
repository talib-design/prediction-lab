from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np
import polars as pl
import pytest

from predlab.backtest.splits import TimeSplit
from predlab.racing.domain import GoingMeasure, Race, Runner, WeatherForecast
from predlab.racing.features import LEVELS, MODEL_FEATURES, live_frame, load_finished
from predlab.racing.marketplus import predict, run
from predlab.racing.profile import build_profile, horse_conditions

from .synthetic_db import make_db

SPLIT = TimeSplit(date(2024, 4, 30), date(2024, 6, 30), date(2099, 1, 1))


@pytest.fixture(scope="module")
def frame(tmp_path_factory: pytest.TempPathFactory) -> pl.DataFrame:
    db = make_db(tmp_path_factory.mktemp("db") / "racing.duckdb", days=240, races_per_day=8)
    return load_finished(db, "PLAT")


def test_history_never_includes_the_race_day_or_later(frame: pl.DataFrame) -> None:
    for prefix in ("h", "hg", "ht", "j", "t"):
        assert frame.filter(pl.col(f"{prefix}_last") >= pl.col("day")).height == 0
    # A horse's first run has no past; later runs count exactly the earlier days.
    horse = frame.filter(pl.col("horse_id") == frame["horse_id"][0]).sort("day")
    assert horse["h_n"][0] is None
    days = horse["day"].to_list()
    expected = [sum(d < day for d in days) or None for day in days]
    assert horse["h_n"].to_list() == expected, "only runs of earlier days count"


def test_every_level_is_known_and_measures_are_consistent(frame: pl.DataFrame) -> None:
    for key, levels in LEVELS.items():
        assert set(frame[key].unique().to_list()) <= set(levels), key
    per_race = frame.group_by("race_id").agg(pl.col("market_p").sum(), pl.col("won").sum())
    assert np.allclose(per_race["market_p"].to_numpy(), 1.0)
    assert (per_race["won"] >= 1).all()
    assert frame["gain"].sum() == pytest.approx(0.0, abs=1e-6), "places gained sum to zero"
    top3 = frame.group_by("race_id").agg(pl.col("exp_top3").sum(), pl.len())
    assert np.allclose(top3["exp_top3"].to_numpy(), np.minimum(3, top3["len"].to_numpy()))


def test_live_frame_equals_the_historical_row(frame: pl.DataFrame) -> None:
    """The same race built live (from domain objects) gets the same model inputs."""
    target = frame.filter(pl.col("day") == date(2024, 6, 3)).sort("race_id", "number")
    race_id = target["race_id"][0]
    rows = target.filter(pl.col("race_id") == race_id)
    r = rows.row(0, named=True)
    race = Race(
        day=r["day"],
        meeting_number=1,
        race_number=int(race_id[-1]),
        off_time=datetime(2024, 6, 3, 12, tzinfo=UTC),
        country_code="FRA",
        venue_code="XXX",
        venue_name="Nulle-Part",
        discipline="PLAT",
        distance_m=r["distance_m"],
        going=GoingMeasure(value=r["going_value"], label=r["going_label"], measured_at_local=None),
        weather=WeatherForecast(
            issued_at=None,
            temperature_c=r["temperature_c"],
            wind_force=r["wind_force"],
            wind_direction=None,
            sky=r["sky"],
        ),
    )
    runners = [
        Runner(
            race_id=race.race_id,
            number=x["number"],
            name=x["horse_id"],
            horse_key=x["horse_id"],
            status="PARTANT",
            age=x["age"],
            sex=x["sex"],
            draw=x["draw"],
            weight_raw=x["weight_raw"],
            jockey=x["jockey"],
            trainer=x["trainer"],
        )
        for x in rows.iter_rows(named=True)
    ]
    assert race.race_id == race_id
    odds = dict(zip(rows["number"].to_list(), rows["odds"].to_list(), strict=True))
    live = live_frame(race, runners, odds, frame)
    for col in ("log_q", *MODEL_FEATURES):
        assert np.allclose(live[col].to_numpy(), rows[col].to_numpy()), col
    # The lab's candidates too: a promoted criterion must be computable on a live race.
    from predlab.racing import lab

    live_c, rows_c = lab.add_candidates(live, "PLAT"), lab.add_candidates(rows, "PLAT")
    for c in lab.CANDIDATES:
        if c.kind == "criterion" and c.source == "history" and "PLAT" in c.disciplines:
            assert np.allclose(
                live_c[c.column].to_numpy(), rows_c[c.column].to_numpy(), equal_nan=True
            ), c.column


def test_profile_race_conditions_look_at_the_favourite(frame: pl.DataFrame) -> None:
    rep = build_profile(frame, "PLAT")
    going = next(f for f in rep["race_factors"] if f["key"] == "going_cat")
    assert sum(lv["races"] for lv in going["levels"]) == rep["n_races"]
    for lv in going["levels"]:
        assert 0 <= lv["favourite_win_rate"] <= 1
    draw = next(f for f in rep["runner_factors"] if f["key"] == "draw_band")
    assert sum(lv["runners"] for lv in draw["levels"]) == rep["n_runners"]
    verdicts = {
        t["verdict"]
        for f in rep["runner_factors"]
        for lv in f["levels"]
        for t in (lv["result_vs_chance"], lv["missed_by_odds"])
    }
    assert verdicts <= {"+", "−", "=", "?"}


def test_horse_conditions_use_only_earlier_runs(frame: pl.DataFrame) -> None:
    horse = frame["horse_id"][0]
    day = frame.filter(pl.col("horse_id") == horse)["day"].max()
    assert isinstance(day, date)
    out = horse_conditions(frame, [horse], day, {"going_cat": "Lourd ou collant"})
    before = frame.filter((pl.col("horse_id") == horse) & (pl.col("day") < day)).height
    assert out[horse]["runs"] == before
    c = out[horse]["conditions"]["going_cat"]
    assert c["level"] == "Lourd ou collant"
    assert c["runs"] + c["elsewhere"]["runs"] == before
    assert 0 <= c["expected_top3"] <= c["runs"]


def test_vectorised_harville_matches_the_reference() -> None:
    from predlab.racing.features import harville_top3
    from predlab.racing.orders import top_k_probabilities

    rng = np.random.default_rng(3)
    for n in (4, 7, 12, 18):
        p = rng.dirichlet(np.ones(n))
        assert np.allclose(harville_top3(p), top_k_probabilities(p, 3))
    assert np.allclose(harville_top3(np.array([0.5, 0.3, 0.2])), 1.0)


def test_model_finds_the_planted_liking_for_heavy_ground(frame: pl.DataFrame) -> None:
    rep = run(frame, "PLAT", SPLIT)
    assert rep is not None
    going = next(c for c in rep["coefficients"] if c["feature"] == "f_going")
    assert going["low"] > 0, "the market ignores heavy-ground specialists; the model must not"
    recul = next(c for c in rep["coefficients"] if c["feature"] == "f_recul")
    assert not recul["active"], "no distance handicap on the flat"
    p = predict(rep["params"], frame.filter(pl.col("race_id") == frame["race_id"][0]))
    assert p.sum() == pytest.approx(1.0) and (p > 0).all()


def test_model_needs_enough_training_races(frame: pl.DataFrame) -> None:
    tiny = frame.filter(pl.col("day") < date(2024, 1, 10))
    assert run(tiny, "PLAT", SPLIT) is None
