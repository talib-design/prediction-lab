"""The analysis battery: exact nulls are calibrated, planted effects are found."""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import stats

from predlab.lottery.analysis import (
    BALLS,
    all_combinations,
    bh_adjust,
    bins_from_pmf,
    causal_selection_test,
    current_gaps,
    exact_pmf,
    gap_top_rule,
    homogeneity_test,
    hot_rule,
    incidence,
    repeat_rule,
    repeated_combinations,
    selection_stats,
    serial_tests,
    top_weights,
    uniformity_test,
)
from predlab.lottery.gamespec import NumberPool


def fair(n: int, size: int = 50, k: int = 5, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return np.sort(np.argsort(rng.random((n, size)), axis=1)[:, :k] + 1, axis=1)


def biased(n: int, favoured: tuple[int, ...], factor: float, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    w = np.ones(50)
    w[np.array(favoured) - 1] = factor
    p = w / w.sum()
    return np.sort(
        np.array([rng.choice(50, size=5, replace=False, p=p) + 1 for _ in range(n)]), axis=1
    )


def test_top_weights_share_ties_and_sum_to_m() -> None:
    w = top_weights(np.array([3.0, 2, 2, 2, 1]), 2)
    assert w.tolist() == pytest.approx([1, 1 / 3, 1 / 3, 1 / 3, 0])
    assert w.sum() == pytest.approx(2)


def test_current_gaps() -> None:
    x = incidence(np.array([[1, 2, 3, 4, 5], [1, 6, 7, 8, 9], [1, 2, 10, 11, 12]]), BALLS)
    g = current_gaps(x, 3)
    assert g[0] == 0  # number 1 just out
    assert g[1] == 0  # number 2 in last draw
    assert g[5] == 1  # number 6 one draw ago
    assert g[2] == 2  # number 3 two draws ago
    assert g[49] == 3  # never seen: gap = t


@pytest.mark.parametrize("rule", [hot_rule(20, 10), repeat_rule(), gap_top_rule(10)])
def test_selection_z_is_standard_normal_under_fair_draws(rule: object) -> None:
    zs = []
    for seed in range(120):
        x = incidence(fair(260, seed=seed), BALLS)
        zs.append(selection_stats(x, BALLS, rule, start=60).z)  # type: ignore[arg-type]
    zs_arr = np.array(zs)
    assert abs(zs_arr.mean()) < 0.3
    assert 0.75 < zs_arr.std() < 1.25
    assert stats.kstest(zs_arr, "norm").pvalue > 0.01


def test_hot_rule_finds_a_planted_persistent_bias() -> None:
    draws = biased(1500, favoured=(7, 18, 33), factor=1.8)
    later = np.zeros(len(draws), dtype=bool)
    later[750:] = True
    r = causal_selection_test(
        draws,
        BALLS,
        hot_rule(100, 10),
        start=100,
        later=later,
        test_id="t",
        hypothesis="h",
        label="l",
    )
    assert r.statistic > 3
    assert r.detail["late"]["z"] > 0


def test_uniformity_mc_and_asymptotic_agree_and_detect_bias() -> None:
    ok = uniformity_test(fair(800), BALLS, test_id="t", label="l", n_simulations=2000)
    assert abs(ok.p_value - ok.detail["p_asymptotic_scaled"]) < 0.08
    bad = uniformity_test(
        biased(1500, (1, 2, 3, 4, 5), 2.0), BALLS, test_id="t", label="l", n_simulations=2000
    )
    assert bad.p_value < 0.001


def test_exact_pmf_of_odd_count_is_hypergeometric() -> None:
    combos = all_combinations()
    assert len(combos) == math.comb(50, 5)
    pmf = exact_pmf((combos % 2 == 1).sum(axis=1))
    for j in range(6):
        assert pmf[j] == pytest.approx(stats.hypergeom.pmf(j, 50, 25, 5))
    assert exact_pmf(combos.sum(axis=1))[15] == pytest.approx(1 / math.comb(50, 5))


def test_bins_have_expected_count_at_least_five() -> None:
    combos = all_combinations()
    for values in (combos.sum(axis=1), combos.max(axis=1) - combos.min(axis=1)):
        pmf = exact_pmf(values)
        for b in bins_from_pmf(pmf, 1987):
            assert 1987 * sum(pmf[v] for v in b) >= 5


def test_repeated_combinations_poisson_mean() -> None:
    r = repeated_combinations(fair(1987))
    assert r.expected == pytest.approx(0.931, abs=0.001)


def test_serial_tests_calm_on_iid_and_alarm_on_ar1() -> None:
    rng = np.random.default_rng(3)
    iid = rng.normal(size=2000)
    assert min(t.p_value for t in serial_tests(iid)) > 0.001
    ar = np.zeros(2000)
    for t in range(1, 2000):
        ar[t] = 0.3 * ar[t - 1] + rng.normal()
    assert all(t.p_value < 1e-6 for t in serial_tests(ar))


def test_homogeneity_permutation() -> None:
    a = fair(600, seed=1)
    labels = np.array([0] * 300 + [1] * 300)
    calm = homogeneity_test(a, labels, BALLS, test_id="t", label="l", n_permutations=500)
    assert calm.p_value > 0.01
    mixed = np.vstack([fair(400, seed=2), biased(400, (1, 2, 3, 4, 5), 3.0, seed=3)])
    labels2 = np.array([0] * 400 + [1] * 400)
    loud = homogeneity_test(mixed, labels2, BALLS, test_id="t", label="l", n_permutations=500)
    assert loud.p_value < 0.01


def test_bh_adjust_textbook_example() -> None:
    q = bh_adjust([0.01, 0.04, 0.03, 0.005])
    assert q.tolist() == pytest.approx([0.02, 0.04, 0.04, 0.02])


def test_stars_pool_selection_moments() -> None:
    stars = NumberPool(name="stars", low=1, high=12, k=2)
    x = incidence(fair(400, size=12, k=2), stars)
    s = selection_stats(x, stars, repeat_rule(), start=1)
    # repeat of 2 stars out of 12: E = 2*2/12 per draw
    assert s.expected == pytest.approx(399 * 4 / 12)
