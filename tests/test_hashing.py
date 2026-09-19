from __future__ import annotations

import json
from pathlib import Path

import pytest

from predlab.core.hashing import GENESIS, AppendOnlyLedger, LedgerCorruptionError, canonical_json


def test_canonical_json_is_key_order_independent() -> None:
    assert canonical_json({"a": 1, "b": 2}) == canonical_json({"b": 2, "a": 1})


def test_append_and_verify(tmp_path: Path) -> None:
    ledger = AppendOnlyLedger(tmp_path / "l.jsonl")
    assert ledger.head_hash() == GENESIS
    first = ledger.append({"n": 1})
    second = ledger.append({"n": 2})
    assert second["prev_hash"] == first["record_hash"]
    assert len(ledger) == 2
    ledger.verify()


def test_editing_a_record_is_detected(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    ledger = AppendOnlyLedger(path)
    ledger.append({"prediction": [1, 2, 3]})
    ledger.append({"prediction": [4, 5, 6]})

    lines = path.read_text(encoding="utf-8").splitlines()
    rec = json.loads(lines[0])
    rec["prediction"] = [9, 9, 9]
    lines[0] = json.dumps(rec, sort_keys=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(LedgerCorruptionError, match="edited after the fact"):
        ledger.verify()


def test_deleting_a_record_is_detected(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    ledger = AppendOnlyLedger(path)
    for i in range(3):
        ledger.append({"n": i})
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join([lines[0], lines[2]]) + "\n", encoding="utf-8")
    with pytest.raises(LedgerCorruptionError, match="inserted, removed or reordered"):
        ledger.verify()


def test_payload_cannot_smuggle_chain_fields(tmp_path: Path) -> None:
    ledger = AppendOnlyLedger(tmp_path / "l.jsonl")
    with pytest.raises(ValueError):
        ledger.append({"n": 1, "prev_hash": "deadbeef"})
