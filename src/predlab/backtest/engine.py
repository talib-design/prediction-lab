"""Walk-forward backtesting.

One rule governs this module: at every step, the model sees a history that ends before
the draw it is asked to predict, and nothing else. The engine builds that history,
hands it over, takes the forecast, and only then looks at what came out.

The engine also records everything needed to reproduce the run -- dataset fingerprint,
model versions and configurations, split boundaries, seed, code version. A result that
cannot be reproduced is not evidence.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any, Protocol

import numpy as np

from predlab import __version__
from predlab.backtest.splits import TimeSplit
from predlab.core.gamespec import GameSpec
from predlab.core.hashing import sha256_bytes
from predlab.core.historyview import build_view
from predlab.eval.metrics import count_matches, score_forecast
from predlab.models.base import Forecast, Predictor

METRICS = ("log_loss", "brier", "mass_on_drawn")


class SelectionPolicy(Protocol):
    @property
    def name(self) -> str: ...

    def ticket(self, forecast: Forecast) -> dict[str, tuple[int, ...]]: ...


@dataclass(frozen=True, slots=True)
class BacktestConfig:
    """Everything that changes what a backtest does, in one hashable object."""

    min_train_draws: int = 200
    start_date: date | None = None
    end_date: date | None = None
    seed: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "min_train_draws": self.min_train_draws,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "seed": self.seed,
        }


@dataclass(frozen=True, slots=True)
class ModelRun:
    """Per-draw results for one model over the whole evaluation window."""

    model_name: str
    model_version: str
    model_config: dict[str, Any]
    target_dates: list[date]
    phases: list[str]
    scores: dict[str, dict[str, np.ndarray]]
    matches: dict[str, np.ndarray]
    predicted_probs: dict[str, np.ndarray]
    outcomes: dict[str, np.ndarray]
    n_training_draws: np.ndarray

    def series(self, pool: str, metric: str) -> np.ndarray:
        return self.scores[pool][metric]

    def mask_for(self, phase: str | None) -> np.ndarray:
        if phase is None:
            return np.ones(len(self.target_dates), dtype=bool)
        return np.array([p == phase for p in self.phases], dtype=bool)


@dataclass(frozen=True, slots=True)
class BacktestResult:
    """A complete, reproducible record of one evaluation."""

    spec: GameSpec
    config: BacktestConfig
    split: TimeSplit | None
    policy_name: str
    dataset_fingerprint: str
    n_draws_total: int
    runs: list[ModelRun]
    code_version: str = field(default=__version__)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds"))

    def run_for(self, model_name: str) -> ModelRun:
        for run in self.runs:
            if run.model_name == model_name:
                return run
        raise KeyError(f"no run for model {model_name!r}")

    def provenance(self) -> dict[str, Any]:
        return {
            "game": self.spec.key,
            "code_version": self.code_version,
            "created_at": self.created_at,
            "dataset_fingerprint": self.dataset_fingerprint,
            "n_draws_total": self.n_draws_total,
            "config": self.config.as_dict(),
            "split": self.split.as_dict() if self.split else None,
            "selection_policy": self.policy_name,
            "models": [
                {"name": r.model_name, "version": r.model_version, "config": r.model_config}
                for r in self.runs
            ],
        }


def dataset_fingerprint(dates: np.ndarray, pool_draws: dict[str, np.ndarray]) -> str:
    """Hash of the exact numbers a run was computed on."""
    parts = [np.ascontiguousarray(dates).tobytes()]
    for name in sorted(pool_draws):
        parts.append(name.encode())
        parts.append(np.ascontiguousarray(pool_draws[name]).tobytes())
    return sha256_bytes(b"|".join(parts))


def run_backtest(
    spec: GameSpec,
    dates: np.ndarray,
    pool_draws: dict[str, np.ndarray],
    models: Sequence[Predictor],
    policy: SelectionPolicy,
    config: BacktestConfig | None = None,
    split: TimeSplit | None = None,
) -> BacktestResult:
    """Evaluate every model on every eligible draw, strictly in time order."""
    config = config or BacktestConfig()
    if len(dates) == 0:
        raise ValueError("no draws to evaluate")
    if not np.all(dates[:-1] <= dates[1:]):
        raise ValueError("draws must be sorted ascending by date")

    targets = _eligible_targets(dates, config)
    if not targets:
        raise ValueError(
            f"no eligible target draws: need more than min_train_draws="
            f"{config.min_train_draws} before the evaluation window"
        )

    runs = [
        _run_one_model(spec, dates, pool_draws, model, policy, targets, split) for model in models
    ]
    return BacktestResult(
        spec=spec,
        config=config,
        split=split,
        policy_name=policy.name,
        dataset_fingerprint=dataset_fingerprint(dates, pool_draws),
        n_draws_total=len(dates),
        runs=runs,
    )


def _eligible_targets(dates: np.ndarray, config: BacktestConfig) -> list[int]:
    indices = range(config.min_train_draws, len(dates))
    out = []
    for i in indices:
        day = dates[i].astype("datetime64[D]").astype(date)
        if config.start_date and day < config.start_date:
            continue
        if config.end_date and day > config.end_date:
            continue
        out.append(i)
    return out


def _run_one_model(
    spec: GameSpec,
    dates: np.ndarray,
    pool_draws: dict[str, np.ndarray],
    model: Predictor,
    policy: SelectionPolicy,
    targets: list[int],
    split: TimeSplit | None,
) -> ModelRun:
    pool_names = [p.name for p in spec.pools]
    n = len(targets)

    scores: dict[str, dict[str, np.ndarray]] = {
        name: {m: np.empty(n, dtype=np.float64) for m in METRICS} for name in pool_names
    }
    matches = {name: np.empty(n, dtype=np.int16) for name in pool_names}
    probs = {name: np.empty((n, spec.pool(name).size), dtype=np.float64) for name in pool_names}
    outcomes = {name: np.zeros((n, spec.pool(name).size), dtype=np.int8) for name in pool_names}
    n_train = np.empty(n, dtype=np.int32)
    target_dates: list[date] = []
    phases: list[str] = []

    for row, t in enumerate(targets):
        target_day = dates[t].astype("datetime64[D]").astype(date)
        history = build_view(spec, dates, pool_draws, as_of=target_day)

        forecast = model.forecast(history, target_day)
        if forecast.target_date != target_day:
            raise ValueError(
                f"{model.name} returned a forecast for {forecast.target_date}, "
                f"asked for {target_day}"
            )

        actual = {name: pool_draws[name][t] for name in pool_names}
        pool_scores = score_forecast(forecast, actual)
        ticket = policy.ticket(forecast)

        for name in pool_names:
            s = pool_scores[name]
            scores[name]["log_loss"][row] = s.log_loss
            scores[name]["brier"][row] = s.brier
            scores[name]["mass_on_drawn"][row] = s.mass_on_drawn
            matches[name][row] = count_matches(ticket[name], actual[name])
            pf = forecast.pools[name]
            probs[name][row] = pf.inclusion_probs
            outcomes[name][row] = pf.outcome_vector(actual[name]).astype(np.int8)

        n_train[row] = forecast.n_training_draws
        target_dates.append(target_day)
        phases.append(split.phase_of(target_day) if split else "all")

    return ModelRun(
        model_name=model.name,
        model_version=model.version,
        model_config=model.config(),
        target_dates=target_dates,
        phases=phases,
        scores=scores,
        matches=matches,
        predicted_probs=probs,
        outcomes=outcomes,
        n_training_draws=n_train,
    )
