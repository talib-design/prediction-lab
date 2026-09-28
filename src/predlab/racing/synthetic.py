"""Synthetic races whose truth is known: the bench is tested before it is trusted.

Level 1 of the success criterion (docs/METHODOLOGY.md §5): before any real result is
believed, the same engine and report must

1. find a real edge -- an *oracle* that knows the true probabilities must be declared
   better than the calibrated market;
2. correct a planted market bias -- raw odds distorted by a favourite-longshot bias
   must be declared worse than the calibrated market;
3. refuse a fake edge -- a model that is the market plus noise must *not* be declared
   better.

The world: each starter has a latent strength; true win probabilities are its
softmax. The public's probabilities flatten the truth (p ∝ truth^flb, flb < 1 means
longshots are over-bet), add noise, and pay out after a takeout. Only the winner
matters for scoring, so no finishing order beyond first is simulated.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any

import numpy as np

from predlab.core.probability import normalise_to_total
from predlab.racing.events import RaceCard, RaceEvent, RaceOutcome, Starter, result_known_at
from predlab.racing.knowledge import Knowledge
from predlab.racing.models import MarketModel, market_probabilities


@dataclass
class SyntheticWorld:
    events: list[RaceEvent]
    truth: dict[str, np.ndarray]


def _softmax(x: np.ndarray) -> np.ndarray:
    z = np.exp(x - x.max())
    return z / z.sum()


def make_world(
    n_races: int = 3000,
    *,
    seed: int = 0,
    flb: float = 0.8,
    market_noise: float = 0.15,
    takeout: float = 0.18,
    start: date = date(2020, 1, 1),
) -> SyntheticWorld:
    rng = np.random.default_rng(seed)
    events, truth = [], {}
    for i in range(n_races):
        day = start + timedelta(days=i // 8)
        off = datetime(day.year, day.month, day.day, 12, 0, tzinfo=UTC) + timedelta(
            minutes=30 * (i % 8)
        )
        n = int(rng.integers(6, 15))
        p = _softmax(rng.normal(0.0, 1.0, n))
        public = _softmax(flb * np.log(p) + rng.normal(0.0, market_noise, n))
        odds = np.maximum(1.1, np.round(1.0 / (public * (1.0 + takeout)), 1))
        winner = int(rng.choice(n, p=p))
        race_id = f"{day.isoformat()}/S{i}"
        starters = tuple(
            Starter(
                number=j + 1,
                horse_id=f"H{i}-{j}",
                jockey=f"J{int(rng.integers(0, 50))}",
                trainer=f"T{int(rng.integers(0, 50))}",
                draw=j + 1,
                weight_raw=None,
                age=None,
                odds=float(odds[j]),
                odds_reported_at=off - timedelta(minutes=30),
            )
            for j in range(n)
        )
        card = RaceCard(
            race_id, day, off, off - timedelta(minutes=25), "SYN", None, None, None, starters
        )
        outcome = RaceOutcome(race_id, {j + 1: (1 if j == winner else None) for j in range(n)})
        events.append(RaceEvent(card, outcome, result_known_at(day)))
        truth[race_id] = p
    return SyntheticWorld(events, truth)


class OracleModel:
    """Knows the true probabilities. Exists only to prove an edge can be detected."""

    name, version = "oracle", "1"

    def __init__(self, truth: dict[str, np.ndarray]) -> None:
        self.truth = truth

    def config(self) -> dict[str, Any]:
        return {}

    def observe(self, event: RaceEvent, knowledge: Knowledge) -> None:
        return None

    def predict(self, card: RaceCard, knowledge: Knowledge) -> np.ndarray:
        return normalise_to_total(self.truth[card.race_id], 1.0)


class JitteredMarketModel(MarketModel):
    """The market plus multiplicative noise: a fake edge that must not pass."""

    name = "market_jittered"

    def __init__(self, sigma: float = 0.05, seed: int = 0) -> None:
        self.sigma, self.seed = sigma, seed

    def config(self) -> dict[str, Any]:
        return {"sigma": self.sigma, "seed": self.seed}

    def predict(self, card: RaceCard, knowledge: Knowledge) -> np.ndarray:
        digest = hashlib.sha256(f"{self.seed}:{card.race_id}".encode()).digest()
        rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
        q = market_probabilities(card) * rng.lognormal(0.0, self.sigma, card.n)
        return normalise_to_total(q, 1.0)
