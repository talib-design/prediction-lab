"""Measuring what the instrument can actually see.

`eval.power` says, from a formula, how large a bias would have to be before it could
be detected. This module plants biases of known size and counts how often they *are*
detected. If the two disagree, the formula is describing a test the pipeline does not
run -- and the quoted detection floors have been decorating reports rather than
bounding them.

Two tests are measured, because they are not the same test:

* **per-number**: an exact two-sided binomial test on each number's count, corrected
  across the pool. This is what the analytic formula describes.
* **omnibus**: the Monte-Carlo chi-square over the whole pool, which is what the
  descriptive section of the report actually runs. It answers "is this pool uniform",
  not "is number 7 biased", and for a single-number departure its power differs.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats

from predlab.benchmarks.generators import weak_bias
from predlab.core.gamespec import GameSpec, NumberPool
from predlab.eval.power import analytic_power, fair_null_distribution, uniformity_p_value
from predlab.eval.uncertainty import benjamini_hochberg


def per_number_p_values(counts: np.ndarray, pool: NumberPool, n_draws: int) -> np.ndarray:
    """Exact two-sided binomial p-value for every number in the pool."""
    p0 = pool.marginal_probability
    return np.array([stats.binomtest(int(c), n_draws, p0).pvalue for c in counts], dtype=np.float64)


def per_number_detects(
    counts: np.ndarray,
    pool: NumberPool,
    n_draws: int,
    *,
    alpha: float = 0.05,
    correction: str = "bonferroni",
) -> bool:
    """Does any number look biased, after correcting for testing all of them?"""
    p_values = per_number_p_values(counts, pool, n_draws)
    if correction == "bonferroni":
        return bool((p_values < alpha / pool.size).any())
    if correction == "fdr":
        return bool(benjamini_hochberg(p_values, q=alpha).any())
    if correction == "none":
        return bool((p_values < alpha).any())
    raise ValueError(f"unknown correction {correction!r}")


@dataclass(frozen=True, slots=True)
class SweepPoint:
    """One effect size, measured."""

    relative_effect: float
    n_draws: int
    replications: int
    per_number_rate: float
    omnibus_rate: float
    analytic_power: float

    def describe(self) -> str:
        return (
            f"effect {self.relative_effect * 100:6.1f}%  "
            f"per-number {self.per_number_rate:5.2f}  "
            f"omnibus {self.omnibus_rate:5.2f}  "
            f"analytic {self.analytic_power:5.2f}"
        )


def power_sweep(
    spec: GameSpec,
    effects: list[float],
    *,
    n_draws: int = 1075,
    replications: int = 40,
    alpha: float = 0.05,
    n_null_simulations: int = 4000,
    seed: int = 0,
    biased_number: int = 7,
) -> list[SweepPoint]:
    """Detection rate versus planted effect size, for both tests.

    The fair null is simulated once and reused across every replication: it depends
    only on ``(pool, n_draws)``, and rebuilding it each time would dominate the cost
    without changing a single answer.
    """
    pool = spec.pool("main")
    null = fair_null_distribution(pool, n_draws, n_simulations=n_null_simulations, seed=seed)

    points: list[SweepPoint] = []
    for effect_index, effect in enumerate(effects):
        per_number_hits = 0
        omnibus_hits = 0
        for rep in range(replications):
            case = weak_bias(
                spec,
                n_draws,
                relative_effect=effect,
                number=biased_number,
                seed=seed + 1000 * (effect_index + 1) + rep,
            )
            counts = np.bincount(case.pool_draws["main"].ravel() - pool.low, minlength=pool.size)
            if per_number_detects(counts, pool, n_draws, alpha=alpha):
                per_number_hits += 1
            if uniformity_p_value(counts, pool, n_draws, null)[1] < alpha:
                omnibus_hits += 1

        points.append(
            SweepPoint(
                relative_effect=effect,
                n_draws=n_draws,
                replications=replications,
                per_number_rate=per_number_hits / replications,
                omnibus_rate=omnibus_hits / replications,
                analytic_power=(
                    alpha if effect == 0.0 else analytic_power(pool, n_draws, effect, alpha=alpha)
                ),
            )
        )
    return points
