from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from predlab.racing.collect import (
    HISTORY,
    RESULT,
    SNAPSHOT,
    CollectConfig,
    plan_race_tasks,
    run_collect,
)
from predlab.racing.domain import Race
from predlab.racing.sources.pmu.client import Endpoint, FetchResult, capture_key
from predlab.racing.store.raw import Capture, RawStore

from .conftest import FakeTransport, fixture_bytes, make_client

OFF = datetime(2026, 9, 28, 14, 0, tzinfo=UTC)
CFG = CollectConfig()


def race(**kw: object) -> Race:
    base: dict[str, object] = {
        "day": date(2026, 9, 28),
        "meeting_number": 2,
        "race_number": 1,
        "off_time": OFF,
        "country_code": "FRA",
        "venue_code": "CRA",
        "venue_name": "CRAON",
        "discipline": "PLAT",
    }
    base.update(kw)
    return Race.model_validate(base)


def cap(key: str, purpose: str, at: datetime, ok: bool = True) -> Capture:
    return Capture(
        key,
        "participants",
        purpose,
        "u",
        at,
        200 if ok else 0,
        ok,
        None if ok else "x",
        "h" if ok else None,
        1,
        "b" if ok else None,
    )


KEY = capture_key(Endpoint.PARTICIPANTS, date(2026, 9, 28), 2, 1)


def purposes(tasks: list) -> set[tuple[str, str]]:
    return {(t.endpoint.value, t.purpose) for t in tasks}


def test_non_target_races_are_ignored() -> None:
    now = OFF - timedelta(minutes=30)
    assert plan_race_tasks(now, [race(discipline="ATTELE"), race(country_code="GB")], {}, CFG) == []


def test_near_the_off_every_run_takes_a_snapshot() -> None:
    now = OFF - timedelta(minutes=30)
    index = {KEY: [cap(KEY, SNAPSHOT, now - timedelta(minutes=5))]}
    tasks = plan_race_tasks(now, [race()], index, CFG)
    assert ("participants", SNAPSHOT) in purposes(tasks)


def test_near_the_off_snapshots_are_not_duplicated_within_the_interval() -> None:
    now = OFF - timedelta(minutes=30)
    index = {KEY: [cap(KEY, SNAPSHOT, now - timedelta(minutes=2))]}
    assert ("participants", SNAPSHOT) not in purposes(plan_race_tasks(now, [race()], index, CFG))


def test_far_from_the_off_snapshots_are_hourly() -> None:
    now = OFF - timedelta(hours=6)
    recent = {KEY: [cap(KEY, SNAPSHOT, now - timedelta(minutes=30))]}
    stale = {KEY: [cap(KEY, SNAPSHOT, now - timedelta(minutes=61))]}
    assert ("participants", SNAPSHOT) not in purposes(plan_race_tasks(now, [race()], recent, CFG))
    assert ("participants", SNAPSHOT) in purposes(plan_race_tasks(now, [race()], stale, CFG))


def test_just_after_the_off_the_final_odds_are_still_collected() -> None:
    now = OFF + timedelta(minutes=10)
    assert ("participants", SNAPSHOT) in purposes(plan_race_tasks(now, [race()], {}, CFG))
    later = OFF + timedelta(minutes=45)
    assert plan_race_tasks(later, [race()], {}, CFG) == []


def test_official_result_triggers_one_result_capture() -> None:
    now = OFF + timedelta(minutes=20)
    done = race(is_final=True, status_category="ARRIVEE")
    tasks = plan_race_tasks(now, [done], {}, CFG)
    assert purposes(tasks) == {("participants", RESULT), ("rapports", RESULT)}
    div_key = capture_key(Endpoint.RAPPORTS, date(2026, 9, 28), 2, 1)
    index = {KEY: [cap(KEY, RESULT, now)], div_key: [cap(div_key, RESULT, now)]}
    assert plan_race_tasks(now, [done], index, CFG) == []


def test_a_failed_result_capture_is_retried() -> None:
    now = OFF + timedelta(minutes=20)
    index = {KEY: [cap(KEY, RESULT, now, ok=False)]}
    tasks = plan_race_tasks(now, [race(is_final=True)], index, CFG)
    assert ("participants", RESULT) in purposes(tasks)


def test_history_is_fetched_once_within_24h() -> None:
    now = OFF - timedelta(hours=3)
    assert ("performances", HISTORY) in purposes(plan_race_tasks(now, [race()], {}, CFG))
    perf_key = capture_key(Endpoint.PERFORMANCES, date(2026, 9, 28), 2, 1)
    index = {perf_key: [cap(perf_key, HISTORY, now)]}
    assert ("performances", HISTORY) not in purposes(plan_race_tasks(now, [race()], index, CFG))
    far = OFF - timedelta(hours=30)
    assert ("performances", HISTORY) not in purposes(plan_race_tasks(far, [race()], {}, CFG))


def test_most_urgent_task_comes_first() -> None:
    now = OFF - timedelta(hours=1)
    soon = race(race_number=2, off_time=now + timedelta(minutes=10))
    later = race(race_number=3, off_time=now + timedelta(minutes=90))
    tasks = plan_race_tasks(now, [later, soon], {}, CFG)
    assert tasks[0].race == 2


# ---------------------------------------------------------------------- end to end


def test_a_collect_run_stores_programme_snapshot_and_history(tmp_path: Path, t0: datetime) -> None:
    transport = FakeTransport(
        {
            "/1/programme/28092026": (200, fixture_bytes("programme_2026-09-28_excerpt.json")),
            "/R2/C1/participants": (
                200,
                fixture_bytes("participants_2026-09-28_R2C1_excerpt.json"),
            ),
            "/R2/C1/performances-detaillees/pretty": (200, b'{"participants":[]}'),
        }
    )
    store = RawStore(tmp_path)
    report = run_collect(make_client(transport, t0), store, now=t0)

    keys = {(c.key, c.purpose, c.ok) for c in store.captures()}
    assert ("programme/2026-09-28", "programme", True) in keys
    assert ("programme/2026-09-29", "programme", False) in keys, (
        "tomorrow 404 is recorded, not hidden"
    )
    assert ("participants/2026-09-28/R2C1", SNAPSHOT, True) in keys
    assert ("performances/2026-09-28/R2C1", HISTORY, True) in keys
    assert not any("R1C1" in c.key for c in store.captures()), "trot race must not be collected"
    assert report.target_races == 1
    assert store.verify() == len(store.captures())

    # Two minutes later: nothing is due, nothing is fetched.
    transport.calls.clear()
    run_collect(
        make_client(transport, t0 + timedelta(minutes=2)), store, now=t0 + timedelta(minutes=2)
    )
    assert transport.calls == []


def test_dry_run_fetches_nothing(tmp_path: Path, t0: datetime) -> None:
    transport = FakeTransport()
    report = run_collect(make_client(transport, t0), RawStore(tmp_path), now=t0, dry_run=True)
    assert transport.calls == []
    assert any("would fetch programme" in m for m in report.messages)


def test_request_cap_is_respected(tmp_path: Path, t0: datetime) -> None:
    transport = FakeTransport(
        {"/1/programme/28092026": (200, fixture_bytes("programme_2026-09-28_excerpt.json"))}
    )
    report = run_collect(
        make_client(transport, t0), RawStore(tmp_path), now=t0, config=CollectConfig(max_requests=2)
    )
    assert len(transport.calls) == 2
    assert report.skipped_over_cap >= 1


def test_unparseable_programme_is_kept_and_reported(tmp_path: Path, t0: datetime) -> None:
    transport = FakeTransport({"/1/programme/28092026": (200, b'{"programme":{}}')})
    store = RawStore(tmp_path)
    report = run_collect(make_client(transport, t0), store, now=t0)
    assert any("could not be parsed" in m for m in report.messages)
    assert any(c.ok and c.key == "programme/2026-09-28" for c in store.captures())


def test_fetch_result_ok_requires_a_body() -> None:
    assert not FetchResult("u", 200, b"", OFF).ok
