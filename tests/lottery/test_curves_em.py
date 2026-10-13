"""Chance bands for gains and losses over time."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pytest

from predlab.lottery.analysis import incidence
from predlab.lottery.curves_em import GridSeries, payout_curves, relabelled_totals
from predlab.lottery.gamespec import EM_2016_09
from predlab.lottery.payouts import grid_payouts

BALLS = EM_2016_09.pool("main")
STARS = EM_2016_09.pool("stars")


def world(n: int, seed: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    balls = np.sort(np.argsort(rng.random((n, 50)), axis=1)[:, :5] + 1, axis=1)
    stars = np.sort(np.argsort(rng.random((n, 12)), axis=1)[:, :2] + 1, axis=1)
    rapports = np.tile(
        np.array([np.nan, 3e5, 3e4, 2e3, 150, 70, 50, 16, 12, 10, 8, 6, 4.0]), (n, 1)
    )
    return balls, stars, rapports


def series(
    grid_b: np.ndarray,
    grid_s: np.ndarray,
    balls: np.ndarray,
    stars: np.ndarray,
    rapports: np.ndarray,
) -> GridSeries:
    hb = np.array([len(set(g) & set(d)) for g, d in zip(grid_b, balls, strict=True)])
    hs = np.array([len(set(g) & set(d)) for g, d in zip(grid_s, stars, strict=True)])
    pay, _ = grid_payouts(hb, hs, rapports, "2016-09")
    return GridSeries([None if np.isnan(v) else float(v) for v in pay], grid_b, grid_s)


def test_bands_are_ordered_and_cover_every_draw() -> None:
    n = 120
    balls, stars, rapports = world(n)
    fixed_b = np.tile(np.array([1, 2, 3, 4, 5]), (n, 1))
    fixed_s = np.tile(np.array([1, 2]), (n, 1))
    grids = {"a": series(fixed_b, fixed_s, balls, stars, rapports)}
    out = payout_curves(
        [date(2020, 1, 3) + timedelta(days=3 * i) for i in range(n)],
        incidence(balls, BALLS), incidence(stars, STARS), rapports, "2016-09", grids,
        balls=BALLS, stars=STARS, players=300,
    )  # fmt: skip
    for band in ("single_band", "total_band"):
        q = out[band]
        assert len(q["q500"]) == n
        assert all(a <= b <= c for a, b, c in zip(q["q025"], q["q500"], q["q975"], strict=True))
    assert 0.0 <= out["percentile"]["a"] <= 1.0
    # with one grid the two bands describe the same thing
    assert out["single_band"]["q500"][-1] == pytest.approx(out["total_band"]["q500"][-1], rel=0.1)


def test_duplicated_grids_widen_the_total_band() -> None:
    n = 300
    _, _, rapports = world(n, seed=2)
    rng = np.random.default_rng(5)
    gb = np.sort(np.argsort(rng.random((n, 50)), axis=1)[:, :5] + 1, axis=1)
    gs = np.sort(np.argsort(rng.random((n, 12)), axis=1)[:, :2] + 1, axis=1)
    gb2 = np.sort(np.argsort(rng.random((n, 50)), axis=1)[:, :5] + 1, axis=1)
    twin = relabelled_totals(np.stack([gb, gb], 1), np.stack([gs, gs], 1), rapports, "2016-09",
                             balls=BALLS, stars=STARS, players=600, seed=1)  # fmt: skip
    pair = relabelled_totals(np.stack([gb, gb2], 1), np.stack([gs, gs], 1), rapports, "2016-09",
                             balls=BALLS, stars=STARS, players=600, seed=1)  # fmt: skip
    assert twin.sum(axis=1).std() > pair.sum(axis=1).std()
    # same expected payout whatever the overlap
    assert twin.mean() == pytest.approx(pair.mean(), rel=0.1)


def test_mismatched_grid_length_is_refused() -> None:
    balls, stars, rapports = world(10)
    bad = GridSeries([0.0] * 9, np.ones((10, 5), dtype=int), np.ones((10, 2), dtype=int))
    with pytest.raises(ValueError):
        payout_curves(
            [date(2020, 1, 3)] * 10, incidence(balls, BALLS), incidence(stars, STARS), rapports,
            "2016-09", {"x": bad}, balls=BALLS, stars=STARS, players=10,
        )  # fmt: skip
