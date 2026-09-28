from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from predlab.core.probability import PROB_EPSILON, implied_probabilities, normalise_to_total


def test_win_probabilities_sum_to_one() -> None:
    p = normalise_to_total(np.array([3.0, 1.0, 1.0, 5.0]), 1.0)
    assert p.sum() == pytest.approx(1.0, abs=1e-9)
    assert p.argmax() == 3


def test_top3_probabilities_sum_to_three() -> None:
    p = normalise_to_total(np.array([5.0, 4.0, 3.0, 2.0, 1.0, 1.0]), 3.0)
    assert p.sum() == pytest.approx(3.0, abs=1e-9)
    assert p.max() < 1.0


def test_certainty_is_never_produced() -> None:
    p = normalise_to_total(np.array([1e12, 1.0, 1.0]), 1.0)
    assert p.max() <= 1.0 - PROB_EPSILON
    assert p.min() >= PROB_EPSILON


def test_all_zero_scores_are_refused() -> None:
    with pytest.raises(ValueError, match="all zero"):
        normalise_to_total(np.zeros(5), 1.0)


def test_infeasible_total_is_refused() -> None:
    with pytest.raises(ValueError, match="infeasible"):
        normalise_to_total(np.ones(2), 3.0)


@settings(max_examples=200, deadline=None)
@given(
    raw=st.lists(
        st.floats(min_value=0.0, max_value=1e9, allow_nan=False, allow_infinity=False),
        min_size=2,
        max_size=20,
    ),
)
def test_any_non_negative_scores_yield_a_valid_distribution(raw: list[float]) -> None:
    scores = np.array(raw)
    if scores.max() <= 0:
        with pytest.raises(ValueError):
            normalise_to_total(scores, 1.0)
        return
    p = normalise_to_total(scores, 1.0)
    assert p.sum() == pytest.approx(1.0, abs=1e-9)
    assert np.all((p >= PROB_EPSILON) & (p <= 1 - PROB_EPSILON))


def test_implied_probabilities_remove_the_overround() -> None:
    odds = np.array([2.0, 3.0, 6.0, 10.0])
    raw = 1 / odds
    assert raw.sum() > 1.0
    p = implied_probabilities(odds)
    assert p.sum() == pytest.approx(1.0)
    assert np.all(np.diff(p) < 0), "shorter odds must mean higher probability"


def test_implied_probabilities_refuse_impossible_odds() -> None:
    with pytest.raises(ValueError):
        implied_probabilities(np.array([1.0, 3.0]))
