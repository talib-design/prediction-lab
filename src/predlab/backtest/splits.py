"""Time-ordered splits.

There is no shuffling anywhere in this module, and that is the point. A random split
of draws would let a model be tuned on draws that happen after the ones it is tested
on, which for a time series is not a mild optimism -- it is the difference between
measuring prediction and measuring memorisation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np


@dataclass(frozen=True, slots=True)
class TimeSplit:
    """Three consecutive, non-overlapping windows over the draw timeline.

    ``train`` is what a model may learn from, ``validation`` is where free parameters
    (a window length, a smoothing constant) are chosen, and ``test`` is looked at once.
    Choosing a parameter on ``test`` and then reporting ``test`` performance is the
    most common way to manufacture a result, so the split is an object the run record
    carries, not a convention someone remembers.
    """

    train_end: date
    validation_end: date
    test_end: date

    def __post_init__(self) -> None:
        if not self.train_end < self.validation_end < self.test_end:
            raise ValueError(
                "split boundaries must be strictly increasing: "
                f"{self.train_end} < {self.validation_end} < {self.test_end}"
            )

    def phase_of(self, day: date) -> str:
        if day <= self.train_end:
            return "train"
        if day <= self.validation_end:
            return "validation"
        if day <= self.test_end:
            return "test"
        return "future"

    def as_dict(self) -> dict[str, str]:
        return {
            "train_end": self.train_end.isoformat(),
            "validation_end": self.validation_end.isoformat(),
            "test_end": self.test_end.isoformat(),
        }


def proportional_split(dates: np.ndarray, train: float = 0.6, validation: float = 0.2) -> TimeSplit:
    """Split the timeline by position, keeping chronological order."""
    if not 0 < train < 1 or not 0 < validation < 1 or train + validation >= 1:
        raise ValueError("train and validation must be positive fractions summing below 1")
    n = len(dates)
    if n < 3:
        raise ValueError("need at least 3 draws to form three windows")
    i_train = max(0, int(n * train) - 1)
    i_val = max(i_train + 1, int(n * (train + validation)) - 1)
    i_val = min(i_val, n - 2)
    return TimeSplit(
        train_end=_as_date(dates[i_train]),
        validation_end=_as_date(dates[i_val]),
        test_end=_as_date(dates[-1]),
    )


def _as_date(value: np.datetime64) -> date:
    return value.astype("datetime64[D]").astype(date)
