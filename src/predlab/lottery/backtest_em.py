"""D1 / D2 / R1: walk-forward backtest of the prediction logics against pure chance.

Two walk-forward runs, each starting at the 201st draw of its data set:

* **balls, 2004-2026** (``EM_MAIN_2004``, 1 987 draws): the decision run for D1;
* **full grid, era 2016-09** (5 balls + 2 stars of 12, 1 047 draws): stars and the fictive
  payouts of D2, because only this era has a single star pool and a verified rank table.

"Hasard" appears three ways, so a reader can choose the one that speaks to them:

* the exact law (hypergeometric) of the number of matches of any grid chosen without
  seeing the draw -- the reference for the z tests;
* the witness player of em-R1: one random grid per draw, seeded by the draw date;
* 1 000 random players, to show the spread chance alone produces (percentiles).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date
from typing import Any

import numpy as np
from scipy import stats

from predlab.eval.uncertainty import block_bootstrap, paired_block_permutation_test
from predlab.lottery.analysis import bh_adjust
from predlab.lottery.baselines import (
    FrequencyPredictor,
    GapPredictor,
    ShrunkFrequencyPredictor,
    UniformPredictor,
)
from predlab.lottery.engine import BacktestConfig, BacktestResult, ModelRun, run_backtest
from predlab.lottery.gamespec import GameSpec, NumberPool
from predlab.lottery.logics_em import SelectionPredictor
from predlab.lottery.payouts import GRID_PRICE_EUR, grid_payouts
from predlab.lottery.selection import TopKPolicy

SPLIT = np.datetime64("2020-01-01", "D")
N_PLAYERS = 1000

LOGIC_LABELS = {
    "frequency": "fréquence totale",
    "rolling_frequency_100": "fréquence 100 derniers",
    "rolling_frequency_300": "fréquence 300 derniers",
    "shrunk_frequency": "fréquence rétrécie (James-Stein)",
    "gap": "retard",
    "hot50": "chauds (50 derniers)",
    "cold50": "froids (50 derniers)",
    "repeat": "répétition du dernier tirage",
}


def logic_models(spec: GameSpec) -> list[Any]:
    """Uniform reference first, then the eight logics registered in em-D1."""
    return [
        UniformPredictor(spec=spec),
        FrequencyPredictor(spec=spec, window=None),
        FrequencyPredictor(spec=spec, window=100),
        FrequencyPredictor(spec=spec, window=300),
        ShrunkFrequencyPredictor(spec=spec),
        GapPredictor(spec=spec),
        SelectionPredictor(spec=spec, kind="hot", window=50),
        SelectionPredictor(spec=spec, kind="cold", window=50),
        SelectionPredictor(spec=spec, kind="repeat"),
    ]


def hypergeometric_matches(pool: NumberPool) -> tuple[float, float]:
    """Mean and variance of the matches of a k-number grid chosen blind."""
    rv = stats.hypergeom(pool.size, pool.k, pool.k)
    return float(rv.mean()), float(rv.var())


def witness_grid(day: date, pools: tuple[NumberPool, ...]) -> dict[str, tuple[int, ...]]:
    """em-R1: the witness's grid for ``day``. Depends on the date only, so anyone can
    recompute it and nobody can re-roll it."""
    seed = int.from_bytes(hashlib.sha256(f"em-R1|{day.isoformat()}".encode()).digest()[:8], "big")
    rng = np.random.default_rng(seed)
    return {
        p.name: tuple(
            sorted(int(v) for v in rng.choice(np.arange(p.low, p.high + 1), p.k, replace=False))
        )
        for p in pools
    }


def random_players_matches(
    outcomes: np.ndarray, pool: NumberPool, players: int = N_PLAYERS, seed: int = 7
) -> np.ndarray:
    """``(players, n)`` matches of independent random grids on the same draws."""
    n = outcomes.shape[0]
    rng = np.random.default_rng(seed)
    out = np.empty((players, n), dtype=np.int8)
    chunk = max(1, 2_000_000 // max(1, n * pool.size))
    rows = np.arange(n)[None, :, None]
    for s in range(0, players, chunk):
        e = min(players, s + chunk)
        picks = np.argpartition(rng.random((e - s, n, pool.size), dtype=np.float32), pool.k, axis=2)
        picks = picks[:, :, : pool.k]
        out[s:e] = outcomes[rows, picks].sum(axis=2)
    return out


@dataclass(frozen=True, slots=True)
class PoolComparison:
    logic: str
    pool: str
    n: int
    logloss_diff: float  # logic - uniform, per draw (negative = better than uniform)
    logloss_ci: tuple[float, float]
    logloss_p: float
    logloss_diff_early: float
    logloss_diff_late: float
    mean_matches: float
    matches_z: float
    matches_p: float
    percentile_vs_players: float  # share of random players with fewer total matches

    def as_dict(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


def compare_pool(
    result: BacktestResult, pool_name: str, players: np.ndarray, *, seed: int = 0
) -> list[PoolComparison]:
    uniform = result.run_for("uniform")
    pool = result.spec.pool(pool_name)
    mean0, var0 = hypergeometric_matches(pool)
    dates = np.array(uniform.target_dates, dtype="datetime64[D]")
    late = dates >= SPLIT
    totals = players.sum(axis=1)
    out: list[PoolComparison] = []
    base = uniform.series(pool_name, "log_loss")
    for run in result.runs:
        if run.model_name == "uniform":
            continue
        ll = run.series(pool_name, "log_loss")
        diff = ll - base
        ci = block_bootstrap(diff, seed=seed)
        test = paired_block_permutation_test(ll, base, seed=seed)
        m = run.matches[pool_name].astype(np.float64)
        n = len(m)
        z = (m.sum() - n * mean0) / np.sqrt(n * var0)
        out.append(
            PoolComparison(
                logic=run.model_name,
                pool=pool_name,
                n=n,
                logloss_diff=float(diff.mean()),
                logloss_ci=(ci.low, ci.high),
                logloss_p=test.p_value,
                logloss_diff_early=float(diff[~late].mean()) if (~late).any() else float("nan"),
                logloss_diff_late=float(diff[late].mean()) if late.any() else float("nan"),
                mean_matches=float(m.mean()),
                matches_z=float(z),
                matches_p=float(2 * stats.norm.sf(abs(z))),
                percentile_vs_players=float((totals < m.sum()).mean()),
            )
        )
    return out


def _witness_matches(run: ModelRun, spec: GameSpec, pool_name: str) -> np.ndarray:
    pool = spec.pool(pool_name)
    out = np.empty(len(run.target_dates), dtype=np.int8)
    for i, day in enumerate(run.target_dates):
        grid = np.array(witness_grid(day, spec.pools)[pool_name]) - pool.low
        out[i] = run.outcomes[pool_name][i, grid].sum()
    return out


def run_d1(
    spec: GameSpec, dates: np.ndarray, pools: dict[str, np.ndarray]
) -> tuple[BacktestResult, dict[str, Any]]:
    """Walk-forward for one data set; returns the engine result and a JSON-able summary."""
    result = run_backtest(
        spec, dates, pools, logic_models(spec), TopKPolicy(), BacktestConfig(min_train_draws=200)
    )
    uniform = result.run_for("uniform")
    summary: dict[str, Any] = {
        "spec": spec.key,
        "n_draws_total": result.n_draws_total,
        "n_targets": len(uniform.target_dates),
        "first_target": uniform.target_dates[0].isoformat(),
        "last_target": uniform.target_dates[-1].isoformat(),
        "dataset_fingerprint": result.dataset_fingerprint,
        "pools": {},
    }
    for pool in spec.pools:
        players = random_players_matches(uniform.outcomes[pool.name], pool)
        comps = compare_pool(result, pool.name, players)
        qs = bh_adjust([c.logloss_p for c in comps])  # BH across the 8 logics, per pool
        witness = _witness_matches(uniform, spec, pool.name).astype(np.float64)
        mean0, var0 = hypergeometric_matches(pool)
        wz = (witness.sum() - len(witness) * mean0) / np.sqrt(len(witness) * var0)
        totals = players.sum(axis=1) / players.shape[1]
        summary["pools"][pool.name] = {
            "expected_matches": mean0,
            "variance_matches": var0,
            "logics": [
                {**c.as_dict(), "logloss_q": float(q)} for c, q in zip(comps, qs, strict=True)
            ],
            "witness_r1": {"mean_matches": float(witness.mean()), "z": float(wz)},
            "random_players": {
                "players": int(players.shape[0]),
                "mean_matches_quantiles": {
                    str(q): float(np.quantile(totals, q)) for q in (0.025, 0.5, 0.975)
                },
                "best": float(totals.max()),
                "worst": float(totals.min()),
            },
        }
    return result, summary


def run_d2(result: BacktestResult, rapports: np.ndarray, era: str) -> dict[str, Any]:
    """Fictive payouts, one grid per draw, at the official rapport (era 2016-09 only)."""
    uniform = result.run_for("uniform")
    main, stars = result.spec.pool("main"), result.spec.pool("stars")
    out: dict[str, Any] = {"price_eur": GRID_PRICE_EUR, "n_draws": len(uniform.target_dates)}

    def describe(pay: np.ndarray, rank: np.ndarray) -> dict[str, Any]:
        known = pay[~np.isnan(pay)]
        ci = block_bootstrap(known, seed=0)
        return {
            "mean_payout_eur": float(known.mean()),
            "ci95": [ci.low, ci.high],
            "roi": float(known.mean() / GRID_PRICE_EUR - 1),
            "wins": int((rank > 0).sum()),
            "rank_counts": {
                str(r): int((rank == r).sum()) for r in range(1, 14) if (rank == r).any()
            },
            "unknown_rank1": int(np.isnan(pay).sum()),
        }

    players_main = random_players_matches(uniform.outcomes["main"], main, seed=11)
    players_stars = random_players_matches(uniform.outcomes["stars"], stars, seed=12)
    p_pay, _ = grid_payouts(players_main, players_stars, rapports, era)
    p_mean = np.nanmean(p_pay, axis=1)
    out["random_players"] = {
        "players": int(p_pay.shape[0]),
        "mean_payout_quantiles": {
            str(q): float(np.quantile(p_mean, q)) for q in (0.025, 0.5, 0.975)
        },
        "roi_median": float(np.median(p_mean) / GRID_PRICE_EUR - 1),
    }
    w_main = _witness_matches(uniform, result.spec, "main")
    w_stars = _witness_matches(uniform, result.spec, "stars")
    out["witness_r1"] = describe(*grid_payouts(w_main, w_stars, rapports, era))
    out["logics"] = {}
    for run in result.runs:
        if run.model_name == "uniform":
            continue
        pay, rank = grid_payouts(run.matches["main"], run.matches["stars"], rapports, era)
        info = describe(pay, rank)
        info["percentile_vs_players"] = float((p_mean < np.nanmean(pay)).mean())
        out["logics"][run.model_name] = info
    return out
