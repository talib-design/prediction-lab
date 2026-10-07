"""Prediction "logics" for EuroMillions, written as honest probability models.

A logic picks a set of numbers it believes in (hot, cold, last draw...). To be scored by a
proper scoring rule it must state probabilities, so each logic gives its selected numbers a
fixed, modest boost (``beta = 0.5``: +50 % weight, chosen before any result and never
tuned) and spreads the rest uniformly. Its grid is the ``k`` most likely numbers, i.e. its
own selection. The boost only matters for log loss; the grid does not depend on it.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Any

import numpy as np

from predlab.lottery.analysis import cold_rule, hot_rule, incidence, repeat_rule
from predlab.lottery.base import Forecast, PoolForecast, normalise_to_k
from predlab.lottery.gamespec import GameSpec
from predlab.lottery.historyview import HistoryView

BETA = 0.5
Rule = Callable[[np.ndarray, int], np.ndarray]


@dataclass(slots=True)
class SelectionPredictor:
    """Boost the numbers a causal rule selects from the history it is handed."""

    spec: GameSpec
    kind: str  # "hot" | "cold" | "repeat"
    window: int = 50
    m_main: int = 10
    m_stars: int = 3
    beta: float = BETA
    version: str = "1"

    @property
    def name(self) -> str:
        return self.kind if self.kind == "repeat" else f"{self.kind}{self.window}"

    def config(self) -> dict[str, Any]:
        return {
            "game": self.spec.key,
            "kind": self.kind,
            "window": self.window,
            "m_main": self.m_main,
            "m_stars": self.m_stars,
            "beta": self.beta,
        }

    def _rule(self, m: int, available: int) -> Rule:
        w = min(self.window, available)
        if self.kind == "hot":
            return hot_rule(w, m)
        if self.kind == "cold":
            return cold_rule(w, m)
        if self.kind == "repeat":
            return repeat_rule()
        raise ValueError(f"unknown logic {self.kind!r}")

    def forecast(self, history: HistoryView, target_date: date) -> Forecast:
        pools: dict[str, PoolForecast] = {}
        n = len(history)
        for pool in self.spec.pools:
            if n == 0:
                probs = np.full(pool.size, pool.marginal_probability)
            else:
                x = incidence(np.asarray(history.pool_draws[pool.name], dtype=np.int64), pool)
                m = self.m_main if pool.name == "main" else self.m_stars
                w = self._rule(m, n)(x, n)
                probs = normalise_to_k(1.0 + self.beta * w, pool)
            pools[pool.name] = PoolForecast(pool=pool, inclusion_probs=probs)
        return Forecast(spec=self.spec, target_date=target_date, pools=pools, n_training_draws=n)
