"""Baselines. Benchmarks, not candidates.

Every model maps a :class:`RaceCard` and the released :class:`Knowledge` to one win
probability per starter, in card order, summing to 1. Hyper-parameters are fixed here
*before* any backtest (docs/METHODOLOGY.md): a baseline tuned on the test window would
be a candidate pretending to be a benchmark.

| model | what it asserts |
|---|---|
| ``random`` | nothing; Dirichlet(1) noise. Must lose to ``uniform`` under a proper score |
| ``uniform`` | every starter equal |
| ``horse_win_rate`` | a horse's past win rate, shrunk toward the base rate |
| ``form`` | recent relative finishing positions, from our own history (not the musique) |
| ``market`` | normalised implied probabilities from the latest pre-horizon odds |
| ``market_calibrated`` | the same, corrected for the favourite-longshot bias by a power
  law refitted on released history only -- **the bar to beat** |
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np
from scipy.optimize import minimize_scalar

from predlab.core.probability import implied_probabilities, normalise_to_total
from predlab.racing.events import RaceCard, RaceEvent
from predlab.racing.knowledge import Knowledge


class RaceModel(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    def config(self) -> dict[str, Any]: ...

    def predict(self, card: RaceCard, knowledge: Knowledge) -> np.ndarray: ...

    def observe(self, event: RaceEvent, knowledge: Knowledge) -> None:
        """Called once per race when its result is released. Default: nothing."""
        ...


class _Base:
    name = "base"
    version = "1"

    def config(self) -> dict[str, Any]:
        return {}

    def observe(self, event: RaceEvent, knowledge: Knowledge) -> None:
        return None


class UniformModel(_Base):
    name = "uniform"

    def predict(self, card: RaceCard, knowledge: Knowledge) -> np.ndarray:
        return np.full(card.n, 1.0 / card.n)


class RandomModel(_Base):
    name = "random"

    def __init__(self, seed: int = 0) -> None:
        self.seed = seed

    def config(self) -> dict[str, Any]:
        return {"seed": self.seed}

    def predict(self, card: RaceCard, knowledge: Knowledge) -> np.ndarray:
        digest = hashlib.sha256(f"{self.seed}:{card.race_id}".encode()).digest()
        rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
        return normalise_to_total(rng.dirichlet(np.ones(card.n)), 1.0)


class HorseWinRateModel(_Base):
    name = "horse_win_rate"

    def __init__(self, prior_strength: float = 5.0) -> None:
        self.prior_strength = prior_strength

    def config(self) -> dict[str, Any]:
        return {"prior_strength": self.prior_strength}

    def predict(self, card: RaceCard, knowledge: Knowledge) -> np.ndarray:
        a, r0 = self.prior_strength, knowledge.base_rate
        scores = []
        for s in card.starters:
            runs = knowledge.horse_runs(s.horse_id)
            wins = sum(r.position == 1 for r in runs)
            scores.append((wins + a * r0) / (len(runs) + a))
        return normalise_to_total(np.array(scores), 1.0)


class FormModel(_Base):
    name = "form"

    def __init__(self, window: int = 3, beta: float = 3.0, neutral: float = 0.5) -> None:
        self.window, self.beta, self.neutral = window, beta, neutral

    def config(self) -> dict[str, Any]:
        return {"window": self.window, "beta": self.beta, "neutral": self.neutral}

    def predict(self, card: RaceCard, knowledge: Knowledge) -> np.ndarray:
        scores = []
        for s in card.starters:
            recent = knowledge.horse_runs(s.horse_id)[-self.window :]
            x = float(np.mean([r.relative_position for r in recent])) if recent else self.neutral
            scores.append(math.exp(-self.beta * x))
        return normalise_to_total(np.array(scores), 1.0)


def market_probabilities(card: RaceCard) -> np.ndarray:
    if not card.market_complete:
        raise ValueError(f"{card.race_id}: market incomplete at prediction time")
    return implied_probabilities(np.array([s.odds for s in card.starters], dtype=float))


class MarketModel(_Base):
    name = "market"

    def predict(self, card: RaceCard, knowledge: Knowledge) -> np.ndarray:
        return normalise_to_total(market_probabilities(card), 1.0)


def _power(q: np.ndarray, alpha: float) -> np.ndarray:
    z = np.power(q, alpha)
    return z / z.sum()


@dataclass
class CalibratedMarketModel:
    """p_i ∝ q_i^α. α > 1 sharpens toward favourites, the usual direction of the
    favourite-longshot correction. α is refitted every ``refit_every`` released races,
    on released races only; until ``min_races`` are available, α = 1 (raw market)."""

    refit_every: int = 500
    min_races: int = 300
    bounds: tuple[float, float] = (0.5, 2.5)
    name: str = "market_calibrated"
    version: str = "1"
    alpha: float = 1.0
    _pairs: list[tuple[np.ndarray, list[int]]] = field(default_factory=list, repr=False)
    _since_fit: int = 0
    history: list[tuple[str, float]] = field(default_factory=list)

    def config(self) -> dict[str, Any]:
        return {"refit_every": self.refit_every, "min_races": self.min_races, "bounds": self.bounds}

    def predict(self, card: RaceCard, knowledge: Knowledge) -> np.ndarray:
        return normalise_to_total(_power(market_probabilities(card), self.alpha), 1.0)

    def observe(self, event: RaceEvent, knowledge: Knowledge) -> None:
        if not event.card.market_complete:
            return
        self._pairs.append((market_probabilities(event.card), event.winner_indices()))
        self._since_fit += 1
        if len(self._pairs) >= self.min_races and self._since_fit >= self.refit_every:
            self.alpha = fit_power(self._pairs, self.bounds)
            self._since_fit = 0
            self.history.append((event.card.race_id, self.alpha))


def fit_power(pairs: list[tuple[np.ndarray, list[int]]], bounds: tuple[float, float]) -> float:
    """Maximum-likelihood α for p ∝ q^α, vectorised over padded fields.

    A dead heat counts each co-winner with weight 1/k, as in the scoring rule.
    """
    width = max(len(q) for q, _ in pairs)
    logq = np.zeros((len(pairs), width))
    mask = np.zeros((len(pairs), width), dtype=bool)
    weight = np.zeros((len(pairs), width))
    for i, (q, winners) in enumerate(pairs):
        logq[i, : len(q)] = np.log(np.clip(q, 1e-12, None))
        mask[i, : len(q)] = True
        weight[i, winners] = 1.0 / len(winners)

    def loss(alpha: float) -> float:
        z = np.where(mask, alpha * logq, -np.inf)
        top = z.max(axis=1, keepdims=True)
        log_norm = top[:, 0] + np.log(np.exp(z - top).sum(axis=1))
        log_p = np.where(mask, alpha * logq - log_norm[:, None], 0.0)
        return float(-(weight * log_p).sum(axis=1).mean())

    fitted = minimize_scalar(loss, bounds=bounds, method="bounded")
    return float(fitted.x)  # pyright: ignore[reportAttributeAccessIssue]


def default_models() -> list[Any]:
    return [
        RandomModel(),
        UniformModel(),
        HorseWinRateModel(),
        FormModel(),
        MarketModel(),
        CalibratedMarketModel(),
    ]
