"""Read-only HTTP API for the dashboard.

The interface never touches data files: it asks this API. Three sources, each used for
what it is good at:

* the **raw store** for anything about a given day's races -- it is always current
  (the collector writes to it every 5 minutes), and it holds every odds snapshot;
* the **DuckDB database** for history and aggregates (horse careers, jockey and
  trainer tallies) -- rebuilt nightly;
* the **reports** in ``data/runs/`` for model performance and simulations.

Everything here reads; nothing writes, bets, or calls the PMU.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from predlab import __version__
from predlab.core.clock import PARIS, minutes_between, paris_day, utcnow
from predlab.core.hashing import AppendOnlyLedger, LedgerCorruptionError
from predlab.core.paths import Paths, default_paths
from predlab.core.probability import implied_probabilities
from predlab.racing.carnet import entries as carnet_entries
from predlab.racing.carnet import summarise_entries
from predlab.racing.domain import Race, Runner
from predlab.racing.orders import places_paid, top_k_probabilities
from predlab.racing.report import discipline_label, latest_alpha
from predlab.racing.sources.pmu.client import Endpoint, capture_key
from predlab.racing.sources.pmu.parser import (
    PmuFormatError,
    parse_dividends,
    parse_participants,
    parse_programme_detailed,
)
from predlab.racing.store.raw import Capture, RawStore
from predlab.registry.hypotheses import HypothesisRegistry

TARGETS = ("PLAT", "ATTELE", "MONTE")
SHOWN_BETS = ("SIMPLE_GAGNANT", "SIMPLE_PLACE", "COUPLE_GAGNANT", "TRIO", "TIERCE", "QUINTE_PLUS")
WEB_DIST = Path(__file__).resolve().parents[3] / "web" / "dist"


# ------------------------------------------------------------------------ caching


@dataclass
class IndexCache:
    """Manifest index, rebuilt only when a manifest file changed size."""

    store: RawStore
    signature: tuple[tuple[str, int], ...] = ()
    index: dict[str, list[Capture]] = field(default_factory=dict)

    def get(self) -> dict[str, list[Capture]]:
        files = (
            sorted(self.store.manifests.glob("*.jsonl")) if self.store.manifests.exists() else []
        )
        sig = tuple((f.name, f.stat().st_size) for f in files)
        if sig != self.signature:
            self.index = self.store.index()
            self.signature = sig
        return self.index


@lru_cache(maxsize=256)
def _read_blob(root: str, blob: str) -> bytes:
    import gzip

    return gzip.decompress((Path(root) / blob).read_bytes())


def _latest_ok(captures: list[Capture]) -> Capture | None:
    ok = [c for c in captures if c.ok]
    return max(ok, key=lambda c: c.retrieved_at) if ok else None


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


def _local(dt: datetime) -> str:
    return dt.astimezone(PARIS).strftime("%H:%M")


# ---------------------------------------------------------------------- app state


class Lab:
    def __init__(self, paths: Paths) -> None:
        self.paths = paths
        self.store = RawStore(paths.raw_pmu)
        self.cache = IndexCache(self.store)

    def read(self, cap: Capture) -> bytes:
        if not cap.blob:
            raise FileNotFoundError(cap.key)
        return _read_blob(str(self.store.root), cap.blob)

    def programme(self, day: date) -> tuple[list[Race], Capture | None]:
        cap = _latest_ok(self.cache.get().get(capture_key(Endpoint.PROGRAMME, day), []))
        if cap is None:
            return [], None
        try:
            return parse_programme_detailed(self.read(cap)).races, cap
        except PmuFormatError:
            return [], cap

    def db(self) -> Any | None:
        if not self.paths.database.exists():
            return None
        import duckdb

        return duckdb.connect(str(self.paths.database), read_only=True)


def _race_summary(race: Race, index: dict[str, list[Capture]]) -> dict[str, Any]:
    key = capture_key(Endpoint.PARTICIPANTS, race.day, race.meeting_number, race.race_number)
    snaps = [c for c in index.get(key, []) if c.ok and c.retrieved_at < race.off_time]
    return {
        "race_id": race.race_id,
        "day": race.day.isoformat(),
        "rc": f"R{race.meeting_number}C{race.race_number}",
        "meeting": race.meeting_number,
        "number": race.race_number,
        "off_time": _iso(race.off_time),
        "off_local": _local(race.off_time),
        "venue": race.venue_name or race.venue_code,
        "discipline": race.discipline,
        "discipline_label": discipline_label(race.discipline),
        "name": race.name,
        "distance_m": race.distance_m,
        "category": race.category,
        "declared_runners": race.declared_runners,
        "status": race.status,
        "status_category": race.status_category,
        "is_final": race.is_final,
        "has_quinte": race.has_quinte,
        "going": race.going.label if race.going else None,
        "going_value": race.going.value if race.going else None,
        "snapshots": len(snaps),
    }


def _alpha_for(paths: Paths, discipline: str) -> float | None:
    return latest_alpha(paths.runs, discipline)


# ---------------------------------------------------------------------------- app


def create_app(paths: Paths | None = None) -> FastAPI:
    lab = Lab(paths or default_paths())
    app = FastAPI(title="Prediction Lab", version=__version__, docs_url="/api/docs")

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "version": __version__, "now": _iso(utcnow())}

    @app.get("/api/races")
    def races(day: str | None = None) -> dict[str, Any]:
        d = date.fromisoformat(day) if day else paris_day(utcnow())
        items, cap = lab.programme(d)
        index = lab.cache.get()
        targets = [r for r in items if r.country_code == "FRA" and r.discipline in TARGETS]
        return {
            "day": d.isoformat(),
            "programme_retrieved_at": _iso(cap.retrieved_at) if cap else None,
            "races": [_race_summary(r, index) for r in sorted(targets, key=lambda r: r.off_time)],
            "other_races": len(items) - len(targets),
        }

    @app.get("/api/races/{day}/{rc}")
    def race_detail(day: str, rc: str) -> dict[str, Any]:
        d = date.fromisoformat(day)
        items, _ = lab.programme(d)
        race = next((r for r in items if f"R{r.meeting_number}C{r.race_number}" == rc), None)
        if race is None:
            raise HTTPException(404, f"course {day}/{rc} introuvable")
        index = lab.cache.get()
        key = capture_key(Endpoint.PARTICIPANTS, race.day, race.meeting_number, race.race_number)
        caps = sorted((c for c in index.get(key, []) if c.ok), key=lambda c: c.retrieved_at)
        runners: list[Runner] = []
        series: dict[int, dict[str, tuple[str, float]]] = defaultdict(dict)
        for cap in caps:
            try:
                parsed = parse_participants(lab.read(cap), race.race_id)
            except PmuFormatError:
                continue
            runners = parsed
            for x in parsed:
                for q in (x.odds_reference, x.odds_direct):
                    if q is not None:
                        series[x.number][q.reported_at.isoformat()] = (q.kind, q.odds)
        starters = [x for x in runners if x.is_runner]

        # Market: latest quote per starter quoted before the off.
        latest: dict[int, tuple[datetime, float]] = {}
        for number, points in series.items():
            for stamp, (_, odds) in points.items():
                t = datetime.fromisoformat(stamp)
                if t < race.off_time and (number not in latest or t > latest[number][0]):
                    latest[number] = (t, odds)
        market: dict[int, float] = {}
        calibrated: dict[int, float] = {}
        place: dict[int, float] = {}
        alpha = _alpha_for(lab.paths, race.discipline)
        if starters and all(x.number in latest and latest[x.number][1] > 1 for x in starters):
            q = implied_probabilities(np.array([latest[x.number][1] for x in starters]))
            market = {x.number: float(p) for x, p in zip(starters, q, strict=True)}
            base = q
            if alpha is not None:
                base = np.power(q, alpha)
                base = base / base.sum()
                calibrated = {x.number: float(p) for x, p in zip(starters, base, strict=True)}
            k = places_paid(len(starters))
            place = {
                x.number: float(p)
                for x, p in zip(starters, top_k_probabilities(base, k), strict=True)
            }
        market_as_of = max((t for t, _ in latest.values()), default=None)

        history = _histories(lab, race, runners)
        dividends: list[dict[str, Any]] = []
        div_cap = _latest_ok(
            index.get(
                capture_key(Endpoint.RAPPORTS, race.day, race.meeting_number, race.race_number), []
            )
        )
        if div_cap is not None:
            try:
                for dv in parse_dividends(lab.read(div_cap), race.race_id):
                    if dv.bet_type in SHOWN_BETS:
                        dividends.append(
                            {
                                "bet_type": dv.bet_type,
                                "label": dv.label,
                                "combination": "-".join(dv.combination),
                                "per_euro": dv.per_euro,
                                "base_stake": dv.base_stake,
                                "refunded": dv.refunded,
                            }
                        )
            except PmuFormatError:
                pass

        rows = []
        for x in runners:
            pts = sorted(series.get(x.number, {}).items())
            rows.append(
                {
                    "number": x.number,
                    "name": x.name,
                    "horse_id": x.identity_key,
                    "status": x.status,
                    "age": x.age,
                    "sex": x.sex,
                    "jockey": x.jockey,
                    "trainer": x.trainer,
                    "draw": x.draw,
                    "weight_kg": x.weight_kg,
                    "handicap_distance": x.handicap_distance,
                    "shoeing": x.shoeing,
                    "odds": latest.get(x.number, (None, None))[1],
                    "market_p": market.get(x.number),
                    "calibrated_p": calibrated.get(x.number),
                    "place_p": place.get(x.number),
                    "finish_position": x.finish_position if race.is_final else None,
                    "odds_series": [{"t": t, "kind": kind, "odds": o} for t, (kind, o) in pts],
                    "history": history.get("horses", {}).get(x.identity_key or ""),
                    "jockey_stats": history.get("jockeys", {}).get(x.jockey or ""),
                    "trainer_stats": history.get("trainers", {}).get(x.trainer or ""),
                }
            )
        rows.sort(key=lambda r: (r["status"] != "PARTANT", -(r["market_p"] or 0), r["number"]))
        return {
            "race": _race_summary(race, index),
            "conditions": {
                "handedness": race.handedness,
                "age_condition": race.age_condition,
                "prize_eur": race.prize_eur,
                "weather": race.weather.model_dump(mode="json") if race.weather else None,
            },
            "market_as_of": _iso(market_as_of),
            "minutes_before_off": round(minutes_between(market_as_of, race.off_time), 1)
            if market_as_of
            else None,
            "calibration_alpha": alpha,
            "finish_order": race.finish_order,
            "runners": rows,
            "dividends": dividends,
            "snapshots": len([c for c in caps if c.retrieved_at < race.off_time]),
            "carnet": _carnet_entry(lab, race.race_id),
        }

    @app.get("/api/horses/{horse_id}")
    def horse(horse_id: str) -> dict[str, Any]:
        con = lab.db()
        if con is None:
            raise HTTPException(503, "base absente : lancez `predlab racing build`")
        try:
            info = con.execute(
                "SELECT horse_id, name, sire, dam, dam_sire, breed, birth_year, n_races FROM horses WHERE horse_id = ?",
                [horse_id],
            ).fetchone()
            if info is None:
                raise HTTPException(404, "cheval inconnu de la base")
            runs = con.execute(
                """
                SELECT r.race_id, CAST(r.day AS VARCHAR), r.venue_name, r.discipline, r.distance_m,
                       r.going_label, u.number, u.finish_position, u.status, u.jockey, u.trainer,
                       u.draw, u.weight_raw, r.declared_runners
                FROM runners u JOIN races r USING (race_id)
                WHERE u.horse_id = ? ORDER BY r.off_time DESC
                """,
                [horse_id],
            ).fetchall()
        finally:
            con.close()
        keys = ["horse_id", "name", "sire", "dam", "dam_sire", "breed", "birth_year", "n_races"]
        return {
            "horse": dict(zip(keys, info, strict=True)),
            "runs": [
                {
                    "race_id": r[0],
                    "day": r[1],
                    "venue": r[2],
                    "discipline": r[3],
                    "distance_m": r[4],
                    "going": r[5],
                    "number": r[6],
                    "position": r[7],
                    "status": r[8],
                    "jockey": r[9],
                    "trainer": r[10],
                    "draw": r[11],
                    "weight_kg": r[12] / 10 if r[12] else None,
                    "field": r[13],
                }
                for r in runs
            ],
        }

    @app.get("/api/reports")
    def reports() -> dict[str, Any]:
        out = []
        for f in sorted(lab.paths.runs.glob("*/report.json")) if lab.paths.runs.exists() else []:
            try:
                rep = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            kind = "simulation" if f.parent.name.startswith("simulation") else "backtest"
            out.append(
                {
                    "id": f.parent.name,
                    "kind": kind,
                    "discipline": rep.get("discipline", "PLAT"),
                    "generated_at": rep.get("generated_at"),
                    "n_eligible": rep.get("n_eligible"),
                }
            )
        out.sort(key=lambda r: r["generated_at"] or "", reverse=True)
        return {"reports": out}

    @app.get("/api/reports/{report_id}")
    def report(report_id: str) -> dict[str, Any]:
        f = lab.paths.runs / report_id / "report.json"
        if "/" in report_id or not f.exists():
            raise HTTPException(404, "rapport introuvable")
        return json.loads(f.read_text(encoding="utf-8"))

    @app.get("/api/status")
    def status() -> dict[str, Any]:
        return _status(lab)

    @app.get("/api/carnet")
    def carnet(day: str | None = None) -> dict[str, Any]:
        ledger = AppendOnlyLedger(lab.paths.carnet)
        try:
            ledger.verify()
            integrity: str | None = None
        except LedgerCorruptionError as exc:
            integrity = str(exc)
        # A broken chain is shown as such; nothing from it is summarised.
        items = [] if integrity else carnet_entries(ledger)
        shown = [e for e in items if day is None or e["day"] == day]
        days = sorted({e["day"] for e in items}, reverse=True)
        return {
            "records": len(ledger),
            "head_hash": ledger.head_hash(),
            "integrity_error": integrity,
            "first_day": days[-1] if days else None,
            "days": days,
            "races": len(items),
            "settled": sum(e["settled"] for e in items),
            "summary": summarise_entries(items),
            "entries": sorted(shown, key=lambda e: e["off_time"], reverse=True),
        }

    @app.get("/api/hypotheses")
    def hypotheses() -> dict[str, Any]:
        reg = HypothesisRegistry(AppendOnlyLedger(lab.paths.hypotheses))
        return {"hypotheses": [h.model_dump(mode="json") for h in reg.current()]}

    if WEB_DIST.exists():
        app.mount("/assets", StaticFiles(directory=WEB_DIST / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str) -> FileResponse:
            if path.startswith("api/"):
                raise HTTPException(404, "route inconnue")
            return FileResponse(WEB_DIST / "index.html")

    return app


# ------------------------------------------------------------------------ helpers


def _histories(lab: Lab, race: Race, runners: list[Runner]) -> dict[str, dict[str, Any]]:
    """What the database knew *before* the race day: careers, jockey and trainer tallies."""
    con = lab.db()
    if con is None or not runners:
        return {}
    horses = [x.identity_key for x in runners if x.identity_key]
    jockeys = [x.jockey for x in runners if x.jockey]
    trainers = [x.trainer for x in runners if x.trainer]
    out: dict[str, dict[str, Any]] = {"horses": {}, "jockeys": {}, "trainers": {}}
    try:
        if horses:
            rows = con.execute(
                """
                SELECT u.horse_id, count(*) AS runs,
                       count(*) FILTER (WHERE u.finish_position = 1) AS wins,
                       count(*) FILTER (WHERE u.finish_position <= 3) AS places,
                       list(coalesce(CAST(u.finish_position AS VARCHAR), '-') ORDER BY r.off_time DESC)[1:5] AS last5,
                       CAST(max(r.day) AS VARCHAR) AS last_day
                FROM runners u JOIN races r USING (race_id)
                WHERE u.horse_id IN (SELECT unnest(?)) AND r.day < ? AND u.status = 'PARTANT'
                GROUP BY u.horse_id
                """,
                [horses, race.day],
            ).fetchall()
            for h, runs, wins, places, last5, last_day in rows:
                out["horses"][h] = {
                    "runs": runs,
                    "wins": wins,
                    "places": places,
                    "last5": last5,
                    "last_day": last_day,
                }
        for label, column, names in (
            ("jockeys", "jockey", jockeys),
            ("trainers", "trainer", trainers),
        ):
            if not names:
                continue
            rows = con.execute(
                f"""
                SELECT u.{column}, count(*), count(*) FILTER (WHERE u.finish_position = 1)
                FROM runners u JOIN races r USING (race_id)
                WHERE u.{column} IN (SELECT unnest(?)) AND r.day < ? AND u.status = 'PARTANT'
                  AND r.discipline = ?
                GROUP BY u.{column}
                """,
                [names, race.day, race.discipline],
            ).fetchall()
            for name, runs, wins in rows:
                out[label][name] = {"runs": runs, "wins": wins}
    finally:
        con.close()
    return out


def _carnet_entry(lab: Lab, race_id: str) -> dict[str, Any] | None:
    try:
        return next(
            (
                e
                for e in carnet_entries(AppendOnlyLedger(lab.paths.carnet))
                if e["race_id"] == race_id
            ),
            None,
        )
    except (KeyError, ValueError, TypeError):
        return None


def _tail(path: Path, n: int = 5) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines()[-n:]


def _status(lab: Lab) -> dict[str, Any]:
    paths = lab.paths
    index = lab.cache.get()
    captures = [c for items in index.values() for c in items]
    last = max((c.retrieved_at for c in captures), default=None)
    today = paris_day(utcnow())
    backfill = []
    from predlab.racing.backfill import DEFAULT_PLAN, parse_plan

    for discipline, start in parse_plan(DEFAULT_PLAN):
        suffix = "" if discipline == "PLAT" else f"_{discipline}"
        f = paths.raw_pmu / f"backfill_done_v2{suffix}.json"
        done = json.loads(f.read_text()) if f.exists() else []
        total = (today - timedelta(days=2) - start).days + 1
        backfill.append(
            {
                "discipline": discipline,
                "label": discipline_label(discipline),
                "start": start.isoformat(),
                "days_done": len(done),
                "days_total": total,
                "oldest_done": min(done) if done else None,
            }
        )
    db: dict[str, Any] = {"exists": paths.database.exists()}
    con = lab.db()
    if con is not None:
        try:
            for table in ("races", "runners", "odds", "dividends", "horses"):
                db[table] = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]  # type: ignore[index]
            db["by_discipline"] = [
                {"discipline": d, "races": n, "with_runners": m}
                for d, n, m in con.execute(
                    """
                    SELECT r.discipline, count(DISTINCT r.race_id), count(DISTINCT u.race_id)
                    FROM races r LEFT JOIN runners u USING (race_id)
                    WHERE r.country_code = 'FRA' AND r.discipline IN ('PLAT', 'ATTELE', 'MONTE')
                    GROUP BY 1 ORDER BY 1
                    """
                ).fetchall()
            ]
        finally:
            con.close()
        db["built_at"] = (
            datetime.fromtimestamp(paths.database.stat().st_mtime).astimezone().isoformat()
        )
    return {
        "now": _iso(utcnow()),
        "captures": len(captures),
        "failed_captures": sum(1 for c in captures if not c.ok),
        "last_capture": _iso(last),
        "minutes_since_last_capture": round(minutes_between(last, utcnow()), 1) if last else None,
        "collect_log": _tail(paths.logs / "collect.log"),
        "backfill_log": _tail(paths.logs / "backfill.out.log"),
        "backfill": backfill,
        "database": db,
    }
