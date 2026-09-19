from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pytest

from predlab.core.gamespec import LOTO_2019_11, GameSpec


@pytest.fixture
def loto() -> GameSpec:
    return LOTO_2019_11


def synthetic_draws(
    spec: GameSpec, n: int, seed: int = 0, start: date = date(2020, 1, 1)
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """A fair, uniform, strictly increasing-date dataset for structural tests.

    This is a fixture for testing plumbing, not a scientific synthetic benchmark.
    """
    rng = np.random.default_rng(seed)
    dates = np.array(
        [np.datetime64(start + timedelta(days=2 * i), "D") for i in range(n)],
        dtype="datetime64[D]",
    )
    pools: dict[str, np.ndarray] = {}
    for pool in spec.pools:
        rows = np.empty((n, pool.k), dtype=np.int16)
        for i in range(n):
            rows[i] = rng.choice(np.arange(pool.low, pool.high + 1), size=pool.k, replace=False)
        pools[pool.name] = rows
    return dates, pools
