"""What a forecast is in this project: a distribution, never a number.

A point forecast cannot be wrong in any useful sense. "12 400 offers in October" is
either exactly right, which it never is, or wrong by an amount nobody agreed how to
judge. Worse, it hides the only thing a decision-maker actually needs, which is how
far out the truth could plausibly be -- and a model with no stated uncertainty cannot
be caught being overconfident, so it never is.

So every forecast here is a set of quantiles, and the evaluation scores those
quantiles with the pinball loss and checks whether stated intervals contain the truth
as often as they claim. A model whose 80% interval covers 55% of outcomes is broken,
and this is the machinery that says so.

How the quantiles are obtained matters as much as that they exist. Each baseline
derives them from **its own past errors at the same horizon, computed only on the
visible history** -- not from a normality assumption, which this series (August every
year, March 2020) would violate. That makes the intervals empirical, testable, and
honest about the method's actual track record rather than about an idealised one.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np

from predlab.ts.seriesview import SeriesView

DEFAULT_LEVELS: tuple[float, ...] = (0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)
"""Quantile levels every model reports. The median is the point forecast if one is
needed, and 0.10/0.90 plus 0.05/0.95 give the 80% and 90% intervals whose coverage
the evaluation checks."""


class ForecastError(RuntimeError):
    """A forecast is not a usable distribution."""


@dataclass(frozen=True, slots=True)
class QuantileForecast:
    """Predicted quantiles for one period.

    Attributes:
        period: ``YYYY-MM`` being forecast.
        horizon: steps ahead of the last observed period (``>= 1``).
        levels: ascending probabilities in (0, 1).
        quantiles: predicted values, aligned with ``levels``, non-decreasing.
    """

    period: str
    horizon: int
    levels: tuple[float, ...]
    quantiles: tuple[float, ...]

    def __post_init__(self) -> None:
        if self.horizon < 1:
            raise ForecastError(f"horizon must be >= 1, got {self.horizon}")
        if len(self.levels) != len(self.quantiles):
            raise ForecastError(f"{len(self.levels)} levels but {len(self.quantiles)} quantiles")
        if not self.levels:
            raise ForecastError("a forecast with no quantile is not a forecast")
        if any(not 0.0 < p < 1.0 for p in self.levels):
            raise ForecastError(f"levels must lie strictly in (0, 1): {self.levels}")
        if any(a >= b for a, b in zip(self.levels, self.levels[1:], strict=False)):
            raise ForecastError(f"levels must be strictly ascending: {self.levels}")
        if any(not np.isfinite(q) for q in self.quantiles):
            raise ForecastError(f"non-finite quantile in {self.quantiles}")
        # Crossing quantiles are not a cosmetic defect: they make the implied
        # distribution incoherent, and the pinball loss would still return a number.
        if any(a > b for a, b in zip(self.quantiles, self.quantiles[1:], strict=False)):
            raise ForecastError(f"quantiles cross: {self.quantiles}")

    def median(self) -> float:
        """The 0.50 quantile, or the nearest level if 0.50 was not requested."""
        idx = int(np.argmin(np.abs(np.asarray(self.levels) - 0.5)))
        return self.quantiles[idx]

    def interval(self, coverage: float) -> tuple[float, float]:
        """The central interval with the requested nominal coverage.

        Raises if the two levels it needs were not reported, rather than silently
        substituting a wider pair and overstating the interval.
        """
        low, high = (1.0 - coverage) / 2.0, 1.0 - (1.0 - coverage) / 2.0
        try:
            i = self.levels.index(round(low, 6))
            j = self.levels.index(round(high, 6))
        except ValueError:
            raise ForecastError(
                f"a {coverage:.0%} interval needs levels {low:.3f} and {high:.3f}, "
                f"which are not among {self.levels}"
            ) from None
        return self.quantiles[i], self.quantiles[j]


@runtime_checkable
class Forecaster(Protocol):
    """What the backtest requires of a model.

    ``forecast`` receives a view that physically cannot contain the target period, and
    returns one :class:`QuantileForecast` per requested horizon.
    """

    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    def forecast(
        self,
        view: SeriesView,
        horizons: tuple[int, ...],
        levels: tuple[float, ...] = DEFAULT_LEVELS,
    ) -> tuple[QuantileForecast, ...]: ...


def quantiles_from_relative_residuals(
    centre: float,
    ratios: np.ndarray,
    levels: tuple[float, ...],
    *,
    floor: float = 0.0,
) -> tuple[float, ...]:
    """Empirical quantiles built from *relative* errors, not absolute ones.

    Absolute residuals assume the spread of a method's errors is stable over time.
    On this series it is not: the level runs from about 4 000 in 1996 to 19 000 in
    2022, so an error of 1 000 is enormous at one end of the history and routine at
    the other. Pooling them produces an interval sized for some average level and
    therefore too narrow whenever the series is high -- which is exactly when a
    forecast is being used. The first backtest showed this plainly: every baseline
    came out "overconfident", all of them by a similar amount, which is the signature
    of a construction fault rather than of five separate modelling failures.

    ``ratios`` are past ``actual / predicted``. Their quantiles scale the point
    forecast multiplicatively, so the interval's width grows with the level, as the
    errors of a count series do. Ratios are centred on their own median for the same
    reason the absolute version is: the 0.50 quantile must remain the method's own
    point forecast, not a quietly bias-corrected version of it.
    """
    if ratios.size == 0:
        return tuple(float(max(centre, floor)) for _ in levels)
    factors = np.quantile(ratios, np.asarray(levels, dtype=np.float64))
    median = float(np.median(ratios))
    if median <= 0.0:
        # Degenerate history (a method that mostly predicted above every actual).
        # Fall back to a point forecast rather than inventing a scale.
        return tuple(float(max(centre, floor)) for _ in levels)
    values = np.maximum(centre * factors / median, floor)
    return tuple(float(v) for v in np.maximum.accumulate(values))


def quantiles_from_residuals(
    centre: float,
    residuals: np.ndarray,
    levels: tuple[float, ...],
    *,
    floor: float = 0.0,
) -> tuple[float, ...]:
    """Empirical quantiles around a point forecast, from that method's own errors.

    ``residuals`` are past ``actual - predicted`` values of the same method at the same
    horizon, computed on visible history only. Their empirical quantiles are added to
    ``centre``: no distributional assumption, and the resulting interval is as wide as
    the method's track record says it should be.

    With too few residuals to estimate anything, the spread is not invented -- the
    forecast degenerates to a point repeated at every level, which the calibration
    check will then correctly report as having no coverage at all.

    ``floor`` clips the result from below (counts cannot be negative). Clipping is
    applied after the quantiles are taken, so it cannot reorder them.
    """
    if residuals.size == 0:
        return tuple(float(max(centre, floor)) for _ in levels)
    offsets = np.quantile(residuals, np.asarray(levels, dtype=np.float64))
    # Centre the offsets on their own median, so that the 0.50 quantile is exactly
    # the method's point forecast. Without this the residuals' own median would be
    # added in, silently turning every baseline into a bias-corrected variant of
    # itself: `seasonal_naive` would no longer be last year's same month, a reader
    # checking the number by hand would not find it, and the comparison between
    # methods would confound the method with an undeclared correction.
    #
    # The cost is deliberate. A method that really is biased now produces intervals
    # sitting off-centre, and the coverage check reports that as poor calibration --
    # which is the honest outcome, rather than hiding the bias inside the interval.
    offsets = offsets - float(np.median(residuals))
    values = np.maximum(centre + offsets, floor)
    # np.quantile is monotone in the level, and adding a constant then clipping from
    # below both preserve order -- but assert it rather than trust it.
    return tuple(float(v) for v in np.maximum.accumulate(values))
