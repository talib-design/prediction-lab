"""Normalized store: typed tables rebuilt from the raw captures, never edited by hand.

``predlab racing build`` re-reads every stored capture and writes:

    data/normalized/races.parquet     one row per race (latest programme capture)
    data/normalized/runners.parquet   one row per runner (latest runners capture)
    data/normalized/odds.parquet      every distinct odds quote ever captured
    data/racing.duckdb                the same, as DuckDB tables, plus ``horses``

The build is a pure function of the raw store: delete the outputs and rebuild, and
you get the same tables. Both outputs contain PMU data and are git-ignored.

Two provenance columns matter for honest evaluation later:

* ``retrieved_at`` on every row -- the ``known_at`` of that fact;
* ``captured_after_off`` on runners -- True when the runner row comes from a capture
  taken after the race started. Backfilled rows are all in that case, and fields such
  as ``form`` (musique), career counts and earnings could in principle include the
  race itself. Measured 2026-09-28: the musique does not (its first result equals
  the finishing position ~10% of the time, i.e. chance, over ~9 400 runners); career
  counts matched pre-race snapshots on 23 runners -- to be confirmed at scale.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import duckdb
import polars as pl

from predlab.racing.sources.pmu.client import Endpoint
from predlab.racing.sources.pmu.parser import (
    PmuFormatError,
    parse_participants,
    parse_programme_detailed,
)
from predlab.racing.store.raw import Capture, RawStore

RACE_SCHEMA: dict[str, Any] = {
    "race_id": pl.Utf8,
    "day": pl.Date,
    "meeting_number": pl.Int32,
    "race_number": pl.Int32,
    "off_time": pl.Datetime("us", "UTC"),
    "country_code": pl.Utf8,
    "venue_code": pl.Utf8,
    "venue_name": pl.Utf8,
    "name": pl.Utf8,
    "discipline": pl.Utf8,
    "specialty": pl.Utf8,
    "category": pl.Utf8,
    "age_condition": pl.Utf8,
    "sex_condition": pl.Utf8,
    "distance_m": pl.Int32,
    "handedness": pl.Utf8,
    "declared_runners": pl.Int32,
    "prize_eur": pl.Int64,
    "status": pl.Utf8,
    "status_category": pl.Utf8,
    "going_value": pl.Float64,
    "going_label": pl.Utf8,
    "weather_issued_at": pl.Datetime("us", "UTC"),
    "temperature_c": pl.Float64,
    "wind_force": pl.Float64,
    "wind_direction": pl.Utf8,
    "sky": pl.Utf8,
    "is_final": pl.Boolean,
    "finish_order": pl.Utf8,
    "retrieved_at": pl.Datetime("us", "UTC"),
}

RUNNER_SCHEMA: dict[str, Any] = {
    "race_id": pl.Utf8,
    "number": pl.Int32,
    "name": pl.Utf8,
    "horse_id": pl.Utf8,
    "horse_key_published": pl.Boolean,
    "status": pl.Utf8,
    "age": pl.Int32,
    "sex": pl.Utf8,
    "breed": pl.Utf8,
    "draw": pl.Int32,
    "weight_raw": pl.Int32,
    "handicap_value": pl.Float64,
    "jockey": pl.Utf8,
    "jockey_changed": pl.Boolean,
    "trainer": pl.Utf8,
    "owner": pl.Utf8,
    "sire": pl.Utf8,
    "dam": pl.Utf8,
    "dam_sire": pl.Utf8,
    "blinkers": pl.Utf8,
    "form": pl.Utf8,
    "career_starts": pl.Int32,
    "career_wins": pl.Int32,
    "career_places": pl.Int32,
    "earnings_raw": pl.Int64,
    "finish_position": pl.Int32,
    "retrieved_at": pl.Datetime("us", "UTC"),
}

ODDS_SCHEMA: dict[str, Any] = {
    "race_id": pl.Utf8,
    "number": pl.Int32,
    "kind": pl.Utf8,
    "odds": pl.Float64,
    "reported_at": pl.Datetime("us", "UTC"),
    "favourite": pl.Boolean,
    "retrieved_at": pl.Datetime("us", "UTC"),
}


@dataclass
class BuildReport:
    races: int = 0
    runners: int = 0
    odds: int = 0
    horses: int = 0
    errors: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"{self.races} courses, {self.runners} partants, {self.odds} cotes, "
            f"{self.horses} chevaux ; {len(self.errors)} erreur(s) de parsing"
        )


def _race_id_from_key(key: str) -> str:
    """``participants/2026-09-28/R2C1`` -> ``2026-09-28/R2C1``."""
    return key.split("/", 1)[1]


def _latest(captures: list[Capture]) -> Capture:
    return max(captures, key=lambda c: c.retrieved_at)


def build(store: RawStore, out_dir: Path, db_path: Path) -> BuildReport:
    report = BuildReport()
    ok = [c for c in store.captures() if c.ok]
    programmes: dict[str, list[Capture]] = {}
    participants: dict[str, list[Capture]] = {}
    for c in ok:
        if c.endpoint == Endpoint.PROGRAMME:
            programmes.setdefault(c.key, []).append(c)
        elif c.endpoint == Endpoint.PARTICIPANTS:
            participants.setdefault(c.key, []).append(c)

    race_rows: list[dict[str, Any]] = []
    for key in sorted(programmes):
        cap = _latest(programmes[key])
        try:
            parsed = parse_programme_detailed(store.read(cap))
        except PmuFormatError as exc:
            report.errors.append(f"{key}: {exc}")
            continue
        report.errors.extend(f"{key}: {e}" for e in parsed.errors)
        for r in parsed.races:
            race_rows.append(
                {
                    "race_id": r.race_id,
                    "day": r.day,
                    "meeting_number": r.meeting_number,
                    "race_number": r.race_number,
                    "off_time": r.off_time,
                    "country_code": r.country_code,
                    "venue_code": r.venue_code,
                    "venue_name": r.venue_name,
                    "name": r.name,
                    "discipline": r.discipline,
                    "specialty": r.specialty,
                    "category": r.category,
                    "age_condition": r.age_condition,
                    "sex_condition": r.sex_condition,
                    "distance_m": r.distance_m,
                    "handedness": r.handedness,
                    "declared_runners": r.declared_runners,
                    "prize_eur": r.prize_eur,
                    "status": r.status,
                    "status_category": r.status_category,
                    "going_value": r.going.value if r.going else None,
                    "going_label": r.going.label if r.going else None,
                    "weather_issued_at": r.weather.issued_at if r.weather else None,
                    "temperature_c": r.weather.temperature_c if r.weather else None,
                    "wind_force": r.weather.wind_force if r.weather else None,
                    "wind_direction": r.weather.wind_direction if r.weather else None,
                    "sky": r.weather.sky if r.weather else None,
                    "is_final": r.is_final,
                    "finish_order": json.dumps(r.finish_order) if r.finish_order else None,
                    "retrieved_at": cap.retrieved_at,
                }
            )

    runner_rows: list[dict[str, Any]] = []
    odds_seen: dict[tuple[str, int, str, Any], dict[str, Any]] = {}
    for key in sorted(participants):
        race_id = _race_id_from_key(key)
        caps = sorted(participants[key], key=lambda c: c.retrieved_at)
        for cap in caps:
            try:
                runners = parse_participants(store.read(cap), race_id)
            except PmuFormatError as exc:
                report.errors.append(f"{key}@{cap.retrieved_at.isoformat()}: {exc}")
                continue
            for x in runners:
                for quote in (x.odds_reference, x.odds_direct):
                    if quote is None:
                        continue
                    ident = (race_id, x.number, quote.kind, quote.reported_at)
                    # First capture that saw a quote is when we knew it.
                    odds_seen.setdefault(
                        ident,
                        {
                            "race_id": race_id,
                            "number": x.number,
                            "kind": quote.kind,
                            "odds": quote.odds,
                            "reported_at": quote.reported_at,
                            "favourite": quote.favourite,
                            "retrieved_at": cap.retrieved_at,
                        },
                    )
            if cap is caps[-1]:
                for x in runners:
                    runner_rows.append(
                        {
                            "race_id": race_id,
                            "number": x.number,
                            "name": x.name,
                            "horse_id": x.identity_key,
                            "horse_key_published": x.horse_key is not None,
                            "status": x.status,
                            "age": x.age,
                            "sex": x.sex,
                            "breed": x.breed,
                            "draw": x.draw,
                            "weight_raw": x.weight_raw,
                            "handicap_value": x.handicap_value,
                            "jockey": x.jockey,
                            "jockey_changed": x.jockey_changed,
                            "trainer": x.trainer,
                            "owner": x.owner,
                            "sire": x.sire,
                            "dam": x.dam,
                            "dam_sire": x.dam_sire,
                            "blinkers": x.blinkers,
                            "form": x.form,
                            "career_starts": x.career_starts,
                            "career_wins": x.career_wins,
                            "career_places": x.career_places,
                            "earnings_raw": x.earnings_raw,
                            "finish_position": x.finish_position,
                            "retrieved_at": cap.retrieved_at,
                        }
                    )

    out_dir.mkdir(parents=True, exist_ok=True)
    frames = {
        "races": pl.DataFrame(race_rows, schema=RACE_SCHEMA),
        "runners": pl.DataFrame(runner_rows, schema=RUNNER_SCHEMA),
        "odds": pl.DataFrame(list(odds_seen.values()), schema=ODDS_SCHEMA),
    }
    for name, frame in frames.items():
        frame.write_parquet(out_dir / f"{name}.parquet")

    tmp_db = db_path.with_suffix(".tmp.duckdb")
    tmp_db.unlink(missing_ok=True)
    con = duckdb.connect(str(tmp_db))
    try:
        for name in frames:
            path = (out_dir / f"{name}.parquet").as_posix().replace("'", "''")
            con.execute(f"CREATE TABLE {name} AS SELECT * FROM read_parquet('{path}')")
        con.execute(
            """
            CREATE TABLE runners_enriched AS
            SELECT u.*, r.day, r.off_time, r.country_code, r.discipline,
                   u.retrieved_at >= r.off_time AS captured_after_off
            FROM runners u LEFT JOIN races r USING (race_id)
            """
        )
        con.execute(
            """
            CREATE TABLE horses AS
            SELECT horse_id,
                   any_value(name) AS name,
                   any_value(sire) AS sire,
                   any_value(dam) AS dam,
                   any_value(dam_sire) AS dam_sire,
                   any_value(breed) AS breed,
                   mode(year(day) - age) AS birth_year,
                   min(day) AS first_seen,
                   max(day) AS last_seen,
                   count(*) AS n_races
            FROM runners_enriched
            WHERE horse_id IS NOT NULL
            GROUP BY horse_id
            """
        )
        report.races = con.execute("SELECT count(*) FROM races").fetchone()[0]  # type: ignore[index]
        report.runners = con.execute("SELECT count(*) FROM runners").fetchone()[0]  # type: ignore[index]
        report.odds = con.execute("SELECT count(*) FROM odds").fetchone()[0]  # type: ignore[index]
        report.horses = con.execute("SELECT count(*) FROM horses").fetchone()[0]  # type: ignore[index]
    finally:
        con.close()
    tmp_db.replace(db_path)
    return report
