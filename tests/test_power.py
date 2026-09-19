from __future__ import annotations

import numpy as np
import pytest

from predlab.core.gamespec import LOTO_2019_11, NumberPool
from predlab.eval.power import (
    analytic_power,
    draws_required,
    fair_null_distribution,
    minimum_detectable_effect,
    simulate_fair_counts,
    uniformity_monte_carlo,
    uniformity_p_value,
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


def test_cached_null_matches_the_one_shot_call() -> None:
    """The convenience wrapper and the cached path must agree exactly."""
    pool = NumberPool("chance", 1, 10, 1)
    counts = np.array([45, 38, 41, 39, 44, 36, 40, 42, 37, 38])
    direct = uniformity_monte_carlo(counts, pool, 400, n_simulations=300, seed=9)
    null = fair_null_distribution(pool, 400, n_simulations=300, seed=9)
    cached = uniformity_p_value(counts, pool, 400, null)
    assert direct == cached


def test_a_cached_null_is_reusable_across_datasets() -> None:
    pool = NumberPool("chance", 1, 10, 1)
    null = fair_null_distribution(pool, 300, n_simulations=300, seed=10)
    rng = np.random.default_rng(11)
    fair = simulate_fair_counts(pool, 300, 3, rng)
    for counts in fair:
        _, p_value = uniformity_p_value(counts, pool, 300, null)
        assert 0.0 < p_value <= 1.0
    _, biased_p = uniformity_p_value(np.array([150, *([17] * 9)]), pool, 303, null)
    assert biased_p < 0.01


def test_analytic_power_inverts_the_detection_floor() -> None:
    """Feed the floor back in and the power that produced it must come out."""
    for n in (500, 1075, 10_000):
        floor = minimum_detectable_effect(MAIN, n, power=0.80)
        recovered = analytic_power(MAIN, n, floor.relative_effect)
        assert recovered == pytest.approx(0.80, abs=0.01)


def test_analytic_power_rises_with_effect_and_sample() -> None:
    assert analytic_power(MAIN, 1075, 0.6) > analytic_power(MAIN, 1075, 0.3)
    assert analytic_power(MAIN, 5000, 0.3) > analytic_power(MAIN, 1075, 0.3)


def test_analytic_power_at_zero_effect_is_the_significance_level() -> None:
    assert analytic_power(MAIN, 1075, 0.0, alpha=0.05) == pytest.approx(0.05)
