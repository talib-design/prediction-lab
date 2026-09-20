"""Causally truncated view of a monthly series.

The counterpart, for continuous series, of :mod:`predlab.core.historyview`, and for
the same reason: a forecaster never receives the whole series. It receives a
:class:`SeriesView` already sliced to the periods strictly *before* the one being
forecast. The future is not hidden behind a guard that a careless model could bypass
-- it is absent from the object it was handed.

This matters more here than it does for a lottery. In a time series the future is
genuinely informative, so a leak does not merely flatter a model, it manufactures
skill out of nothing and does so silently: the backtest simply reports excellent
numbers. Every published forecasting result that later failed in production had this
bug available to it.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from predlab.data.sources.dares import MonthlySeries, month_index, period_of

SEASON = 12
"""Months in a seasonal cycle. Monthly data is all this engine handles today."""


class LeakageError(RuntimeError):
    """A view would have exposed an observation at or after its cutoff."""


@dataclass(frozen=True, slots=True)
class SeriesView:
    """Read-only observations strictly earlier than :attr:`as_of`.

    Attributes:
        as_of: ``YYYY-MM``. Exclusive upper bound; every value here precedes it.
        start: ``YYYY-MM`` of ``values[0]``.
        values: ``float64`` array, ascending in time, contiguous months, read-only.
    """

    as_of: str
    start: str
    values: np.ndarray

    def __post_init__(self) -> None:
        if self.values.ndim != 1:
            raise ValueError(f"values must be 1-D, got shape {self.values.shape}")
        span = month_index(self.start) + len(self.values)
        if span > month_index(self.as_of):
            raise LeakageError(
                f"view starting {self.start} with {len(self.values)} months would "
                f"reach {period_of(span - 1)}, at or after as_of={self.as_of}"
            )
        if self.values.flags.writeable:
            raise ValueError("values must be read-only; build views with of()")

    def __len__(self) -> int:
        return len(self.values)

    @property
    def end(self) -> str:
        """Last period present. Raises if the view is empty."""
        if not len(self.values):
            raise ValueError("an empty view has no last period")
        return period_of(month_index(self.start) + len(self.values) - 1)

    def period_at(self, offset: int) -> str:
        """Period of ``values[offset]``, supporting negative offsets."""
        if not -len(self.values) <= offset < len(self.values):
            raise IndexError(f"offset {offset} outside a view of {len(self.values)}")
        if offset < 0:
            offset += len(self.values)
        return period_of(month_index(self.start) + offset)

    def horizon_period(self, h: int) -> str:
        """The period ``h`` steps after the last observed one (``h >= 1``).

        The first forecastable period is ``h = 1``, which is ``as_of`` itself when the
        view ends immediately before it -- the usual case in a walk-forward backtest.
        """
        if h < 1:
            raise ValueError(f"horizon must be >= 1, got {h}")
        if not len(self.values):
            raise ValueError("an empty view has no horizon")
        return period_of(month_index(self.end) + h)

    def season_position(self, h: int) -> int:
        """Calendar month (1-12) of the period ``h`` steps ahead.

        A seasonal model needs to know *which* month it is forecasting, and deriving
        it from the period keeps that independent of how many observations happen to
        be in the view.
        """
        return month_index(self.horizon_period(h)) % SEASON + 1


def _frozen(values: np.ndarray) -> np.ndarray:
    arr = np.ascontiguousarray(values, dtype=np.float64)
    arr.setflags(write=False)
    return arr


def build_view(series: MonthlySeries, as_of: str) -> SeriesView:
    """Everything in ``series`` strictly before ``as_of``.

    The slice is computed from periods rather than from a count, so a series that
    starts at a different month still truncates at the right place.
    """
    first = month_index(series.start)
    cut = max(0, min(len(series), month_index(as_of) - first))
    return SeriesView(
        as_of=as_of,
        start=series.start,
        values=_frozen(np.asarray(series.values[:cut], dtype=np.float64)),
    )


def view_of(values: list[float] | np.ndarray, start: str, as_of: str) -> SeriesView:
    """Build a view directly from values. Mainly for tests and synthetic cases."""
    return SeriesView(as_of=as_of, start=start, values=_frozen(np.asarray(values)))
