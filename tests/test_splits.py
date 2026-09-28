from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pytest

from predlab.backtest.splits import TimeSplit, proportional_split

START = date(2024, 1, 1)


def _dates(n: int) -> np.ndarray:
    return np.array([np.datetime64(START + timedelta(days=i), "D") for i in range(n)])


def test_split_boundaries_must_increase() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        TimeSplit(date(2021, 1, 1), date(2020, 1, 1), date(2022, 1, 1))


def test_proportional_split_is_chronological() -> None:
    split = proportional_split(_dates(100), train=0.6, validation=0.2)
    assert split.train_end < split.validation_end < split.test_end
    assert split.phase_of(START) == "train"
    assert split.phase_of(split.validation_end) == "validation"
    assert split.phase_of(split.test_end) == "test"
    assert split.phase_of(split.test_end + timedelta(days=1)) == "future"
    assert set(split.as_dict()) == {"train_end", "validation_end", "test_end"}


def test_proportional_split_refuses_bad_inputs() -> None:
    with pytest.raises(ValueError):
        proportional_split(_dates(2))
    with pytest.raises(ValueError):
        proportional_split(_dates(100), train=0.9, validation=0.2)
