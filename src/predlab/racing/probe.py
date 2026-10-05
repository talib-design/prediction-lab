"""Foreign races probe (decision of Chris, 2026-10-05).

The PMU programme already lists the foreign races the PMU takes bets on (≈ 5 500 to 6 200
a year since 2024, more flat races than in France). The project drops them at the
``country_code = 'FRA'`` filter, so nothing is known yet about their runners. Before
any foreign history is fetched, this probe reads a small sample -- runners, official
dividends and past performances of ~100 races spread over countries and disciplines --
and measures what the feed gives on them: form string, weight, draw, jockey, trainer,
pedigree, T-30 reference odds and when they were taken, finishing order, simple-bet
dividends. Nothing is tested and nothing enters a model: it answers "is there enough
to study criteria abroad?".

Same rules as the backfill: one request at a time, ≥ 1 s apart, nothing already
stored is fetched again, raw bodies stay in the git-ignored raw store. Only the
aggregate report (shares of fields present) is written to ``data/lab``.
"""

from __future__ import annotations

import hashlib
import json
import statistics
from collections import defaultdict
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from predlab.racing.sources.pmu.client import Endpoint, PmuClient, capture_key, url_for
from predlab.racing.sources.pmu.parser import (
    PmuFormatError,
    _quote,
    parse_dividends,
    parse_participants,
)
from predlab.racing.store.raw import Capture, RawStore

PROBE = "probe"
SAMPLE_FROM = date(2024, 1, 1)
DISCIPLINES = ("PLAT", "ATTELE", "MONTE")
ENDPOINTS = (Endpoint.PARTICIPANTS, Endpoint.RAPPORTS, Endpoint.PERFORMANCES)

# Runner fields looked at, by discipline family. Names are the feed's own.
COMMON = (
    "musique",
    "driver",
    "entraineur",
    "age",
    "sexe",
    "nomPere",
    "nomMere",
    "nombreCourses",
    "gainsCarriere",
    "oeilleres",
    "ordreArrivee",
)
FLAT = ("handicapPoids", "placeCorde", "handicapValeur")
TROT = ("deferre", "handicapDistance", "reductionKilometrique")


@dataclass(frozen=True)
class Target:
    race_id: str
    day: date
    meeting: int
    race: int
    country: str
    discipline: str
    venue: str
    off_time: datetime


def sample(
    db_path: Path, n: int = 100, *, seed: str = "2026-10-05", until: date | None = None
) -> list[Target]:
    """Finished foreign races since 2024, spread over (country, discipline): one race per
    group in turn, largest groups first, in a fixed pseudo-random order inside each
    group (``seed``), so the same command always draws the same races."""
    import duckdb

    con = duckdb.connect(str(db_path), read_only=True)
    try:
        rows = con.execute(
            """
            SELECT race_id, day, meeting_number, race_number, country_code, discipline,
                   venue_name, epoch_ms(off_time)
            FROM races
            WHERE is_final AND country_code <> 'FRA' AND discipline IN ('PLAT','ATTELE','MONTE')
              AND day >= ? AND day <= ? AND coalesce(status, '') NOT LIKE '%ANNULEE%'
            """,
            [SAMPLE_FROM, until or date.max],
        ).fetchall()
    finally:
        con.close()
    groups: dict[tuple[str, str], list[Target]] = defaultdict(list)
    for rid, day, m, r, cc, disc, venue, off in rows:
        off = datetime.fromtimestamp(off / 1000, UTC)
        groups[(cc, disc)].append(Target(rid, day, int(m), int(r), cc, disc, venue or "", off))

    def rank(t: Target) -> str:
        return hashlib.sha256(f"{seed}|{t.race_id}".encode()).hexdigest()

    queues = [
        sorted(groups[g], key=rank) for g in sorted(groups, key=lambda g: (-len(groups[g]), g))
    ]
    out: list[Target] = []
    while len(out) < n and any(queues):
        for q in queues:
            if q and len(out) < n:
                out.append(q.pop(0))
    return out


def fetch(
    client: PmuClient,
    store: RawStore,
    targets: list[Target],
    progress: Callable[[str], None] | None = None,
) -> int:
    """Runners, dividends and past performances of each target, unless already stored.
    Returns the number of requests made."""
    index = store.index()
    before = client.requests_made
    for i, t in enumerate(targets, 1):
        for ep in ENDPOINTS:
            key = capture_key(ep, t.day, t.meeting, t.race)
            if any(c.ok for c in index.get(key, [])):
                continue
            cap = store.record(
                client.fetch(url_for(ep, t.day, t.meeting, t.race)),
                key=key,
                endpoint=ep,
                purpose=PROBE,
            )
            index.setdefault(key, []).append(cap)
        if progress and i % 10 == 0:
            progress(f"{i}/{len(targets)} courses, {client.requests_made - before} requêtes")
    return client.requests_made - before


# ------------------------------------------------------------------------------ report


def _latest_ok(caps: list[Capture]) -> Capture | None:
    ok = [c for c in caps if c.ok]
    return max(ok, key=lambda c: c.retrieved_at) if ok else None


def _present(p: dict[str, Any], field: str) -> bool:
    if field == "gainsCarriere":
        g = p.get("gainsParticipant")
        return isinstance(g, dict) and g.get("gainsCarriere") is not None
    return p.get(field) not in (None, "")


def _odds(p: dict[str, Any], field: str) -> tuple[float, float] | None:
    """(odds, epoch ms), read exactly as the parser reads a quote."""
    q = _quote(p.get(field))
    return (q.odds, q.reported_at.timestamp() * 1000) if q else None


def _race_facts(store: RawStore, index: dict[str, list[Capture]], t: Target) -> dict[str, Any]:
    facts: dict[str, Any] = {"race_id": t.race_id, "country": t.country, "discipline": t.discipline}
    caps = {
        ep: _latest_ok(index.get(capture_key(ep, t.day, t.meeting, t.race), [])) for ep in ENDPOINTS
    }
    facts["fetched"] = {str(ep): caps[ep] is not None for ep in ENDPOINTS}

    part = caps[Endpoint.PARTICIPANTS]
    if part is not None:
        raw = store.read(part)
        try:
            parse_participants(raw, t.race_id)
            facts["parser_ok"] = True
        except PmuFormatError as exc:
            facts["parser_ok"] = False
            facts["parser_error"] = str(exc)[:200]
        doc = json.loads(raw)
        starters = [p for p in doc.get("participants") or [] if p.get("statut") == "PARTANT"]
        fields = COMMON + (FLAT if t.discipline == "PLAT" else TROT)
        facts["runners"] = len(starters)
        facts["fields"] = {f: sum(_present(p, f) for p in starters) for f in fields}
        ref = [o for p in starters if (o := _odds(p, "dernierRapportReference"))]
        facts["odds_reference"] = len(ref)
        facts["odds_direct"] = sum(bool(_odds(p, "dernierRapportDirect")) for p in starters)
        if ref:
            off_ms = t.off_time.timestamp() * 1000
            facts["reference_minutes_before_off"] = round(
                (off_ms - statistics.median(s for _, s in ref)) / 60000, 1
            )
        if len(ref) == len(starters) and starters:
            facts["overround"] = round(sum(1 / o for o, _ in ref), 3)

    div = caps[Endpoint.RAPPORTS]
    if div is not None:
        try:
            types = sorted({d.bet_type for d in parse_dividends(store.read(div), t.race_id)})
            facts["bet_types"] = types
        except PmuFormatError as exc:
            facts["bet_types"] = []
            facts["dividends_error"] = str(exc)[:200]

    perf = caps[Endpoint.PERFORMANCES]
    if perf is not None:
        doc = json.loads(store.read(perf))
        runs = [len(p.get("coursesCourues") or []) for p in doc.get("participants") or []]
        facts["past_runs"] = runs
    return facts


def _share(num: float, den: float) -> float | None:
    return round(num / den, 3) if den else None


def _summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    with_runners = [r for r in rows if r.get("runners")]
    starters = sum(r["runners"] for r in with_runners)
    fields: dict[str, int] = defaultdict(int)
    for r in with_runners:
        for f, k in r["fields"].items():
            fields[f] += k
    timing = [
        r["reference_minutes_before_off"] for r in rows if "reference_minutes_before_off" in r
    ]
    over = [r["overround"] for r in rows if "overround" in r]
    past = [k for r in rows for k in r.get("past_runs", [])]
    bets = [r.get("bet_types") for r in rows if "bet_types" in r]
    return {
        "races": n,
        "fetched": {
            str(ep): _share(sum(r["fetched"][str(ep)] for r in rows), n) for ep in ENDPOINTS
        },
        "parser_ok": _share(sum(bool(r.get("parser_ok")) for r in rows), n),
        "runners": starters,
        "fields": {f: _share(k, starters) for f, k in sorted(fields.items())},
        "odds_reference": _share(sum(r.get("odds_reference", 0) for r in with_runners), starters),
        "odds_direct": _share(sum(r.get("odds_direct", 0) for r in with_runners), starters),
        "reference_minutes_before_off": statistics.median(timing) if timing else None,
        "overround": statistics.median(over) if over else None,
        "simple_gagnant": _share(sum("SIMPLE_GAGNANT" in (b or []) for b in bets), len(bets)),
        "simple_place": _share(sum("SIMPLE_PLACE" in (b or []) for b in bets), len(bets)),
        "bet_types": sorted({t for b in bets for t in (b or [])}),
        "past_runs_median": statistics.median(past) if past else None,
        "past_runs_any": _share(sum(k > 0 for k in past), len(past)),
    }


def report(store: RawStore, targets: list[Target], now: datetime) -> dict[str, Any]:
    index = store.index()
    rows = [_race_facts(store, index, t) for t in targets]
    by_disc: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_disc[r["discipline"]].append(r)
        by_group[f"{r['country']}:{r['discipline']}"].append(r)
    return {
        "generated_at": now.isoformat(timespec="seconds"),
        "sample_from": SAMPLE_FROM.isoformat(),
        "targets": [
            {**asdict(t), "day": t.day.isoformat(), "off_time": t.off_time.isoformat()}
            for t in targets
        ],
        "overall": _summarise(rows),
        "by_discipline": {d: _summarise(v) for d, v in sorted(by_disc.items())},
        "by_country": {g: _summarise(v) for g, v in sorted(by_group.items())},
        "parser_errors": [
            {"race_id": r["race_id"], "error": r["parser_error"]}
            for r in rows
            if "parser_error" in r
        ],
    }


def write_report(rep: dict[str, Any], lab_dir: Path) -> Path:
    lab_dir.mkdir(parents=True, exist_ok=True)
    path = lab_dir / "probe_foreign.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(path)
    return path
