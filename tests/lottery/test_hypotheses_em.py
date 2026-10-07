"""EuroMillions pre-registration is idempotent and never rewrites a record."""

from __future__ import annotations

from pathlib import Path

from predlab.core.hashing import AppendOnlyLedger
from predlab.lottery.hypotheses_em import EM_HYPOTHESES, register_all
from predlab.registry.hypotheses import HypothesisRegistry


def test_register_all_is_idempotent(tmp_path: Path) -> None:
    registry = HypothesisRegistry(AppendOnlyLedger(tmp_path / "h.jsonl"))
    first = register_all(registry)
    second = register_all(registry)
    assert first == [h.hypothesis_id for h in EM_HYPOTHESES]
    assert second == []
    registry.verify()
    assert len(registry.history()) == len(EM_HYPOTHESES)


def test_ids_are_unique_and_prefixed() -> None:
    ids = [h.hypothesis_id for h in EM_HYPOTHESES]
    assert len(set(ids)) == len(ids)
    assert all(i.startswith("em-") for i in ids)
