"""The dashboard's manifest index is extended incrementally, never rebuilt on every change."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from predlab.api.app import IndexCache, IndexSnapshot
from predlab.racing.sources.pmu.client import FetchResult
from predlab.racing.store.raw import ManifestRewoundError, RawStore

T = datetime(2026, 10, 15, 22, 0, tzinfo=UTC)


def _put(store: RawStore, key: str, at: datetime, *, ok: bool = True) -> None:
    result = FetchResult("u", 200 if ok else 500, b'{"a":1}' if ok else b"", at)
    store.record(result, key=key, endpoint="participants", purpose="snapshot")


def _same_as_full_rebuild(cache: IndexCache, store: RawStore) -> IndexSnapshot:
    snap = cache.snapshot()
    full = store.index()
    assert snap.index == full
    captures = [c for items in full.values() for c in items]
    assert snap.count == len(captures)
    assert snap.failed == sum(1 for c in captures if not c.ok)
    assert snap.last == max((c.retrieved_at for c in captures), default=None)
    return snap


def test_incremental_index_matches_a_full_rebuild_at_every_step(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    cache = IndexCache(store)
    assert _same_as_full_rebuild(cache, store).count == 0  # no manifest directory yet

    _put(store, "participants/2026-10-15/R1C1", T)
    _put(store, "participants/2026-10-15/R1C2", T + timedelta(minutes=5), ok=False)
    first = _same_as_full_rebuild(cache, store)
    assert first.count == 2 and first.failed == 1

    # same key again, a new key, and a capture on the next UTC day (a second manifest file)
    _put(store, "participants/2026-10-15/R1C1", T + timedelta(minutes=10))
    _put(store, "participants/2026-10-16/R1C1", T + timedelta(hours=3))
    second = _same_as_full_rebuild(cache, store)
    assert second.count == 4
    assert [c.retrieved_at for c in second.index["participants/2026-10-15/R1C1"]] == [
        T,
        T + timedelta(minutes=10),
    ]
    # readers of the earlier snapshot keep a coherent view
    assert first.count == 2 and len(first.index["participants/2026-10-15/R1C1"]) == 1


def test_unchanged_manifests_are_not_reread(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    _put(store, "participants/2026-10-15/R1C1", T)
    cache = IndexCache(store)
    snap = cache.snapshot()
    assert cache.snapshot() is snap
    assert (
        store.captures_since(
            {f.name: f.stat().st_size for f in store.manifests.glob("*") if f.suffix == ".jsonl"}
        )[0]
        == []
    )


def test_a_line_still_being_written_is_picked_up_once_complete(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    _put(store, "participants/2026-10-15/R1C1", T)
    cache = IndexCache(store)
    assert cache.snapshot().count == 1

    manifest = next(store.manifests.glob("*.jsonl"))
    record = json.loads(manifest.read_text().splitlines()[-1])
    record["key"] = "participants/2026-10-15/R1C2"
    line = json.dumps(record, sort_keys=True)
    with manifest.open("a") as fh:
        fh.write(line[:40])  # the collector is half-way through the line
    assert cache.snapshot().count == 1
    with manifest.open("a") as fh:
        fh.write(line[40:] + "\n")
    snap = _same_as_full_rebuild(cache, store)
    assert snap.count == 2 and "participants/2026-10-15/R1C2" in snap.index


def test_a_shortened_manifest_forces_a_full_rebuild(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    for minutes in range(3):
        _put(store, "participants/2026-10-15/R1C1", T + timedelta(minutes=minutes))
    cache = IndexCache(store)
    assert cache.snapshot().count == 3

    manifest = next(store.manifests.glob("*.jsonl"))
    kept = manifest.read_text().splitlines(keepends=True)[:1]
    manifest.write_text("".join(kept))  # history rewritten: the offsets can no longer be trusted
    with pytest.raises(ManifestRewoundError):
        store.captures_since({manifest.name: 10**9})
    assert _same_as_full_rebuild(cache, store).count == 1


def test_a_malformed_line_is_reported_not_skipped(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    _put(store, "participants/2026-10-15/R1C1", T)
    manifest = next(store.manifests.glob("*.jsonl"))
    with manifest.open("a") as fh:
        fh.write("{not json\n")
    with pytest.raises(ValueError, match="malformed JSON"):
        IndexCache(store).snapshot()


def test_simultaneous_requests_while_the_collector_writes(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    for i in range(20):
        _put(store, f"participants/2026-10-15/R1C{i}", T + timedelta(seconds=i))
    cache = IndexCache(store)

    def reader(_: int) -> int:
        return max(cache.snapshot().count for _ in range(30))

    with ThreadPoolExecutor(max_workers=8) as pool:
        readers = [pool.submit(reader, n) for n in range(8)]
        for i in range(20, 40):
            _put(store, f"participants/2026-10-15/R1C{i}", T + timedelta(seconds=i))
        counts = [f.result() for f in readers]
    assert all(20 <= c <= 40 for c in counts)
    assert _same_as_full_rebuild(cache, store).count == 40
