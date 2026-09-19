"""Selection policies: same forecast, different tickets, identical score."""

from __future__ import annotations

from collections import Counter
from datetime import date

import numpy as np

from predlab.core.gamespec import GameSpec
from predlab.core.historyview import build_view
from predlab.models.base import Forecast, PoolForecast, normalise_to_k
from predlab.models.baselines import UniformPredictor
from predlab.models.selection import ProportionalSamplingPolicy, TopKPolicy

from .conftest import synthetic_draws

TARGET = date(2026, 1, 7)


def _forecast(loto: GameSpec) -> Forecast:
    dates, pools = synthetic_draws(loto, 200, seed=0, start=date(2020, 1, 1))
    history = build_view(loto, dates, pools, as_of=TARGET)
    return UniformPredictor(spec=loto).forecast(history, TARGET)


def test_both_policies_emit_legal_tickets(loto: GameSpec) -> None:
    forecast = _forecast(loto)
    for policy in (TopKPolicy(), ProportionalSamplingPolicy(seed=3)):
        ticket = policy.ticket(forecast)
        for pool in loto.pools:
            pool.validate_combination(ticket[pool.name])


def test_top_k_is_deterministic_and_breaks_ties_by_lower_number(loto: GameSpec) -> None:
    forecast = _forecast(loto)  # uniform: every number tied
    ticket = TopKPolicy().ticket(forecast)
    assert ticket["main"] == (1, 2, 3, 4, 5)
    assert ticket == TopKPolicy().ticket(forecast)


def test_top_k_follows_the_probabilities(loto: GameSpec) -> None:
    pool = loto.pool("main")
    scores = np.ones(pool.size)
    scores[[6, 12, 21, 37, 43]] = 50.0  # numbers 7, 13, 22, 38, 44
    forecast = Forecast(
        spec=loto,
        target_date=TARGET,
        pools={
            "main": PoolForecast(pool=pool, inclusion_probs=normalise_to_k(scores, pool)),
            "chance": PoolForecast(
                pool=loto.pool("chance"),
                inclusion_probs=np.full(10, 0.1),
            ),
        },
        n_training_draws=0,
    )
    assert TopKPolicy().ticket(forecast)["main"] == (7, 13, 22, 38, 44)


def test_sampling_is_reproducible_but_varies_with_the_seed(loto: GameSpec) -> None:
    forecast = _forecast(loto)
    a = ProportionalSamplingPolicy(seed=1)
    assert a.ticket(forecast) == a.ticket(forecast)
    seen = {tuple(ProportionalSamplingPolicy(seed=s).ticket(forecast)["main"]) for s in range(20)}
    assert len(seen) > 1, "sampling should not collapse to one ticket"


def test_sampling_spreads_over_the_pool_under_a_uniform_forecast(loto: GameSpec) -> None:
    forecast = _forecast(loto)
    counter: Counter[int] = Counter()
    for seed in range(200):
        counter.update(ProportionalSamplingPolicy(seed=seed).ticket(forecast)["main"])
    assert len(counter) > 40, "a uniform forecast should not favour a handful of numbers"
