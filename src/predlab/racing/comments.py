"""Post-race comments: collected while the PMU still publishes them (decision of Chris,
2026-10-05).

Each runner of a finished race gets a short French comment in the runners feed
(``commentaireApresCourse``, source DATAHIPPIQUE): "Attentiste à l'arrière du peloton,
a fini honorablement…". Measured on 2026-10-05: about half the runners have one the day
after the race, all of them 4 to 7 days after, none once the race is a month old -- the
feed drops them. There is therefore no history to backfill: they must be read while they
are there.

Each night, every finished French race (plat, attelé, monté) run 4 to 30 days ago whose
runners were never read at least 4 days after the off is read once more (one request per
race, under the backfill lock: the feed sees one reader). The comments are then
extracted to ``data/normalized/comments.parquet`` (PMU text: never committed).

What a comment says about a horse is only usable for its *next* race, and a criterion
built on it (an "excuse" last time: blocked, badly away, finished strongly…) can only be
judged forward, once enough horses have run again.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import polars as pl

from predlab.racing.sources.pmu.client import Endpoint, PmuClient, capture_key, url_for
from predlab.racing.store.raw import Capture, RawStore

COMMENT = "comment"
DELAY = timedelta(days=4)  # comments are complete 4 to 7 days after the race
WINDOW = timedelta(days=30)  # and gone after about a month
DISCIPLINES = ("PLAT", "ATTELE", "MONTE")

COMMENTS_SCHEMA: dict[str, Any] = {
    "race_id": pl.Utf8,
    "number": pl.Int64,
    "name": pl.Utf8,
    "comment": pl.Utf8,
    "source": pl.Utf8,
    "retrieved_at": pl.Datetime("us", "UTC"),
}


@dataclass(frozen=True)
class Due:
    race_id: str
    day: date
    meeting: int
    race: int
    off_time: datetime


@dataclass
class CommentReport:
    due: int = 0
    requests: int = 0
    failures: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"commentaires : {self.due} courses à relire, {self.requests} requêtes, "
            f"{len(self.failures)} échecs"
        )


def finished_races(db_path: Path, now: datetime) -> list[Due]:
    """French target races whose off was between 30 and 4 days ago."""
    import duckdb

    if not db_path.exists():
        return []
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        rows = con.execute(
            """
            SELECT race_id, day, meeting_number, race_number, epoch_ms(off_time)
            FROM races
            WHERE is_final AND country_code = 'FRA'
              AND discipline IN ('PLAT', 'ATTELE', 'MONTE')
              AND coalesce(status, '') NOT LIKE '%ANNULEE%'
              AND epoch_ms(off_time) BETWEEN ? AND ?
            ORDER BY off_time
            """,
            [
                int((now - WINDOW).timestamp() * 1000),
                int((now - DELAY).timestamp() * 1000),
            ],
        ).fetchall()
    finally:
        con.close()
    return [
        Due(rid, day, int(m), int(r), datetime.fromtimestamp(off / 1000, UTC))
        for rid, day, m, r, off in rows
    ]


def _read_late(caps: list[Capture], off: datetime) -> bool:
    return any(c.ok and c.retrieved_at >= off + DELAY for c in caps)


def due(db_path: Path, store: RawStore, now: datetime) -> list[Due]:
    index = store.index()
    return [
        d
        for d in finished_races(db_path, now)
        if not _read_late(
            index.get(capture_key(Endpoint.PARTICIPANTS, d.day, d.meeting, d.race), []),
            d.off_time,
        )
    ]


def fetch(
    client: PmuClient,
    store: RawStore,
    races: list[Due],
    *,
    max_requests: int = 1500,
    progress: Callable[[str], None] | None = None,
) -> CommentReport:
    report = CommentReport(due=len(races))
    before = client.requests_made
    for i, d in enumerate(races, 1):
        if client.requests_made - before >= max_requests:
            break
        cap = store.record(
            client.fetch(url_for(Endpoint.PARTICIPANTS, d.day, d.meeting, d.race)),
            key=capture_key(Endpoint.PARTICIPANTS, d.day, d.meeting, d.race),
            endpoint=Endpoint.PARTICIPANTS,
            purpose=COMMENT,
        )
        if not cap.ok:
            report.failures.append(f"{d.race_id}: {cap.error}")
        if progress and i % 100 == 0:
            progress(f"commentaires : {i}/{len(races)} courses relues")
    report.requests = client.requests_made - before
    return report


def extract(store: RawStore) -> pl.DataFrame:
    """One row per runner comment, from the latest comment read of each race."""
    latest: dict[str, Capture] = {}
    for key, caps in store.index().items():
        if not key.startswith(f"{Endpoint.PARTICIPANTS}/"):
            continue
        ok = [c for c in caps if c.ok and c.purpose == COMMENT]
        if ok:
            latest[key] = max(ok, key=lambda c: c.retrieved_at)
    rows: list[dict[str, Any]] = []
    for key, cap in sorted(latest.items()):
        race_id = key.split("/", 1)[1]
        try:
            doc = json.loads(store.read(cap))
        except (OSError, ValueError):
            continue
        for p in doc.get("participants") or []:
            c = p.get("commentaireApresCourse") or {}
            text = c.get("texte") if isinstance(c, dict) else None
            if not text:
                continue
            rows.append(
                {
                    "race_id": race_id,
                    "number": p.get("numPmu"),
                    "name": p.get("nom"),
                    "comment": text,
                    "source": c.get("source"),
                    "retrieved_at": cap.retrieved_at,
                }
            )
    return pl.DataFrame(rows, schema=COMMENTS_SCHEMA)


def write(frame: pl.DataFrame, normalized: Path) -> Path:
    normalized.mkdir(parents=True, exist_ok=True)
    path = normalized / "comments.parquet"
    tmp = path.with_suffix(".tmp")
    frame.write_parquet(tmp)
    tmp.replace(path)
    return path
