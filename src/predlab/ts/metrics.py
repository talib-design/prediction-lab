"""Metrics chosen for what they can catch, not for what they report.

**MASE** rather than MAPE. MAPE is the industry habit and it is a bad habit here: it
divides by the actual, so it punishes under-forecasting more than over-forecasting,
explodes when the level is low -- August, every year -- and is not comparable between
series. MASE divides instead by the in-sample error of the seasonal naive, which makes
1.0 mean exactly one thing: *no better than knowing the calendar*. Above 1.0, worse
than the calendar. That is the number to put in front of a decision-maker.

**Pinball loss** rather than an error on the point forecast. It is the proper scoring
rule for quantiles: it is minimised, in expectation, precisely when the reported
quantile equals the true one. A model cannot improve it by being vague, nor by being
confident, only by being right about the shape of its own uncertainty.

**Interval coverage** alongside both. A model whose 80% interval contains the truth
55% of the time is overconfident, and neither MASE nor pinball says so in a form a
reader can act on. Coverage does, in one number, against a stated target.

MAPE is computed too -- not because it is good, but because it is what everyone else
quotes, and a result has to be translatable into the room's vocabulary.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from predlab.ts.forecast import QuantileForecast
from predlab.ts.seriesview import SEASON


class MetricError(RuntimeError):
    """A metric was asked for something it cannot compute honestly."""


def seasonal_scale(values: np.ndarray, season: int = SEASON) -> float:
    """MASE denominator: mean absolute seasonal-naive error on the training data.

    This is what makes MASE scale-free and interpretable. It is computed once, on the
    training portion only -- computing it over the whole series would leak the test
    period into the denominator and quietly shrink everyone's score.
    """
    values = np.asarray(values, dtype=np.float64)
    if len(values) <= season:
        raise MetricError(
            f"need more than {season} training observations to scale MASE, got {len(values)}"
        )
    scale = float(np.mean(np.abs(values[season:] - values[:-season])))
    if scale <= 0.0:
        raise MetricError(
            "the seasonal-naive error on the training data is zero, so MASE is "
            "undefined -- the series is exactly periodic"
        )
    return scale


def mase(actuals: np.ndarray, predictions: np.ndarray, scale: float) -> float:
    """Mean absolute error in units of the training seasonal-naive error.

    1.0 means no better than the calendar. There is no other threshold worth naming.
    """
    actuals = np.asarray(actuals, dtype=np.float64)
    predictions = np.asarray(predictions, dtype=np.float64)
    if actuals.shape != predictions.shape:
        raise MetricError(f"shape mismatch {actuals.shape} vs {predictions.shape}")
    if scale <= 0.0:
        raise MetricError(f"MASE scale must be positive, got {scale}")
    return float(np.mean(np.abs(actuals - predictions)) / scale)


def mape(actuals: np.ndarray, predictions: np.ndarray) -> float:
    """Mean absolute percentage error. Reported for translation, not for judging.

    Refuses to run on a zero actual rather than returning infinity or skipping the
    point silently -- both of which have been the source of published nonsense.
    """
    actuals = np.asarray(actuals, dtype=np.float64)
    predictions = np.asarray(predictions, dtype=np.float64)
    if np.any(actuals == 0.0):
        raise MetricError("MAPE is undefined when an actual value is zero")
    return float(np.mean(np.abs((actuals - predictions) / actuals)))


def pinball_loss(actual: float, forecast: QuantileForecast) -> float:
    """Average pinball loss over a forecast's quantiles. Lower is better.

    For level ``p`` and quantile ``q``: ``p * (y - q)`` when the actual exceeds the
    quantile, ``(1 - p) * (q - y)`` otherwise. Minimised in expectation exactly at the
    true quantile, which is what makes it proper.
    """
    levels = np.asarray(forecast.levels, dtype=np.float64)
    quantiles = np.asarray(forecast.quantiles, dtype=np.float64)
    diff = actual - quantiles
    losses = np.where(diff >= 0.0, levels * diff, (levels - 1.0) * diff)
    return float(np.mean(losses))


@dataclass(frozen=True, slots=True)
class CoverageResult:
    """How often a stated interval actually contained the truth."""

    nominal: float
    empirical: float
    n: int
    mean_width: float

    @property
    def gap(self) -> float:
        """Empirical minus nominal. Negative means overconfident."""
        return self.empirical - self.nominal

    def verdict(self, tolerance: float = 0.05) -> str:
        """A plain reading of the gap, for the report."""
        if abs(self.gap) <= tolerance:
            return "calibré"
        return "trop confiant" if self.gap < 0 else "trop prudent"


def interval_coverage(
    actuals: np.ndarray,
    forecasts: list[QuantileForecast],
    coverage: float = 0.80,
) -> CoverageResult:
    """Empirical coverage and mean width of a stated central interval.

    Width travels with coverage on purpose: an interval can always be made to cover by
    being made useless, and reporting coverage alone would hide that trade.
    """
    actuals = np.asarray(actuals, dtype=np.float64)
    if len(actuals) != len(forecasts):
        raise MetricError(f"{len(actuals)} actuals but {len(forecasts)} forecasts")
    if not forecasts:
        raise MetricError("no forecast to evaluate")
    inside, widths = [], []
    for actual, forecast in zip(actuals, forecasts, strict=True):
        low, high = forecast.interval(coverage)
        inside.append(low <= actual <= high)
        widths.append(high - low)
    return CoverageResult(
        nominal=coverage,
        empirical=float(np.mean(inside)),
        n=len(actuals),
        mean_width=float(np.mean(widths)),
    )
