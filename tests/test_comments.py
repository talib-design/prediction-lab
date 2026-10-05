from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from predlab.racing import comments
from predlab.racing.sources.pmu.client import FetchResult, PmuClient
from predlab.racing.store.raw import RawStore

from .synthetic_db import make_db

# The synthetic base runs from 2024-01-02, 6 races a day at 12:00-17:00 UTC.
NOW = datetime(2024, 2, 10, 20, tzinfo=UTC)


def _participants(text: str | None) -> bytes:
    p = {"numPmu": 1, "nom": "A", "statut": "PARTANT"}
    if text:
        p["commentaireApresCourse"] = {"texte": text, "source": "DATAHIPPIQUE"}
    return json.dumps(
        {"participants": [p, {"numPmu": 2, "nom": "B", "statut": "PARTANT"}]}
    ).encode()


def test_due_races_are_those_4_to_30_days_old_not_yet_read_late(tmp_path: Path) -> None:
    db = make_db(tmp_path / "r.duckdb", days=60, races_per_day=2)
    store = RawStore(tmp_path / "raw")
    due = comments.due(db, store, NOW)
    days = {d.day for d in due}
    assert min(days) >= (NOW - comments.WINDOW).date() and max(days) <= date(2024, 2, 6)
    first = due[0]
    # Read the day after the race: still due. Read 5 days after: done.
    store.record(
        FetchResult("u", 200, _participants(None), first.off_time + timedelta(days=1)),
        key=f"participants/{first.day}/R{first.meeting}C{first.race}",
        endpoint="participants",
        purpose="result",
    )
    assert first in comments.due(db, store, NOW)
    store.record(
        FetchResult("u", 200, _participants("A fini fort."), first.off_time + timedelta(days=5)),
        key=f"participants/{first.day}/R{first.meeting}C{first.race}",
        endpoint="participants",
        purpose=comments.COMMENT,
    )
    assert first not in comments.due(db, store, NOW)


def test_fetch_and_extract(tmp_path: Path) -> None:
    db = make_db(tmp_path / "r.duckdb", days=60, races_per_day=2)
    store = RawStore(tmp_path / "raw")
    due = comments.due(db, store, NOW)
    calls: list[str] = []

    def transport(url: str, timeout: float) -> tuple[int, bytes]:
        calls.append(url)
        return 200, _participants("Attentiste, a fini honorablement." if len(calls) % 2 else None)

    client = PmuClient(transport=transport, sleep=lambda _: None)
    report = comments.fetch(client, store, due, max_requests=5)
    assert report.requests == 5 and len(calls) == 5 and not report.failures
    frame = comments.extract(store)
    assert frame.height == 3, "one comment in every other read"
    assert set(frame["source"]) == {"DATAHIPPIQUE"} and set(frame["number"]) == {1}
    path = comments.write(frame, tmp_path / "normalized")
    assert path.exists()
