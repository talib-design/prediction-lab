"""Raw capture store: every byte received, when it was received, from where.

Why raw first. The feed is undocumented and the parser will change; odds snapshots,
once missed, can never be taken again. So collection is decoupled from parsing: the
collector stores the exact response and a manifest record, and nothing downstream is
allowed to be the only copy of anything.

Layout, under ``data/raw/pmu/`` (git-ignored, never redistributed):

    blobs/ab/abcdef....json.gz     content-addressed: identical bodies stored once
    manifest/2026-09-28.jsonl      one hash-chained ledger per UTC retrieval day

A manifest record says *what* (key, endpoint, url), *when* (``retrieved_at``, UTC),
*why* (``purpose``), *how it went* (HTTP status, error) and *which bytes* (sha256).
``retrieved_at`` is the project's ``known_at`` for anything parsed from that blob:
the earliest moment the information can be claimed to have been available to us.

Failed requests are recorded too. A hole in the odds history must be distinguishable
from "never tried".
"""

from __future__ import annotations

import fcntl
import gzip
import hashlib
import os
from collections import defaultdict
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from predlab import __version__
from predlab.core.hashing import AppendOnlyLedger
from predlab.racing.sources.pmu.client import FetchResult


@dataclass(frozen=True, slots=True)
class Capture:
    """One manifest record, typed."""

    key: str
    endpoint: str
    purpose: str
    url: str
    retrieved_at: datetime
    http_status: int
    ok: bool
    error: str | None
    sha256: str | None
    n_bytes: int
    blob: str | None

    @classmethod
    def from_record(cls, rec: dict[str, Any]) -> Capture:
        return cls(
            key=rec["key"],
            endpoint=rec["endpoint"],
            purpose=rec["purpose"],
            url=rec["url"],
            retrieved_at=datetime.fromisoformat(rec["retrieved_at"]),
            http_status=int(rec["http_status"]),
            ok=bool(rec["ok"]),
            error=rec.get("error"),
            sha256=rec.get("sha256"),
            n_bytes=int(rec.get("n_bytes", 0)),
            blob=rec.get("blob"),
        )


class RawStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    @property
    def blobs(self) -> Path:
        return self.root / "blobs"

    @property
    def manifests(self) -> Path:
        return self.root / "manifest"

    def _ledger(self, day: date) -> AppendOnlyLedger:
        return AppendOnlyLedger(self.manifests / f"{day.isoformat()}.jsonl")

    # ------------------------------------------------------------------ writing

    def record(self, result: FetchResult, *, key: str, endpoint: str, purpose: str) -> Capture:
        """Store the body (if any) and append one manifest record. Returns the record."""
        sha = blob_rel = None
        if result.ok:
            sha = hashlib.sha256(result.body).hexdigest()
            blob_rel = f"blobs/{sha[:2]}/{sha}.json.gz"
            self._write_blob(self.root / blob_rel, result.body)
        payload = {
            "key": key,
            "endpoint": endpoint,
            "purpose": purpose,
            "url": result.url,
            "retrieved_at": result.retrieved_at.isoformat(),
            "http_status": result.status,
            "ok": result.ok,
            "error": result.error,
            "attempts": result.attempts,
            "sha256": sha,
            "n_bytes": len(result.body),
            "blob": blob_rel,
            "collector_version": __version__,
        }
        with self._manifest_lock():
            self._ledger(result.retrieved_at.date()).append(payload)
        return Capture.from_record(payload)

    @contextmanager
    def _manifest_lock(self, *, shared: bool = False) -> Iterator[None]:
        """Serialise appends across processes.

        The live collector and the nightly backfill can run at the same moment. Two
        appends reading the same chain head would fork the hash chain, so every
        append holds an exclusive advisory lock (POSIX ``flock``; macOS and Linux).
        """
        self.manifests.mkdir(parents=True, exist_ok=True)
        with (self.manifests / ".lock").open("a") as fh:
            fcntl.flock(fh.fileno(), fcntl.LOCK_SH if shared else fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)

    @staticmethod
    def _write_blob(path: Path, body: bytes) -> None:
        if path.exists():
            return  # content-addressed: same hash, same bytes
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + f".tmp{os.getpid()}")
        # mtime=0 makes the gzip bytes themselves reproducible.
        tmp.write_bytes(gzip.compress(body, mtime=0))
        tmp.replace(path)

    # ------------------------------------------------------------------ reading

    def manifest_days(self) -> list[date]:
        if not self.manifests.exists():
            return []
        return sorted(date.fromisoformat(p.stem) for p in self.manifests.glob("*.jsonl"))

    def captures(self, days: Iterable[date] | None = None) -> list[Capture]:
        selected = self.manifest_days() if days is None else sorted(set(days))
        out: list[Capture] = []
        # Shared lock: never read a line another process is half-way through writing.
        with self._manifest_lock(shared=True):
            for day in selected:
                ledger = self._ledger(day)
                if ledger.path.exists():
                    out.extend(Capture.from_record(r) for r in ledger.records())
        return out

    def index(self, days: Iterable[date] | None = None) -> dict[str, list[Capture]]:
        """Captures grouped by key, oldest first."""
        grouped: dict[str, list[Capture]] = defaultdict(list)
        for capture in self.captures(days):
            grouped[capture.key].append(capture)
        for items in grouped.values():
            items.sort(key=lambda c: c.retrieved_at)
        return dict(grouped)

    def read(self, capture: Capture) -> bytes:
        if not capture.blob:
            raise FileNotFoundError(
                f"capture of {capture.key} at {capture.retrieved_at} has no body"
            )
        data = gzip.decompress((self.root / capture.blob).read_bytes())
        if capture.sha256 and hashlib.sha256(data).hexdigest() != capture.sha256:
            raise ValueError(f"blob {capture.blob} does not match its recorded hash")
        return data

    def verify(self) -> int:
        """Verify every manifest chain. Returns the number of records checked."""
        n = 0
        for day in self.manifest_days():
            ledger = self._ledger(day)
            ledger.verify()
            n += len(ledger)
        return n
