"""The live collector: racecards, odds snapshots and results, as they happen.

This is the only irreversible clock in the project. A pre-race odds snapshot not taken
today can never be taken later: the feed keeps only two quotes per runner once a race
is over (docs/DATA_SOURCES.md). So the collector is designed to be run often (every
5 minutes by launchd) and to decide, each time, what is worth fetching *now*.

Each run:

1. refreshes the programme of today (and, less often, tomorrow; and yesterday while
   some of its target races still lack a final result);
2. plans per-race fetches from a pure function, :func:`plan_race_tasks`, which is where
   the snapshot policy lives and what the tests pin down;
3. fetches the most urgent tasks first, up to a per-run cap, and records every
   response -- or failure -- in the raw store.

Snapshot policy for a target race, with ``m`` = minutes until the scheduled off:

=====================  ==========================================================
``m`` > 24 h           runners + odds every 3 h (declarations, early market)
2 h < ``m`` ≤ 24 h     every 60 min
-30 min ≤ ``m`` ≤ 2 h  every run (≥ 4 min apart): the pre-off market, then the
                       final odds as the pools close
official result        runners (finishing positions) and dividends, once
``m`` ≤ 24 h           past performances, once
=====================  ==========================================================

Nothing here bets, stakes or connects to an account. It reads public race data.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from predlab.core.clock import minutes_between, paris_day
from predlab.racing.domain import Race
from predlab.racing.sources.pmu.client import Endpoint, PmuClient, capture_key, url_for
from predlab.racing.sources.pmu.parser import PmuFormatError, parse_programme_detailed
from predlab.racing.store.raw import Capture, RawStore

SNAPSHOT = "snapshot"
RESULT = "result"
HISTORY = "history"
PROGRAMME = "programme"


@dataclass(frozen=True)
class CollectConfig:
    countries: frozenset[str] = frozenset({"FRA"})
    disciplines: frozenset[str] = frozenset({"PLAT"})
    near_window_min: float = 120.0
    near_interval_min: float = 4.0
    far_interval_min: float = 60.0
    day_before_interval_min: float = 180.0
    after_off_window_min: float = 30.0
    today_programme_interval_min: float = 4.0
    other_programme_interval_min: float = 180.0
    stale_yesterday_interval_min: float = 60.0
    max_requests: int = 60

    def is_target(self, race: Race) -> bool:
        return race.country_code in self.countries and race.discipline in self.disciplines


@dataclass(frozen=True, order=True)
class Task:
    priority: float
    key: str = field(compare=False)
    endpoint: Endpoint = field(compare=False)
    purpose: str = field(compare=False)
    day: date = field(compare=False)
    meeting: int | None = field(default=None, compare=False)
    race: int | None = field(default=None, compare=False)

    @property
    def url(self) -> str:
        return url_for(self.endpoint, self.day, self.meeting, self.race)


def _last(captures: Iterable[Capture], purpose: str, *, ok_only: bool = False) -> Capture | None:
    matching = [c for c in captures if c.purpose == purpose and (c.ok or not ok_only)]
    return max(matching, key=lambda c: c.retrieved_at, default=None)


def _due(last: Capture | None, now: datetime, interval_min: float) -> bool:
    return last is None or minutes_between(last.retrieved_at, now) >= interval_min


def plan_race_tasks(
    now: datetime,
    races: Iterable[Race],
    index: dict[str, list[Capture]],
    config: CollectConfig,
) -> list[Task]:
    """Everything worth fetching now for these races, most urgent first. Pure."""
    tasks: list[Task] = []
    for race in races:
        if not config.is_target(race):
            continue
        m = minutes_between(now, race.off_time)
        ids = {"day": race.day, "meeting": race.meeting_number, "race": race.race_number}
        runners_key = capture_key(
            Endpoint.PARTICIPANTS, race.day, race.meeting_number, race.race_number
        )
        runners_caps = index.get(runners_key, [])

        if race.is_final:
            if _last(runners_caps, RESULT, ok_only=True) is None:
                tasks.append(Task(50.0, runners_key, Endpoint.PARTICIPANTS, RESULT, **ids))
            div_key = capture_key(
                Endpoint.RAPPORTS, race.day, race.meeting_number, race.race_number
            )
            if _last(index.get(div_key, []), RESULT, ok_only=True) is None:
                tasks.append(Task(51.0, div_key, Endpoint.RAPPORTS, RESULT, **ids))
            continue

        if m < -config.after_off_window_min:
            continue  # off long ago, result not official yet: nothing new to snapshot

        if m <= config.near_window_min:
            interval = config.near_interval_min
        elif m <= 24 * 60:
            interval = config.far_interval_min
        else:
            interval = config.day_before_interval_min
        if _due(_last(runners_caps, SNAPSHOT), now, interval):
            tasks.append(Task(max(m, 0.0), runners_key, Endpoint.PARTICIPANTS, SNAPSHOT, **ids))

        if m <= 24 * 60:
            perf_key = capture_key(
                Endpoint.PERFORMANCES, race.day, race.meeting_number, race.race_number
            )
            if _last(index.get(perf_key, []), HISTORY, ok_only=True) is None:
                tasks.append(Task(1000.0 + m, perf_key, Endpoint.PERFORMANCES, HISTORY, **ids))
    return sorted(tasks)


@dataclass
class CollectReport:
    started_at: datetime
    programmes: dict[str, str] = field(default_factory=dict)
    planned: int = 0
    fetched: int = 0
    failed: int = 0
    skipped_over_cap: int = 0
    target_races: int = 0
    messages: list[str] = field(default_factory=list)

    def summary(self) -> str:
        head = (
            f"{self.started_at.isoformat(timespec='seconds')} | target races {self.target_races} | "
            f"planned {self.planned} | fetched {self.fetched} | failed {self.failed} | "
            f"deferred {self.skipped_over_cap}"
        )
        return "\n".join([head, *(f"  - {m}" for m in self.messages)])


def _latest_programme(
    store: RawStore, index: dict[str, list[Capture]], day: date
) -> tuple[list[Race] | None, str | None]:
    last = _last(index.get(capture_key(Endpoint.PROGRAMME, day), []), PROGRAMME, ok_only=True)
    if last is None:
        return None, None
    try:
        parsed = parse_programme_detailed(store.read(last))
    except PmuFormatError as exc:
        return None, f"programme {day} could not be parsed (raw kept): {exc}"
    note = None
    if parsed.errors:
        note = (
            f"programme {day}: {len(parsed.errors)} meeting(s)/race(s) skipped: {parsed.errors[0]}"
        )
    return parsed.races, note


def run_collect(
    client: PmuClient,
    store: RawStore,
    *,
    now: datetime,
    config: CollectConfig | None = None,
    dry_run: bool = False,
    log: Callable[[str], None] | None = None,
) -> CollectReport:
    config = config or CollectConfig()
    report = CollectReport(started_at=now)
    today = paris_day(now)
    yesterday, tomorrow = today - timedelta(days=1), today + timedelta(days=1)
    retrieval_days = [today - timedelta(days=d) for d in (-1, 0, 1, 2, 3)]
    index = store.index(retrieval_days)

    # 1. programmes
    wanted: list[tuple[date, float]] = [
        (today, config.today_programme_interval_min),
        (tomorrow, config.other_programme_interval_min),
    ]
    stored_yesterday, _ = _latest_programme(store, index, yesterday)
    if stored_yesterday and any(config.is_target(r) and not r.is_final for r in stored_yesterday):
        wanted.append((yesterday, config.stale_yesterday_interval_min))
    for day, interval in wanted:
        key = capture_key(Endpoint.PROGRAMME, day)
        if not _due(_last(index.get(key, []), PROGRAMME), now, interval):
            continue
        if dry_run:
            report.messages.append(f"would fetch programme {day}")
            continue
        result = client.fetch(url_for(Endpoint.PROGRAMME, day))
        cap = store.record(result, key=key, endpoint=Endpoint.PROGRAMME, purpose=PROGRAMME)
        index.setdefault(key, []).append(cap)
        report.fetched += 1
        if not cap.ok:
            report.failed += 1
            report.messages.append(f"programme {day}: {cap.error}")

    # 2. plan
    tasks: list[Task] = []
    for day in (yesterday, today, tomorrow):
        races, error = _latest_programme(store, index, day)
        if error:
            report.messages.append(error)
        if not races:
            report.programmes[day.isoformat()] = "absent" if error is None else "unparseable"
            continue
        targets = [r for r in races if config.is_target(r)]
        report.programmes[day.isoformat()] = f"{len(races)} races, {len(targets)} target"
        if day == today:
            report.target_races = len(targets)
        tasks.extend(plan_race_tasks(now, targets, index, config))
    tasks.sort()
    report.planned = len(tasks)
    runnable = tasks[: max(config.max_requests - report.fetched, 0)]
    report.skipped_over_cap = len(tasks) - len(runnable)

    # 3. fetch
    for task in runnable:
        if dry_run:
            report.messages.append(f"would fetch {task.purpose} {task.key}")
            continue
        result = client.fetch(task.url)
        cap = store.record(result, key=task.key, endpoint=task.endpoint, purpose=task.purpose)
        report.fetched += 1
        if not cap.ok:
            report.failed += 1
            report.messages.append(f"{task.purpose} {task.key}: {cap.error}")
    if log:
        log(report.summary())
    return report
