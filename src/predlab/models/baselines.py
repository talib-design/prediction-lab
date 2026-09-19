"""Baselines.

These exist to be *benchmarks*, not candidates. Nothing here is expected to work. If
a later model cannot beat them by more than sampling noise, that model has
demonstrated nothing.

One identity worth stating rather than hiding: at the level of marginal inclusion
probabilities, "generate a random ticket" and "assume uniformity" are the *same
model*. They differ only in the ticket they emit, not in the probabilities they
assert. Both are implemented so that the evaluation makes that identity visible --
they should come out statistically indistinguishable, and if they ever do not, the
evaluation harness is broken.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

import numpy as np

from predlab.core.gamespec import GameSpec
from predlab.core.historyview import HistoryView
from predlab.models.base import Forecast, PoolForecast, normalise_to_k


def _uniform_pools(spec: GameSpec) -> dict[str, PoolForecast]:
    return {
        pool.name: PoolForecast(
            pool=pool,
            inclusion_probs=np.full(pool.size, pool.marginal_probability, dtype=np.float64),
        )
        for pool in spec.pools
    }


@dataclass(slots=True)
class UniformPredictor:
    """Every number equally likely: ``p = k / size``. The reference point.

    This is the correct model if the draw is fair. Any challenger must beat it, and
    "beating" must mean more than beating it once.
    """

    spec: GameSpec
    name: str = "uniform"
    version: str = "1"

    def config(self) -> dict[str, Any]:
        return {"game": self.spec.key}

    def forecast(self, history: HistoryView, target_date: date) -> Forecast:
        return Forecast(
            spec=self.spec,
            target_date=target_date,
            pools=_uniform_pools(self.spec),
            n_training_draws=len(history),
        )


@dataclass(slots=True)
class RandomTicketPredictor:
    """Picks a legal ticket at random, asserting no information about the numbers.

    Its *probabilities* are uniform, because that is what "I chose at random" honestly
    means. The seed affects only which ticket is emitted, never the forecast, so its
    score must match :class:`UniformPredictor` exactly. That equality is asserted in
    the test suite and is a cheap integrity check on the whole harness.
    """

    spec: GameSpec
    seed: int = 0
    name: str = "random"
    version: str = "1"

    def config(self) -> dict[str, Any]:
        return {"game": self.spec.key, "seed": self.seed}

    def forecast(self, history: HistoryView, target_date: date) -> Forecast:
        return Forecast(
            spec=self.spec,
            target_date=target_date,
            pools=_uniform_pools(self.spec),
            n_training_draws=len(history),
        )

    def ticket(self, target_date: date) -> dict[str, tuple[int, ...]]:
        """A legal random ticket, reproducible from ``(seed, target_date)``."""
        rng = np.random.default_rng([self.seed, target_date.toordinal()])
        return {
            pool.name: tuple(
                sorted(
                    int(n)
                    for n in rng.choice(
                        np.arange(pool.low, pool.high + 1), size=pool.k, replace=False
                    )
                )
            )
            for pool in self.spec.pools
        }


@dataclass(slots=True)
class FrequencyPredictor:
    """Inclusion probability proportional to how often a number has appeared.

    ``window`` limits the count to the most recent N draws; ``None`` uses all history.

    ``alpha`` is additive (Laplace) smoothing. It is not cosmetic: without it a number
    that has never appeared gets probability zero, and a single appearance would cost
    the model infinite log loss. With few draws the unsmoothed estimator is also wildly
    overconfident about pure sampling noise. ``alpha`` therefore encodes a prior that
    the mechanism is fair, and shrinks towards uniform as history gets short.

    Stating the obvious so it is not mistaken for a claim: past frequency is only
    predictive if the mechanism is biased *and* stable. This model assumes both in
    order to test both.

    On ``alpha``: 1.0 is Laplace's flat Beta(1, 1) prior per number. Fisher's objection
    applies -- a flat prior on ``p`` is not a flat prior on a reparametrisation of
    ``p``, so "uninformative" is doing unearned work. Jeffreys' prior for a Bernoulli
    is Beta(1/2, 1/2), i.e. ``alpha = 0.5`` (Wasserman, *All of Statistics*, §11.6).

    More honestly: ``alpha`` is a free parameter that was never chosen on validation,
    which contradicts this project's own methodology. Rather than tune an arbitrary
    prior, :class:`ShrunkFrequencyPredictor` estimates the right amount of shrinkage
    from the data. Treat this class as the naive reference it is.
    """

    spec: GameSpec
    window: int | None = None
    alpha: float = 1.0
    name: str = field(init=False, default="frequency")
    version: str = "1"

    def __post_init__(self) -> None:
        if self.alpha <= 0:
            raise ValueError("alpha must be > 0; zero smoothing makes log loss infinite")
        if self.window is not None and self.window < 1:
            raise ValueError("window must be >= 1 or None")
        self.name = "frequency" if self.window is None else f"rolling_frequency_{self.window}"

    def config(self) -> dict[str, Any]:
        return {"game": self.spec.key, "window": self.window, "alpha": self.alpha}

    def forecast(self, history: HistoryView, target_date: date) -> Forecast:
        view = history if self.window is None else history.tail(self.window)
        pools: dict[str, PoolForecast] = {}
        for pool in self.spec.pools:
            if view.is_empty:
                # No evidence yet: the honest answer is the uniform prior.
                probs = np.full(pool.size, pool.marginal_probability, dtype=np.float64)
            else:
                scores = view.counts(pool.name).astype(np.float64) + self.alpha
                probs = normalise_to_k(scores, pool)
            pools[pool.name] = PoolForecast(pool=pool, inclusion_probs=probs)
        return Forecast(
            spec=self.spec,
            target_date=target_date,
            pools=pools,
            n_training_draws=len(view),
        )


@dataclass(slots=True)
class ShrunkFrequencyPredictor:
    """Observed frequencies, shrunk toward uniform by the James-Stein rule.

    The motivating fact, from Efron (*To Think Like a Statistician*, §1.6 and appendix
    A.2) on the 18 baseball players: a set of noisy parallel estimates is **more spread
    out than the truth**, because noise exaggerates differences. Estimating 49 ball
    probabilities from a few hundred appearances each is exactly that situation, and
    :class:`FrequencyPredictor` takes the exaggerated spread at face value. Its measured
    behaviour -- reliably worse than assuming fairness -- is what that error looks like.

    The James-Stein estimate pulls every number back toward the grand mean by a factor
    estimated from the data itself::

        js[i] = M + [1 - (K - 3) * V / S] * (x[i] - M)

    where ``M`` is the grand mean, ``V`` the binomial variance of one estimate, and
    ``S`` the observed spread. When the observed spread is no larger than noise alone
    would produce, the factor collapses to zero and the model *becomes* the uniform
    model. That is the point: it knows how much to trust its own counts.

    This replaces an arbitrary smoothing constant with a quantity estimated from the
    sample, which is the empirical-Bayes answer to "what should alpha be?".
    """

    spec: GameSpec
    window: int | None = None
    name: str = field(init=False, default="shrunk_frequency")
    version: str = "1"

    def __post_init__(self) -> None:
        if self.window is not None and self.window < 1:
            raise ValueError("window must be >= 1 or None")
        self.name = "shrunk_frequency" if self.window is None else f"shrunk_frequency_{self.window}"

    def config(self) -> dict[str, Any]:
        return {"game": self.spec.key, "window": self.window, "estimator": "james-stein"}

    def shrinkage_factor(self, view: HistoryView, pool_name: str) -> float:
        """The bracketed factor: 1 means trust the counts, 0 means fall back to uniform.

        Clamped to [0, 1]. A negative raw factor means the observed spread is *smaller*
        than pure noise would give -- there is nothing to shrink toward the mean because
        the estimates are already less dispersed than chance. Clamping at zero is the
        standard positive-part rule (Wasserman, §12.7).
        """
        pool = self.spec.pool(pool_name)
        n = len(view)
        if n < 2 or pool.size < 4:
            return 0.0
        x = view.counts(pool_name) / n
        mean = pool.marginal_probability
        variance = mean * (1.0 - mean) / n
        spread = float(((x - mean) ** 2).sum())
        if spread <= 0.0:
            return 0.0
        return float(min(1.0, max(0.0, 1.0 - (pool.size - 3) * variance / spread)))

    def forecast(self, history: HistoryView, target_date: date) -> Forecast:
        view = history if self.window is None else history.tail(self.window)
        pools: dict[str, PoolForecast] = {}
        for pool in self.spec.pools:
            mean = pool.marginal_probability
            if view.is_empty:
                probs = np.full(pool.size, mean, dtype=np.float64)
            else:
                observed = view.counts(pool.name) / len(view)
                factor = self.shrinkage_factor(view, pool.name)
                # Sums to k by construction: sum(observed) == k and sum(mean) == k.
                shrunk = mean + factor * (observed - mean)
                probs = normalise_to_k(shrunk, pool)
            pools[pool.name] = PoolForecast(pool=pool, inclusion_probs=probs)
        return Forecast(
            spec=self.spec,
            target_date=target_date,
            pools=pools,
            n_training_draws=len(view),
        )


@dataclass(slots=True)
class GapPredictor:
    """The "due number" folk heuristic, implemented so it can be refuted.

    Inclusion probability increases with the number of draws since a number last
    appeared. Under a fair mechanism this is exactly the gambler's fallacy: draws are
    independent, so a long absence carries no information.

    It is included because "we tested it and it does not work" is a more useful
    statement than "we assumed it does not work". It is not a candidate model and
    should never be promoted to champion on the strength of an in-sample result.
    """

    spec: GameSpec
    alpha: float = 1.0
    name: str = "gap"
    version: str = "1"

    def config(self) -> dict[str, Any]:
        return {"game": self.spec.key, "alpha": self.alpha}

    def forecast(self, history: HistoryView, target_date: date) -> Forecast:
        pools: dict[str, PoolForecast] = {}
        n = len(history)
        for pool in self.spec.pools:
            if history.is_empty:
                probs = np.full(pool.size, pool.marginal_probability, dtype=np.float64)
            else:
                draws = history.pool_draws[pool.name]
                # gaps[i] = draws since number (low + i) last appeared; n if never.
                last_seen = np.full(pool.size, -1, dtype=np.int64)
                row_ids = np.repeat(np.arange(n, dtype=np.int64), pool.k)
                np.maximum.at(last_seen, (draws - pool.low).ravel(), row_ids)
                gaps = np.where(last_seen >= 0, n - 1 - last_seen, n).astype(np.float64)
                probs = normalise_to_k(gaps + self.alpha, pool)
            pools[pool.name] = PoolForecast(pool=pool, inclusion_probs=probs)
        return Forecast(
            spec=self.spec,
            target_date=target_date,
            pools=pools,
            n_training_draws=n,
        )


def default_baselines(spec: GameSpec, *, seed: int = 0) -> list[Any]:
    """The Milestone 1 benchmark set, in the order they belong in a report."""
    return [
        UniformPredictor(spec=spec),
        RandomTicketPredictor(spec=spec, seed=seed),
        FrequencyPredictor(spec=spec, window=None),
        FrequencyPredictor(spec=spec, window=100),
        FrequencyPredictor(spec=spec, window=300),
        ShrunkFrequencyPredictor(spec=spec),
        ShrunkFrequencyPredictor(spec=spec, window=300),
        GapPredictor(spec=spec),
    ]
