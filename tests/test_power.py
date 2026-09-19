from __future__ import annotations

import numpy as np
import pytest

from predlab.core.gamespec import LOTO_2019_11, NumberPool
from predlab.eval.power import (
    draws_required,
    minimum_detectable_effect,
    simulate_fair_counts,
    uniformity_monte_carlo,
)

MAIN = LOTO_2019_11.pool("main")


def test_more_draws_lower_the_detection_floor() -> None:
    small = minimum_detectable_effect(MAIN, 500)
    large = minimum_detectable_effect(MAIN, 50_000)
    assert large.absolute_effect < small.absolute_effect


def test_multiplicity_correction_raises_the_floor() -> None:
    plain = minimum_detectable_effect(MAIN, 1075, multiplicity_correction=False)
    corrected = minimum_detectable_effect(MAIN, 1075, multiplicity_correction=True)
    assert corrected.absolute_effect > plain.absolute_effect


def test_the_current_era_cannot_detect_a_small_bias() -> None:
    """The finding that frames every Milestone 1 result.

    With the draws actually available, only an enormous departure from fairness is
    detectable. "No signal found" therefore says far less than it sounds like.
    """
    floor = minimum_detectable_effect(MAIN, 1075, multiplicity_correction=True)
    assert floor.relative_effect > 0.30


def test_detecting_a_plausible_bias_would_take_longer_than_the_game_has_existed() -> None:
    # Three draws a week since 1976 is roughly 7 800 draws.
    assert draws_required(MAIN, 0.05) > 50_000


def test_required_draws_and_detection_floor_agree() -> None:
    n = draws_required(MAIN, 0.20)
    floor = minimum_detectable_effect(MAIN, n)
    assert floor.relative_effect == pytest.approx(0.20, rel=0.05)


def test_invalid_inputs_are_refused() -> None:
    with pytest.raises(ValueError):
        minimum_detectable_effect(MAIN, 0)
    with pytest.raises(ValueError):
        minimum_detectable_effect(MAIN, 100, alpha=1.5)
    with pytest.raises(ValueError):
        draws_required(MAIN, 0.0)


def test_simulated_fair_counts_have_the_right_mean_and_variance() -> None:
    """Exactly k numbers per draw makes counts less variable than multinomial."""
    pool = NumberPool("main", 1, 49, 5)
    rng = np.random.default_rng(0)
    counts = simulate_fair_counts(pool, n_draws=200, n_simulations=400, rng=rng)
    assert counts.sum(axis=1).tolist() == [1000] * 400
    p = pool.marginal_probability
    assert counts.mean() == pytest.approx(200 * p, rel=0.02)
    multinomial_var = 200 * 5 * (1 / 49) * (1 - 1 / 49)
    assert counts.var() < multinomial_var


def test_fair_counts_are_not_flagged_as_biased() -> None:
    pool = NumberPool("chance", 1, 10, 1)
    rng = np.random.default_rng(1)
    observed = simulate_fair_counts(pool, n_draws=400, n_simulations=1, rng=rng)[0]
    _, p_value = uniformity_monte_carlo(observed, pool, 400, n_simulations=400, seed=2)
    assert p_value > 0.05


def test_a_blatant_bias_is_flagged() -> None:
    pool = NumberPool("chance", 1, 10, 1)
    observed = np.array([200, *([20] * 9)])
    _, p_value = uniformity_monte_carlo(observed, pool, 380, n_simulations=400, seed=3)
    assert p_value < 0.01


def test_uniformity_test_has_the_right_false_positive_rate() -> None:
    """Calibration of the descriptive test itself.

    Run on many genuinely fair histories, a 5% test must reject about 5% of the time.
    Too often and it manufactures anomalies; too rarely and it is blind to real ones.
    Observed here: 5% on 40 histories of the main pool during development.
    """
    pool = NumberPool("chance", 1, 10, 1)
    rng = np.random.default_rng(42)
    histories = simulate_fair_counts(pool, n_draws=300, n_simulations=50, rng=rng)
    rejections = sum(
        uniformity_monte_carlo(h, pool, 300, n_simulations=200, seed=i)[1] < 0.05
        for i, h in enumerate(histories)
    )
    assert rejections <= 8, f"{rejections}/50 false positives is too many for a 5% test"
