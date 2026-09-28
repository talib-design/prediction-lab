"""Data audit: is there enough honest data for the question we want to ask?

This is the Phase 1 gate. Before building anything on French flat racing, measure:

* **volume** -- races per year, by country and discipline, estimated from a sample of
  days (a step coprime with 7, so every weekday is sampled, not only Sundays);
* **completeness** -- how often each field the models will need is actually present,
  year by year (the 2015 sample already lacked ``idCheval``);
* **odds timing** -- when the two archived quotes were really taken, relative to the
  off. This decides which prediction horizons can be backtested at all. In the three
  races checked by hand on 2026-09-28 the REFERENCE quote sat ~30 min before the off
  and the last DIRECT quote after it. Three races are an anecdote; this is the census.

Every response is stored in the raw store like any other capture, and a day already
captured is never fetched twice: re-running the audit is free.
"""

from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from predlab.core.clock import minutes_between
from predlab.racing.domain import Race, Runner
from predlab.racing.sources.pmu.client import Endpoint, PmuClient, capture_key, url_for
from predlab.racing.sources.pmu.parser import PmuFormatError, parse_participants, parse_programme
from predlab.racing.store.raw import Capture, RawStore

AUDIT = "audit"

RACE_FIELDS: dict[str, Callable[[Race], bool]] = {
    "distance": lambda r: r.distance_m is not None,
    "handedness": lambda r: r.handedness is not None,
    "going_value": lambda r: r.going is not None and r.going.value is not None,
    "category": lambda r: r.category is not None,
    "age_condition": lambda r: r.age_condition is not None,
    "prize": lambda r: r.prize_eur is not None,
    "weather_forecast": lambda r: r.weather is not None,
    "declared_runners": lambda r: r.declared_runners is not None,
    "finish_order": lambda r: bool(r.finish_order),
}

RUNNER_FIELDS: dict[str, Callable[[Runner], bool]] = {
    "horse_key": lambda x: x.horse_key is not None,
    "draw": lambda x: x.draw is not None,
    "weight": lambda x: x.weight_raw is not None,
    "handicap_value": lambda x: x.handicap_value is not None,
    "jockey": lambda x: bool(x.jockey),
    "trainer": lambda x: bool(x.trainer),
    "sire": lambda x: bool(x.sire),
    "form": lambda x: x.form is not None,
    "odds_reference": lambda x: x.odds_reference is not None,
    "odds_direct": lambda x: x.odds_direct is not None,
    "finish_position": lambda x: x.finish_position is not None,
}


@dataclass
class YearStats:
    sampled_days: int = 0
    days_in_range: int = 0
    races: Counter[str] = field(default_factory=Counter)  # "FRA/PLAT" -> n
    target_races: int = 0
    race_fields: Counter[str] = field(default_factory=Counter)
    sampled_target_races: int = 0
    runners: int = 0
    runner_fields: Counter[str] = field(default_factory=Counter)
    reference_offsets: list[float] = field(default_factory=list)
    direct_offsets: list[float] = field(default_factory=list)
    field_sizes: list[int] = field(default_factory=list)


@dataclass
class AuditResult:
    start: date
    end: date
    step: int
    discipline: str
    country: str
    years: dict[int, YearStats]
    requests: int
    failures: list[str]
    parse_errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "step_days": self.step,
            "target": f"{self.country}/{self.discipline}",
            "requests": self.requests,
            "failures": self.failures,
            "parse_errors": self.parse_errors,
            "years": {},
        }
        for year, s in sorted(self.years.items()):
            scale = s.days_in_range / s.sampled_days if s.sampled_days else 0.0
            out["years"][str(year)] = {
                "sampled_days": s.sampled_days,
                "estimated_target_races": round(s.target_races * scale),
                "estimated_races_by_group": {k: round(v * scale) for k, v in s.races.most_common()},
                "race_field_presence": _rates(s.race_fields, s.target_races),
                "sampled_target_races_with_runners": s.sampled_target_races,
                "median_field_size": statistics.median(s.field_sizes) if s.field_sizes else None,
                "runner_field_presence": _rates(s.runner_fields, s.runners),
                "reference_odds_minutes_from_off": _quantiles(s.reference_offsets),
                "direct_odds_minutes_from_off": _quantiles(s.direct_offsets),
            }
        return out


def _rates(counts: Counter[str], n: int) -> dict[str, float | None]:
    return {k: (round(v / n, 3) if n else None) for k, v in sorted(counts.items())}


def _quantiles(values: list[float]) -> dict[str, float] | None:
    if not values:
        return None
    ordered = sorted(values)

    def q(p: float) -> float:
        return round(ordered[min(len(ordered) - 1, int(p * len(ordered)))], 1)

    return {
        "n": len(ordered),
        "p10": q(0.10),
        "median": q(0.50),
        "p90": q(0.90),
        "share_after_off": round(sum(v > 0 for v in ordered) / len(ordered), 3),
    }


def sample_days(start: date, end: date, step: int) -> list[date]:
    if step < 1:
        raise ValueError("step must be >= 1")
    if step % 7 == 0:
        raise ValueError("a step that is a multiple of 7 samples a single weekday; use e.g. 5")
    days, d = [], start
    while d <= end:
        days.append(d)
        d += timedelta(days=step)
    return days


def _pick(races: list[Race], k: int, salt: str) -> list[Race]:
    """Deterministic pseudo-random choice, so re-runs hit the cache."""
    ranked = sorted(races, key=lambda r: hashlib.sha256(f"{salt}{r.race_id}".encode()).hexdigest())
    return ranked[:k]


def run_audit(
    client: PmuClient,
    store: RawStore,
    *,
    start: date,
    end: date,
    step: int = 5,
    runners_per_day: int = 1,
    country: str = "FRA",
    discipline: str = "PLAT",
    progress: Callable[[str], None] | None = None,
) -> AuditResult:
    days = sample_days(start, end, step)
    index = store.index()
    years: dict[int, YearStats] = defaultdict(YearStats)
    failures: list[str] = []
    parse_errors: list[str] = []
    before = client.requests_made

    for year in {d.year for d in days}:
        lo, hi = max(start, date(year, 1, 1)), min(end, date(year, 12, 31))
        years[year].days_in_range = (hi - lo).days + 1

    def cached_or_fetch(
        endpoint: Endpoint, day: date, meeting: int | None = None, race: int | None = None
    ) -> bytes | None:
        key = capture_key(endpoint, day, meeting, race)
        ok = [c for c in index.get(key, []) if c.ok]
        cap: Capture | None = max(ok, key=lambda c: c.retrieved_at) if ok else None
        if cap is None:
            result = client.fetch(url_for(endpoint, day, meeting, race))
            cap = store.record(result, key=key, endpoint=endpoint, purpose=AUDIT)
            index.setdefault(key, []).append(cap)
            if not cap.ok:
                failures.append(f"{key}: {cap.error}")
                return None
        return store.read(cap)

    for i, day in enumerate(days):
        if progress and i % 20 == 0:
            progress(f"{i}/{len(days)} days, {client.requests_made - before} requests")
        stats = years[day.year]
        body = cached_or_fetch(Endpoint.PROGRAMME, day)
        if body is None:
            continue
        try:
            races = parse_programme(body)
        except PmuFormatError as exc:
            parse_errors.append(f"programme {day}: {exc}")
            continue
        stats.sampled_days += 1
        for r in races:
            stats.races[f"{'FRA' if r.country_code == 'FRA' else 'other'}/{r.discipline}"] += 1
        targets = [r for r in races if r.country_code == country and r.discipline == discipline]
        stats.target_races += len(targets)
        for r in targets:
            for name, present in RACE_FIELDS.items():
                stats.race_fields[name] += int(present(r))

        for race in _pick([r for r in targets if r.is_final], runners_per_day, day.isoformat()):
            body = cached_or_fetch(
                Endpoint.PARTICIPANTS, day, race.meeting_number, race.race_number
            )
            if body is None:
                continue
            try:
                runners = parse_participants(body, race.race_id)
            except PmuFormatError as exc:
                parse_errors.append(f"participants {race.race_id}: {exc}")
                continue
            stats.sampled_target_races += 1
            starters = [x for x in runners if x.is_runner]
            stats.field_sizes.append(len(starters))
            for x in starters:
                stats.runners += 1
                for name, present in RUNNER_FIELDS.items():
                    stats.runner_fields[name] += int(present(x))
                if x.odds_reference:
                    stats.reference_offsets.append(
                        minutes_between(race.off_time, x.odds_reference.reported_at)
                    )
                if x.odds_direct:
                    stats.direct_offsets.append(
                        minutes_between(race.off_time, x.odds_direct.reported_at)
                    )

    return AuditResult(
        start=start,
        end=end,
        step=step,
        discipline=discipline,
        country=country,
        years=dict(years),
        requests=client.requests_made - before,
        failures=failures,
        parse_errors=parse_errors,
    )


def render_markdown(result: AuditResult, generated_at: datetime) -> str:
    d = result.to_dict()
    lines = [
        f"# Audit des données — {d['target']}",
        "",
        f"Généré le {generated_at.isoformat(timespec='seconds')}. Période {d['start']} → {d['end']}, "
        f"un jour sur {d['step_days']}. Requêtes réseau : {d['requests']}. "
        f"Échecs : {len(d['failures'])}. Erreurs de parsing : {len(d['parse_errors'])}.",
        "",
        "Les volumes sont **estimés** à partir des jours échantillonnés. Les écarts de cotes sont en "
        "minutes par rapport au départ programmé (négatif = avant le départ).",
        "",
        "## Volume et cotes par année",
        "",
        "| Année | Jours | Courses cibles (estim.) | Partants médians | Réf. : médiane (min) | Réf. après départ | Direct : médiane (min) | Direct après départ |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for year, y in d["years"].items():
        ref, direct = (
            y["reference_odds_minutes_from_off"] or {},
            y["direct_odds_minutes_from_off"] or {},
        )
        lines.append(
            f"| {year} | {y['sampled_days']} | {y['estimated_target_races']} | "
            f"{y['median_field_size'] if y['median_field_size'] is not None else '—'} | "
            f"{ref.get('median', '—')} | {ref.get('share_after_off', '—')} | "
            f"{direct.get('median', '—')} | {direct.get('share_after_off', '—')} |"
        )
    lines += ["", "## Complétude des champs (part des partants échantillonnés)", ""]
    names = list(RUNNER_FIELDS)
    lines += ["| Année | " + " | ".join(names) + " |", "|---|" + "---:|" * len(names)]
    for year, y in d["years"].items():
        rates = y["runner_field_presence"]
        lines.append(f"| {year} | " + " | ".join(str(rates.get(n, "—")) for n in names) + " |")
    lines += ["", "## Complétude des champs de course", ""]
    names = list(RACE_FIELDS)
    lines += ["| Année | " + " | ".join(names) + " |", "|---|" + "---:|" * len(names)]
    for year, y in d["years"].items():
        rates = y["race_field_presence"]
        lines.append(f"| {year} | " + " | ".join(str(rates.get(n, "—")) for n in names) + " |")
    if d["failures"] or d["parse_errors"]:
        lines += ["", "## Problèmes", ""]
        lines += [f"- {x}" for x in (d["failures"] + d["parse_errors"])[:50]]
    lines.append("")
    return "\n".join(lines)


def write_report(result: AuditResult, directory: Path, generated_at: datetime) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    stem = f"audit_{result.start.isoformat()}_{result.end.isoformat()}"
    md, js = directory / f"{stem}.md", directory / f"{stem}.json"
    md.write_text(render_markdown(result, generated_at), encoding="utf-8")
    js.write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return md, js
