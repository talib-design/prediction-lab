"""Walk-forward evaluation of race models.

One loop, one rule. Races are visited in prediction-time order; before each forecast
the engine releases -- into :class:`Knowledge` and to every model's ``observe`` -- the
results that were known by then, and nothing later. The model receives the race card,
which has no result in it. Only after all models have answered does the engine look at
the outcome and score.

Scores (per race, lower is better unless stated):

* ``log_loss`` -- −log p(winner); for a dead heat, the mean over co-winners. **Decides.**
* ``brier`` -- Σ (p_i − y_i)², with y split 1/k over k co-winners.
* ``top1`` -- 1 if the most probable starter won (higher is better; diagnostic only).
* ``rr`` -- reciprocal rank of the best-ranked winner (higher is better; diagnostic).

Runner-level (p, y) pairs are kept for calibration.

Eligibility: a race is scored only if every starter has a pre-horizon odds quote, so
that every model, the market included, is judged on exactly the same races.
"""

from __future__ import annotations

import heapq
import itertools
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any

import numpy as np
import numpy.typing as npt

from predlab import __version__
from predlab.backtest.splits import TimeSplit
from predlab.core.probability import PROB_EPSILON
from predlab.racing.events import RaceCard, RaceEvent, fingerprint
from predlab.racing.knowledge import Knowledge

METRICS = ("log_loss", "brier", "top1", "rr")

# Pre-registered on 2026-09-28 (docs/METHODOLOGY.md §6), revised on 2026-09-30 when the
# history was cut to start in 2024 -- before any challenger model had been evaluated:
# train = 2024 H1, validation = 2024 H2, test = 2025 onwards (unchanged).
PREREGISTERED_SPLIT = TimeSplit(
    train_end=date(2024, 6, 30), validation_end=date(2024, 12, 31), test_end=date(2099, 12, 31)
)
DEFAULT_HORIZON_MINUTES = 25.0


class ForecastError(ValueError):
    """A model returned something that is not a probability distribution."""


def validate(p: np.ndarray, card: RaceCard, model: str) -> np.ndarray:
    p = np.asarray(p, dtype=np.float64)
    if p.shape != (card.n,):
        raise ForecastError(
            f"{model}: expected {card.n} probabilities for {card.race_id}, got {p.shape}"
        )
    if not np.all(np.isfinite(p)) or p.min() <= 0.0 or p.max() >= 1.0:
        raise ForecastError(
            f"{model}: probabilities must lie strictly in (0, 1) for {card.race_id}"
        )
    if abs(p.sum() - 1.0) > 1e-6:
        raise ForecastError(f"{model}: probabilities sum to {p.sum()} for {card.race_id}")
    return p


def score(p: np.ndarray, winners: list[int]) -> dict[str, float]:
    y = np.zeros_like(p)
    y[winners] = 1.0 / len(winners)
    order = np.argsort(-p, kind="stable")
    best_rank = min(int(np.where(order == w)[0][0]) for w in winners) + 1
    return {
        "log_loss": float(np.mean([-np.log(max(p[w], PROB_EPSILON)) for w in winners])),
        "brier": float(np.sum((p - y) ** 2)),
        "top1": float(order[0] in winners),
        "rr": 1.0 / best_rank,
    }


@dataclass
class ModelRun:
    name: str
    version: str
    config: dict[str, Any]
    race_ids: list[str] = field(default_factory=list)
    days: list[Any] = field(default_factory=list)
    phases: list[str] = field(default_factory=list)
    scores: dict[str, list[float]] = field(default_factory=lambda: {m: [] for m in METRICS})
    probs: list[float] = field(default_factory=list)
    outcomes: list[float] = field(default_factory=list)
    runner_phases: list[str] = field(default_factory=list)

    def series(self, metric: str, phase: str | None = None) -> np.ndarray:
        values = np.array(self.scores[metric])
        if phase is None:
            return values
        return values[np.array([p == phase for p in self.phases], dtype=bool)]


@dataclass
class BacktestResult:
    horizon_minutes: float
    split: TimeSplit | None
    n_events: int
    n_eligible: int
    dataset_fingerprint: str
    runs: list[ModelRun]
    code_version: str = __version__
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds"))
    # Filled only with keep_forecasts=True: what each model said, race by race.
    forecasts: dict[str, dict[str, np.ndarray]] = field(default_factory=dict)
    scored_events: list[RaceEvent] = field(default_factory=list)

    def run(self, name: str) -> ModelRun:
        for r in self.runs:
            if r.name == name:
                return r
        raise KeyError(name)


def run_backtest(
    events: Sequence[RaceEvent],
    models: Sequence[Any],
    *,
    horizon_minutes: float,
    split: TimeSplit | None = None,
    eligible: Callable[[RaceCard], bool] = lambda c: c.market_complete,
    keep_forecasts: bool = False,
) -> BacktestResult:
    ordered = sorted(events, key=lambda e: (e.card.prediction_time, e.card.race_id))
    pending: list[tuple[datetime, str, RaceEvent]] = []
    for e in ordered:
        heapq.heappush(pending, (e.known_at, e.card.race_id, e))
    knowledge = Knowledge()
    runs = [ModelRun(m.name, m.version, m.config()) for m in models]
    n_eligible = 0
    forecasts: dict[str, dict[str, np.ndarray]] = {}
    scored: list[RaceEvent] = []

    for event in ordered:
        card = event.card
        while pending and pending[0][0] <= card.prediction_time:
            _, _, done = heapq.heappop(pending)
            knowledge.release(done)
            for m in models:
                m.observe(done, knowledge)
        if card.race_id in knowledge.released:
            raise AssertionError(f"{card.race_id} was released before its own forecast")
        if not eligible(card):
            continue
        n_eligible += 1
        winners = event.winner_indices()
        phase = split.phase_of(card.day) if split else "all"
        if keep_forecasts:
            forecasts[card.race_id] = {}
            scored.append(event)
        for m, run in zip(models, runs, strict=True):
            p = validate(m.predict(card, knowledge), card, m.name)
            if keep_forecasts:
                forecasts[card.race_id][m.name] = p
            for k, v in score(p, winners).items():
                run.scores[k].append(v)
            run.race_ids.append(card.race_id)
            run.days.append(card.day)
            run.phases.append(phase)
            y = np.zeros(card.n)
            y[winners] = 1.0 / len(winners)
            run.probs.extend(p.tolist())
            run.outcomes.extend(y.tolist())
            run.runner_phases.extend([phase] * card.n)

    return BacktestResult(
        horizon_minutes=horizon_minutes,
        split=split,
        n_events=len(ordered),
        n_eligible=n_eligible,
        dataset_fingerprint=fingerprint(ordered),
        runs=runs,
        forecasts=forecasts,
        scored_events=scored,
    )


BINS = (0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0)


def calibration_table(
    probs: npt.ArrayLike, outcomes: npt.ArrayLike, bins: Sequence[float] = BINS
) -> list[dict[str, Any]]:
    """Mean forecast vs observed frequency, per probability bucket (runner level)."""
    p, y = np.asarray(probs), np.asarray(outcomes)
    rows = []
    for lo, hi in itertools.pairwise(bins):
        mask = (p >= lo) & (p < hi) if hi < 1.0 else (p >= lo) & (p <= hi)
        if mask.sum() == 0:
            continue
        rows.append(
            {
                "bucket": f"{lo:.2f}-{hi:.2f}",
                "n": int(mask.sum()),
                "mean_forecast": float(p[mask].mean()),
                "observed": float(y[mask].mean()),
            }
        )
    return rows


def calibration_error(probs: npt.ArrayLike, outcomes: npt.ArrayLike) -> float:
    """Expected calibration error over the buckets of :func:`calibration_table`."""
    rows = calibration_table(probs, outcomes)
    total = sum(r["n"] for r in rows)
    if not total:
        return float("nan")
    return float(sum(r["n"] * abs(r["mean_forecast"] - r["observed"]) for r in rows) / total)
