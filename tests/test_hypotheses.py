from __future__ import annotations

from pathlib import Path

import pytest

from predlab.core.hashing import AppendOnlyLedger
from predlab.registry.hypotheses import Hypothesis, HypothesisRegistry, Status


def _registry(tmp_path: Path) -> HypothesisRegistry:
    return HypothesisRegistry(AppendOnlyLedger(tmp_path / "hypotheses.jsonl"))


def test_hypotheses_are_appended_and_listed(tmp_path: Path) -> None:
    reg = _registry(tmp_path)
    reg.add(Hypothesis(description="Jockey form predicts wins."))
    reg.add(Hypothesis(description="Draw matters on tight tracks."))
    assert len(reg.current()) == 2
    reg.verify()


def test_updating_supersedes_rather_than_rewrites(tmp_path: Path) -> None:
    reg = _registry(tmp_path)
    h = reg.add(Hypothesis(description="Jockey form predicts wins."))
    updated = reg.update(h.hypothesis_id, status=Status.REJECTED, conclusion="No lift.")

    current = reg.current()
    assert len(current) == 1
    assert current[0].status == Status.REJECTED
    assert updated.hypothesis_id == h.hypothesis_id
    assert updated.revision == 1
    assert len(reg.history()) == 2, "the original record must still be there"
    assert reg.history()[0].status == Status.PROPOSED
    reg.verify()


def test_inconclusive_is_available_and_distinct_from_rejected() -> None:
    """Failing to detect an effect is not the same as showing there is none."""
    assert Status.INCONCLUSIVE != Status.REJECTED
    assert set(Status) >= {
        Status.PROPOSED,
        Status.TESTING,
        Status.REJECTED,
        Status.INCONCLUSIVE,
        Status.SUPPORTED,
    }


def test_unknown_hypothesis_raises(tmp_path: Path) -> None:
    with pytest.raises(KeyError):
        _registry(tmp_path).get("nope")
