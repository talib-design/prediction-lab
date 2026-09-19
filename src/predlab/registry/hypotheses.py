"""A record of what has already been tried.

Small on purpose. Its job in Milestone 1 is not to be a research platform but to stop
the same dead end being rediscovered -- by a future agent, or by a future me at
2 a.m. who has forgotten that rolling frequency was already tested and lost.

The statuses deliberately include INCONCLUSIVE. Most of what this project tests will
land there rather than in REJECTED, because failing to detect an effect is not the
same as showing there is none, and collapsing the two would quietly turn "we could
not see it" into "it is not there".
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from predlab.core.hashing import AppendOnlyLedger


class Status(StrEnum):
    PROPOSED = "PROPOSED"
    TESTING = "TESTING"
    REJECTED = "REJECTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    SUPPORTED = "SUPPORTED"


class Origin(StrEnum):
    HUMAN = "human"
    LITERATURE = "literature"
    FOLK_HEURISTIC = "folk_heuristic"
    AUTOMATED = "automated"


class Hypothesis(BaseModel, frozen=True):
    """One version of one hypothesis.

    ``hypothesis_id`` is stable across versions; ``revision`` increments. Nothing is
    ever edited in place, so the full history of how a conclusion was reached stays
    readable -- including the versions that were wrong.
    """

    hypothesis_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    revision: int = 0
    description: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    origin: Origin = Origin.HUMAN
    dataset: str | None = None
    experiment: str | None = None
    status: Status = Status.PROPOSED
    in_sample_result: str | None = None
    out_of_sample_result: str | None = None
    forward_result: str | None = None
    conclusion: str | None = None

    def payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


class HypothesisRegistry:
    """Append-only. An update writes a new record that supersedes the previous one."""

    def __init__(self, ledger: AppendOnlyLedger) -> None:
        self.ledger = ledger

    def add(self, hypothesis: Hypothesis) -> Hypothesis:
        self.ledger.append(hypothesis.payload())
        return hypothesis

    def update(self, hypothesis_id: str, **changes: Any) -> Hypothesis:
        """Append a new revision. The previous one stays in the ledger."""
        current = self.get(hypothesis_id)
        updated = current.model_copy(
            update={
                **changes,
                "revision": current.revision + 1,
                "created_at": datetime.now(UTC),
            }
        )
        self.ledger.append(updated.payload())
        return updated

    def history(self) -> list[Hypothesis]:
        """Every revision ever written, in the order written."""
        return [Hypothesis(**_strip(r)) for r in self.ledger.records()]

    def current(self) -> list[Hypothesis]:
        """Latest revision of each hypothesis, in order of first appearance."""
        latest: dict[str, Hypothesis] = {}
        for h in self.history():
            known = latest.get(h.hypothesis_id)
            if known is None or h.revision >= known.revision:
                latest[h.hypothesis_id] = h
        return list(latest.values())

    def get(self, hypothesis_id: str) -> Hypothesis:
        """The latest revision of one hypothesis."""
        for h in reversed(self.history()):
            if h.hypothesis_id == hypothesis_id:
                return h
        raise KeyError(f"no hypothesis {hypothesis_id!r}")

    def verify(self) -> None:
        self.ledger.verify()


def _strip(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in ("record_hash", "prev_hash")}
