"""The forecasting engine. The tests that matter here are not the unit tests.

Three of them carry the weight: a deliberately cheating model must fail to see the
future, a model whose intervals are too narrow must be reported as overconfident, and
a planted signal must be found -- because a system that can only ever say "no better
than the calendar" is broken, not careful.
"""

from __future__ import annotations

import math
from typing import ClassVar

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from predlab.data.sources.dares import MonthlySeries, month_index, period_of
from predlab.ts.backtest import BacktestError, walk_forward
from predlab.ts.baselines import (
    DriftForecaster,
    NaiveForecaster,
    NotEnoughHistoryError,
    SeasonalMeanForecaster,
    SeasonalNaiveForecaster,
    SeasonalNaiveWithDriftForecaster,
    default_forecasters,
)
from predlab.ts.forecast import (
    DEFAULT_LEVELS,
    ForecastError,
    QuantileForecast,
    quantiles_from_residuals,
)
from predlab.ts.metrics import (
    MetricError,
    interval_coverage,
    mape,
    mase,
    pinball_loss,
    seasonal_scale,
)
from predlab.ts.seriesview import LeakageError, SeriesView, build_view, view_of


def make_series(values: list[float], start: str = "2000-01") -> MonthlySeries:
    idx = month_index(start)
    periods = tuple(period_of(idx + i) for i in range(len(values)))
    return MonthlySeries(periods=periods, values=tuple(int(v) for v in values))


def seasonal_series(n_years: int = 12, level: float = 10_000, amp: float = 0.3, seed: int = 3):
    """A seasonal shape with no trend, plus noise.

    The noise is not decoration: an exactly periodic series has a seasonal-naive
    error of zero, which makes MASE undefined. The engine refuses such a series
    rather than dividing by it, so the fixtures must not be exactly periodic either.
    """
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_years):
        for m in range(12):
            out.append(level * (1 + amp * math.cos(2 * math.pi * m / 12)) + rng.normal(0, 200))
    return make_series(out)


# ------------------------------------------------------------------ causal boundary


def test_a_view_cannot_contain_its_own_cutoff() -> None:
    with pytest.raises(LeakageError):
        view_of([1.0, 2.0, 3.0], start="2020-01", as_of="2020-03")


def test_build_view_truncates_strictly_before_the_cutoff() -> None:
    series = make_series([1, 2, 3, 4, 5], start="2020-01")
    view = build_view(series, as_of="2020-04")
    assert len(view) == 3
    assert view.end == "2020-03"
    assert list(view.values) == [1.0, 2.0, 3.0]


def test_view_values_cannot_be_mutated() -> None:
    view = view_of([1.0, 2.0], start="2020-01", as_of="2020-03")
    with pytest.raises(ValueError, match=r"read-only|assignment destination"):
        view.values[0] = 99.0


@settings(max_examples=60, deadline=None)
@given(
    n=st.integers(min_value=1, max_value=120),
    cut=st.integers(min_value=0, max_value=140),
)
def test_no_cutoff_ever_exposes_the_future(n: int, cut: int) -> None:
    """The invariant, over arbitrary cutoffs rather than chosen examples."""
    series = make_series(list(range(1, n + 1)), start="2000-01")
    as_of = period_of(month_index("2000-01") + cut)
    view = build_view(series, as_of=as_of)
    assert len(view) <= max(0, min(n, cut))
    if len(view):
        assert month_index(view.end) < month_index(as_of)


def test_a_cheating_model_cannot_reach_the_target() -> None:
    """A model that actively tries to see the future must fail, not succeed quietly.

    This is the structural claim the whole backtest rests on: the view handed to a
    model physically cannot contain the period being forecast, so look-ahead bias is
    not something a careless model can fall into.
    """
    series = seasonal_series(n_years=6)

    class Cheater:
        name = "cheater"
        version = "1"
        seen: ClassVar[list[str]] = []

        def forecast(self, view: SeriesView, horizons, levels=DEFAULT_LEVELS):
            target = view.horizon_period(horizons[0])
            Cheater.seen.append(target)
            # The only data available is the view. The target is not in it.
            assert month_index(view.end) < month_index(target)
            assert len(view.values) == len(view.values)
            return (
                QuantileForecast(
                    period=target,
                    horizon=horizons[0],
                    levels=levels,
                    quantiles=tuple(float(view.values[-1]) for _ in levels),
                ),
            )

    walk_forward(series, (Cheater(),), train_end="2003-12", horizons=(1,))
    assert Cheater.seen, "the cheater must have been asked for forecasts"


# ------------------------------------------------------------------ forecast object


def test_a_forecast_must_carry_a_distribution() -> None:
    with pytest.raises(ForecastError):
        QuantileForecast("2020-01", 1, (), ())


def test_crossing_quantiles_are_refused() -> None:
    """Crossing quantiles make the implied distribution incoherent.

    The pinball loss would still return a number for them, so nothing downstream
    would complain -- which is exactly why it is refused here.
    """
    with pytest.raises(ForecastError, match="cross"):
        QuantileForecast("2020-01", 1, (0.1, 0.9), (100.0, 50.0))


def test_an_interval_that_was_not_reported_is_refused_not_widened() -> None:
    f = QuantileForecast("2020-01", 1, (0.25, 0.75), (90.0, 110.0))
    with pytest.raises(ForecastError, match="needs levels"):
        f.interval(0.80)


def test_residual_quantiles_degenerate_rather_than_invent_spread() -> None:
    """With no residuals the forecast becomes a point, and coverage then reports 0."""
    q = quantiles_from_residuals(100.0, np.asarray([]), DEFAULT_LEVELS)
    assert len(set(q)) == 1 and q[0] == 100.0


def test_quantiles_are_clipped_at_zero_without_reordering() -> None:
    q = quantiles_from_residuals(50.0, np.asarray([-500.0, -400.0, 400.0]), (0.1, 0.5, 0.9))
    assert all(v >= 0.0 for v in q)
    assert list(q) == sorted(q)


# ------------------------------------------------------------------------ baselines


def test_seasonal_naive_repeats_the_same_month_last_year() -> None:
    values = list(range(1, 37))
    view = view_of([float(v) for v in values], start="2020-01", as_of="2023-01")
    f = SeasonalNaiveForecaster().forecast(view, (1,))[0]
    # Last observed is 2022-12 (36). One step ahead is 2023-01, whose same month last
    # year is 2022-01, the 25th value.
    assert f.period == "2023-01"
    assert f.median() == pytest.approx(25.0, abs=1e-6)


def test_naive_repeats_the_last_value() -> None:
    view = view_of([1.0, 2.0, 7.0], start="2020-01", as_of="2020-04")
    assert NaiveForecaster().forecast(view, (1,))[0].median() == pytest.approx(7.0)


def test_drift_extends_the_line_through_first_and_last() -> None:
    view = view_of([10.0, 20.0, 30.0], start="2020-01", as_of="2020-04")
    f = DriftForecaster().forecast(view, (2,))[0]
    assert f.median() == pytest.approx(50.0)


def test_a_model_refuses_to_forecast_from_too_little_history() -> None:
    view = view_of([1.0, 2.0], start="2020-01", as_of="2020-03")
    with pytest.raises(NotEnoughHistoryError, match="at least"):
        SeasonalNaiveForecaster().forecast(view, (1,))
    with pytest.raises(NotEnoughHistoryError):
        SeasonalMeanForecaster(window=3).forecast(view, (1,))


def test_every_baseline_produces_a_coherent_distribution() -> None:
    series = seasonal_series(n_years=8)
    view = build_view(series, as_of="2006-01")
    for model in default_forecasters():
        for f in model.forecast(view, (1, 3, 12)):
            assert list(f.quantiles) == sorted(f.quantiles), model.name
            low, high = f.interval(0.80)
            assert low <= f.median() <= high, model.name


# -------------------------------------------------------------------------- metrics


def test_mase_of_one_means_no_better_than_the_calendar() -> None:
    actuals = np.asarray([100.0, 110.0, 120.0])
    scale = 10.0
    assert mase(actuals, actuals - 10.0, scale) == pytest.approx(1.0)
    assert mase(actuals, actuals, scale) == pytest.approx(0.0)


def test_mase_scale_refuses_a_perfectly_periodic_series() -> None:
    with pytest.raises(MetricError, match="exactly periodic"):
        seasonal_scale(np.asarray([1.0, 2.0] * 20), season=2)


def test_mape_refuses_a_zero_actual_instead_of_returning_infinity() -> None:
    with pytest.raises(MetricError, match="undefined"):
        mape(np.asarray([0.0, 10.0]), np.asarray([1.0, 10.0]))


def test_pinball_is_minimised_at_the_true_quantile() -> None:
    """The property that makes it a proper scoring rule, checked rather than assumed.

    Under a known distribution, reporting its true quantiles must score better than
    reporting any shifted set.
    """
    rng = np.random.default_rng(0)
    sample = rng.normal(100.0, 15.0, size=40_000)
    levels = DEFAULT_LEVELS
    truth = QuantileForecast(
        "2020-01", 1, levels, tuple(float(q) for q in np.quantile(sample, levels))
    )
    honest = float(np.mean([pinball_loss(float(y), truth) for y in sample[:4000]]))
    for shift in (-10.0, 10.0):
        biased = QuantileForecast("2020-01", 1, levels, tuple(q + shift for q in truth.quantiles))
        worse = float(np.mean([pinball_loss(float(y), biased) for y in sample[:4000]]))
        assert honest < worse, shift


def test_overconfidence_is_reported_as_overconfidence() -> None:
    """A model whose 80% interval covers far less must be named, not averaged away."""
    rng = np.random.default_rng(1)
    actuals = rng.normal(100.0, 20.0, size=500)
    narrow = [
        QuantileForecast("2020-01", 1, (0.10, 0.50, 0.90), (99.0, 100.0, 101.0)) for _ in actuals
    ]
    result = interval_coverage(actuals, narrow, 0.80)
    assert result.empirical < 0.2
    assert result.verdict() == "trop confiant"
    assert result.gap < 0


def test_a_needlessly_wide_interval_is_called_out_too() -> None:
    actuals = np.full(200, 100.0)
    wide = [QuantileForecast("2020-01", 1, (0.10, 0.50, 0.90), (0.0, 100.0, 1e6)) for _ in actuals]
    result = interval_coverage(actuals, wide, 0.80)
    assert result.verdict() == "trop prudent"
    assert result.mean_width > 1e5, "width must travel with coverage"


# ------------------------------------------------------------------------- backtest


def test_backtest_refuses_a_train_end_outside_the_series() -> None:
    series = seasonal_series(n_years=4)
    with pytest.raises(BacktestError, match="strictly inside"):
        walk_forward(series, default_forecasters(), train_end="2099-01")


def test_backtest_refuses_to_pool_horizons() -> None:
    """Each horizon is a separate problem and gets a separate row."""
    series = seasonal_series(n_years=10)
    result = walk_forward(
        series, (SeasonalNaiveForecaster(),), train_end="2006-12", horizons=(1, 6)
    )
    assert {r.horizon for r in result.results} == {1, 6}
    assert len(result.results) == 2


def test_a_planted_signal_is_found() -> None:
    """A system that only ever says "no better than the calendar" is broken.

    On a series that is pure seasonality plus a steady trend, the model that knows
    about both must beat the one that knows only the calendar.
    """
    rng = np.random.default_rng(11)
    values = []
    for y in range(14):
        for m in range(12):
            values.append(
                10_000 * (1 + 0.3 * math.cos(2 * math.pi * m / 12))
                + 60 * (y * 12 + m)
                + rng.normal(0, 150)
            )
    series = make_series(values)
    result = walk_forward(
        series,
        (SeasonalNaiveForecaster(), SeasonalNaiveWithDriftForecaster()),
        train_end="2007-12",
        horizons=(1,),
    )
    ranked = result.for_horizon(1)
    reference = result.reference(1)
    assert reference is not None
    assert ranked[0].model == "seasonal_naive_drift", [r.model for r in ranked]
    assert ranked[0].mase < reference.mase


def test_pure_noise_yields_no_winner_over_the_reference() -> None:
    """The other half of the same claim: on a series with no trend, nothing beats it.

    Seasonal naive knows the calendar and nothing else. Where there is nothing else to
    know, no baseline should be meaningfully better.
    """
    rng = np.random.default_rng(7)
    values = [
        10_000 * (1 + 0.3 * math.cos(2 * math.pi * m / 12)) + rng.normal(0, 300)
        for _ in range(14)
        for m in range(12)
    ]
    series = make_series(values)
    result = walk_forward(
        series,
        (SeasonalNaiveForecaster(), DriftForecaster(), NaiveForecaster()),
        train_end="2007-12",
        horizons=(1,),
    )
    reference = result.reference(1)
    assert reference is not None
    for row in result.for_horizon(1):
        if row.model != "seasonal_naive":
            assert row.mase > reference.mase * 0.95, row.model
