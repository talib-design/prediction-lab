"""Forward predictions, recorded before the draw they are about.

A backtest can always be rerun until it looks good. A prediction written down before
the balls came out cannot. That asymmetry is the only fully convincing evidence this
project can generate about itself, so the recording rules are strict:

* the target draw must lie in the **future** at the moment of recording -- predicting
  a draw that has already happened is refused, not warned about;
* the target must not already exist in the dataset;
* records are appended to a hash-chained ledger and never edited. A correction is a
  new record that supersedes the old one, and both stay visible.

As with the ledger itself, the honest claim is tamper *evidence*. The recommended
practice is to commit the ledger to git immediately after writing, which timestamps
it independently of this process.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from predlab import __version__
from predlab.core.gamespec import GameSpec
from predlab.core.hashing import AppendOnlyLedger
from predlab.models.base import Forecast

EXPERIMENT_VERSION = "m1"


class PrematureScoringError(RuntimeError):
    """Asked to score a prediction whose draw has not happened yet."""


class HindsightError(ValueError):
    """Refused to record a 'prediction' about a draw that is not in the future."""


class ForwardPrediction(BaseModel, frozen=True):
    """One immutable probabilistic statement about one future draw."""

    prediction_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    game: str
    era: str
    target_draw_key: str
    target_date: date
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    model_name: str
    model_version: str
    experiment_version: str = EXPERIMENT_VERSION
    code_version: str = __version__
    training_cutoff: date
    n_training_draws: int
    dataset_fingerprint: str
    inclusion_probabilities: dict[str, list[float]]
    ticket: dict[str, list[int]]
    selection_policy: str
    config: dict[str, Any] = Field(default_factory=dict)
    seed: int | None = None
    supersedes: str | None = None

    @field_validator("inclusion_probabilities")
    @classmethod
    def _probabilities_are_finite(cls, value: dict[str, list[float]]) -> dict[str, list[float]]:
        for pool, probs in value.items():
            if not probs:
                raise ValueError(f"{pool}: empty probability vector")
            if any(not (0.0 < p < 1.0) for p in probs):
                raise ValueError(f"{pool}: probabilities must lie strictly in (0, 1)")
        return value

    def payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


class PredictionLedger:
    """Append-only, hash-chained store of forward predictions."""

    def __init__(self, ledger: AppendOnlyLedger) -> None:
        self.ledger = ledger

    def record(
        self,
        spec: GameSpec,
        forecast: Forecast,
        ticket: dict[str, tuple[int, ...]],
        *,
        selection_policy: str,
        model_name: str,
        model_version: str,
        config: dict[str, Any],
        training_cutoff: date,
        dataset_fingerprint: str,
        seed: int | None = None,
        known_draw_dates: frozenset[date] = frozenset(),
        today: date | None = None,
    ) -> ForwardPrediction:
        """Validate and append one prediction. Raises rather than recording a fake one."""
        now = today or datetime.now(UTC).date()
        if forecast.target_date <= now:
            raise HindsightError(
                f"target draw {forecast.target_date} is not in the future (today is {now}); "
                "a forward prediction must be recorded before the draw"
            )
        if forecast.target_date in known_draw_dates:
            raise HindsightError(
                f"draw {forecast.target_date} is already in the dataset; "
                "this would be a backtest entry, not a forward prediction"
            )
        if forecast.target_date.isoweekday() not in spec.draw_weekdays:
            raise ValueError(f"{forecast.target_date} is not a draw day for {spec.key}")

        prediction = ForwardPrediction(
            game=spec.game,
            era=spec.era,
            target_draw_key=f"{spec.key}/{forecast.target_date.isoformat()}",
            target_date=forecast.target_date,
            model_name=model_name,
            model_version=model_version,
            training_cutoff=training_cutoff,
            n_training_draws=forecast.n_training_draws,
            dataset_fingerprint=dataset_fingerprint,
            inclusion_probabilities={
                name: [float(x) for x in pf.inclusion_probs] for name, pf in forecast.pools.items()
            },
            ticket={name: list(numbers) for name, numbers in ticket.items()},
            selection_policy=selection_policy,
            config=config,
            seed=seed,
        )
        self.ledger.append(prediction.payload())
        return prediction

    def all(self) -> list[ForwardPrediction]:
        return [ForwardPrediction(**_strip_chain(r)) for r in self.ledger.records()]

    def pending(self, today: date | None = None) -> list[ForwardPrediction]:
        now = today or datetime.now(UTC).date()
        return [p for p in self.all() if p.target_date > now]

    def matured(self, today: date | None = None) -> list[ForwardPrediction]:
        now = today or datetime.now(UTC).date()
        return [p for p in self.all() if p.target_date <= now]

    def verify(self) -> None:
        self.ledger.verify()


def _strip_chain(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in ("record_hash", "prev_hash")}
