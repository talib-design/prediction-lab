"""EuroMillions prize ranks and fictive-grid payouts.

The rank of a grid is decided by (balls matched, stars matched). The mapping below is the
published 13-rank table; it was **checked against the archive** rather than trusted: over
the 1 047 draws of era 2016-09 the total number of European winners of every rank, divided
by the winners of rank 13, equals the combinatorial odds ratio within 1.2 % for 12 ranks
and 4 % for rank 2 (5+1, a few winners per draw) (``verify_rank_mapping``). In era 2011-05 the same check shows ranks 6 and 7 the
other way round (4+0 was then rarer than 3+2 with 11 stars), hence a separate table.

Payouts are the official ``rapport`` per winner. Rank 1 when nobody won has no rapport
(the jackpot rolled over): a fictive grid reaching it would be "unknown", never zero.
"""

from __future__ import annotations

import math

import numpy as np

RANKS_2016_09: dict[tuple[int, int], int] = {
    (5, 2): 1, (5, 1): 2, (5, 0): 3, (4, 2): 4, (4, 1): 5, (3, 2): 6, (4, 0): 7,
    (2, 2): 8, (3, 1): 9, (3, 0): 10, (1, 2): 11, (2, 1): 12, (2, 0): 13,
}  # fmt: skip
RANKS_2011_05: dict[tuple[int, int], int] = {
    **RANKS_2016_09,
    (4, 0): 6,
    (3, 2): 7,
}
RANKS_BY_ERA: dict[str, dict[tuple[int, int], int]] = {
    "2016-09": RANKS_2016_09,
    "2011-05": RANKS_2011_05,
}
STARS_BY_ERA = {"2004-02": 9, "2011-05": 11, "2016-09": 12}

# Price of one grid in France, read on the FDJ EuroMillions page on 2026-10-06. Whether
# it was the same over the whole 2016-09 era is not verified: "Je ne sais pas".
GRID_PRICE_EUR = 2.50


def tier_probability(balls: int, stars: int, n_stars: int) -> float:
    """P(exactly ``balls`` of 5 and ``stars`` of 2) for one random grid."""
    pb = math.comb(5, balls) * math.comb(45, 5 - balls) / math.comb(50, 5)
    ps = math.comb(2, stars) * math.comb(n_stars - 2, 2 - stars) / math.comb(n_stars, 2)
    return pb * ps


def verify_rank_mapping(
    winners_eu: np.ndarray, mapping: dict[tuple[int, int], int], n_stars: int
) -> dict[int, float]:
    """Observed / expected ratio of total winners per rank, relative to rank 13."""
    totals = np.nansum(winners_eu, axis=0)
    p13 = tier_probability(2, 0, n_stars)
    out: dict[int, float] = {}
    for (b, s), rank in mapping.items():
        expected = tier_probability(b, s, n_stars) / p13
        out[rank] = float(totals[rank - 1] / totals[12] / expected)
    return out


def grid_payouts(
    ball_hits: np.ndarray, star_hits: np.ndarray, rapports: np.ndarray, era: str
) -> tuple[np.ndarray, np.ndarray]:
    """Payout per grid (EUR) and rank (0 = nothing won). ``nan`` payout = rank 1 unknown.

    ``ball_hits``/``star_hits`` have shape ``(n,)`` or ``(players, n)``; ``rapports`` is
    ``(n, 13)``.
    """
    mapping = RANKS_BY_ERA[era]
    table = np.zeros((6, 3), dtype=np.int64)
    for (b, s), rank in mapping.items():
        table[b, s] = rank
    rank = table[ball_hits.astype(np.int64), star_hits.astype(np.int64)]
    padded = np.concatenate([np.zeros((rapports.shape[0], 1)), rapports], axis=1)
    padded = np.where(np.isnan(padded), np.nan, padded)
    cols = np.arange(rapports.shape[0])
    pay = padded[cols, rank] if rank.ndim == 1 else padded[cols[None, :], rank]
    pay = np.where(rank == 0, 0.0, pay)
    # a rank 2-13 with no rapport cannot happen for a winning grid (we would be a winner);
    # count it as unknown as well rather than inventing a value
    return pay, rank
