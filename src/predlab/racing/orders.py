"""From win probabilities to finishing orders (Harville / Plackett-Luce).

Harville's assumption: once the winner is known, the remaining starters finish second
in proportion to their own win probabilities, and so on. It turns a win model into a
model of the whole order -- what place, tiercé and quinté bets need.

It is known to be biased: it over-states favourites for the minor places (Henery
1981; Lo & Bacon-Shone 1994). That bias is measured here, not assumed away: the
simulation report shows the calibration of these place probabilities, and a
discounted variant is a registered hypothesis for later.
"""

from __future__ import annotations

import numpy as np


def top_k_probabilities(p: np.ndarray, k: int) -> np.ndarray:
    """P(runner i finishes in the first k), k in {1, 2, 3}, exactly under Harville."""
    p = np.asarray(p, dtype=np.float64)
    n = p.size
    if k < 1 or k > 3:
        raise ValueError("k must be 1, 2 or 3")
    k = min(k, n)
    out = p.copy()
    if k == 1:
        return out
    # second place: sum over the winner j != i
    rest1 = 1.0 - p  # probability mass left after j wins
    second = np.zeros(n)
    for j in range(n):
        if rest1[j] <= 0:
            continue
        share = p / rest1[j]
        share[j] = 0.0
        second += p[j] * share
    out += second
    if k == 2:
        return np.minimum(out, 1.0)
    third = np.zeros(n)
    for j in range(n):
        for m in range(n):
            if m == j:
                continue
            rest2 = 1.0 - p[j] - p[m]
            if rest1[j] <= 0 or rest2 <= 0:
                continue
            pjm = p[j] * p[m] / rest1[j]
            share = p / rest2
            share[j] = share[m] = 0.0
            third += pjm * share
    return np.minimum(out + third, 1.0)


def most_likely_order(p: np.ndarray, k: int) -> list[int]:
    """Indices of the k most likely first finishers, in order.

    Under Harville the most probable ordered k-tuple is the k highest probabilities
    in decreasing order (an adjacent swap can only lower the product).
    """
    order = np.argsort(-np.asarray(p), kind="stable")
    return [int(i) for i in order[:k]]


def places_paid(n_starters: int) -> int:
    """PMU Simple placé: first 3 with 8 or more starters, first 2 with 4 to 7."""
    return 3 if n_starters >= 8 else 2
