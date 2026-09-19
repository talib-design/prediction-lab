"""Content hashing and tamper-evident append-only ledgers.

Honesty note, stated here rather than buried in a doc: on an ordinary filesystem
nothing is truly immutable. A user with a text editor can rewrite any file. What the
hash chain below provides is **tamper evidence**, not immutability -- an edited record
breaks the chain and ``verify_chain`` says so. Committing the ledger to git after each
forward prediction adds an independent timestamped anchor, which is what actually
makes a "this was written before the draw" claim credible.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

GENESIS = "0" * 64
_CHUNK = 1 << 20


def sha256_file(path: Path) -> str:
    """SHA-256 of a file's bytes, streamed."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(_CHUNK):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(payload: Mapping[str, Any]) -> bytes:
    """Deterministic JSON encoding: sorted keys, no insignificant whitespace.

    Two payloads that are equal as data must produce identical bytes, otherwise
    hashes are not comparable across runs or machines.
    """
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str
    ).encode("utf-8")


def record_hash(payload: Mapping[str, Any], prev_hash: str) -> str:
    """Hash of a ledger record, chained to its predecessor.

    ``payload`` must NOT already contain ``record_hash`` or ``prev_hash``.
    """
    for reserved in ("record_hash", "prev_hash"):
        if reserved in payload:
            raise ValueError(f"payload must not contain {reserved!r}")
    body = dict(payload)
    body["prev_hash"] = prev_hash
    return sha256_bytes(canonical_json(body))


class AppendOnlyLedger:
    """A JSONL file where each record is hash-chained to the previous one.

    Records are only ever appended. Rewriting history is detectable via
    :meth:`verify`, which is the whole point.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def _read_raw(self) -> Iterator[dict[str, Any]]:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{self.path}:{line_no}: malformed JSON") from exc

    def records(self) -> list[dict[str, Any]]:
        return list(self._read_raw())

    def head_hash(self) -> str:
        """Hash of the last record, or the genesis value for an empty ledger."""
        last = GENESIS
        for rec in self._read_raw():
            last = rec["record_hash"]
        return last

    def append(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Append one record and return it, including its chain fields."""
        prev = self.head_hash()
        rec = dict(payload)
        rec["prev_hash"] = prev
        rec["record_hash"] = record_hash(payload, prev)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True, ensure_ascii=False, default=str))
            fh.write("\n")
        return rec

    def verify(self) -> None:
        """Raise ``LedgerCorruptionError`` on the first record that fails its check."""
        prev = GENESIS
        for i, rec in enumerate(self._read_raw()):
            stored = rec.get("record_hash")
            declared_prev = rec.get("prev_hash")
            if not isinstance(stored, str) or not isinstance(declared_prev, str):
                raise LedgerCorruptionError(f"{self.path}: record {i} is missing its chain fields")
            if declared_prev != prev:
                raise LedgerCorruptionError(
                    f"{self.path}: record {i} has prev_hash={declared_prev!r}, "
                    f"expected {prev!r} -- a record was inserted, removed or reordered"
                )
            payload = {k: v for k, v in rec.items() if k not in ("record_hash", "prev_hash")}
            if stored != record_hash(payload, prev):
                raise LedgerCorruptionError(
                    f"{self.path}: record {i} content does not match its hash "
                    "-- edited after the fact"
                )
            prev = stored

    def __len__(self) -> int:
        return sum(1 for _ in self._read_raw())


class LedgerCorruptionError(RuntimeError):
    """Raised when an append-only ledger fails its integrity check."""
