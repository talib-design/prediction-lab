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

import contextlib
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
from predlab.api.lottery import lottery_router
from predlab.core.clock import PARIS, minutes_between, paris_day, utcnow
from predlab.core.hashing import AppendOnlyLedger, LedgerCorruptionError
from predlab.core.paths import Paths, default_paths
from predlab.core.probability import implied_probabilities
from predlab.racing import strategies as banc_lib
from predlab.racing.backtest import DEFAULT_HORIZON_MINUTES
from predlab.racing.carnet import entries as carnet_entries
from predlab.racing.carnet import summarise_entries
from predlab.racing.domain import Race, Runner
from predlab.racing.features import RACE_FACTORS, history, live_frame
from predlab.racing.marketplus import latest_params
from predlab.racing.marketplus import predict as predict_plus
from predlab.racing.orders import places_paid, top_k_probabilities
from predlab.racing.profile import horse_conditions
from predlab.racing.profile import latest as latest_report
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
        carnet = _carnet_by_race(lab)
        now = utcnow()
        return {
            "day": d.isoformat(),
            "programme_retrieved_at": _iso(cap.retrieved_at) if cap else None,
            "races": [
                {**_race_summary(r, index), "carnet": _carnet_state(r, carnet.get(r.race_id), now)}
                for r in sorted(targets, key=lambda r: r.off_time)
            ],
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
        plus, plus_meta = _model_probabilities(lab, race, starters, latest, market)

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
                    "model_p": plus.get(x.number),
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
            "model": plus_meta,
            "finish_order": race.finish_order,
            "runners": rows,
            "dividends": dividends,
            "snapshots": len([c for c in caps if c.retrieved_at < race.off_time]),
            "carnet": _carnet_entry(lab, race.race_id),
            "banc": _banc_race(lab, race.race_id),
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
            kind = next(
                (
                    k
                    for k in ("simulation", "profile", "model", "replay")
                    if f.parent.name.startswith(k)
                ),
                "backtest",
            )
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
            "entries": [
                {**e, "duel": _duel_of(e)}
                for e in sorted(shown, key=lambda e: e["off_time"], reverse=True)
            ],
        }

    @app.get("/api/carnet/periods")
    def carnet_periods() -> dict[str, Any]:
        """The model against the favourite on the same races: today, this week, this
        month, since the model first played; the days ahead of it in a row."""
        today = paris_day(utcnow())
        duels = _duels(lab)
        days = _duel_days(duels)
        return {
            "today": today.isoformat(),
            "periods": _periods(duels, today),
            "streak": _ahead_streak(days),
            "days": days[-14:],
            "series": _series(lab),
        }

    @app.get("/api/replay")
    def replay(discipline: str = "PLAT", since: str | None = None) -> dict[str, Any]:
        """Historical curve, favourite vs model, on every past race (nightly
        reconstruction). ``ALL`` adds the disciplines up; ``since`` restarts the totals."""
        if discipline not in (*TARGETS, "ALL"):
            raise HTTPException(404, "discipline inconnue")
        reps = {d: latest_report(lab.paths.runs, "replay", d) for d in TARGETS}
        available = [d for d, r in reps.items() if r]
        chosen = [
            r
            for d in (available if discipline == "ALL" else [discipline])
            if (r := reps[d]) is not None
        ]
        if not chosen:
            return {"discipline": discipline, "available": available, "report": None}
        return {
            "discipline": discipline,
            "available": available,
            "report": {
                "generated_at": max(r["generated_at"] for r in chosen),
                "method": chosen[0]["method"],
                "summary": chosen[0]["summary"] if len(chosen) == 1 else None,
                "series": _merge_series([r["series"] for r in chosen], since),
            },
        }

    @app.get("/api/profile")
    def profile(discipline: str = "PLAT") -> dict[str, Any]:
        """Latest winners' profile and Marché+ report of a discipline (nightly)."""
        if discipline not in TARGETS:
            raise HTTPException(404, "discipline inconnue")
        return {
            "discipline": discipline,
            "profile": latest_report(lab.paths.runs, "profile", discipline),
            "model": _model_summary(latest_report(lab.paths.runs, "model", discipline)),
        }

    @app.get("/api/races/{day}/{rc}/profile")
    def race_profile(day: str, rc: str) -> dict[str, Any]:
        """This race's conditions, and each starter's record in those conditions."""
        d = date.fromisoformat(day)
        items, _ = lab.programme(d)
        race = next((r for r in items if f"R{r.meeting_number}C{r.race_number}" == rc), None)
        if race is None:
            raise HTTPException(404, f"course {day}/{rc} introuvable")
        runners = _latest_runners(lab, race)
        hist = _history_or_none(lab, race.discipline)
        conditions: dict[str, str] = {}
        horses: dict[str, Any] = {}
        if hist is not None and runners:
            frame = live_frame(race, runners, {}, hist)
            row = frame.row(0, named=True)
            conditions = {k: row[k] for k in RACE_FACTORS}
            per_horse = horse_conditions(
                hist,
                [x.identity_key for x in runners if x.identity_key],
                race.day,
                {k: conditions[k] for k in ("going_cat", "temp_band", "dist_band")},
            )
            for x, r in zip(runners, frame.iter_rows(named=True), strict=True):
                horses[str(x.number)] = {
                    "name": x.name,
                    "record": per_horse.get(x.identity_key or ""),
                    "levels": {
                        k: r[k]
                        for k in (
                            "draw_band",
                            "rest_band",
                            "age_band",
                            "sex_cat",
                            "weight_band",
                            "recul_band",
                            "shoeing_cat",
                        )
                    },
                }
        return {
            "race_id": race.race_id,
            "discipline": race.discipline,
            "conditions": conditions,
            "horses": horses,
            "profile": latest_report(lab.paths.runs, "profile", race.discipline),
            "model": _model_summary(latest_report(lab.paths.runs, "model", race.discipline)),
        }

    @app.get("/api/banc")
    def banc(discipline: str | None = None) -> dict[str, Any]:
        """The strategy bench: its strategies, their record, its own balance."""
        return _banc(lab, discipline)

    @app.get("/api/hypotheses")
    def hypotheses() -> dict[str, Any]:
        reg = HypothesisRegistry(AppendOnlyLedger(lab.paths.hypotheses))
        return {"hypotheses": [h.model_dump(mode="json") for h in reg.current()]}

    @app.get("/api/lab")
    def lab_view() -> dict[str, Any]:
        """The lab: each criterion test with its pre-registration date and result, and the
        favourites study per discipline."""
        return _lab(lab)

    app.include_router(lottery_router(lab.paths))

    if WEB_DIST.exists():
        app.mount("/assets", StaticFiles(directory=WEB_DIST / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str) -> FileResponse:
            if path.startswith("api/"):
                raise HTTPException(404, "route inconnue")
            return FileResponse(WEB_DIST / "index.html")

    return app


# ------------------------------------------------------------------------ helpers


def _banc_ledger(lab: Lab) -> AppendOnlyLedger:
    return AppendOnlyLedger(lab.paths.banc / "ledger.jsonl")


def _banc(lab: Lab, discipline: str | None) -> dict[str, Any]:
    panel = banc_lib.Panel.load(lab.paths.banc / "panel.json")
    ledger = _banc_ledger(lab)
    per, meta = banc_lib.live_returns(ledger)
    today = paris_day(utcnow()).isoformat()
    rows = []
    for s in panel.strategies:
        if discipline and s["discipline"] != discipline:
            continue
        live = banc_lib.summarise_returns(np.array(per.get(s["id"], []), dtype=float))
        rows.append(
            {
                **s,
                "bet_label": banc_lib.BET_LABEL[s["bet"]],
                "criteria_list": [
                    {"key": k, "label": banc_lib.DIM_LABEL.get(k, k), "level": v}
                    for k, v in sorted(s["criteria"].items())
                ],
                "live": live,
                "pending": meta["pending"].get(s["id"], 0),
                "status": banc_lib.status(s, live),
            }
        )
    days = meta["days"]

    def total(ds: list[dict[str, float]]) -> dict[str, Any]:
        stake = sum(d["stake"] for d in ds)
        back = sum(d["returned"] for d in ds)
        return {
            "tickets": int(sum(d["tickets"] for d in ds)),
            "stake": stake,
            "returned": back,
            "net": back - stake,
            "roi": back / stake - 1 if stake else None,
        }

    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    return {
        "updated_at": panel.updated_at,
        "gauge": panel.gauge,
        "rules": {
            "win_bets": banc_lib.WIN_BETS,
            "kill_bets": banc_lib.KILL_BETS,
            "kill_roi": banc_lib.KILL_ROI,
            "target_roi": banc_lib.TARGET_ROI,
        },
        "totals": {
            "today": total([days[today]] if today in days else []),
            "all": total(list(days.values())),
            "pending": int(sum(meta["pending"].values())),
            "races": meta["races"],
            "first_day": min(days) if days else None,
        },
        "counts": counts,
        "strategies": rows,
    }


def _banc_race(lab: Lab, race_id: str) -> dict[str, Any] | None:
    """What the bench froze on this race, by horse, and what it paid once settled."""
    ledger = _banc_ledger(lab)
    if not ledger.path.exists():
        return None
    freeze = settle = None
    for r in ledger.records():
        if r.get("race_id") != race_id:
            continue
        if r.get("kind") == "freeze":
            freeze = r
        elif r.get("kind") == "settle":
            settle = r
    if freeze is None:
        return None
    panel = {s["id"]: s for s in banc_lib.Panel.load(lab.paths.banc / "panel.json").strategies}
    tickets = []
    for i, (sid, bet, number) in enumerate(freeze["tickets"]):
        s = panel.get(sid, {})
        tickets.append(
            {
                "strategy": sid,
                "label": s.get("label", sid),
                "bet": bet,
                "number": number,
                "returned": settle["returns"][i] if settle else None,
            }
        )
    return {
        "frozen_at": freeze["frozen_at"],
        "settled": settle is not None,
        "tickets": tickets,
        "stake": float(len(tickets)),
        "returned": float(sum(settle["returns"])) if settle else None,
    }


def _history_or_none(lab: Lab, discipline: str) -> Any:
    if not lab.paths.database.exists():
        return None
    try:
        return history(lab.paths.database, discipline)
    except Exception:  # a base being rebuilt, or built by an older version
        return None


def _latest_runners(lab: Lab, race: Race) -> list[Runner]:
    key = capture_key(Endpoint.PARTICIPANTS, race.day, race.meeting_number, race.race_number)
    cap = _latest_ok(lab.cache.get().get(key, []))
    if cap is None:
        return []
    try:
        return [x for x in parse_participants(lab.read(cap), race.race_id) if x.is_runner]
    except PmuFormatError:
        return []


def _model_summary(rep: dict[str, Any] | None) -> dict[str, Any] | None:
    if rep is None:
        return None
    return {
        k: rep.get(k)
        for k in (
            "id",
            "generated_at",
            "races",
            "lambda",
            "market_alpha",
            "coefficients",
            "validation",
            "test",
            "test_bets",
        )
    }


def _model_probabilities(
    lab: Lab,
    race: Race,
    starters: list[Runner],
    latest: dict[int, tuple[datetime, float]],
    market: dict[int, float],
) -> tuple[dict[int, float], dict[str, Any] | None]:
    """Marché+ on the latest pre-off quotes (the carnet keeps its own, frozen at T-25)."""
    if not market:
        return {}, None
    params = latest_params(lab.paths.runs, race.discipline)
    hist = _history_or_none(lab, race.discipline) if params else None
    if params is None or hist is None:
        return {}, None
    try:
        odds = {x.number: latest[x.number][1] for x in starters}
        p = predict_plus(params, live_frame(race, starters, odds, hist))
    except Exception:
        return {}, None
    return (
        {x.number: float(v) for x, v in zip(starters, p, strict=True)},
        {"report": params["report"], "fitted_through": params["fitted_through"]},
    )


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


def _pick_of(strategy: str) -> str:
    from predlab.racing.carnet import PREV, VALUE_RULE

    if PREV in strategy:
        return "ancien"
    if VALUE_RULE in strategy:
        return "valeur"
    return "modèle" if "marche_plus" in strategy else "favori"


def _series(lab: Lab) -> list[dict[str, Any]]:
    """Per strategy of the carnet, its settled results day by day and the running total:
    the chart "is it going up, down or flat?", favourite against model on the same races.
    The side lines (version replaced by a promotion, admitted rule) are counted on those
    same races and appear once they have played."""
    from predlab.racing.carnet import OPTIONAL, STRATEGIES, strategy_label

    per: dict[str, dict[str, dict[str, float]]] = {s: {} for s in (*STRATEGIES, *OPTIONAL)}
    for e in _carnet_by_race(lab).values():
        if not e["settled"]:
            continue
        for bet in ("SG", "SP"):
            # Paired: a race counts for a bet type only if the favourite AND the model
            # played it, so the lines are compared on exactly the same races.
            mine = [t for t in e["tickets"] if t["strategy"].startswith(bet)]
            picks = {_pick_of(t["strategy"]) for t in mine}
            if not {"favori", "modèle"} <= picks:
                continue
            by: dict[str, list[dict[str, Any]]] = {}
            for t in mine:
                by.setdefault(t["strategy"], []).append(t)
            for strategy, ts in by.items():
                day = per.setdefault(strategy, {}).setdefault(
                    e["day"], {"races": 0, "stake": 0.0, "returned": 0.0}
                )
                day["races"] += 1
                day["stake"] += sum(t["stake"] for t in ts)
                day["returned"] += sum(t["returned"] or 0.0 for t in ts)
    out = []
    for strategy in (*STRATEGIES, *OPTIONAL):
        days = per.get(strategy, {})
        if strategy in OPTIONAL and not days:
            continue
        cum, points = 0.0, []
        for d in sorted(days):
            v = days[d]
            net = v["returned"] - v["stake"]
            cum += net
            points.append({"day": d, **v, "net": net, "cum": cum})
        out.append(
            {
                "strategy": strategy,
                "label": strategy_label(strategy),
                "bet": "SG" if strategy.startswith("SG") else "SP",
                "pick": _pick_of(strategy),
                "points": points,
            }
        )
    return out


def _lab(lab: Lab) -> dict[str, Any]:
    from predlab.racing import lab as lab_lib

    reg = HypothesisRegistry(AppendOnlyLedger(lab.paths.hypotheses))
    first: dict[str, str] = {}
    for h in reg.history():
        first.setdefault(h.hypothesis_id, h.created_at.isoformat(timespec="seconds"))
    results = lab_lib.results(lab.paths.lab)
    experiments = []
    for h in reg.current():
        exp = h.experiment or ""
        if ":" not in exp:
            continue
        cid, discipline, *rest = exp.split(":")
        c = lab_lib.BY_ID.get(cid)
        experiments.append(
            {
                "experiment": exp,
                "candidate": cid,
                "label": c.label if c else h.description.split(" (")[0],
                "hypothesis": c.hypothesis if c else h.description,
                "discipline": discipline,
                "source": c.source if c else "study",
                "kind": c.kind if c else "study",
                "fresh_from": c.fresh_from.isoformat() if c and c.fresh_from else None,
                "protocol": rest[0] if rest else "v1",
                "origin": h.origin.value,
                "status": h.status.value,
                "registered_at": first.get(h.hypothesis_id),
                "updated_at": h.created_at.isoformat(timespec="seconds"),
                "conclusion": h.conclusion,
                "waiting": h.forward_result if h.status.value == "TESTING" else None,
                "result": results.get(exp),
            }
        )
    favourites = {}
    for d in TARGETS:
        f = lab.paths.lab / f"favourites_{d}.json"
        if f.exists():
            with contextlib.suppress(OSError, json.JSONDecodeError):
                favourites[d] = json.loads(f.read_text(encoding="utf-8"))
    from predlab.racing.champion import OBJECTIVE

    return {
        "objective": OBJECTIVE,
        "scoreboard": _scoreboard(lab, experiments),
        "experiments": experiments,
        "favourites": favourites,
        "rule": lab_lib.RULE,
        "catalogue": len(lab_lib.CANDIDATES),
    }


def _live_vs_favourite(lab: Lab, discipline: str) -> dict[str, Any]:
    """The carnet, favourite against model on the races where both played (SG + SP)."""
    tot = {"favori": [0.0, 0.0], "modèle": [0.0, 0.0]}
    races, differ, first = 0, 0, None
    for e in _carnet_by_race(lab).values():
        if not e["settled"] or e["discipline"] != discipline:
            continue
        by = {t["strategy"]: t for t in e["tickets"]}
        pairs = [(f"{b} favori", f"{b} top marche_plus") for b in ("SG", "SP")]
        pairs = [(f, m) for f, m in pairs if f in by and m in by]
        if not pairs:
            continue
        races += 1
        first = min(first or e["day"], e["day"])
        if by.get("SG favori", {}).get("numbers") != by.get("SG top marche_plus", {}).get(
            "numbers"
        ):
            differ += 1
        for f, m in pairs:
            for pick, t in (("favori", by[f]), ("modèle", by[m])):
                tot[pick][0] += t["stake"]
                tot[pick][1] += t["returned"] or 0.0

    def roi(pick: str) -> float | None:
        stake, ret = tot[pick]
        return ret / stake - 1 if stake else None

    return {
        "races": races,
        "since": first,
        "races_where_picks_differ": differ,
        "favori": {
            "stake": tot["favori"][0],
            "net": tot["favori"][1] - tot["favori"][0],
            "roi": roi("favori"),
        },
        "modèle": {
            "stake": tot["modèle"][0],
            "net": tot["modèle"][1] - tot["modèle"][0],
            "roi": roi("modèle"),
        },
    }


def _scoreboard(lab: Lab, experiments: list[dict[str, Any]]) -> dict[str, Any]:
    """Per discipline: the champion and its versions, model − favourite live (carnet) and
    on the history (replay), the extended history's coverage, the vault, the tests."""
    from predlab.racing.champion import EXTENDED, Champion, history_coverage, races_since

    out: dict[str, Any] = {}
    for d in TARGETS:
        if not (lab.paths.lab / f"champion_{d}.json").exists():
            continue
        champ = Champion.load(lab.paths.lab, d)
        versions = [
            {k: v for k, v in x.items() if k != "frozen_params"} for x in champ.data["versions"]
        ]
        start = champ.vault_start(EXTENDED)
        replay = latest_report(lab.paths.runs, "replay", d)
        protocol = f"obj{champ.current['version']}"
        mine = [e for e in experiments if e["discipline"] == d and e.get("protocol") == protocol]
        counts: dict[str, int] = {}
        for e in mine:
            counts[e["status"]] = counts.get(e["status"], 0) + 1
        out[d] = {
            "champion": {
                "version": champ.current["version"],
                "origin": champ.current.get("origin"),
                "promoted_at": champ.current.get("promoted_at"),
                "features": len(champ.features),
                "tau": champ.tau,
                "rules": champ.rules,
            },
            "versions": versions,
            "attempts": champ.data.get("attempts", []),
            "coverage": history_coverage(lab.paths.database, d),
            "vault": {
                "start": start.isoformat(),
                "races": races_since(lab.paths.database, d, start),
                "min_races": EXTENDED.vault_min_races,
                "used_until": champ.data.get("vault_used_until"),
            },
            "live": _live_vs_favourite(lab, d),
            "history": (replay or {}).get("summary"),
            "tests": {"protocol": protocol, "total": len(mine), "by_status": counts},
        }
    return out


def _merge_series(groups: list[list[dict[str, Any]]], since: str | None) -> list[dict[str, Any]]:
    """Add day-by-day series of the same (bet, pick) across disciplines; keep the days from
    ``since`` on and recompute the running totals from there."""
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for series in groups:
        for s in series:
            m = merged.setdefault(
                (s["bet"], s["pick"]),
                {**{k: s[k] for k in ("strategy", "label", "bet", "pick")}, "days": {}},
            )
            for p in s["points"]:
                if since and p["day"] < since:
                    continue
                d = m["days"].setdefault(p["day"], {"races": 0, "stake": 0.0, "returned": 0.0})
                d["races"] += p["races"]
                d["stake"] += p["stake"]
                d["returned"] += p["returned"]
    out = []
    for m in merged.values():
        cum, points = 0.0, []
        for day in sorted(m["days"]):
            v = m["days"][day]
            net = v["returned"] - v["stake"]
            cum += net
            points.append({"day": day, **v, "net": round(net, 2), "cum": round(cum, 2)})
        out.append({**{k: m[k] for k in ("strategy", "label", "bet", "pick")}, "points": points})
    return out


def _duel_of(e: dict[str, Any]) -> dict[str, Any] | None:
    """The favourite against the model on one carnet race, or None if they did not both
    play it.

    Paired per bet type, as in the chart: a simple gagnant (or placé) counts only if
    both sides played it, so the two are always compared on exactly the same tickets.
    The side lines (former version, value rule) stay out. ``net`` is None until the race
    is settled; ``win`` says whether the side's simple gagnant paid (None if not paired
    in gagnant, or not settled).
    """
    from predlab.racing.carnet import STRATEGIES as CORE_STRATEGIES

    sides: dict[str, dict[str, Any]] = {
        s: {"numbers": [], "stake": 0.0, "returned": 0.0, "win": None} for s in ("model", "favori")
    }
    paired = differ = False
    for bet in ("SG", "SP"):
        by: dict[str, list[dict[str, Any]]] = {}
        for t in e["tickets"]:
            if t["strategy"] in CORE_STRATEGIES and t["strategy"].startswith(bet):
                by.setdefault(_pick_of(t["strategy"]), []).append(t)
        if not {"favori", "modèle"} <= by.keys():
            continue
        paired = True
        picks = {k: sorted(n for t in ts for n in t.get("numbers") or ()) for k, ts in by.items()}
        differ = differ or picks["favori"] != picks["modèle"]
        for side, pick in (("model", "modèle"), ("favori", "favori")):
            v = sides[side]
            v["numbers"] = v["numbers"] or picks[pick]
            v["stake"] += sum(t["stake"] for t in by[pick])
            v["returned"] += sum(t["returned"] or 0.0 for t in by[pick])
            if bet == "SG" and e["settled"]:
                v["win"] = any((t["returned"] or 0.0) > 0 for t in by[pick])
    if not paired:
        return None
    for v in sides.values():
        v["net"] = v["returned"] - v["stake"] if e["settled"] else None
    return {"differ": differ, **sides}


def _duels(lab: Lab) -> list[dict[str, Any]]:
    """Each race where the favourite and the model both played, with what each side
    staked and got back, oldest first."""
    out = []
    for e in sorted(_carnet_by_race(lab).values(), key=lambda e: e["off_time"]):
        d = _duel_of(e)
        if d is not None:
            out.append({"day": e["day"], "settled": e["settled"], **d})
    return out


def _side(duels: list[dict[str, Any]], side: str) -> dict[str, Any]:
    stake = sum(d[side]["stake"] for d in duels)
    returned = sum(d[side]["returned"] for d in duels)
    return {
        "stake": stake,
        "returned": returned,
        "net": returned - stake,
        "roi": (returned / stake - 1) if stake else None,
    }


def _state(diff: float) -> str:
    """Who came out ahead: to the cent, so that identical choices are never split by a
    rounding error."""
    cents = round(diff * 100)
    return "ahead" if cents > 0 else "behind" if cents < 0 else "same"


def _duel_days(duels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per day with settled duels: the model's net, the favourite's, who was ahead."""
    by_day: dict[str, list[dict[str, Any]]] = {}
    for d in duels:
        if d["settled"]:
            by_day.setdefault(d["day"], []).append(d)
    rows = []
    for day in sorted(by_day):
        items = by_day[day]
        model, favori = _side(items, "model")["net"], _side(items, "favori")["net"]
        rows.append(
            {
                "day": day,
                "races": len(items),
                "differ": sum(d["differ"] for d in items),
                "model_net": model,
                "favori_net": favori,
                "diff": model - favori,
                "state": _state(model - favori),
            }
        )
    return rows


def _ahead_streak(days: list[dict[str, Any]]) -> dict[str, int]:
    """Days in a row the model ended ahead of the favourite.

    A day level with it (most often the same horse everywhere) neither extends nor breaks
    the run; a day behind breaks it. ``current`` ends at the latest settled day, today
    included as it stands.
    """
    best = run = 0
    for d in days:
        if d["state"] == "ahead":
            run += 1
        elif d["state"] == "behind":
            run = 0
        best = max(best, run)
    count = {s: sum(d["state"] == s for d in days) for s in ("ahead", "behind", "same")}
    return {"current": run, "best": best, **count}


def _periods(duels: list[dict[str, Any]], today: date) -> list[dict[str, Any]]:
    """The model and the favourite over the same races, per period. "Depuis le début"
    starts the first day the model played."""
    first = min((date.fromisoformat(d["day"]) for d in duels), default=today)
    spans = [
        ("day", "Aujourd'hui", today),
        ("week", "Cette semaine", today - timedelta(days=today.weekday())),
        ("month", "Ce mois", today.replace(day=1)),
        ("all", "Depuis le début", first),
    ]
    out = []
    for key, label, start in spans:
        chosen = [d for d in duels if start <= date.fromisoformat(d["day"]) <= today]
        settled = [d for d in chosen if d["settled"]]
        pending = [d for d in chosen if not d["settled"]]
        model, favori = _side(settled, "model"), _side(settled, "favori")
        out.append(
            {
                "key": key,
                "label": label,
                "start": start.isoformat(),
                "races": len(settled),
                "differ": sum(d["differ"] for d in settled),
                "model": model,
                "favori": favori,
                "diff": model["net"] - favori["net"],
                "pending": len(pending),
                "pending_stake": sum(d["model"]["stake"] for d in pending),
            }
        )
    return out


def _carnet_by_race(lab: Lab) -> dict[str, dict[str, Any]]:
    try:
        return {e["race_id"]: e for e in carnet_entries(AppendOnlyLedger(lab.paths.carnet))}
    except (KeyError, ValueError, TypeError):
        return {}


def _carnet_state(race: Race, entry: dict[str, Any] | None, now: datetime) -> dict[str, Any]:
    """What the lab did (or will do) on this race, in one line for the day's list.

    upcoming: tickets will be frozen at ``freeze_at``; open: inside the window, the next
    collection pass freezes them; frozen: tickets written, result pending; settled:
    paid at the official dividends; missed: the off passed without tickets;
    cancelled: race cancelled.
    """
    freeze_at = race.off_time - timedelta(minutes=DEFAULT_HORIZON_MINUTES)
    base: dict[str, Any] = {"freeze_at": _iso(freeze_at)}
    if entry is not None:
        tickets = [
            {k: t[k] for k in ("strategy", "bet_type", "numbers", "stake", "returned")}
            for t in entry["tickets"]
        ]
        stake = sum(t["stake"] for t in tickets)
        returned = sum(t["returned"] or 0 for t in tickets) if entry["settled"] else None
        return {
            **base,
            "state": "settled" if entry["settled"] else "frozen",
            "frozen_at": entry["frozen_at"],
            "tickets": tickets,
            "stake": stake,
            "returned": returned,
        }
    if "ANNULEE" in (race.status or ""):
        return {**base, "state": "cancelled"}
    if now >= race.off_time:
        return {**base, "state": "missed"}
    return {**base, "state": "open" if now >= freeze_at else "upcoming"}


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
    from predlab.racing.backfill import DEFAULT_PLAN, parse_plan, targets

    for discipline, start in targets(parse_plan(DEFAULT_PLAN)):
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
            present = {t for (t,) in con.execute("SHOW TABLES").fetchall()}
            for table in ("races", "runners", "odds", "dividends", "horses"):
                # A base built by an older version may lack a table: say so, don't crash.
                db[table] = (
                    con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]  # type: ignore[index]
                    if table in present
                    else None
                )
            db["missing_tables"] = sorted(
                {"races", "runners", "odds", "dividends", "horses"} - present
            )
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
