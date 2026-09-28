from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from predlab.racing.backtest import ForecastError, run_backtest, score, validate
from predlab.racing.events import RaceCard, RaceEvent, load_events
from predlab.racing.knowledge import Knowledge
from predlab.racing.models import (
    CalibratedMarketModel,
    FormModel,
    HorseWinRateModel,
    MarketModel,
    RandomModel,
    UniformModel,
    default_models,
)
from predlab.racing.report import build_report, compare, render_markdown
from predlab.racing.sources.pmu.client import FetchResult
from predlab.racing.store.normalized import build
from predlab.racing.store.raw import RawStore
from predlab.racing.synthetic import OracleModel, make_world

from .conftest import fixture_bytes


class Snoop(UniformModel):
    """Tries to cheat: records everything it can see at prediction time."""

    name = "snoop"

    def __init__(self, events: list[RaceEvent]) -> None:
        self.by_id = {e.card.race_id: e for e in events}
        self.violations: list[str] = []

    def predict(self, card: RaceCard, knowledge: Knowledge) -> np.ndarray:
        for race_id in knowledge.released:
            released = self.by_id[race_id]
            if released.known_at > card.prediction_time or race_id == card.race_id:
                self.violations.append(race_id)
            if released.card.day == card.day:
                self.violations.append(f"same-day {race_id}")
        return super().predict(card, knowledge)


def test_no_model_ever_sees_a_result_before_it_was_known() -> None:
    world = make_world(400, seed=3)
    snoop = Snoop(world.events)
    run_backtest(world.events, [snoop], horizon_minutes=25)
    assert snoop.violations == []


def test_history_does_accumulate() -> None:
    world = make_world(200, seed=4)
    seen: list[int] = []

    class Counter(UniformModel):
        def predict(self, card: RaceCard, knowledge: Knowledge) -> np.ndarray:
            seen.append(len(knowledge.released))
            return super().predict(card, knowledge)

    run_backtest(world.events, [Counter()], horizon_minutes=25)
    assert seen[0] == 0 and seen[-1] > 150, "races of previous days must be released"


def test_forecasts_are_validated() -> None:
    card = make_world(1).events[0].card
    with pytest.raises(ForecastError):
        validate(np.full(card.n, 0.5), card, "bad")
    with pytest.raises(ForecastError):
        validate(np.ones(card.n - 1) / (card.n - 1), card, "short")


def test_scoring_handles_a_dead_heat() -> None:
    p = np.array([0.5, 0.3, 0.2])
    s = score(p, [0, 2])
    assert s["log_loss"] == pytest.approx(-(np.log(0.5) + np.log(0.2)) / 2)
    assert s["brier"] == pytest.approx(0.0**2 + 0.3**2 + 0.3**2)
    assert s["top1"] == 1.0 and s["rr"] == 1.0


def test_proper_score_ranks_the_models_as_it_should() -> None:
    world = make_world(3000, seed=5)
    models: list[Any] = [RandomModel(), UniformModel(), MarketModel(), OracleModel(world.truth)]
    result = run_backtest(world.events, models, horizon_minutes=25)
    ll = {r.name: r.series("log_loss").mean() for r in result.runs}
    assert ll["oracle"] < ll["market"] < ll["uniform"] < ll["random"]


def test_calibration_recovers_the_planted_bias() -> None:
    world = make_world(6000, seed=6, flb=0.7, market_noise=0.0)
    model = CalibratedMarketModel()
    run_backtest(world.events, [model], horizon_minutes=25)
    assert model.alpha == pytest.approx(1 / 0.7, abs=0.12)


def test_history_models_use_history() -> None:
    world = make_world(50, seed=7)
    card = world.events[0].card
    knowledge = Knowledge()
    for m in (HorseWinRateModel(), FormModel()):
        p = m.predict(card, knowledge)
        assert p == pytest.approx(np.full(card.n, 1 / card.n)), "no history: no preference"


def test_report_on_synthetic_data() -> None:
    world = make_world(600, seed=8)
    result = run_backtest(world.events, default_models(), horizon_minutes=25)
    report = build_report(result)
    assert {c["model"] for c in report["comparisons"]} == {
        "random",
        "uniform",
        "horse_win_rate",
        "form",
        "market",
    }
    md = render_markdown(report)
    assert "## 1. Puissance" in md and "market_calibrated" in md
    assert any(c.get("verdict") == "moins bon que la référence" for c in compare(result, "all"))


# ------------------------------------------------------------------ database loading


def _db(tmp_path: Path) -> Path:
    store = RawStore(tmp_path / "raw")
    t = datetime(2026, 9, 28, 9, 0, tzinfo=UTC)
    store.record(
        FetchResult("u", 200, fixture_bytes("programme_2026-09-27_R1C1_partial.json"), t),
        key="programme/2026-09-27",
        endpoint="programme",
        purpose="backfill",
    )
    store.record(
        FetchResult("u", 200, fixture_bytes("participants_2026-09-27_R1C1_partial.json"), t),
        key="participants/2026-09-27/R1C1",
        endpoint="participants",
        purpose="backfill",
    )
    build(store, tmp_path / "normalized", tmp_path / "racing.duckdb")
    return tmp_path / "racing.duckdb"


def test_loading_uses_only_quotes_published_before_the_horizon(tmp_path: Path) -> None:
    db = _db(tmp_path)
    [event] = load_events(db, horizon_minutes=25, discipline="ATTELE")
    assert event.card.n == 10, "the non-runner is not a starter"
    assert event.card.market_complete
    for s in event.card.starters:
        assert s.odds_reported_at is not None
        assert s.odds_reported_at <= event.card.prediction_time, "no post-horizon quote"
    assert event.outcome.winners == (4,)
    assert event.known_at > event.card.off_time

    [early] = load_events(db, horizon_minutes=40, discipline="ATTELE")
    assert not early.card.market_complete, "at T-40 the T-33 quote did not exist yet"
