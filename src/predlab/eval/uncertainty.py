"""Uncertainty around a score difference.

The naive approach -- resample per-draw scores independently -- is wrong here, and
wrong in the dangerous direction. A frequency model's forecast barely changes from one
draw to the next, so its per-draw scores are strongly autocorrelated. An i.i.d.
bootstrap treats those correlated observations as independent evidence and returns an
interval that is too narrow, which manufactures significance.

So: moving-block resampling, which keeps neighbouring draws together, and a *paired*
permutation test that flips the sign of whole blocks rather than single draws.

Interval method: percentile. Efron's BCa would correct for bias and skew and is the
better tool when a statistic is visibly skewed; it is noted as a deliberate future
refinement rather than silently omitted.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class Interval:
    """A point estimate with a resampling interval and the recipe that produced it."""

    point: float
    low: float
    high: float
    level: float
    method: str
    n_resamples: int
    block_size: int

    def excludes(self, value: float) -> bool:
        """True if ``value`` lies outside the interval."""
        return not (self.low <= value <= self.high)

    def format(self, digits: int = 4) -> str:
        return f"{self.point:.{digits}f} [{self.low:.{digits}f}, {self.high:.{digits}f}]"


def suggested_block_size(n: int) -> int:
    """A pragmatic ``n**(1/3)`` block length, floored at 2.

    Not optimal -- optimal block length depends on the autocorrelation structure and
    is itself estimated with uncertainty. This is a documented default, meant to be
    overridden when a series is visibly more persistent.
    """
    return max(2, round(n ** (1 / 3)))


def _block_indices(n: int, block_size: int, rng: np.random.Generator) -> np.ndarray:
    n_blocks = int(np.ceil(n / block_size))
    starts = rng.integers(0, max(1, n - block_size + 1), size=n_blocks)
    offsets = np.arange(block_size)
    idx = (starts[:, None] + offsets[None, :]).ravel()[:n]
    return np.minimum(idx, n - 1)


def block_bootstrap(
    series: np.ndarray,
    statistic: Callable[[np.ndarray], float] = lambda x: float(np.mean(x)),
    *,
    n_resamples: int = 2000,
    level: float = 0.95,
    block_size: int | None = None,
    seed: int = 0,
) -> Interval:
    """Moving-block bootstrap interval for a statistic of a time-ordered series."""
    series = np.asarray(series, dtype=np.float64)
    n = len(series)
    if n < 2:
        raise ValueError("need at least 2 observations")
    block = block_size or suggested_block_size(n)
    rng = np.random.default_rng(seed)

    draws = np.empty(n_resamples, dtype=np.float64)
    for i in range(n_resamples):
        draws[i] = statistic(series[_block_indices(n, block, rng)])

    alpha = (1.0 - level) / 2.0
    low, high = np.quantile(draws, [alpha, 1.0 - alpha])
    return Interval(
        point=statistic(series),
        low=float(low),
        high=float(high),
        level=level,
        method="moving-block percentile bootstrap",
        n_resamples=n_resamples,
        block_size=block,
    )


@dataclass(frozen=True, slots=True)
class PairedTest:
    """Result of comparing two models on the same draws."""

    mean_difference: float
    p_value: float
    n_permutations: int
    block_size: int
    method: str
    lower_is_better: bool

    def verdict(self, alpha: float = 0.05) -> str:
        if self.p_value >= alpha:
            return "indistinguishable"
        return "better" if (self.mean_difference < 0) == self.lower_is_better else "worse"


def paired_block_permutation_test(
    model_scores: np.ndarray,
    baseline_scores: np.ndarray,
    *,
    n_permutations: int = 5000,
    block_size: int | None = None,
    seed: int = 0,
    lower_is_better: bool = True,
) -> PairedTest:
    """Two-sided test of whether two models score differently on the same draws.

    The null is exchangeability of the paired difference's sign. Signs are flipped in
    contiguous blocks, because adjacent differences are not independent; flipping them
    one at a time would understate the null variance and overstate significance.

    The p-value uses the ``(hits + 1) / (n + 1)`` convention, so it is never reported
    as exactly zero -- with 5000 permutations the smallest attainable value is 1/5001,
    and claiming more precision than the simulation supports would be false.
    """
    a = np.asarray(model_scores, dtype=np.float64)
    b = np.asarray(baseline_scores, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError("paired series must have the same length")
    diff = a - b
    n = len(diff)
    if n < 2:
        raise ValueError("need at least 2 paired observations")

    block = block_size or suggested_block_size(n)
    n_blocks = int(np.ceil(n / block))
    observed = float(np.mean(diff))
    rng = np.random.default_rng(seed)

    hits = 0
    for _ in range(n_permutations):
        signs = np.repeat(rng.choice(np.array([-1.0, 1.0]), size=n_blocks), block)[:n]
        if abs(float(np.mean(diff * signs))) >= abs(observed):
            hits += 1

    return PairedTest(
        mean_difference=observed,
        p_value=(hits + 1) / (n_permutations + 1),
        n_permutations=n_permutations,
        block_size=block,
        method="paired block sign-flip permutation",
        lower_is_better=lower_is_better,
    )


def benjamini_hochberg(
    p_values: np.ndarray, q: float = 0.05, *, dependent: bool = True
) -> np.ndarray:
    """Step-up FDR control: which hypotheses survive at false discovery rate ``q``.

    Needed the moment anything is tested repeatedly: 49 independent tests at 5% yield
    two or three "significant" balls by construction, and reporting those as findings
    is the easiest way to manufacture a false discovery here.

    ``dependent`` selects the Benjamini-Yekutieli variant, which divides the step-up
    thresholds by the harmonic number ``C_m = sum_{i=1..m} 1/i``. Wasserman (*All of
    Statistics*, §10.7) states the BH theorem with exactly this factor: ``C_m = 1``
    holds **only when the p-values are independent**.

    The default is ``True`` because in this project they are not. Every model is
    compared to the same reference on the same draws; frequency, rolling-100 and
    rolling-300 are computed from overlapping counts; and the main and chance pools
    come from the same tirages. Using the independent form there would quietly
    overstate how much evidence survives correction -- the exact failure mode this
    module exists to prevent. ``dependent=False`` is available for genuinely
    independent families and costs about a factor of ``C_m`` in strictness
    (``C_m ~ 3.1`` at m = 12, ``~ 4.5`` at m = 49).
    """
    p = np.asarray(p_values, dtype=np.float64)
    m = len(p)
    if m == 0:
        return np.zeros(0, dtype=bool)
    correction = 1.0 if not dependent else float(np.sum(1.0 / np.arange(1, m + 1)))
    order = np.argsort(p)
    ranked = p[order]
    thresholds = q * np.arange(1, m + 1) / (m * correction)
    passing = ranked <= thresholds
    rejected = np.zeros(m, dtype=bool)
    if passing.any():
        cutoff = int(np.max(np.flatnonzero(passing)))
        rejected[order[: cutoff + 1]] = True
    return rejected
