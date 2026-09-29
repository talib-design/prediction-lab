"""What a model may see about a race, and what only the engine may see.

The lottery engine prevented leakage by slicing arrays before the target date. Races
need a finer rule -- several a day, results known at a precise moment -- so the
separation is made in the *types*:

* :class:`RaceCard` is everything knowable at ``prediction_time``: the starters, their
  draw, weight, jockey, trainer, and the latest odds quote whose own timestamp is not
  later than ``prediction_time``. It has **no result field**.
* :class:`RaceOutcome` holds the finishing positions. Models never receive it.
* :class:`RaceEvent` pairs the two with ``known_at``: the moment the result may be
  used as history. v1 rule, deliberately conservative: the start of the next Paris
  day. Same-day earlier results are therefore never used.

Loading from the database only uses odds quotes with ``reported_at <= prediction_time``
(the PMU's own timestamp). The last "direct" quote -- which the audit showed is taken
after the off -- is thus excluded mechanically at any pre-race horizon.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from predlab.core.clock import paris_midnight


@dataclass(frozen=True, slots=True)
class Starter:
    number: int
    horse_id: str | None
    jockey: str | None
    trainer: str | None
    draw: int | None
    weight_raw: int | None
    age: int | None
    odds: float | None
    odds_reported_at: datetime | None


MIN_OVERROUND = 1.05
MAX_OVERROUND = 1.60


@dataclass(frozen=True, slots=True)
class RaceCard:
    race_id: str
    day: date
    off_time: datetime
    prediction_time: datetime
    venue_code: str
    distance_m: int | None
    going_value: float | None
    category: str | None
    starters: tuple[Starter, ...]

    @property
    def n(self) -> int:
        return len(self.starters)

    @property
    def market_complete(self) -> bool:
        return all(s.odds is not None and s.odds > 1.0 for s in self.starters)

    @property
    def overround(self) -> float | None:
        """Sum of 1/odds. A formed PMU win pool sits near 1.19 (it returns ~84 %)."""
        if not self.market_complete:
            return None
        return float(sum(1.0 / s.odds for s in self.starters))  # type: ignore[operator]

    @property
    def market_coherent(self) -> bool:
        """Quotes that describe one market (docs/METHODOLOGY.md §9, rule of 2026-09-29).

        Below 1.05 the quotes cannot all be from a formed pool -- measured on 2025-2026
        flat races: 1.4 % of them at T-25, typically REFERENCE quotes taken while the
        pool was still thin. Every starter then looks like "value"; no bet is imagined.
        """
        o = self.overround
        return o is not None and MIN_OVERROUND <= o <= MAX_OVERROUND


@dataclass(frozen=True, slots=True)
class RaceOutcome:
    race_id: str
    positions: dict[int, int | None]  # starter number -> finishing position (None: unplaced/DQ)

    @property
    def winners(self) -> tuple[int, ...]:
        return tuple(sorted(n for n, p in self.positions.items() if p == 1))


@dataclass(frozen=True, slots=True)
class RaceEvent:
    card: RaceCard
    outcome: RaceOutcome
    known_at: datetime

    def winner_indices(self) -> list[int]:
        winners = set(self.outcome.winners)
        return [i for i, s in enumerate(self.card.starters) if s.number in winners]


def result_known_at(day: date) -> datetime:
    """v1 rule: a result becomes usable history at the next Paris midnight."""
    return paris_midnight(day + timedelta(days=1))


def fingerprint(events: Iterable[RaceEvent]) -> str:
    """Hash of exactly what a run was computed on: races, starters, odds, winners."""
    h = hashlib.sha256()
    for e in events:
        h.update(
            json.dumps(
                [
                    e.card.race_id,
                    e.card.prediction_time.isoformat(),
                    [[s.number, s.horse_id, s.odds] for s in e.card.starters],
                    list(e.outcome.winners),
                ],
                separators=(",", ":"),
            ).encode()
        )
    return h.hexdigest()


def _ts(ms: int | None) -> datetime | None:
    return None if ms is None else datetime.fromtimestamp(ms / 1000, UTC)


def load_events(
    db_path: Path,
    *,
    horizon_minutes: float = 25.0,
    country: str = "FRA",
    discipline: str = "PLAT",
) -> list[RaceEvent]:
    """Finished races with at least two starters and a winner, sorted by off time.

    Timestamps leave DuckDB as epoch milliseconds: returning timezone-aware values
    would require ``pytz``, and integers cannot be misread.
    """
    import duckdb

    con = duckdb.connect(str(db_path), read_only=True)
    try:
        races = con.execute(
            """
            SELECT race_id, day, epoch_ms(off_time), venue_code, distance_m, going_value, category
            FROM races
            WHERE is_final AND country_code = ? AND discipline = ?
            """,
            [country, discipline],
        ).fetchall()
        runners = con.execute(
            """
            SELECT u.race_id, u.number, u.horse_id, u.jockey, u.trainer, u.draw, u.weight_raw,
                   u.age, u.finish_position, u.status
            FROM runners u JOIN races r USING (race_id)
            WHERE r.is_final AND r.country_code = ? AND r.discipline = ?
            """,
            [country, discipline],
        ).fetchall()
        odds = con.execute(
            """
            SELECT o.race_id, o.number,
                   arg_max(o.odds, o.reported_at) AS odds,
                   epoch_ms(max(o.reported_at)) AS reported_ms
            FROM odds o JOIN races r USING (race_id)
            WHERE r.is_final AND r.country_code = ? AND r.discipline = ?
              AND o.reported_at <= r.off_time - to_minutes(CAST(? AS BIGINT))
            GROUP BY o.race_id, o.number
            """,
            [country, discipline, round(horizon_minutes)],
        ).fetchall()
    finally:
        con.close()

    quote = {(r[0], r[1]): (r[2], r[3]) for r in odds}
    by_race: dict[str, list[tuple]] = {}
    for row in runners:
        by_race.setdefault(row[0], []).append(row)

    events: list[RaceEvent] = []
    horizon = timedelta(minutes=horizon_minutes)
    for race_id, day, off_ms, venue, distance, going, category in races:
        rows = sorted(
            (r for r in by_race.get(race_id, []) if r[9] == "PARTANT"), key=lambda r: r[1]
        )
        if len(rows) < 2:
            continue
        off = datetime.fromtimestamp(off_ms / 1000, UTC)
        starters = []
        for _, number, horse, jockey, trainer, draw, weight, age, _pos, _st in rows:
            q = quote.get((race_id, number))
            starters.append(
                Starter(
                    number=number,
                    horse_id=horse,
                    jockey=jockey,
                    trainer=trainer,
                    draw=draw,
                    weight_raw=weight,
                    age=age,
                    odds=q[0] if q else None,
                    odds_reported_at=_ts(q[1]) if q else None,
                )
            )
        outcome = RaceOutcome(race_id, {r[1]: r[8] for r in rows})
        if not outcome.winners:
            continue
        card = RaceCard(
            race_id=race_id,
            day=day,
            off_time=off,
            prediction_time=off - horizon,
            venue_code=venue,
            distance_m=distance,
            going_value=going,
            category=category,
            starters=tuple(starters),
        )
        events.append(RaceEvent(card, outcome, result_known_at(day)))
    events.sort(key=lambda e: (e.card.prediction_time, e.card.race_id))
    return events
