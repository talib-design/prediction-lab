"""The generators' own correctness.

The entire benchmark programme rests on one property: a planted effect is exactly the
size it claims to be. If the generator drifts, a measured detection rate cannot be
attributed to the planted bias and the resulting power curve means nothing. So these
tests check the construction against its closed form, not just that it "looks biased".
"""

from __future__ import annotations

import numpy as np
import pytest

from predlab.benchmarks.generators import (
    BenchmarkCase,
    disappearing_signal,
    draw_dates,
    pure_random,
    regime_change,
    seductive_false_pattern,
    weak_bias,
)
from predlab.core.gamespec import GameSpec


def inclusion_rate(case: BenchmarkCase, number: int, lo: int = 0, hi: int | None = None) -> float:
    rows = case.pool_draws["main"][lo : hi if hi is not None else len(case)]
    return float((rows == number).any(axis=1).mean())


def test_every_case_is_a_legal_history(loto: GameSpec) -> None:
    cases = [
        pure_random(loto, 200, seed=0),
        weak_bias(loto, 200, 0.4, seed=1),
        disappearing_signal(loto, 200, 0.4, seed=2),
        regime_change(loto, 200, 0.4, seed=3),
        seductive_false_pattern(loto, 200, seed=4),
    ]
    for case in cases:
        assert len(case.dates) == 200
        assert np.all(case.dates[:-1] < case.dates[1:])
        for pool in loto.pools:
            rows = case.pool_draws[pool.name]
            assert rows.shape == (200, pool.k)
            for row in rows:
                pool.validate_combination(tuple(int(v) for v in row))


def test_draw_dates_land_only_on_real_draw_days(loto: GameSpec) -> None:
    from datetime import date as _date

    for value in draw_dates(loto, 60):
        day = value.astype("datetime64[D]").astype(_date)
        assert day.isoweekday() in loto.draw_weekdays


def test_planted_bias_is_exact(loto: GameSpec) -> None:
    """The property the power curve depends on."""
    case = weak_bias(loto, 200_000, relative_effect=0.30, number=7, seed=5)
    planted = case.truth.planted_probability
    assert planted is not None
    # Standard error of the rate at n = 200k is about 0.0007; allow four of them.
    assert inclusion_rate(case, 7) == pytest.approx(planted, abs=0.003)


def test_unbiased_numbers_shift_by_exactly_the_closed_form(loto: GameSpec) -> None:
    """Planting a bias on one number necessarily lowers every other one slightly."""
    pool = loto.pool("main")
    case = weak_bias(loto, 200_000, relative_effect=0.30, number=7, seed=6)
    planted = case.truth.planted_probability
    assert planted is not None
    expected_others = (pool.k - planted) / (pool.size - 1)
    for other in (1, 22, 49):
        assert inclusion_rate(case, other) == pytest.approx(expected_others, abs=0.003)


def test_inclusion_probabilities_still_sum_to_k(loto: GameSpec) -> None:
    pool = loto.pool("main")
    case = weak_bias(loto, 50_000, relative_effect=0.5, number=7, seed=7)
    rates = [inclusion_rate(case, n) for n in range(pool.low, pool.high + 1)]
    assert sum(rates) == pytest.approx(pool.k, abs=0.01)


def test_zero_effect_is_indistinguishable_from_fair(loto: GameSpec) -> None:
    pool = loto.pool("main")
    case = weak_bias(loto, 100_000, relative_effect=0.0, number=7, seed=8)
    assert inclusion_rate(case, 7) == pytest.approx(pool.marginal_probability, abs=0.004)


def test_impossible_effects_are_refused(loto: GameSpec) -> None:
    with pytest.raises(ValueError, match="relative_effect"):
        weak_bias(loto, 100, relative_effect=20.0, seed=9)
    with pytest.raises(ValueError, match="relative_effect"):
        weak_bias(loto, 100, relative_effect=-2.0, seed=9)


def test_disappearing_signal_is_present_then_absent(loto: GameSpec) -> None:
    n = 60_000
    case = disappearing_signal(loto, n, relative_effect=0.5, number=7, ends_at=0.5, seed=10)
    early = inclusion_rate(case, 7, 0, n // 2)
    late = inclusion_rate(case, 7, n // 2, n)
    assert early == pytest.approx(case.truth.planted_probability, abs=0.006)
    assert late == pytest.approx(loto.pool("main").marginal_probability, abs=0.006)
    assert case.truth.visible and not case.truth.predictive
    assert case.truth.expected_verdict == "no_signal"


def test_regime_change_moves_the_bias(loto: GameSpec) -> None:
    n = 60_000
    case = regime_change(loto, n, relative_effect=0.5, before=7, after=31, seed=11)
    assert inclusion_rate(case, 7, 0, n // 2) > inclusion_rate(case, 7, n // 2, n)
    assert inclusion_rate(case, 31, n // 2, n) > inclusion_rate(case, 31, 0, n // 2)
    assert case.truth.predictive, "the later bias IS predictive at the end of the series"


def test_seductive_case_plants_nothing_but_names_the_temptation(loto: GameSpec) -> None:
    case = seductive_false_pattern(loto, 400, train_fraction=0.5, seed=12)
    assert case.snooped_number is not None
    assert not case.truth.visible and not case.truth.predictive
    counts = np.bincount(case.pool_draws["main"][:200].ravel() - 1, minlength=49)
    assert int(np.argmax(counts)) + 1 == case.snooped_number


def test_ground_truth_separates_visible_from_predictive(loto: GameSpec) -> None:
    """A pattern can be in the history and useless for the next draw."""
    disappearing = disappearing_signal(loto, 400, 0.5, seed=13).truth
    assert disappearing.visible and not disappearing.predictive
    assert disappearing.expected_verdict == "no_signal"

    weak = weak_bias(loto, 400, 0.5, seed=13).truth
    assert weak.visible and weak.predictive
    assert weak.expected_verdict == "signal"


def test_cases_are_reproducible_from_their_seed(loto: GameSpec) -> None:
    a = weak_bias(loto, 500, 0.3, seed=14)
    b = weak_bias(loto, 500, 0.3, seed=14)
    np.testing.assert_array_equal(a.pool_draws["main"], b.pool_draws["main"])
    c = weak_bias(loto, 500, 0.3, seed=15)
    assert not np.array_equal(a.pool_draws["main"], c.pool_draws["main"])
