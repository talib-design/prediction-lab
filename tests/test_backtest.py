from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import numpy as np
import pytest

from predlab.backtest.engine import BacktestConfig, dataset_fingerprint, run_backtest
from predlab.backtest.splits import TimeSplit, proportional_split
from predlab.core.gamespec import GameSpec
from predlab.core.historyview import HistoryView
from predlab.models.base import Forecast
from predlab.models.baselines import (
    FrequencyPredictor,
    RandomTicketPredictor,
    UniformPredictor,
    default_baselines,
)
from predlab.models.selection import TopKPolicy

from .conftest import synthetic_draws

START = date(2020, 1, 1)


class PeekingPredictor:
    """A model that tries to cheat, to prove it cannot.

    It records the latest date it was shown. If the engine ever leaked a future draw,
    that date would reach or exceed the target.
    """

    name = "peeker"
    version = "1"

    def __init__(self, spec: GameSpec) -> None:
        self.spec = spec
        self.seen: list[tuple[date, date | None]] = []
        self._uniform = UniformPredictor(spec=spec)

    def config(self) -> dict[str, Any]:
        return {}

    def forecast(self, history: HistoryView, target_date: date) -> Forecast:
        latest = history.dates.max().astype("datetime64[D]").astype(date) if len(history) else None
        self.seen.append((target_date, latest))
        return self._uniform.forecast(history, target_date)


def test_engine_never_shows_a_model_the_target_draw(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 260, seed=0, start=START)
    peeker = PeekingPredictor(loto)
    run_backtest(loto, dates, pools, [peeker], TopKPolicy(), BacktestConfig(min_train_draws=200))
    assert peeker.seen
    for target, latest in peeker.seen:
        assert latest is not None and latest < target


def test_every_target_is_evaluated_once_in_chronological_order(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 250, seed=1, start=START)
    result = run_backtest(
        loto,
        dates,
        pools,
        [UniformPredictor(spec=loto)],
        TopKPolicy(),
        BacktestConfig(min_train_draws=200),
    )
    run = result.runs[0]
    assert len(run.target_dates) == 50
    assert run.target_dates == sorted(run.target_dates)
    assert len(set(run.target_dates)) == 50


def test_random_and_uniform_score_identically(loto: GameSpec) -> None:
    """If these ever diverge, the harness is broken, not the models."""
    dates, pools = synthetic_draws(loto, 300, seed=2, start=START)
    result = run_backtest(
        loto,
        dates,
        pools,
        [UniformPredictor(spec=loto), RandomTicketPredictor(spec=loto, seed=5)],
        TopKPolicy(),
        BacktestConfig(min_train_draws=200),
    )
    a = result.run_for("uniform").series("main", "log_loss")
    b = result.run_for("random").series("main", "log_loss")
    np.testing.assert_allclose(a, b)


def test_results_are_reproducible(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 280, seed=3, start=START)
    kwargs = {"policy": TopKPolicy(), "config": BacktestConfig(min_train_draws=200)}
    first = run_backtest(loto, dates, pools, default_baselines(loto), **kwargs)
    second = run_backtest(loto, dates, pools, default_baselines(loto), **kwargs)
    assert first.dataset_fingerprint == second.dataset_fingerprint
    for r1, r2 in zip(first.runs, second.runs, strict=True):
        np.testing.assert_allclose(r1.series("main", "log_loss"), r2.series("main", "log_loss"))


def test_fingerprint_changes_when_a_single_number_changes(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 50, seed=4, start=START)
    tampered = {k: v.copy() for k, v in pools.items()}
    tampered["main"][0, 0] = 1 if tampered["main"][0, 0] != 1 else 2
    assert dataset_fingerprint(dates, pools) != dataset_fingerprint(dates, tampered)


def test_rolling_window_sees_exactly_its_window(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 300, seed=5, start=START)
    result = run_backtest(
        loto,
        dates,
        pools,
        [FrequencyPredictor(spec=loto, window=40)],
        TopKPolicy(),
        BacktestConfig(min_train_draws=200),
    )
    assert set(result.runs[0].n_training_draws.tolist()) == {40}


def test_phases_follow_the_split(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 300, seed=6, start=START)
    split = proportional_split(dates)
    result = run_backtest(
        loto,
        dates,
        pools,
        [UniformPredictor(spec=loto)],
        TopKPolicy(),
        BacktestConfig(min_train_draws=200),
        split=split,
    )
    run = result.runs[0]
    for day, phase in zip(run.target_dates, run.phases, strict=True):
        assert phase == split.phase_of(day)


def test_unsorted_input_is_refused(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 50, seed=7, start=START)
    with pytest.raises(ValueError, match="sorted ascending"):
        run_backtest(loto, dates[::-1].copy(), pools, [UniformPredictor(spec=loto)], TopKPolicy())


def test_too_little_history_is_an_explicit_error(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 30, seed=8, start=START)
    with pytest.raises(ValueError, match="min_train_draws"):
        run_backtest(
            loto,
            dates,
            pools,
            [UniformPredictor(spec=loto)],
            TopKPolicy(),
            BacktestConfig(min_train_draws=200),
        )


def test_split_boundaries_must_increase() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        TimeSplit(date(2021, 1, 1), date(2020, 1, 1), date(2022, 1, 1))


def test_proportional_split_is_chronological(loto: GameSpec) -> None:
    dates, _ = synthetic_draws(loto, 100, seed=9, start=START)
    split = proportional_split(dates, train=0.6, validation=0.2)
    assert split.train_end < split.validation_end < split.test_end
    assert split.phase_of(START) == "train"
    assert split.phase_of(split.test_end + timedelta(days=1)) == "future"


def test_provenance_records_what_is_needed_to_reproduce(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 250, seed=10, start=START)
    result = run_backtest(
        loto,
        dates,
        pools,
        default_baselines(loto),
        TopKPolicy(),
        BacktestConfig(min_train_draws=200),
    )
    p = result.provenance()
    assert p["dataset_fingerprint"] and p["code_version"] and p["created_at"]
    assert p["config"]["min_train_draws"] == 200
    assert {m["name"] for m in p["models"]} == {m.name for m in default_baselines(loto)}
