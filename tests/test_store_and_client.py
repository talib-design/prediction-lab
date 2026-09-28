from __future__ import annotations

import json
import urllib.error
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

from predlab.core.hashing import LedgerCorruptionError
from predlab.racing.sources.pmu.client import (
    Endpoint,
    FetchResult,
    PmuClient,
    capture_key,
    url_for,
)
from predlab.racing.store.raw import RawStore

from .conftest import Clock, FakeTransport

T = datetime(2026, 9, 28, 8, 0, tzinfo=UTC)


def _ok(body: bytes = b'{"a":1}', at: datetime = T) -> FetchResult:
    return FetchResult("https://x/1", 200, body, at)


# ------------------------------------------------------------------ urls and keys


def test_urls_match_the_verified_endpoints() -> None:
    d = date(2026, 9, 28)
    base = "https://online.turfinfo.api.pmu.fr/rest/client"
    assert url_for(Endpoint.PROGRAMME, d) == f"{base}/1/programme/28092026"
    assert (
        url_for(Endpoint.PARTICIPANTS, d, 2, 1) == f"{base}/1/programme/28092026/R2/C1/participants"
    )
    assert url_for(Endpoint.PERFORMANCES, d, 2, 1).endswith(
        "/61/programme/28092026/R2/C1/performances-detaillees/pretty"
    )
    assert url_for(Endpoint.RAPPORTS, d, 2, 1).endswith("/R2/C1/rapports-definitifs")
    assert capture_key(Endpoint.PARTICIPANTS, d, 2, 1) == "participants/2026-09-28/R2C1"
    with pytest.raises(ValueError):
        url_for(Endpoint.PARTICIPANTS, d)


# ------------------------------------------------------------------------- client


def test_client_retries_server_errors_then_succeeds() -> None:
    answers = iter([(503, b""), (200, b"{}")])
    sleeps: list[float] = []
    client = PmuClient(
        transport=lambda u, t: next(answers), min_interval=0, clock=Clock(T), sleep=sleeps.append
    )
    result = client.fetch("u")
    assert result.ok and result.attempts == 2
    assert sleeps, "backoff must wait before retrying"


def test_client_does_not_retry_a_404() -> None:
    transport = FakeTransport()
    client = PmuClient(transport=transport, min_interval=0, clock=Clock(T), sleep=lambda _: None)
    result = client.fetch("https://nowhere")
    assert not result.ok and result.error == "HTTP 404"
    assert len(transport.calls) == 1


def test_network_failure_becomes_a_result_not_an_exception() -> None:
    def broken(url: str, timeout: float) -> tuple[int, bytes]:
        raise urllib.error.URLError("proxy said no")

    client = PmuClient(
        transport=broken, retries=1, min_interval=0, clock=Clock(T), sleep=lambda _: None
    )
    result = client.fetch("u")
    assert not result.ok and result.status == 0
    assert result.error is not None and "network error" in result.error
    assert result.attempts == 2


def test_client_waits_between_requests() -> None:
    sleeps: list[float] = []
    client = PmuClient(
        transport=lambda u, t: (200, b"{}"), min_interval=5.0, clock=Clock(T), sleep=sleeps.append
    )
    client.fetch("a")
    client.fetch("b")
    assert sleeps and sleeps[0] > 4.0
    assert client.requests_made == 2


# -------------------------------------------------------------------------- store


def test_capture_is_stored_and_read_back(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    cap = store.record(_ok(), key="programme/2026-09-28", endpoint="programme", purpose="programme")
    assert cap.ok and cap.blob is not None
    assert store.read(cap) == b'{"a":1}'
    assert store.verify() == 1


def test_identical_bodies_are_stored_once(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    a = store.record(_ok(), key="k", endpoint="programme", purpose="p")
    b = store.record(_ok(at=T + timedelta(minutes=5)), key="k", endpoint="programme", purpose="p")
    assert a.blob == b.blob
    assert len(list((tmp_path / "blobs").rglob("*.gz"))) == 1
    assert [c.retrieved_at for c in store.index()["k"]] == [T, T + timedelta(minutes=5)]


def test_failures_are_recorded_too(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    cap = store.record(
        FetchResult("u", 0, b"", T, "network error: x"), key="k", endpoint="programme", purpose="p"
    )
    assert not cap.ok and cap.blob is None
    with pytest.raises(FileNotFoundError):
        store.read(cap)
    assert store.captures()[0].error == "network error: x"


def test_a_tampered_blob_is_detected(tmp_path: Path) -> None:
    import gzip

    store = RawStore(tmp_path)
    cap = store.record(_ok(), key="k", endpoint="programme", purpose="p")
    assert cap.blob is not None
    (tmp_path / cap.blob).write_bytes(gzip.compress(b'{"a":2}'))
    with pytest.raises(ValueError, match="does not match"):
        store.read(cap)


def test_an_edited_manifest_is_detected(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    store.record(_ok(), key="k", endpoint="programme", purpose="p")
    manifest = next((tmp_path / "manifest").glob("*.jsonl"))
    rec = json.loads(manifest.read_text())
    rec["retrieved_at"] = (T - timedelta(hours=1)).isoformat()  # back-dating a capture
    manifest.write_text(json.dumps(rec) + "\n")
    with pytest.raises(LedgerCorruptionError):
        store.verify()
