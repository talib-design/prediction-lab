from __future__ import annotations

from datetime import date

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from predlab.core.gamespec import LOTO_2019_11, GameSpec, NumberPool
from predlab.core.historyview import build_view
from predlab.models.base import PROB_EPSILON, PoolForecast, Predictor, normalise_to_k
from predlab.models.baselines import (
    FrequencyPredictor,
    GapPredictor,
    RandomTicketPredictor,
    UniformPredictor,
    default_baselines,
)

from .conftest import synthetic_draws

TARGET = date(2026, 1, 7)


def view(loto: GameSpec, n: int = 200, seed: int = 0):
    dates, pools = synthetic_draws(loto, n, seed=seed, start=date(2020, 1, 1))
    return build_view(loto, dates, pools, as_of=TARGET)


def test_predictors_satisfy_the_protocol(loto: GameSpec) -> None:
    for model in default_baselines(loto):
        assert isinstance(model, Predictor)


def test_every_baseline_emits_a_valid_forecast(loto: GameSpec) -> None:
    h = view(loto)
    for model in default_baselines(loto):
        fc = model.forecast(h, TARGET)
        for pool in loto.pools:
            p = fc.pools[pool.name].inclusion_probs
            assert p.sum() == pytest.approx(pool.k, abs=1e-6)
            assert p.min() > 0.0 and p.max() < 1.0


def test_uniform_is_exactly_k_over_size(loto: GameSpec) -> None:
    fc = UniformPredictor(spec=loto).forecast(view(loto), TARGET)
    assert fc.pools["main"].probability_of(17) == pytest.approx(5 / 49)
    assert fc.pools["chance"].probability_of(3) == pytest.approx(1 / 10)


def test_random_ticket_asserts_the_same_probabilities_as_uniform(loto: GameSpec) -> None:
    """A harness integrity check: 'pick at random' IS the uniform model."""
    h = view(loto)
    a = UniformPredictor(spec=loto).forecast(h, TARGET)
    for seed in (0, 1, 999):
        b = RandomTicketPredictor(spec=loto, seed=seed).forecast(h, TARGET)
        for pool in loto.pools:
            np.testing.assert_allclose(
                a.pools[pool.name].inclusion_probs, b.pools[pool.name].inclusion_probs
            )


def test_random_ticket_is_legal_and_reproducible(loto: GameSpec) -> None:
    model = RandomTicketPredictor(spec=loto, seed=7)
    first = model.ticket(TARGET)
    assert first == model.ticket(TARGET)
    for pool in loto.pools:
        pool.validate_combination(first[pool.name])
    assert model.ticket(TARGET) != RandomTicketPredictor(spec=loto, seed=8).ticket(TARGET)


def test_frequency_follows_an_injected_bias(loto: GameSpec) -> None:
    """Sanity: if number 7 is over-represented, it must get more mass than 8."""
    dates, pools = synthetic_draws(loto, 300, seed=2, start=date(2020, 1, 1))
    rigged = pools["main"].copy()
    rigged[:, 0] = 7
    fc = FrequencyPredictor(spec=loto).forecast(
        build_view(loto, dates, {**pools, "main": rigged}, as_of=TARGET), TARGET
    )
    assert fc.pools["main"].probability_of(7) > fc.pools["main"].probability_of(8)


def test_frequency_on_empty_history_falls_back_to_uniform(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 10, seed=3, start=date(2020, 1, 1))
    empty = build_view(loto, dates, pools, as_of=date(2019, 1, 1))
    fc = FrequencyPredictor(spec=loto).forecast(empty, TARGET)
    assert fc.pools["main"].probability_of(1) == pytest.approx(5 / 49)


def test_rolling_window_ignores_older_draws(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 400, seed=4, start=date(2020, 1, 1))
    rigged = pools["main"].copy()
    rigged[:200, 0] = 7  # bias only in the distant past
    h = build_view(loto, dates, {**pools, "main": rigged}, as_of=TARGET)
    recent = FrequencyPredictor(spec=loto, window=50).forecast(h, TARGET)
    allhist = FrequencyPredictor(spec=loto, window=None).forecast(h, TARGET)
    assert recent.pools["main"].probability_of(7) < allhist.pools["main"].probability_of(7)


def test_rolling_window_reports_its_own_training_size(loto: GameSpec) -> None:
    fc = FrequencyPredictor(spec=loto, window=25).forecast(view(loto, n=200), TARGET)
    assert fc.n_training_draws == 25


def test_zero_smoothing_is_refused(loto: GameSpec) -> None:
    with pytest.raises(ValueError, match="infinite"):
        FrequencyPredictor(spec=loto, alpha=0.0)


def test_gap_gives_more_mass_to_long_absent_numbers(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 200, seed=5, start=date(2020, 1, 1))
    rigged = pools["main"].copy()
    rigged[-40:, 0] = 7  # 7 appears constantly at the end, so its gap is 0
    h = build_view(loto, dates, {**pools, "main": rigged}, as_of=TARGET)
    fc = GapPredictor(spec=loto).forecast(h, TARGET)
    assert fc.pools["main"].probability_of(7) == min(fc.pools["main"].inclusion_probs)


def test_normalise_never_produces_an_impossible_probability() -> None:
    """A number is drawn or not: no inclusion probability may reach 1."""
    pool = NumberPool("chance", 1, 10, 1)
    scores = np.array([1e9, *([1.0] * 9)])
    p = normalise_to_k(scores, pool)
    assert p.max() <= 1.0 - PROB_EPSILON
    assert p.sum() == pytest.approx(1.0, abs=1e-6)


def test_forecast_rejects_probabilities_that_do_not_sum_to_k() -> None:
    pool = NumberPool("main", 1, 49, 5)
    with pytest.raises(ValueError, match="must sum to k"):
        PoolForecast(pool=pool, inclusion_probs=np.full(49, 0.5))


def test_forecast_rejects_certainty() -> None:
    """Claiming a number is certain, or impossible, is not a forecast we accept."""
    pool = NumberPool("chance", 1, 10, 1)
    certain = np.zeros(10)
    certain[0] = 1.0
    with pytest.raises(ValueError, match="strictly in"):
        PoolForecast(pool=pool, inclusion_probs=certain)


def test_normalised_extreme_scores_stay_a_valid_forecast() -> None:
    """The end-to-end guard: even absurd scores must yield an acceptable forecast."""
    pool = NumberPool("main", 1, 49, 5)
    scores = np.zeros(49)
    scores[:5] = 1e12
    scores[5:] = 1e-12
    PoolForecast(pool=pool, inclusion_probs=normalise_to_k(scores, pool))


def test_baseline_names_are_unique(loto: GameSpec) -> None:
    names = [m.name for m in default_baselines(loto)]
    assert len(names) == len(set(names))


def test_models_cannot_see_past_the_cutoff(loto: GameSpec) -> None:
    """The view handed to a model contains no draw at or after the target date."""
    dates, pools = synthetic_draws(LOTO_2019_11, 500, seed=6, start=date(2020, 1, 1))
    h = build_view(loto, dates, pools, as_of=TARGET)
    assert h.dates.max() < np.datetime64(TARGET, "D")
    for model in default_baselines(loto):
        assert model.forecast(h, TARGET).n_training_draws <= len(h)


@settings(max_examples=200, deadline=None)
@given(
    raw=st.lists(
        st.floats(min_value=0.0, max_value=1e9, allow_nan=False, allow_infinity=False),
        min_size=49,
        max_size=49,
    )
)
def test_any_non_negative_scores_yield_a_valid_forecast(raw: list[float]) -> None:
    pool = NumberPool("main", 1, 49, 5)
    scores = np.array(raw, dtype=np.float64)
    if scores.sum() <= 0:
        with pytest.raises(ValueError, match="all zero"):
            normalise_to_k(scores, pool)
        return
    PoolForecast(pool=pool, inclusion_probs=normalise_to_k(scores, pool))
