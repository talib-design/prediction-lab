"""Walk-forward evaluation. One rule: the model never sees the period it forecasts.

The rule is enforced structurally rather than by convention. At each step the engine
builds a :class:`SeriesView` truncated before the target period and hands *that* to
the model; there is no argument through which the future could arrive. A model that
wanted to cheat would have to reach outside the object it was given, and the test
suite contains one that tries, to prove the boundary holds.

Evaluation is per horizon, never pooled. A one-month-ahead forecast and a
six-month-ahead forecast are different problems, and averaging them produces a number
that describes neither -- the usual way a forecasting result is made to look better
than it is.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from predlab.data.sources.dares import MonthlySeries, month_index
from predlab.ts.forecast import DEFAULT_LEVELS, Forecaster, QuantileForecast
from predlab.ts.metrics import (
    CoverageResult,
    interval_coverage,
    mape,
    mase,
    pinball_loss,
    seasonal_scale,
)
from predlab.ts.seriesview import SEASON, build_view


class BacktestError(RuntimeError):
    """The backtest cannot be run as configured."""


@dataclass(frozen=True, slots=True)
class HorizonResult:
    """One model's performance at one horizon."""

    model: str
    horizon: int
    n: int
    mase: float
    mape: float
    mae: float
    pinball: float
    coverage_80: CoverageResult
    coverage_90: CoverageResult
    periods: tuple[str, ...] = field(repr=False, default=())
    actuals: tuple[float, ...] = field(repr=False, default=())
    medians: tuple[float, ...] = field(repr=False, default=())
    # The 80% interval, kept so a reader can see the model at work rather than only
    # its score. A forecast chart without its band shows a line that is always wrong
    # by some amount and never says by how much it expected to be.
    lows: tuple[float, ...] = field(repr=False, default=())
    highs: tuple[float, ...] = field(repr=False, default=())

    def summary(self) -> dict[str, object]:
        return {
            "model": self.model,
            "horizon": self.horizon,
            "n": self.n,
            "mase": round(self.mase, 4),
            "mape": round(self.mape, 4),
            "mae": round(self.mae, 1),
            "pinball": round(self.pinball, 2),
            "coverage_80": round(self.coverage_80.empirical, 3),
            "coverage_80_verdict": self.coverage_80.verdict(),
            "coverage_80_width": round(self.coverage_80.mean_width, 1),
            "coverage_90": round(self.coverage_90.empirical, 3),
        }


@dataclass(frozen=True, slots=True)
class BacktestResult:
    """Everything one run produced, plus what it took to reproduce it."""

    series_start: str
    series_end: str
    train_end: str
    horizons: tuple[int, ...]
    scale: float
    results: tuple[HorizonResult, ...]

    def for_horizon(self, h: int) -> tuple[HorizonResult, ...]:
        rows = [r for r in self.results if r.horizon == h]
        return tuple(sorted(rows, key=lambda r: r.mase))

    def reference(self, h: int) -> HorizonResult | None:
        """The seasonal naive at this horizon -- the bar everything else must clear."""
        for r in self.results:
            if r.horizon == h and r.model == "seasonal_naive":
                return r
        return None


def walk_forward(
    series: MonthlySeries,
    forecasters: tuple[Forecaster, ...],
    *,
    train_end: str,
    horizons: tuple[int, ...] = (1, 3, 6, 12),
    levels: tuple[float, ...] = DEFAULT_LEVELS,
) -> BacktestResult:
    """Evaluate each model at each horizon, stepping one month at a time.

    ``train_end`` is the last period that is *never* evaluated: every origin lies
    strictly after it, so the MASE scale is computed on data no forecast is scored
    against. Getting this wrong is how a backtest quietly grades itself on its own
    training set.
    """
    first = month_index(series.start)
    last = month_index(series.end)
    cut = month_index(train_end)
    if not first < cut < last:
        raise BacktestError(
            f"train_end={train_end} must lie strictly inside {series.start}..{series.end}"
        )
    if not horizons or any(h < 1 for h in horizons):
        raise BacktestError(f"horizons must all be >= 1, got {horizons}")

    values = np.asarray(series.values, dtype=np.float64)
    train = values[: cut - first + 1]
    if len(train) <= SEASON:
        raise BacktestError(
            f"training window holds {len(train)} months; MASE needs more than {SEASON}"
        )
    scale = seasonal_scale(train)

    results: list[HorizonResult] = []
    for model in forecasters:
        for h in horizons:
            periods: list[str] = []
            actuals: list[float] = []
            forecasts: list[QuantileForecast] = []
            # Origins run from the end of training to the last one whose target is
            # still inside the series.
            for origin in range(cut, last - h + 1):
                target_idx = origin + h
                view = build_view(series, as_of=series.periods[origin - first + 1])
                try:
                    produced = model.forecast(view, (h,), levels)
                except Exception as exc:
                    raise BacktestError(
                        f"{model.name} failed at origin {view.as_of}, horizon {h}: {exc}"
                    ) from exc
                forecast = produced[0]
                expected = series.periods[target_idx - first]
                if forecast.period != expected:
                    raise BacktestError(
                        f"{model.name} returned a forecast for {forecast.period} when "
                        f"{expected} was requested -- a period-alignment bug"
                    )
                periods.append(expected)
                actuals.append(float(values[target_idx - first]))
                forecasts.append(forecast)

            if not forecasts:
                raise BacktestError(f"horizon {h} leaves no evaluable period after {train_end}")
            actual_arr = np.asarray(actuals, dtype=np.float64)
            median_arr = np.asarray([f.median() for f in forecasts], dtype=np.float64)
            results.append(
                HorizonResult(
                    model=model.name,
                    horizon=h,
                    n=len(actuals),
                    mase=mase(actual_arr, median_arr, scale),
                    mape=mape(actual_arr, median_arr),
                    mae=float(np.mean(np.abs(actual_arr - median_arr))),
                    pinball=float(
                        np.mean(
                            [pinball_loss(a, f) for a, f in zip(actuals, forecasts, strict=True)]
                        )
                    ),
                    coverage_80=interval_coverage(actual_arr, forecasts, 0.80),
                    coverage_90=interval_coverage(actual_arr, forecasts, 0.90),
                    periods=tuple(periods),
                    actuals=tuple(actuals),
                    medians=tuple(float(m) for m in median_arr),
                    lows=tuple(f.interval(0.80)[0] for f in forecasts),
                    highs=tuple(f.interval(0.80)[1] for f in forecasts),
                )
            )

    return BacktestResult(
        series_start=series.start,
        series_end=series.end,
        train_end=train_end,
        horizons=horizons,
        scale=scale,
        results=tuple(results),
    )
