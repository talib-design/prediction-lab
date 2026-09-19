"""The anti-leakage invariant, tested as a property rather than on examples."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from predlab.core.gamespec import LOTO_2019_11, GameSpec
from predlab.core.historyview import HistoryView, LeakageError, build_view

from .conftest import synthetic_draws


@settings(max_examples=150, deadline=None)
@given(
    n=st.integers(min_value=0, max_value=120),
    offset_days=st.integers(min_value=-5, max_value=260),
)
def test_no_draw_at_or_after_the_cutoff_is_ever_visible(n: int, offset_days: int) -> None:
    spec = LOTO_2019_11
    start = date(2020, 1, 1)
    dates, pools = synthetic_draws(spec, n, seed=n, start=start)
    as_of = start + timedelta(days=offset_days)

    view = build_view(spec, dates, pools, as_of=as_of)

    assert len(view) == int((dates < np.datetime64(as_of, "D")).sum())
    if len(view):
        assert view.dates.max() < np.datetime64(as_of, "D")
    for pool in spec.pools:
        assert view.pool_draws[pool.name].shape == (len(view), pool.k)


@settings(max_examples=60, deadline=None)
@given(offset_days=st.integers(min_value=0, max_value=260), window=st.integers(0, 200))
def test_tail_never_widens_the_view(offset_days: int, window: int) -> None:
    spec = LOTO_2019_11
    start = date(2020, 1, 1)
    dates, pools = synthetic_draws(spec, 100, seed=1, start=start)
    view = build_view(spec, dates, pools, as_of=start + timedelta(days=offset_days))
    tail = view.tail(window)
    assert len(tail) <= len(view)
    assert len(tail) == min(window, len(view))
    if len(tail):
        assert tail.dates.max() < np.datetime64(view.as_of, "D")


def test_constructing_a_leaky_view_directly_raises(loto: GameSpec) -> None:
    """Even bypassing build_view, the dataclass refuses to hold future rows."""
    dates, pools = synthetic_draws(loto, 10, seed=3, start=date(2020, 1, 1))
    with pytest.raises(LeakageError):
        HistoryView(spec=loto, as_of=date(2020, 1, 1), dates=dates, pool_draws=pools)


def test_view_arrays_are_read_only(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 10, seed=4, start=date(2020, 1, 1))
    view = build_view(loto, dates, pools, as_of=date(2021, 1, 1))
    with pytest.raises(ValueError):
        view.pool_draws["main"][0, 0] = 42
    with pytest.raises(ValueError):
        view.dates[0] = np.datetime64("2030-01-01", "D")


def test_counts_sum_to_k_times_n(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 50, seed=5, start=date(2020, 1, 1))
    view = build_view(loto, dates, pools, as_of=date(2021, 1, 1))
    for pool in loto.pools:
        counts = view.counts(pool.name)
        assert counts.shape == (pool.size,)
        assert counts.sum() == len(view) * pool.k


def test_empty_history_is_legal(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 10, seed=6, start=date(2020, 1, 1))
    view = build_view(loto, dates, pools, as_of=date(2019, 1, 1))
    assert view.is_empty
    assert view.counts("main").sum() == 0
