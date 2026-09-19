"""The instrument measuring itself.

These run small sweeps: enough to check the machinery behaves, not enough to produce
publication-grade power curves. The full sweep lives in the benchmark report.
"""

from __future__ import annotations

import numpy as np
import pytest

from predlab.benchmarks.sweep import per_number_detects, per_number_p_values, power_sweep
from predlab.core.gamespec import GameSpec
from predlab.eval.power import fair_null_distribution, simulate_fair_counts


def test_per_number_p_values_are_uniform_on_fair_data(loto: GameSpec) -> None:
    pool = loto.pool("chance")
    rng = np.random.default_rng(0)
    counts = simulate_fair_counts(pool, 500, 1, rng)[0]
    p_values = per_number_p_values(counts, pool, 500)
    assert p_values.shape == (pool.size,)
    assert np.all((p_values > 0) & (p_values <= 1))


def test_per_number_test_finds_a_blatant_bias(loto: GameSpec) -> None:
    pool = loto.pool("chance")
    counts = np.array([200, *([22] * 9)])
    assert per_number_detects(counts, pool, 398)


def test_both_corrections_fire_far_less_than_no_correction(loto: GameSpec) -> None:
    """On fair data, 49 uncorrected tests at 5% fire constantly. That is the point."""
    pool = loto.pool("main")
    rng = np.random.default_rng(1)
    fired = {"none": 0, "fdr": 0, "bonferroni": 0}
    trials = 25
    for _ in range(trials):
        counts = simulate_fair_counts(pool, 400, 1, rng)[0]
        for correction in fired:
            fired[correction] += per_number_detects(counts, pool, 400, correction=correction)
    assert fired["none"] > trials // 2, "uncorrected testing should fire most of the time"
    assert fired["fdr"] < fired["none"]
    assert fired["bonferroni"] < fired["none"]


def test_dependent_fdr_can_be_stricter_than_bonferroni_at_small_m(loto: GameSpec) -> None:
    """Documenting a property that looks like a bug the first time you meet it.

    Our FDR control defaults to Benjamini-Yekutieli, valid under *any* dependence,
    which divides the step-up thresholds by ``C_m = sum 1/i``. For m = 49 that is about
    4.5, so the rank-1 threshold (alpha / (m * C_m)) is *below* Bonferroni's
    (alpha / m). BY is therefore the more conservative of the two for the single most
    extreme number, and only becomes more generous further down the ranking.

    The practical consequence, worth stating in any report: "no number flagged" under
    this correction is a weaker statement than it sounds.
    """
    m = loto.pool("main").size
    c_m = sum(1.0 / i for i in range(1, m + 1))
    assert 0.05 / (m * c_m) < 0.05 / m


def test_unknown_correction_is_refused(loto: GameSpec) -> None:
    with pytest.raises(ValueError, match="unknown correction"):
        per_number_detects(np.zeros(49), loto.pool("main"), 100, correction="nope")


def test_sweep_detection_rate_increases_with_effect(loto: GameSpec) -> None:
    points = power_sweep(
        loto,
        [0.0, 0.8],
        n_draws=400,
        replications=8,
        n_null_simulations=300,
        seed=3,
    )
    assert points[0].per_number_rate < points[1].per_number_rate
    assert points[1].per_number_rate > 0.5


def test_sweep_reports_the_analytic_prediction_alongside(loto: GameSpec) -> None:
    points = power_sweep(loto, [0.5], n_draws=400, replications=4, n_null_simulations=200, seed=4)
    assert 0.0 < points[0].analytic_power <= 1.0
    assert "analytic" in points[0].describe()


def test_the_null_is_reused_not_rebuilt(loto: GameSpec) -> None:
    """A cached null must give the same answers as one built per replication."""
    pool = loto.pool("chance")
    a = fair_null_distribution(pool, 300, n_simulations=200, seed=5)
    b = fair_null_distribution(pool, 300, n_simulations=200, seed=5)
    np.testing.assert_array_equal(a, b)
