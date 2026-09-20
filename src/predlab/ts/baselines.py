"""Baselines, and a correction the backtest forced on the way this project reasoned.

The DARES cadre series has a seasonal amplitude of 33% of the annual level against a
median year-on-year move of 12%, from which it seemed to follow that ``seasonal_naive``
had to be the bar to clear. The measurement says otherwise: at every horizon tested,
plain ``naive`` beats it (MASE 1.78 against 2.52 one month out). The reasoning had
skipped a step. Seasonality being large does not make last year's same month a good
forecast, because reaching it costs twelve months of drift -- and this series' level
runs from 4 000 to 19 000 and back to 12 000. The seasonal shape is real; paying a
year of level change to get at it is not worth it.

What does win one month out is ``seasonal_naive_drift``: last year's same month moved
by the recent change in level, i.e. calendar *and* level together. So the conclusion
survives in a weaker form -- seasonality helps, but only once the level is corrected.

Two consequences kept in the code. Every baseline is still reported, ``naive``
included, because which one is the bar is an empirical question and this is the case
that proves it. And at horizon 12 ``seasonal_naive`` reduces *exactly* to ``naive``
(last year's same month, twelve months ahead, is the last observation), which is why
their scores coincide there -- arithmetic, not a bug.

Every baseline derives its quantiles the same way, from its own relative errors at the
same horizon measured on visible history only, so the comparison between them is a
comparison of methods rather than of interval-widening tricks.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from predlab.ts.forecast import (
    DEFAULT_LEVELS,
    QuantileForecast,
    quantiles_from_relative_residuals,
)
from predlab.ts.seriesview import SEASON, SeriesView


class NotEnoughHistoryError(RuntimeError):
    """A method was asked to forecast from less history than it needs."""


@dataclass(frozen=True, slots=True)
class _Base:
    """Shared plumbing: one point forecast per horizon, plus empirical quantiles."""

    def _point(self, values: np.ndarray, h: int, month_of_h: int) -> float:
        raise NotImplementedError

    def _min_history(self) -> int:
        raise NotImplementedError

    def _insample_ratios(self, values: np.ndarray, h: int) -> np.ndarray:
        """Relative errors this method would have made at horizon ``h``.

        Walks the visible history, refits nothing (these methods have nothing to fit)
        and records ``actual / predicted`` each time. The intervals are therefore the
        method's own track record rather than an assumption about it, and they are
        *relative* because this series' level varies fivefold: an absolute error pooled
        across thirty years sizes the interval for an average level and is too narrow
        at every high one.

        A prediction of zero or below yields no usable ratio and is dropped rather
        than clamped, which would fabricate a fake error of a convenient size.
        """
        need = self._min_history()
        out: list[float] = []
        for cut in range(need, len(values) - h + 1):
            past = values[:cut]
            month = (cut + h - 1) % SEASON + 1
            predicted = self._point(past, h, month)
            if predicted > 0.0:
                out.append(float(values[cut + h - 1] / predicted))
        return np.asarray(out, dtype=np.float64)

    def forecast(
        self,
        view: SeriesView,
        horizons: tuple[int, ...],
        levels: tuple[float, ...] = DEFAULT_LEVELS,
    ) -> tuple[QuantileForecast, ...]:
        values = np.asarray(view.values, dtype=np.float64)
        if len(values) < self._min_history():
            raise NotEnoughHistoryError(
                f"{self.name} needs at least {self._min_history()} observations, "
                f"the view has {len(values)}"
            )
        out: list[QuantileForecast] = []
        for h in horizons:
            centre = self._point(values, h, view.season_position(h))
            out.append(
                QuantileForecast(
                    period=view.horizon_period(h),
                    horizon=h,
                    levels=levels,
                    quantiles=quantiles_from_relative_residuals(
                        centre, self._insample_ratios(values, h), levels
                    ),
                )
            )
        return tuple(out)

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def version(self) -> str:
        return "1"


@dataclass(frozen=True, slots=True)
class NaiveForecaster(_Base):
    """Tomorrow equals today. The floor: any method must beat this to exist."""

    @property
    def name(self) -> str:
        return "naive"

    def _min_history(self) -> int:
        return 1

    def _point(self, values: np.ndarray, h: int, month_of_h: int) -> float:
        return float(values[-1])


@dataclass(frozen=True, slots=True)
class SeasonalNaiveForecaster(_Base):
    """The same month, last year. **The reference on this series.**

    It carries no information about the economy whatsoever -- it only knows the
    calendar. That it is hard to beat here is the finding, not a failure.
    """

    @property
    def name(self) -> str:
        return "seasonal_naive"

    def _min_history(self) -> int:
        return SEASON

    def _point(self, values: np.ndarray, h: int, month_of_h: int) -> float:
        # The most recent observation of the same calendar month.
        back = SEASON - ((h - 1) % SEASON)
        return float(values[-back])


@dataclass(frozen=True, slots=True)
class DriftForecaster(_Base):
    """Extend the straight line through the first and last observations.

    A trend model with one parameter and no ability to fit noise -- which makes it a
    fair test of whether the series has a usable trend at all.
    """

    @property
    def name(self) -> str:
        return "drift"

    def _min_history(self) -> int:
        return 2

    def _point(self, values: np.ndarray, h: int, month_of_h: int) -> float:
        slope = (values[-1] - values[0]) / (len(values) - 1)
        return float(values[-1] + h * slope)


@dataclass(frozen=True, slots=True)
class SeasonalMeanForecaster(_Base):
    """Average of the last ``window`` observations of the same calendar month.

    Seasonal naive uses one past year and therefore inherits that year's noise in
    full. Averaging several trades responsiveness for stability; which wins is an
    empirical question, and the point of having both.
    """

    window: int = 3

    @property
    def name(self) -> str:
        return f"seasonal_mean_{self.window}"

    def _min_history(self) -> int:
        return SEASON * self.window

    def _point(self, values: np.ndarray, h: int, month_of_h: int) -> float:
        back = SEASON - ((h - 1) % SEASON)
        picks = [values[-back - SEASON * i] for i in range(self.window)]
        return float(np.mean(picks))


@dataclass(frozen=True, slots=True)
class SeasonalNaiveWithDriftForecaster(_Base):
    """Last year's same month, moved by the recent year-on-year change.

    The simplest model that uses both the calendar and the economy: the seasonal
    shape from a year ago, shifted by how much the level has moved since. If nothing
    beats this, the series' predictable part is calendar plus level, and that is worth
    knowing before anyone builds something more elaborate.
    """

    @property
    def name(self) -> str:
        return "seasonal_naive_drift"

    def _min_history(self) -> int:
        return SEASON * 2

    def _point(self, values: np.ndarray, h: int, month_of_h: int) -> float:
        back = SEASON - ((h - 1) % SEASON)
        last_year = float(values[-back])
        # Year-on-year change over the most recent complete year, per month.
        recent = float(np.mean(values[-SEASON:]))
        previous = float(np.mean(values[-2 * SEASON : -SEASON]))
        step = (recent - previous) / SEASON
        # ``values[-back]`` sits at period T-(back-1) and the target at T+h, so the
        # two are h + back - 1 months apart. Applying the drift over any other span
        # under-corrects (or over-corrects) by a whole year at h = 1.
        return last_year + step * (h + back - 1)


def default_forecasters() -> tuple[_Base, ...]:
    """The set every report runs, cheapest first.

    ``seasonal_naive`` is listed second on purpose: it is the reference the others are
    judged against, and ``naive`` is there to show how much of the apparent skill is
    just the calendar.
    """
    return (
        NaiveForecaster(),
        SeasonalNaiveForecaster(),
        DriftForecaster(),
        SeasonalMeanForecaster(window=3),
        SeasonalNaiveWithDriftForecaster(),
    )
