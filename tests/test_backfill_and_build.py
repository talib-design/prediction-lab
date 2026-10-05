from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import duckdb
import pytest

from predlab.racing.backfill import run_backfill
from predlab.racing.domain import Runner
from predlab.racing.sources.pmu.client import FetchResult
from predlab.racing.sources.pmu.parser import (
    PmuFormatError,
    parse_programme,
    parse_programme_detailed,
)
from predlab.racing.store.normalized import build
from predlab.racing.store.raw import RawStore

from .conftest import Clock, FakeTransport, fixture_bytes, make_client

LATER = datetime(2026, 9, 30, 10, 0, tzinfo=UTC)


# ------------------------------------------------------------------------ parser


def test_a_malformed_meeting_no_longer_costs_the_whole_day() -> None:
    doc = json.loads(fixture_bytes("programme_2026-09-28_excerpt.json"))
    doc["programme"]["reunions"].append({"numOfficiel": 9, "pays": {"code": "GB"}, "courses": []})
    parsed = parse_programme_detailed(doc)
    assert {r.race_id for r in parsed.races} == {"2026-09-28/R1C1", "2026-09-28/R2C1"}
    assert len(parsed.errors) == 1 and "reunions[2].hippodrome" in parsed.errors[0]
    with pytest.raises(PmuFormatError):
        parse_programme(doc)  # the strict form still refuses


def test_identity_key_is_rebuilt_when_not_published() -> None:
    kw = {"race_id": "r", "number": 1, "status": "PARTANT"}
    published = Runner(name="A", horse_key="A-M-P", dam="X", sire="Y", **kw)
    rebuilt = Runner(name="EAST AND WEST", dam="LIVINGINAFANTASY", sire="TERRITORIES", **kw)
    unknown = Runner(name="B", **kw)
    assert published.identity_key == "A-M-P"
    assert rebuilt.identity_key == "EAST AND WEST-LIVINGINAFANTASY-TERRITORIES"
    assert unknown.identity_key is None


# ---------------------------------------------------------------------- backfill


def _transport() -> FakeTransport:
    return FakeTransport(
        {
            "/1/programme/27092026": (200, fixture_bytes("programme_2026-09-27_R1C1_partial.json")),
            "/R1/C1/participants": (
                200,
                fixture_bytes("participants_2026-09-27_R1C1_partial.json"),
            ),
            "/R1/C1/rapports-definitifs": (
                200,
                fixture_bytes("rapports_2026-09-28_R2C1_full.json"),
            ),
        }
    )


def _run(store: RawStore, transport: FakeTransport, **kw: object):
    return run_backfill(
        make_client(transport, LATER),
        store,
        start=date(2026, 9, 27),
        end=date(2026, 9, 27),
        now=Clock(LATER),
        discipline="ATTELE",
        **kw,  # type: ignore[arg-type]
    )


def test_backfill_fetches_programme_and_runners_then_skips_done_days(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    first = _transport()
    report = _run(store, first)
    assert report.races_fetched == 1 and report.days_completed == 1
    assert report.stopped_by == "done"
    assert len(first.calls) == 3, "programme, runners, dividends"

    again = _transport()
    assert _run(store, again).requests == 0
    assert again.calls == []


def test_backfill_respects_its_request_cap(tmp_path: Path) -> None:
    report = _run(RawStore(tmp_path), _transport(), max_requests=1)
    assert report.stopped_by == "plafond de requêtes"
    assert report.days_completed == 0


def test_backfill_does_not_trust_a_pre_race_capture_as_the_result(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    before_off = datetime(2026, 9, 27, 11, 0, tzinfo=UTC)  # off is 11:26 UTC
    store.record(
        FetchResult(
            "u", 200, fixture_bytes("participants_2026-09-27_R1C1_partial.json"), before_off
        ),
        key="participants/2026-09-27/R1C1",
        endpoint="participants",
        purpose="snapshot",
    )
    transport = _transport()
    report = _run(store, transport)
    assert report.races_fetched == 1, "a snapshot taken before the off is not a result"


# ------------------------------------------------------------------------- build


def test_build_produces_tables_with_provenance(tmp_path: Path) -> None:
    store = RawStore(tmp_path / "raw")
    t = datetime(2026, 9, 28, 8, 0, tzinfo=UTC)
    store.record(
        FetchResult("u", 200, fixture_bytes("programme_2026-09-28_excerpt.json"), t),
        key="programme/2026-09-28",
        endpoint="programme",
        purpose="programme",
    )
    for minutes in (0, 5):  # two snapshots with identical quotes -> quotes deduplicated
        store.record(
            FetchResult(
                "u",
                200,
                fixture_bytes("participants_2026-09-28_R2C1_excerpt.json"),
                t + timedelta(minutes=minutes),
            ),
            key="participants/2026-09-28/R2C1",
            endpoint="participants",
            purpose="snapshot",
        )
    report = build(store, tmp_path / "normalized", tmp_path / "racing.duckdb")
    assert (report.races, report.runners, report.odds, report.horses) == (2, 1, 2, 1)

    con = duckdb.connect(str(tmp_path / "racing.duckdb"), read_only=True)
    horse = con.execute("SELECT horse_id, birth_year, sire FROM horses").fetchone()
    assert horse == ("EAST AND WEST-LIVINGINAFANTASY-TERRITORIES", 2024, "TERRITORIES")
    after_off = con.execute("SELECT captured_after_off FROM runners_enriched").fetchone()
    assert after_off == (False,)
    first_seen = con.execute("SELECT epoch(min(retrieved_at)) FROM odds").fetchone()
    assert first_seen is not None and first_seen[0] == t.timestamp(), "known from first capture"
    con.close()


def test_build_is_reproducible(tmp_path: Path) -> None:
    store = RawStore(tmp_path / "raw")
    _run(store, _transport())
    a = build(store, tmp_path / "n1", tmp_path / "a.duckdb")
    b = build(store, tmp_path / "n2", tmp_path / "b.duckdb")
    assert a.summary() == b.summary()
    assert (tmp_path / "n1" / "odds.parquet").read_bytes() == (
        tmp_path / "n2" / "odds.parquet"
    ).read_bytes()


def test_backfill_plan_is_parsed_in_priority_order() -> None:
    from predlab.racing.backfill import DEFAULT_PLAN, parse_plan, targets

    plan = parse_plan(DEFAULT_PLAN)
    assert [d for d, _ in plan] == ["PLAT", "ATTELE", "MONTE"] * 2
    assert [s for _, s in plan[:3]] == [date(2024, 1, 1)] * 3, "2024 first, for every discipline"
    assert [s for _, s in plan[3:]] == [date(2020, 1, 1)] * 3, "then back to 2020"
    assert targets(plan) == [(d, date(2020, 1, 1)) for d in ("PLAT", "ATTELE", "MONTE")]
    with pytest.raises(ValueError):
        parse_plan("PLAT")


def test_a_failed_request_leaves_its_day_open_and_the_backfill_goes_on(tmp_path: Path) -> None:
    transport = _transport()
    transport.routes["/R1/C1/rapports-definitifs"] = (500, b"")
    report = run_backfill(
        make_client(transport, LATER),
        RawStore(tmp_path),
        start=date(2026, 9, 25),
        end=date(2026, 9, 27),
        now=Clock(LATER),
        discipline="ATTELE",
    )
    assert report.days_completed == 0, "the day with a missing dividend stays open"
    assert report.stopped_by == "done", "one failure no longer ends the run"
    assert any("/programme/25092026" in u for u in transport.calls), "older days still visited"


def test_the_backfill_stops_when_the_network_is_down(tmp_path: Path) -> None:
    from predlab.racing.backfill import MAX_CONSECUTIVE_FAILURES

    transport = FakeTransport({})  # every request fails
    report = run_backfill(
        make_client(transport, LATER),
        RawStore(tmp_path),
        start=date(2026, 1, 1),
        end=date(2026, 9, 27),
        now=Clock(LATER),
    )
    assert report.stopped_by.startswith("réseau indisponible")
    assert len(transport.calls) <= MAX_CONSECUTIVE_FAILURES * 4  # client retries included
