from __future__ import annotations

import numpy as np
import pytest

from predlab.eval.uncertainty import (
    benjamini_hochberg,
    block_bootstrap,
    paired_block_permutation_test,
    suggested_block_size,
)


def test_bootstrap_interval_brackets_the_point_estimate() -> None:
    rng = np.random.default_rng(0)
    series = rng.normal(loc=2.0, scale=1.0, size=500)
    ci = block_bootstrap(series, n_resamples=500, seed=1)
    assert ci.low < ci.point < ci.high
    assert ci.point == pytest.approx(series.mean())


def test_bootstrap_interval_narrows_with_more_data() -> None:
    rng = np.random.default_rng(1)
    short = block_bootstrap(rng.normal(size=100), n_resamples=500, seed=2)
    long = block_bootstrap(rng.normal(size=4000), n_resamples=500, seed=2)
    assert (long.high - long.low) < (short.high - short.low)


def test_block_bootstrap_is_wider_than_iid_on_autocorrelated_data() -> None:
    """The whole reason this module exists: i.i.d. resampling understates uncertainty."""
    rng = np.random.default_rng(2)
    noise = rng.normal(size=2000)
    persistent = np.convolve(noise, np.ones(50) / 50, mode="same")  # strongly smoothed
    wide = block_bootstrap(persistent, n_resamples=800, block_size=100, seed=3)
    narrow = block_bootstrap(persistent, n_resamples=800, block_size=1, seed=3)
    assert (wide.high - wide.low) > (narrow.high - narrow.low)


def test_identical_series_are_indistinguishable() -> None:
    rng = np.random.default_rng(3)
    x = rng.normal(size=300)
    result = paired_block_permutation_test(x, x.copy(), n_permutations=500, seed=4)
    assert result.mean_difference == pytest.approx(0.0)
    assert result.p_value > 0.5
    assert result.verdict() == "indistinguishable"


def test_a_large_consistent_difference_is_detected() -> None:
    rng = np.random.default_rng(4)
    baseline = rng.normal(size=400)
    better = baseline - 1.0  # lower is better
    result = paired_block_permutation_test(better, baseline, n_permutations=500, seed=5)
    assert result.p_value < 0.01
    assert result.verdict() == "better"


def test_p_value_is_never_reported_as_zero() -> None:
    baseline = np.zeros(200)
    better = np.full(200, -10.0)
    result = paired_block_permutation_test(better, baseline, n_permutations=99, seed=6)
    assert result.p_value == pytest.approx(1 / 100)


def test_mismatched_lengths_are_refused() -> None:
    with pytest.raises(ValueError, match="same length"):
        paired_block_permutation_test(np.zeros(10), np.zeros(11))


def test_benjamini_hochberg_rejects_nothing_under_the_null() -> None:
    rng = np.random.default_rng(5)
    p = rng.uniform(size=49)  # 49 balls, all fair
    assert benjamini_hochberg(p, q=0.05).sum() <= 1


def test_benjamini_hochberg_is_stricter_than_uncorrected() -> None:
    p = np.array([0.001, 0.02, 0.03, 0.04, *[0.5] * 45])
    uncorrected = (p < 0.05).sum()
    assert benjamini_hochberg(p, q=0.05).sum() < uncorrected


def test_benjamini_hochberg_finds_a_strong_signal() -> None:
    p = np.array([1e-9, 1e-8, *[0.5] * 47])
    assert benjamini_hochberg(p, q=0.05).sum() == 2


def test_suggested_block_size_grows_with_n() -> None:
    assert suggested_block_size(8) == 2
    assert suggested_block_size(1000) == 10


def test_dependent_correction_is_strictly_more_conservative() -> None:
    """Benjamini-Yekutieli vs Benjamini-Hochberg on the same p-values.

    Wasserman states the BH theorem with a factor C_m that equals 1 only when the
    p-values are independent. This project's comparisons are not: every model is
    scored against the same reference on the same draws.
    """
    p = np.array([0.001, 0.004, 0.02, 0.03, *[0.6] * 8])
    independent = benjamini_hochberg(p, q=0.05, dependent=False).sum()
    dependent = benjamini_hochberg(p, q=0.05, dependent=True).sum()
    assert dependent < independent


def test_dependent_correction_matches_the_harmonic_factor() -> None:
    m = 12
    c_m = sum(1.0 / i for i in range(1, m + 1))
    # A p-value just inside the BY threshold for rank 1 must be rejected...
    inside = np.full(m, 0.9)
    inside[0] = 0.05 / (m * c_m) * 0.99
    assert benjamini_hochberg(inside, q=0.05).sum() == 1
    # ...and one just outside it must not.
    outside = np.full(m, 0.9)
    outside[0] = 0.05 / (m * c_m) * 1.01
    assert benjamini_hochberg(outside, q=0.05).sum() == 0


def test_a_genuinely_strong_signal_survives_the_dependent_correction() -> None:
    """Being conservative must not mean being blind."""
    p = np.array([1e-9, 1e-8, *[0.5] * 47])
    assert benjamini_hochberg(p, q=0.05, dependent=True).sum() == 2
