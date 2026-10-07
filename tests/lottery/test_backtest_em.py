"""Logics, witness, random players and payouts."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pytest

from predlab.lottery.analysis import incidence
from predlab.lottery.backtest_em import (
    hypergeometric_matches,
    random_players_matches,
    run_d1,
    run_d2,
    witness_grid,
)
from predlab.lottery.gamespec import EM_2016_09
from predlab.lottery.historyview import build_view
from predlab.lottery.logics_em import SelectionPredictor
from predlab.lottery.payouts import RANKS_2011_05, RANKS_2016_09, grid_payouts, tier_probability

MAIN = EM_2016_09.pool("main")
STARS = EM_2016_09.pool("stars")


def synthetic(n: int, seed: int = 0) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    rng = np.random.default_rng(seed)
    start = date(2016, 9, 27)
    dates = np.array(
        [np.datetime64(start + timedelta(days=3 * i + (i % 2)), "D") for i in range(n)],
        dtype="datetime64[D]",
    )
    main = np.sort(np.argsort(rng.random((n, 50)), axis=1)[:, :5] + 1, axis=1).astype(np.int16)
    stars = np.sort(np.argsort(rng.random((n, 12)), axis=1)[:, :2] + 1, axis=1).astype(np.int16)
    return dates, {"main": main, "stars": stars}


def test_hypergeometric_moments() -> None:
    assert hypergeometric_matches(MAIN) == pytest.approx((0.5, 0.41327), abs=1e-4)
    assert hypergeometric_matches(STARS) == pytest.approx((1 / 3, 0.25253), abs=1e-4)


def test_witness_grid_is_legal_and_depends_on_the_date_only() -> None:
    a = witness_grid(date(2026, 10, 9), EM_2016_09.pools)
    assert a == witness_grid(date(2026, 10, 9), EM_2016_09.pools)
    assert a != witness_grid(date(2026, 10, 13), EM_2016_09.pools)
    MAIN.validate_combination(a["main"])
    STARS.validate_combination(a["stars"])
    # the balls do not depend on whether stars are also drawn
    assert witness_grid(date(2026, 10, 9), (MAIN,))["main"] == a["main"]


def test_random_players_average_the_exact_expectation() -> None:
    _, pools = synthetic(400)
    out = incidence(pools["main"].astype(np.int64), MAIN)
    players = random_players_matches(out, MAIN, players=300)
    assert players.mean() == pytest.approx(0.5, abs=0.01)


def test_selection_predictor_boosts_its_selection() -> None:
    dates, pools = synthetic(120)
    view = build_view(EM_2016_09, dates, pools, as_of=date(2030, 1, 1))
    fc = SelectionPredictor(spec=EM_2016_09, kind="repeat").forecast(view, date(2030, 1, 1))
    probs = fc.pools["main"].inclusion_probs
    last = pools["main"][-1] - 1
    assert probs.sum() == pytest.approx(5)
    others = np.setdiff1d(np.arange(50), last)
    assert np.allclose(probs[last], 1.5 * 5 / 52.5)  # beta = 0.5 on the 5 selected
    assert np.allclose(probs[others], 5 / 52.5)


def test_rank_tables_and_odds() -> None:
    assert 1 / tier_probability(5, 2, 12) == pytest.approx(139_838_160)
    assert 1 / tier_probability(2, 0, 12) == pytest.approx(21.9, abs=0.1)
    assert RANKS_2016_09[(3, 2)] == 6 and RANKS_2011_05[(3, 2)] == 7
    assert sorted(RANKS_2016_09.values()) == list(range(1, 14))
    assert sorted(RANKS_2011_05.values()) == list(range(1, 14))


def test_grid_payouts_lookup_and_unknown_jackpot() -> None:
    rapports = np.full((3, 13), np.nan)
    rapports[:, 12] = 4.1  # rank 13
    rapports[:, 5] = 69.2  # rank 6
    pay, rank = grid_payouts(np.array([2, 3, 5]), np.array([0, 2, 2]), rapports, "2016-09")
    assert rank.tolist() == [13, 6, 1]
    assert pay[:2].tolist() == [4.1, 69.2]
    assert np.isnan(pay[2])  # rank 1 with no rapport: unknown, not zero
    pay2, rank2 = grid_payouts(np.array([[1, 0]]), np.array([[1, 0]]), rapports[:2], "2016-09")
    assert rank2.tolist() == [[0, 0]] and pay2.tolist() == [[0.0, 0.0]]


def test_run_d1_and_d2_on_synthetic_fair_draws() -> None:
    dates, pools = synthetic(260)
    result, summary = run_d1(EM_2016_09, dates, pools)
    assert summary["n_targets"] == 60
    logics = summary["pools"]["main"]["logics"]
    assert len(logics) == 8
    rapports = np.tile(np.array([np.nan] + [1000.0] * 11 + [4.0]), (60, 1))
    d2 = run_d2(result, rapports, "2016-09")
    assert set(d2["logics"]) == {lg["logic"] for lg in logics}
    assert d2["random_players"]["players"] == 1000
