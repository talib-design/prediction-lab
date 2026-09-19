"""How large a bias would have to be before we could see it.

This module answers the question that has to be answered *before* any backtest, and
that is usually skipped: given this many draws, what is the smallest departure from
fairness we could reliably detect?

Without that number, "no signal detected" is ambiguous between two very different
statements:

    "the mechanism looks fair"

and

    "we had no ability to tell"

Only the first is a finding. Prediction Lab is built to be able to say the second out
loud, which means computing it.

Marginal model: over ``n`` draws, the count of a given number is Binomial(n, k/size),
since each draw independently either contains it or not. The normal approximation is
used for the minimum detectable effect; with n in the hundreds and p around 0.1 the
approximation is adequate, and the exact binomial test is available for the actual
per-number testing.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import stats

from predlab.core.gamespec import GameSpec, NumberPool


@dataclass(frozen=True, slots=True)
class DetectionFloor:
    """The smallest detectable departure from fairness, for one pool."""

    pool: str
    n_draws: int
    baseline_probability: float
    alpha: float
    power: float
    correction: str
    absolute_effect: float
    relative_effect: float

    def describe(self) -> str:
        return (
            f"{self.pool}: with {self.n_draws} draws, a number's inclusion probability "
            f"must differ from {self.baseline_probability:.4f} by at least "
            f"{self.absolute_effect:.4f} "
            f"({self.relative_effect * 100:.1f}% relative) to be detected "
            f"{self.power * 100:.0f}% of the time at alpha={self.alpha} "
            f"({self.correction})."
        )


def minimum_detectable_effect(
    pool: NumberPool,
    n_draws: int,
    *,
    alpha: float = 0.05,
    power: float = 0.80,
    multiplicity_correction: bool = True,
) -> DetectionFloor:
    """Smallest absolute change in one number's inclusion probability we could see.

    ``multiplicity_correction`` applies a Bonferroni adjustment across the pool,
    because the realistic question is not "is number 17 biased" chosen in advance, but
    "is *any* number biased", which is ``size`` simultaneous tests.
    """
    if n_draws < 1:
        raise ValueError("n_draws must be >= 1")
    if not 0 < alpha < 1 or not 0 < power < 1:
        raise ValueError("alpha and power must lie in (0, 1)")

    p0 = pool.marginal_probability
    effective_alpha = alpha / pool.size if multiplicity_correction else alpha
    z_alpha = float(stats.norm.ppf(1.0 - effective_alpha / 2.0))
    z_power = float(stats.norm.ppf(power))

    # Fixed-point iteration: the alternative's variance depends on the effect size.
    delta = float((z_alpha + z_power) * math.sqrt(p0 * (1 - p0) / n_draws))
    for _ in range(64):
        p1 = min(1 - 1e-9, p0 + delta)
        new = (z_alpha * math.sqrt(p0 * (1 - p0)) + z_power * math.sqrt(p1 * (1 - p1))) / math.sqrt(
            n_draws
        )
        if abs(new - delta) < 1e-12:
            delta = new
            break
        delta = new

    return DetectionFloor(
        pool=pool.name,
        n_draws=n_draws,
        baseline_probability=p0,
        alpha=alpha,
        power=power,
        correction="Bonferroni across the pool" if multiplicity_correction else "uncorrected",
        absolute_effect=delta,
        relative_effect=delta / p0,
    )


def draws_required(
    pool: NumberPool,
    relative_effect: float,
    *,
    alpha: float = 0.05,
    power: float = 0.80,
    multiplicity_correction: bool = True,
) -> int:
    """How many draws would be needed to detect a bias of this relative size."""
    if relative_effect <= 0:
        raise ValueError("relative_effect must be > 0")
    p0 = pool.marginal_probability
    p1 = min(1 - 1e-9, p0 * (1 + relative_effect))
    effective_alpha = alpha / pool.size if multiplicity_correction else alpha
    z_alpha = float(stats.norm.ppf(1.0 - effective_alpha / 2.0))
    z_power = float(stats.norm.ppf(power))
    numerator = z_alpha * math.sqrt(p0 * (1 - p0)) + z_power * math.sqrt(p1 * (1 - p1))
    return math.ceil((numerator / (p1 - p0)) ** 2)


def power_report(spec: GameSpec, n_draws: int) -> list[DetectionFloor]:
    """Detection floors for every pool, corrected and uncorrected."""
    floors: list[DetectionFloor] = []
    for pool in spec.pools:
        floors.append(minimum_detectable_effect(pool, n_draws, multiplicity_correction=False))
        floors.append(minimum_detectable_effect(pool, n_draws, multiplicity_correction=True))
    return floors


def simulate_fair_counts(
    pool: NumberPool, n_draws: int, n_simulations: int, rng: np.random.Generator
) -> np.ndarray:
    """Count vectors from ``n_simulations`` fair histories of ``n_draws`` draws each.

    Draws are simulated with the real mechanism -- ``k`` distinct numbers per draw --
    rather than as independent multinomial slots, because the two differ: exactly ``k``
    numbers come out each time, which makes the counts negatively dependent and their
    variance smaller than multinomial. Getting this wrong makes the null too wide and
    a real bias easier to miss.
    """
    out = np.empty((n_simulations, pool.size), dtype=np.int64)
    # Batched so memory stays bounded regardless of history length.
    per_batch = max(1, 4_000_000 // max(1, n_draws * pool.size))
    done = 0
    while done < n_simulations:
        batch = min(per_batch, n_simulations - done)
        keys = rng.random((batch, n_draws, pool.size))
        chosen = np.argpartition(keys, pool.k - 1, axis=2)[:, :, : pool.k]
        for b in range(batch):
            out[done + b] = np.bincount(chosen[b].ravel(), minlength=pool.size)
        done += batch
    return out


def chi_square_statistic(counts: np.ndarray, pool: NumberPool, n_draws: int) -> float:
    expected = n_draws * pool.marginal_probability
    return float(np.sum((counts - expected) ** 2, axis=-1) / expected)


def uniformity_monte_carlo(
    counts: np.ndarray,
    pool: NumberPool,
    n_draws: int,
    *,
    n_simulations: int = 2000,
    seed: int = 0,
) -> tuple[float, float]:
    """Test that observed counts are consistent with a fair mechanism, by simulation.

    A textbook chi-square on ball-slot counts is not quite right here: exactly ``k``
    numbers come out of each draw, so the counts are negatively dependent and the
    multinomial variance is too large. That makes the classical test *conservative* --
    it under-rejects, which would let a real bias hide.

    Simulating the actual mechanism sidesteps the approximation. Returns
    ``(statistic, p_value)`` with the ``(hits + 1) / (n + 1)`` convention, so the
    p-value is never reported as zero: with 2000 simulations the smallest attainable
    value is about 0.0005, and claiming more would overstate the simulation.
    """
    observed = chi_square_statistic(np.asarray(counts, dtype=np.float64), pool, n_draws)
    rng = np.random.default_rng(seed)
    simulated = simulate_fair_counts(pool, n_draws, n_simulations, rng)
    null_stats = np.sum((simulated - n_draws * pool.marginal_probability) ** 2, axis=1) / (
        n_draws * pool.marginal_probability
    )
    hits = int((null_stats >= observed).sum())
    return observed, (hits + 1) / (n_simulations + 1)
