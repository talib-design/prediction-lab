"""Turning scores into probabilities a proper scoring rule can judge.

Extracted from the lottery engine, where it turned scores into inclusion probabilities
summing to the number of balls drawn. The problem is the same for a race: win
probabilities must sum to 1, top-3 probabilities to 3 (or to the field size when fewer
than three horses run). Only the total changes.

Three constraints have to hold at once, and naive rescaling satisfies only the third:

* no probability may reach 1 -- certainty is not a forecast;
* none may reach 0 -- log loss would be infinite on a single surprise;
* they must sum to ``total``.

So scores are rescaled, clamped into ``[eps, 1-eps]``, and the mass lost or gained to
clamping is redistributed in proportion to the room each entry has left.
"""

from __future__ import annotations

import numpy as np

# Clipping bound. Reported with every evaluation, because it caps how badly an
# overconfident model can be punished and therefore slightly flatters it.
PROB_EPSILON = 1e-6


def normalise_to_total(
    scores: np.ndarray, total: float, *, name: str = "scores", epsilon: float = PROB_EPSILON
) -> np.ndarray:
    """Non-negative scores -> probabilities in ``[eps, 1-eps]`` summing to ``total``."""
    scores = np.asarray(scores, dtype=np.float64)
    if scores.ndim != 1 or scores.size == 0:
        raise ValueError(f"{name}: expected a non-empty 1-D array")
    if not np.all(np.isfinite(scores)):
        raise ValueError(f"{name}: scores must be finite")
    if np.any(scores < 0):
        raise ValueError(f"{name}: scores must be non-negative")

    largest = float(scores.max(initial=0.0))
    if largest <= 0:
        raise ValueError(f"{name}: scores are all zero; cannot form a distribution")

    floor, ceiling = epsilon, 1.0 - epsilon
    n = scores.size
    if not n * floor <= total <= n * ceiling:
        raise ValueError(
            f"{name}: total={total} is infeasible for {n} entries in [{floor}, {ceiling}]"
        )

    # Divide by the largest score before normalising. Scaling by total/sum directly
    # overflows to infinity when the scores are denormal (found by Hypothesis).
    relative = scores / largest
    p = np.clip(relative * (total / float(relative.sum())), floor, ceiling)

    tolerance = 1e-12 * max(1.0, float(total))
    for _ in range(64):
        residual = total - float(p.sum())
        if abs(residual) <= tolerance:
            return p
        slack = (ceiling - p) if residual > 0 else (p - floor)
        available = float(slack.sum())
        if available <= 0:
            break
        p = np.clip(p + np.sign(residual) * slack * (abs(residual) / available), floor, ceiling)

    raise RuntimeError(f"{name}: could not normalise scores to sum to {total} within bounds")


def implied_probabilities(odds: np.ndarray) -> np.ndarray:
    """Pari-mutuel odds (decimal, stake included) -> probabilities summing to 1.

    ``1/odds`` sums to more than 1: the excess is the pool's takeout plus rounding.
    Dividing by the sum removes it per race, without hard-coding a takeout rate that
    PMU has changed over time. This is the *raw* market baseline; correcting the
    favourite-longshot bias is a separate, fitted step.
    """
    odds = np.asarray(odds, dtype=np.float64)
    if odds.ndim != 1 or odds.size == 0:
        raise ValueError("expected a non-empty 1-D array of odds")
    if not np.all(np.isfinite(odds)) or np.any(odds <= 1.0):
        raise ValueError("decimal odds must be finite and strictly greater than 1")
    inverse = 1.0 / odds
    return inverse / inverse.sum()
