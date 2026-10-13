"""Gains and losses over time, per grid and for all grids played together, against chance.

A cumulative net curve says little on its own: it is a slope of -2.50 EUR per draw with a
few bumps. What makes it readable is the band of what chance alone produces on the very
same draws, with the very same official payouts.

* **One grid**: any grid chosen without seeing the draw is, for the draw, a random grid.
  The band is the 2.5 %, 50 % and 97.5 % quantiles of the cumulative net of 1 000 players
  each playing one random grid per draw.
* **All grids together**: the logics' grids overlap (two of them often play the very same
  grid), so their total swings more than that of independent random grids. The band keeps
  the real grids and replaces each draw by a random one (a random relabelling of the
  numbers: exact under the null that the grids carry no information), 1 000 times. The
  overlap structure, duplicates included, is therefore in the band.

Unknown payouts (rank 1 with no rapport: the jackpot rolled over) count as 0 in the bands
and are reported ``null`` for the grids.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

import numpy as np

from predlab.lottery.backtest_em import random_players_matches
from predlab.lottery.gamespec import NumberPool
from predlab.lottery.payouts import GRID_PRICE_EUR, grid_payouts

QUANTILES = (0.025, 0.5, 0.975)


@dataclass(frozen=True, slots=True)
class GridSeries:
    """One logic's grids over ``n`` draws and what they paid."""

    payouts: Sequence[float | None]  # EUR per draw, None = unknown (rank 1, no rapport)
    balls: np.ndarray  # (n, 5)
    stars: np.ndarray  # (n, 2)


def _band(cum: np.ndarray) -> dict[str, list[float]]:
    qs = np.quantile(cum, QUANTILES, axis=0)
    return {
        f"q{int(q * 1000):03d}": [round(float(v), 2) for v in row]
        for q, row in zip(QUANTILES, qs, strict=True)
    }


def _one_hot(numbers: np.ndarray, pool: NumberPool) -> np.ndarray:
    """``(n, k, m)`` numbers -> ``(n, k, size)`` 0/1."""
    n, k, _ = numbers.shape
    out = np.zeros((n, k, pool.size), dtype=np.float32)
    idx = numbers.astype(np.int64) - pool.low
    np.put_along_axis(out, idx, 1.0, axis=2)
    return out


def _random_draws(rng: np.random.Generator, c: int, n: int, pool: NumberPool) -> np.ndarray:
    keys = rng.random((c, n, pool.size), dtype=np.float32)
    picks = np.argpartition(keys, pool.k, axis=2)[:, :, : pool.k]
    out = np.zeros((c, n, pool.size), dtype=np.float32)
    np.put_along_axis(out, picks, 1.0, axis=2)
    return out


def relabelled_totals(
    grid_balls: np.ndarray,
    grid_stars: np.ndarray,
    rapports: np.ndarray,
    era: str,
    *,
    balls: NumberPool,
    stars: NumberPool,
    players: int,
    seed: int,
) -> np.ndarray:
    """``(players, n)`` total payout of the k real grids against random draws."""
    n, k, _ = grid_balls.shape
    gb = _one_hot(grid_balls, balls)
    gs = _one_hot(grid_stars, stars)
    rng = np.random.default_rng(seed)
    out = np.empty((players, n), dtype=np.float64)
    chunk = max(1, 4_000_000 // max(1, n * balls.size))
    for s in range(0, players, chunk):
        c = min(chunk, players - s)
        bm = np.einsum("cnu,nku->cnk", _random_draws(rng, c, n, balls), gb).round().astype(np.int64)
        sm = np.einsum("cnu,nku->cnk", _random_draws(rng, c, n, stars), gs).round().astype(np.int64)
        flat_b = bm.transpose(0, 2, 1).reshape(c * k, n)
        flat_s = sm.transpose(0, 2, 1).reshape(c * k, n)
        pay, _ = grid_payouts(flat_b, flat_s, rapports, era)
        out[s : s + c] = np.nan_to_num(pay, nan=0.0).reshape(c, k, n).sum(axis=1)
    return out


def payout_curves(
    dates: Sequence[date],
    ball_outcomes: np.ndarray,
    star_outcomes: np.ndarray,
    rapports: np.ndarray,
    era: str,
    grids: Mapping[str, GridSeries],
    *,
    balls: NumberPool,
    stars: NumberPool,
    players: int = 1000,
    seed: int = 31,
    price: float = GRID_PRICE_EUR,
) -> dict[str, Any]:
    """Per-draw payouts of each grid, plus the chance bands for one grid and for all."""
    n = len(dates)
    if not grids:
        raise ValueError("no grids")
    for name, g in grids.items():
        if len(g.payouts) != n or g.balls.shape != (n, balls.k) or g.stars.shape != (n, stars.k):
            raise ValueError(f"grid {name!r} does not cover the {n} draws")
    k = len(grids)
    b = random_players_matches(ball_outcomes, balls, players=players, seed=seed)
    s = random_players_matches(star_outcomes, stars, players=players, seed=seed + 1)
    single_pay, _ = grid_payouts(b, s, rapports, era)
    single = np.cumsum(np.nan_to_num(single_pay, nan=0.0) - price, axis=1)
    totals = relabelled_totals(
        np.stack([g.balls for g in grids.values()], axis=1),
        np.stack([g.stars for g in grids.values()], axis=1),
        rapports,
        era,
        balls=balls,
        stars=stars,
        players=players,
        seed=seed + 2,
    )
    total = np.cumsum(totals - k * price, axis=1)

    def net(g: GridSeries) -> float:
        return float(sum(v or 0.0 for v in g.payouts) - price * n)

    finals = {name: net(g) for name, g in grids.items()}
    grand = sum(finals.values())
    return {
        "dates": [d.isoformat() for d in dates],
        "price": price,
        "players": players,
        "n_grids": k,
        "grids": {
            name: [None if v is None or np.isnan(v) else round(float(v), 2) for v in g.payouts]
            for name, g in grids.items()
        },
        "single_band": _band(single),
        "total_band": _band(total),
        # share of chance players who ended below each grid / below the total
        "percentile": {name: float((single[:, -1] < v).mean()) for name, v in finals.items()},
        "total_percentile": float((total[:, -1] < grand).mean()),
    }
