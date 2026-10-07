"""EuroMillions eras: partition of time, pool sizes, lookup."""

from __future__ import annotations

from datetime import date, timedelta
from itertools import pairwise

import pytest

from predlab.lottery.gamespec import (
    EM_2004_02,
    EM_2011_05,
    EM_2016_09,
    EUROMILLIONS_ERAS,
    FRIDAY,
    TUESDAY,
    euromillions_era_for,
    get_spec,
)


def test_eras_partition_time_without_gap_or_overlap() -> None:
    for earlier, later in pairwise(EUROMILLIONS_ERAS):
        assert earlier.era_end is not None
        assert later.era_start == earlier.era_end + timedelta(days=1)
    assert EUROMILLIONS_ERAS[-1].era_end is None


@pytest.mark.parametrize(
    ("day", "spec"),
    [
        (date(2004, 2, 13), EM_2004_02),
        (date(2011, 5, 6), EM_2004_02),
        (date(2011, 5, 10), EM_2011_05),
        (date(2016, 9, 23), EM_2011_05),
        (date(2016, 9, 27), EM_2016_09),
        (date(2026, 10, 6), EM_2016_09),
    ],
)
def test_era_lookup(day: date, spec: object) -> None:
    assert euromillions_era_for(day) is spec


def test_date_before_first_draw_has_no_era() -> None:
    with pytest.raises(ValueError):
        euromillions_era_for(date(2004, 2, 12))


def test_pools_follow_the_published_format() -> None:
    assert [s.pool("stars").high for s in EUROMILLIONS_ERAS] == [9, 11, 12]
    for spec in EUROMILLIONS_ERAS:
        main = spec.pool("main")
        assert (main.low, main.high, main.k) == (1, 50, 5)
        assert spec.pool("stars").k == 2


def test_draw_weekdays() -> None:
    assert EM_2004_02.draw_weekdays == frozenset({FRIDAY})
    assert EM_2011_05.draw_weekdays == frozenset({TUESDAY, FRIDAY})


def test_default_era_is_the_current_format() -> None:
    assert get_spec("euromillions") is EM_2016_09
