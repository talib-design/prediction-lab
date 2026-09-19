"""Turning a forecast into an actual ticket.

Kept separate from the model because the two answer different questions. The model
says how likely each number is; the policy says which five you would write down. Two
policies applied to the same forecast produce the same score under every proper
scoring rule and different match counts, which is a useful reminder of how little
match count measures.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np

from predlab.models.base import Forecast


@dataclass(frozen=True, slots=True)
class TopKPolicy:
    """Take the ``k`` most likely numbers; ties broken by the lower number.

    Deterministic, and therefore nearly constant over time for a frequency model --
    which is exactly why its per-draw scores are heavily autocorrelated and why
    uncertainty must be estimated with a block method rather than an i.i.d. bootstrap.
    """

    name: str = "top_k"

    def ticket(self, forecast: Forecast) -> dict[str, tuple[int, ...]]:
        out: dict[str, tuple[int, ...]] = {}
        for name, pf in forecast.pools.items():
            order = np.lexsort((np.arange(pf.pool.size), -pf.inclusion_probs))
            out[name] = tuple(sorted(int(i) + pf.pool.low for i in order[: pf.pool.k]))
        return out


@dataclass(frozen=True, slots=True)
class ProportionalSamplingPolicy:
    """Sample ``k`` distinct numbers with probability proportional to the forecast."""

    seed: int = 0
    name: str = "proportional"

    def ticket(self, forecast: Forecast) -> dict[str, tuple[int, ...]]:
        rng = np.random.default_rng([self.seed, _ordinal(forecast.target_date)])
        out: dict[str, tuple[int, ...]] = {}
        for name, pf in forecast.pools.items():
            weights = pf.inclusion_probs / pf.inclusion_probs.sum()
            chosen = rng.choice(pf.pool.size, size=pf.pool.k, replace=False, p=weights)
            out[name] = tuple(sorted(int(i) + pf.pool.low for i in chosen))
        return out


def _ordinal(day: date) -> int:
    return day.toordinal()
