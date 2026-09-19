from __future__ import annotations

import numpy as np
import pytest

from predlab.core.gamespec import GameSpec, NumberPool
from predlab.eval.metrics import (
    count_matches,
    expected_calibration_error,
    score_pool,
)
from predlab.models.base import PoolForecast, normalise_to_k


def uniform_forecast(pool: NumberPool) -> PoolForecast:
    return PoolForecast(pool=pool, inclusion_probs=np.full(pool.size, pool.marginal_probability))


def test_uniform_scores_match_the_closed_form() -> None:
    pool = NumberPool("main", 1, 49, 5)
    p = 5 / 49
    score = score_pool(uniform_forecast(pool), np.array([1, 2, 3, 4, 5]))
    expected_ll = -(5 * np.log(p) + 44 * np.log1p(-p)) / 49
    expected_brier = (5 * (p - 1) ** 2 + 44 * p**2) / 49
    assert score.log_loss == pytest.approx(expected_ll)
    assert score.brier == pytest.approx(expected_brier)


def test_uniform_puts_the_same_mass_on_any_outcome() -> None:
    """The reason mass_on_drawn is a readable baseline: it is constant under fairness."""
    pool = NumberPool("main", 1, 49, 5)
    fc = uniform_forecast(pool)
    for drawn in ([1, 2, 3, 4, 5], [10, 20, 30, 40, 49], [7, 13, 22, 38, 44]):
        score = score_pool(fc, np.array(drawn))
        assert score.mass_on_drawn == pytest.approx(5 * 5 / 49)
        assert score.mass_lift == pytest.approx(1.0)


def test_mass_lift_rises_when_the_model_was_right() -> None:
    pool = NumberPool("main", 1, 49, 5)
    scores = np.ones(49)
    scores[:5] = 10.0  # ten times the weight on 1..5
    fc = PoolForecast(pool=pool, inclusion_probs=normalise_to_k(scores, pool))
    hit = score_pool(fc, np.array([1, 2, 3, 4, 5]))
    miss = score_pool(fc, np.array([40, 41, 42, 43, 44]))
    assert hit.mass_lift > 1.0 > miss.mass_lift


def test_score_rejects_an_illegal_outcome(loto: GameSpec) -> None:
    pool = loto.pool("main")
    with pytest.raises(ValueError):
        score_pool(uniform_forecast(pool), np.array([1, 2, 3, 4, 50]))


def test_count_matches() -> None:
    assert count_matches((1, 2, 3, 4, 5), np.array([3, 4, 5, 6, 7])) == 3
    assert count_matches((1, 2, 3, 4, 5), np.array([6, 7, 8, 9, 10])) == 0


def test_calibration_of_a_perfectly_calibrated_model_is_near_zero() -> None:
    rng = np.random.default_rng(0)
    p = rng.uniform(0.05, 0.95, size=200_000)
    y = (rng.random(size=p.shape) < p).astype(float)
    ece, _, _, counts = expected_calibration_error(p, y, n_bins=10)
    assert ece < 0.01
    assert counts.sum() == len(p)


def test_calibration_detects_overconfidence() -> None:
    rng = np.random.default_rng(1)
    truth = np.full(50_000, 0.5)
    y = (rng.random(size=truth.shape) < truth).astype(float)
    overconfident = np.full(50_000, 0.9)
    ece, _, _, _ = expected_calibration_error(overconfident, y, n_bins=10)
    assert ece == pytest.approx(0.4, abs=0.02)


def test_empty_bins_are_reported_as_nan_not_dropped() -> None:
    p = np.full(100, 0.05)
    y = np.zeros(100)
    _, centres, empirical, counts = expected_calibration_error(p, y, n_bins=10)
    assert counts[0] == 100
    assert np.isnan(centres[5]) and np.isnan(empirical[5])
