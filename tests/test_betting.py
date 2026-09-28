from __future__ import annotations

import itertools
from datetime import date

import numpy as np
import pytest

from predlab.racing.backtest import run_backtest
from predlab.racing.betting import (
    QUINTE,
    SIMPLE_PLACE,
    SIMPLE_WIN,
    TIERCE,
    Ticket,
    exotic_strategies,
    settle,
    simple_strategies,
    simulate,
    summarise,
)
from predlab.racing.domain import Dividend
from predlab.racing.models import CalibratedMarketModel, MarketModel
from predlab.racing.orders import most_likely_order, places_paid, top_k_probabilities
from predlab.racing.sources.pmu.parser import parse_dividends
from predlab.racing.synthetic import make_world

from .conftest import fixture_bytes

REAL = parse_dividends(fixture_bytes("rapports_2026-09-28_R2C1_full.json"), "2026-09-28/R2C1")
QUINTE_DIVS = parse_dividends(
    fixture_bytes("rapports_2026-09-24_R1C1_quinte_excerpt.json"), "2026-09-24/R1C1"
)


# ----------------------------------------------------------------------- dividends


def test_real_dividends_are_parsed_in_euros_per_euro() -> None:
    win = [d for d in REAL if d.bet_type == SIMPLE_WIN]
    assert len(win) == 1 and win[0].numbers == (4,) and win[0].per_euro == pytest.approx(7.60)
    place = {d.numbers: d.per_euro for d in REAL if d.bet_type == SIMPLE_PLACE}
    assert place == {(4,): 1.60, (2,): 1.10, (1,): 1.50}
    assert {d.bet_type for d in REAL} >= {"COUPLE_GAGNANT", "TRIO", "SUPER_QUATRE"}


def test_simple_tickets_settle_on_real_dividends() -> None:
    assert settle(Ticket(SIMPLE_WIN, (4,), 1.0), REAL) == pytest.approx(7.60)
    assert settle(Ticket(SIMPLE_WIN, (2,), 1.0), REAL) == 0.0
    assert settle(Ticket(SIMPLE_PLACE, (2,), 1.0), REAL) == pytest.approx(1.10)
    assert settle(Ticket(SIMPLE_PLACE, (7,), 1.0), REAL) == 0.0


@pytest.mark.parametrize(
    ("numbers", "expected"),
    [
        ((13, 8, 10, 4, 16), 2 * 3237.50),  # ordre
        ((16, 4, 10, 8, 13), 2 * 37.00),  # désordre
        ((13, 8, 10, 4, 1), 2 * 2.30),  # bonus 4 sur 5
        ((13, 8, 10, 1, 2), 2 * 2.10),  # bonus 3
        ((13, 8, 1, 2, 3), 0.0),
    ],
)
def test_quinte_tickets_pay_their_best_rank_only(numbers: tuple[int, ...], expected: float) -> None:
    assert settle(Ticket(QUINTE, numbers, 2.0), QUINTE_DIVS) == pytest.approx(expected)


def test_tierce_order_and_disorder() -> None:
    assert settle(Ticket(TIERCE, (13, 8, 10), 1.0), QUINTE_DIVS) == pytest.approx(399.70)
    assert settle(Ticket(TIERCE, (8, 13, 10), 1.0), QUINTE_DIVS) == pytest.approx(46.20)
    assert settle(Ticket(TIERCE, (8, 13, 1), 1.0), QUINTE_DIVS) == 0.0


def test_a_refunded_bet_returns_the_stake() -> None:
    d = Dividend(
        race_id="r",
        bet_type=TIERCE,
        label="Tiercé Ordre",
        combination=("1", "2", "3"),
        per_euro=0.0,
        base_stake=1.0,
        refunded=True,
    )
    assert settle(Ticket(TIERCE, (4, 5, 6), 1.0), [d]) == 1.0


# -------------------------------------------------------------------------- orders


def _brute_force_top_k(p: np.ndarray, k: int) -> np.ndarray:
    n, out = len(p), np.zeros(len(p))
    for order in itertools.permutations(range(n), k):
        prob, left = 1.0, 1.0
        for i in order:
            prob *= p[i] / left
            left -= p[i]
        for i in order:
            out[i] += prob
    return out


@pytest.mark.parametrize("k", [1, 2, 3])
def test_harville_place_probabilities_are_exact(k: int) -> None:
    p = np.random.default_rng(1).dirichlet(np.ones(6))
    got = top_k_probabilities(p, k)
    assert got == pytest.approx(_brute_force_top_k(p, k))
    assert got.sum() == pytest.approx(k)


def test_order_helpers() -> None:
    assert most_likely_order(np.array([0.1, 0.5, 0.4]), 2) == [1, 2]
    assert places_paid(8) == 3 and places_paid(7) == 2


# ---------------------------------------------------------------------- simulation


def _synthetic_dividends(world) -> dict[str, list[Dividend]]:
    out = {}
    for e in world.events:
        winner = e.outcome.winners[0]
        odds = {s.number: s.odds for s in e.card.starters}
        out[e.card.race_id] = [
            Dividend(
                race_id=e.card.race_id,
                bet_type=SIMPLE_WIN,
                label="Simple gagnant",
                combination=(str(winner),),
                per_euro=odds[winner],
                base_stake=1.0,
            ),
        ]
    return out


def test_simulation_bets_only_on_offered_bet_types() -> None:
    world = make_world(600, seed=11)
    result = run_backtest(
        world.events,
        [MarketModel(), CalibratedMarketModel()],
        horizon_minutes=25,
        keep_forecasts=True,
    )
    strategies = {
        **simple_strategies(["market_calibrated"]),
        **exotic_strategies(["market_calibrated"]),
    }
    ledgers = simulate(result, _synthetic_dividends(world), strategies)
    assert len(ledgers["SG favori"].stake) == 600
    assert ledgers["SP favori"].stake == [], "no place pool offered, no place ticket"
    assert ledgers["Quinté favoris"].stake == [] and ledgers["Tiercé hasard"].stake == []
    rows = {r["strategy"]: r for r in summarise(ledgers, None)}
    # The synthetic market over-bets longshots (flb < 1): random picks must lose more.
    assert rows["SG hasard"]["roi"] < rows["SG favori"]["roi"]
    assert rows["SG hasard"]["roi"] < 0


def test_value_rule_uses_only_horizon_odds() -> None:
    world = make_world(50, seed=12)
    result = run_backtest(
        world.events, [CalibratedMarketModel()], horizon_minutes=25, keep_forecasts=True
    )
    ledgers = simulate(
        result, _synthetic_dividends(world), simple_strategies(["market_calibrated"])
    )
    # α = 1 before 300 released races: calibrated == raw market, p × odds < 1 always.
    assert ledgers["SG valeur market_calibrated"].stake == []
    assert date(2020, 1, 1) <= world.events[0].card.day
