"""Causally truncated history.

This module is the structural defence against look-ahead bias. A model never receives
the full dataset: it receives a :class:`HistoryView` whose arrays have already been
sliced to the observations strictly *before* the target draw. Future rows are not
hidden behind a guard that a careless model could bypass -- they are simply absent
from the object.

The consequence worth stating plainly: leaking the future requires deliberately
reaching outside the API you were handed, not merely forgetting a filter.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np

from predlab.core.gamespec import GameSpec


@dataclass(frozen=True, slots=True)
class HistoryView:
    """Read-only history of completed draws, strictly earlier than :attr:`as_of`.

    Attributes:
        spec: the game/era these draws belong to.
        as_of: exclusive upper bound. Every draw in this view happened before it.
        dates: ``datetime64[D]`` array, ascending, length ``n``.
        pool_draws: mapping pool name -> ``int16`` array of shape ``(n, k)``.
    """

    spec: GameSpec
    as_of: date
    dates: np.ndarray
    pool_draws: dict[str, np.ndarray]

    def __post_init__(self) -> None:
        n = len(self.dates)
        if n and self.dates.max() >= np.datetime64(self.as_of, "D"):
            raise LeakageError(
                f"HistoryView would expose a draw dated {self.dates.max()} "
                f"at or after as_of={self.as_of}"
            )
        if n > 1 and not np.all(self.dates[:-1] <= self.dates[1:]):
            raise ValueError("dates must be sorted ascending")
        for pool in self.spec.pools:
            arr = self.pool_draws.get(pool.name)
            if arr is None:
                raise ValueError(f"missing pool {pool.name!r} in view")
            if arr.shape != (n, pool.k):
                raise ValueError(
                    f"pool {pool.name!r}: expected shape {(n, pool.k)}, got {arr.shape}"
                )

    def __len__(self) -> int:
        return len(self.dates)

    @property
    def is_empty(self) -> bool:
        return len(self.dates) == 0

    def counts(self, pool_name: str) -> np.ndarray:
        """Observed frequency of every number in a pool, as a length-``size`` array.

        Index ``i`` corresponds to number ``low + i``.
        """
        pool = self.spec.pool(pool_name)
        flat = self.pool_draws[pool_name].ravel()
        return np.bincount(flat - pool.low, minlength=pool.size).astype(np.int64)

    def tail(self, window: int) -> HistoryView:
        """A further-truncated view keeping only the ``window`` most recent draws.

        Truncating the past can never introduce leakage, so this is always safe.
        """
        if window < 0:
            raise ValueError("window must be >= 0")
        if window >= len(self):
            return self
        cut = len(self) - window
        return HistoryView(
            spec=self.spec,
            as_of=self.as_of,
            dates=_freeze(self.dates[cut:]),
            pool_draws={k: _freeze(v[cut:]) for k, v in self.pool_draws.items()},
        )


class LeakageError(AssertionError):
    """Raised when a view would expose an observation at or after its cutoff."""


def _freeze(arr: np.ndarray) -> np.ndarray:
    view = arr.view()
    view.setflags(write=False)
    return view


def build_view(
    spec: GameSpec,
    dates: np.ndarray,
    pool_draws: dict[str, np.ndarray],
    as_of: date,
) -> HistoryView:
    """Slice a full, date-sorted dataset down to what was knowable before ``as_of``.

    This is the *only* supported way to construct a view from a complete dataset.
    """
    if len(dates) > 1 and not np.all(dates[:-1] <= dates[1:]):
        raise ValueError("dates must be sorted ascending before slicing")
    cutoff = np.datetime64(as_of, "D")
    n_visible = int(np.searchsorted(dates, cutoff, side="left"))
    return HistoryView(
        spec=spec,
        as_of=as_of,
        dates=_freeze(dates[:n_visible]),
        pool_draws={k: _freeze(v[:n_visible]) for k, v in pool_draws.items()},
    )
