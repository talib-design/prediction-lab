"""What a model is allowed to say.

A predictor does **not** return five numbers. It returns, for each pool, an
*inclusion probability* for every number: the probability that this number appears in
the next draw. Picking a ticket from those probabilities is a separate, swappable
policy.

Why this separation matters more than it looks:

* Proper scoring rules (log loss, Brier) need probabilities. A bare ticket cannot be
  scored in a way that rewards honesty about uncertainty.
* Under a fair mechanism every number has inclusion probability ``k / size``, so every
  legal ticket has the *same* expected match count. Match count therefore cannot
  distinguish models. Probabilities can.
* It forces a model to state how confident it is, which is exactly what we want to
  measure and what a lottery model has no honest basis for exaggerating.

**Scope limit, stated once and meant:** these are *marginal* probabilities. We score
each number as a Bernoulli outcome, not the joint distribution over all C(49,5)
combinations. A model that captured dependence between numbers while keeping the same
marginals would score identically here. That is a deliberate restriction of the
hypothesis space to what this sample size can actually test, not an oversight.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol, runtime_checkable

import numpy as np

from predlab.core.gamespec import GameSpec, NumberPool
from predlab.core.historyview import HistoryView

# Probabilities are clipped away from 0 and 1 so that log loss stays finite. The bound
# is reported in every run's metadata because it caps how badly a model can be
# punished, and therefore slightly flatters overconfident models.
PROB_EPSILON = 1e-6


@dataclass(frozen=True, slots=True)
class PoolForecast:
    """Inclusion probabilities for one pool, indexed by ``number - pool.low``."""

    pool: NumberPool
    inclusion_probs: np.ndarray

    def __post_init__(self) -> None:
        p = self.inclusion_probs
        if p.shape != (self.pool.size,):
            raise ValueError(f"{self.pool.name}: expected shape {(self.pool.size,)}, got {p.shape}")
        if not np.all(np.isfinite(p)):
            raise ValueError(f"{self.pool.name}: non-finite probability")
        if p.min() <= 0.0 or p.max() >= 1.0:
            raise ValueError(
                f"{self.pool.name}: probabilities must lie strictly in (0, 1); "
                f"got [{p.min()}, {p.max()}]"
            )
        total = float(p.sum())
        if not np.isclose(total, self.pool.k, rtol=0, atol=1e-6):
            raise ValueError(
                f"{self.pool.name}: inclusion probabilities must sum to k={self.pool.k} "
                f"(exactly {self.pool.k} numbers are drawn), got {total}"
            )

    def probability_of(self, number: int) -> float:
        if not self.pool.contains(number):
            raise KeyError(f"{number} is not in pool {self.pool.name}")
        return float(self.inclusion_probs[number - self.pool.low])

    def outcome_vector(self, drawn: np.ndarray) -> np.ndarray:
        """One-hot style 0/1 vector of what actually came out."""
        y = np.zeros(self.pool.size, dtype=np.float64)
        y[np.asarray(drawn) - self.pool.low] = 1.0
        return y


@dataclass(frozen=True, slots=True)
class Forecast:
    """A model's complete probabilistic statement about one future draw."""

    spec: GameSpec
    target_date: date
    pools: dict[str, PoolForecast]
    n_training_draws: int

    def __post_init__(self) -> None:
        missing = [p.name for p in self.spec.pools if p.name not in self.pools]
        if missing:
            raise ValueError(f"forecast is missing pools: {missing}")


@runtime_checkable
class Predictor(Protocol):
    """Anything that can turn a causally-truncated history into a forecast."""

    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    def config(self) -> dict[str, Any]:
        """Everything needed to rebuild this model identically. Goes into the run record."""
        ...

    def forecast(self, history: HistoryView, target_date: date) -> Forecast:
        """Predict the draw of ``target_date`` using only ``history``."""
        ...


def normalise_to_k(scores: np.ndarray, pool: NumberPool) -> np.ndarray:
    """Turn non-negative scores into valid inclusion probabilities summing to ``k``.

    Three constraints have to hold at once, and naive rescaling satisfies only the
    third:

    * no probability may reach 1 -- a number drawn with certainty is not a forecast;
    * none may reach 0 -- that would make log loss infinite on a single surprise;
    * they must sum to ``k``, because exactly ``k`` numbers come out.

    So scores are rescaled, clamped into ``[eps, 1-eps]``, and the mass lost or gained
    to clamping is redistributed in proportion to how much room each number has left.
    The result is a coherent statement about a draw of ``k`` numbers, whatever the
    scores looked like.
    """
    if np.any(scores < 0):
        raise ValueError(f"{pool.name}: scores must be non-negative")
    total = float(scores.sum())
    if total <= 0:
        raise ValueError(f"{pool.name}: scores are all zero; cannot form a distribution")

    floor, ceiling = PROB_EPSILON, 1.0 - PROB_EPSILON
    if not pool.size * floor <= pool.k <= pool.size * ceiling:
        raise ValueError(f"{pool.name}: k={pool.k} is infeasible within [{floor}, {ceiling}]")

    p = np.clip(scores.astype(np.float64) * (pool.k / total), floor, ceiling)

    tolerance = 1e-12 * max(1.0, float(pool.k))
    for _ in range(64):
        residual = pool.k - float(p.sum())
        if abs(residual) <= tolerance:
            return p
        slack = (ceiling - p) if residual > 0 else (p - floor)
        available = float(slack.sum())
        if available <= 0:
            break
        p = np.clip(p + np.sign(residual) * slack * (abs(residual) / available), floor, ceiling)

    raise RuntimeError(f"{pool.name}: could not normalise scores to sum to {pool.k} within bounds")
