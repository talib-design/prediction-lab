"""Historical backfill: French flat and trot races since 2023, fetched once, politely.

Scale, from the audit: ~4 000 flat and ~7 000 trot races a year in France; since 2023
that is ~40 000 races, two requests each (runners, dividends). It therefore runs
in bounded slices (a request cap and a deadline), typically a few hours a night, and
resumes where it stopped. There is no progress file to trust: the raw store *is* the
state. A day is done when its programme and every target race's post-race runners
capture are stored; a small checkpoint only remembers fully closed days so later runs
skip them without re-reading their programmes.

Order: newest first. The most recent seasons are the ones a test window will use, so
they become usable soonest.

Dividends (``rapports-definitifs``) are fetched too: the betting simulation settles
fictitious tickets against them. Past performances (``performances-detaillees``) are opt-in: the runners of every race
already give each horse's French history within the window; performances add older
runs at the cost of one more request per race.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

from predlab.racing.domain import Race
from predlab.racing.sources.pmu.client import Endpoint, PmuClient, capture_key, url_for
from predlab.racing.sources.pmu.parser import PmuFormatError, parse_programme_detailed
from predlab.racing.store.raw import Capture, RawStore

BACKFILL = "backfill"
RESULT_DELAY = timedelta(hours=1)
# A failed request no longer ends the night: its day is left open (retried next run)
# and the backfill moves on. Only this many failures in a row -- the network is down,
# or the Mac is asleep -- stop it.
MAX_CONSECUTIVE_FAILURES = 20


@dataclass
class BackfillReport:
    days_seen: int = 0
    days_completed: int = 0
    races_fetched: int = 0
    requests: int = 0
    failures: list[str] = field(default_factory=list)
    stopped_by: str = "done"
    oldest_day_reached: date | None = None

    def summary(self) -> str:
        return (
            f"backfill: {self.requests} requêtes, {self.races_fetched} courses, "
            f"{self.days_completed} jours complétés, jusqu'au {self.oldest_day_reached}, "
            f"arrêt : {self.stopped_by}, échecs : {len(self.failures)}"
        )


def _has_post_race_capture(captures: list[Capture], race: Race) -> bool:
    return any(c.ok and c.retrieved_at >= race.off_time + RESULT_DELAY for c in captures)


def _is_target(race: Race, country: str, discipline: str) -> bool:
    return (
        race.country_code == country
        and race.discipline == discipline
        and "ANNULEE" not in (race.status or "")
    )


def _load_checkpoint(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(json.loads(path.read_text(encoding="utf-8")))


def _save_checkpoint(path: Path, done: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(sorted(done)), encoding="utf-8")
    tmp.replace(path)


def run_backfill(
    client: PmuClient,
    store: RawStore,
    *,
    start: date,
    end: date,
    now: Callable[[], datetime],
    max_requests: int = 20_000,
    deadline: datetime | None = None,
    with_performances: bool = False,
    with_dividends: bool = True,
    country: str = "FRA",
    discipline: str = "PLAT",
    progress: Callable[[str], None] | None = None,
) -> BackfillReport:
    report = BackfillReport()
    # v2: a day is complete only once its dividends are stored too (needed by the
    # betting simulation). Days closed under v1 are rescanned; their programmes and
    # runners are cached, so only the dividends are fetched.
    suffix = "" if discipline == "PLAT" else f"_{discipline}"
    checkpoint = store.root / f"backfill_done_v2{suffix}.json"
    done = _load_checkpoint(checkpoint)
    index = store.index()
    before = client.requests_made
    streak = 0

    def budget_left() -> bool:
        if streak >= MAX_CONSECUTIVE_FAILURES:
            report.stopped_by = f"réseau indisponible ({streak} échecs d'affilée)"
            return False
        if client.requests_made - before >= max_requests:
            report.stopped_by = "plafond de requêtes"
            return False
        if deadline is not None and now() >= deadline:
            report.stopped_by = "heure limite"
            return False
        return True

    def fetch(
        endpoint: Endpoint, day: date, meeting: int | None = None, race: int | None = None
    ) -> Capture:
        key = capture_key(endpoint, day, meeting, race)
        cap = store.record(
            client.fetch(url_for(endpoint, day, meeting, race)),
            key=key,
            endpoint=endpoint,
            purpose=BACKFILL,
        )
        nonlocal streak
        index.setdefault(key, []).append(cap)
        if not cap.ok:
            report.failures.append(f"{key}: {cap.error}")
            streak += 1
        else:
            streak = 0
        return cap

    day = end
    while day >= start:
        if day.isoformat() in done:
            day -= timedelta(days=1)
            continue
        if not budget_left():
            break
        report.days_seen += 1
        report.oldest_day_reached = day

        prog_key = capture_key(Endpoint.PROGRAMME, day)
        ok_progs = [c for c in index.get(prog_key, []) if c.ok]
        # A programme captured before the day was over lacks the results: refetch.
        closed = [c for c in ok_progs if c.retrieved_at.date() > day]
        cap = (
            max(closed, key=lambda c: c.retrieved_at) if closed else fetch(Endpoint.PROGRAMME, day)
        )
        if not cap.ok:
            if not budget_left():
                break
            day -= timedelta(days=1)
            continue
        try:
            parsed = parse_programme_detailed(store.read(cap))
        except PmuFormatError as exc:
            report.failures.append(f"{prog_key}: {exc}")
            day -= timedelta(days=1)
            continue

        complete = True
        out_of_budget = False
        for race in (r for r in parsed.races if _is_target(r, country, discipline)):
            key = capture_key(
                Endpoint.PARTICIPANTS, race.day, race.meeting_number, race.race_number
            )
            if not _has_post_race_capture(index.get(key, []), race):
                if not budget_left():
                    complete, out_of_budget = False, True
                    break
                if fetch(Endpoint.PARTICIPANTS, race.day, race.meeting_number, race.race_number).ok:
                    report.races_fetched += 1
                else:
                    complete = False
            if with_dividends:
                div_key = capture_key(
                    Endpoint.RAPPORTS, race.day, race.meeting_number, race.race_number
                )
                if not any(c.ok for c in index.get(div_key, [])):
                    if not budget_left():
                        complete, out_of_budget = False, True
                        break
                    complete &= fetch(
                        Endpoint.RAPPORTS, race.day, race.meeting_number, race.race_number
                    ).ok
            if with_performances:
                perf_key = capture_key(
                    Endpoint.PERFORMANCES, race.day, race.meeting_number, race.race_number
                )
                if not any(c.ok for c in index.get(perf_key, [])):
                    if not budget_left():
                        complete, out_of_budget = False, True
                        break
                    complete &= fetch(
                        Endpoint.PERFORMANCES, race.day, race.meeting_number, race.race_number
                    ).ok
        if out_of_budget:
            break
        if complete and day < now().date() - timedelta(days=2):
            done.add(day.isoformat())
            report.days_completed += 1
        if progress and report.days_seen % 30 == 0:
            progress(f"{day} — {client.requests_made - before} requêtes")
        day -= timedelta(days=1)

    report.requests = client.requests_made - before
    _save_checkpoint(checkpoint, done)
    return report


# From 2023 for every discipline (decision of 2026-09-28): the horses running now, with
# their recent careers; three full seasons before the test window. Older seasons can
# be added later by passing an earlier date -- nothing already stored is refetched.
DEFAULT_PLAN = "PLAT:2023-01-01,ATTELE:2023-01-01,MONTE:2023-01-01"


def parse_plan(text: str) -> list[tuple[str, date]]:
    """``"PLAT:2023-01-01,ATTELE:2023-01-01"`` -> [("PLAT", date), ...], in priority order."""
    plan = []
    for part in text.split(","):
        discipline, _, start = part.strip().partition(":")
        if not discipline or not start:
            raise ValueError(f"plan entry {part!r}: expected DISCIPLINE:AAAA-MM-JJ")
        plan.append((discipline.strip().upper(), date.fromisoformat(start.strip())))
    return plan


def run_backfill_plan(
    client: PmuClient,
    store: RawStore,
    *,
    plan: list[tuple[str, date]],
    end: date,
    now: Callable[[], datetime],
    max_requests: int = 20_000,
    deadline: datetime | None = None,
    progress: Callable[[str], None] | None = None,
) -> list[tuple[str, BackfillReport]]:
    """Disciplines one after the other: the first is completed before the next starts.

    Flat racing first (the project's first model), then trot. The request budget and
    the deadline are shared by the whole plan.
    """
    reports = []
    used = 0
    for discipline, start in plan:
        if used >= max_requests or (deadline is not None and now() >= deadline):
            break
        report = run_backfill(
            client,
            store,
            start=start,
            end=end,
            now=now,
            max_requests=max_requests - used,
            deadline=deadline,
            discipline=discipline,
            progress=progress,
        )
        used += report.requests
        reports.append((discipline, report))
        if report.stopped_by != "done":
            break
    return reports
