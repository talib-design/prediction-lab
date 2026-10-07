"""F1 / R1 forward: grids frozen before each EuroMillions draw, settled after it.

The carnet is an append-only, hash-chained ledger (``data/lottery/euromillions_carnet.jsonl``)
holding two kinds of record:

* ``grid``  -- one per logic and per upcoming draw, written *before* the draw, with the
  history it was computed from (last draw known, number of draws, data fingerprint);
* ``result`` -- written once the official result and payouts are in the store.

Timing: sales close at 20:00 Paris on draw day, at tobacconists and online (Chris,
2026-10-06), so a grid for draw day D is only frozen before 20:00 Paris on D; the exact
draw time is not verified, so results are only looked for after 23:30 Paris. A draw missed by the Mac (asleep, offline) is
simply not played; nothing is ever back-filled.

The witness (em-R1) plays every draw with a grid derived from the date alone.
"""

from __future__ import annotations

import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

from predlab import __version__
from predlab.core.clock import PARIS
from predlab.core.hashing import AppendOnlyLedger, sha256_bytes
from predlab.lottery.backtest_em import hypergeometric_matches, logic_models, witness_grid
from predlab.lottery.engine import dataset_fingerprint
from predlab.lottery.euromillions import CURRENT_ARCHIVE_URL, EuroMillionsStore
from predlab.lottery.gamespec import EM_2016_09, GameSpec
from predlab.lottery.historyview import build_view
from predlab.lottery.payouts import GRID_PRICE_EUR, grid_payouts
from predlab.lottery.selection import TopKPolicy

FREEZE_CUTOFF = time(20, 0)  # Paris, on draw day: sales close at 20:00 (Chris)
RESULTS_FROM = time(23, 30)  # Paris, on draw day
WITNESS = "temoin_r1"


def next_draw_date(after: date, spec: GameSpec = EM_2016_09) -> date:
    """First scheduled draw strictly after ``after``."""
    day = after + timedelta(days=1)
    while day.isoweekday() not in spec.draw_weekdays:
        day += timedelta(days=1)
    return day


def latest_due_draw(now: datetime, spec: GameSpec = EM_2016_09) -> date:
    """Most recent draw whose result should be published by ``now``."""
    local = now.astimezone(PARIS)
    day = local.date()
    if local.time() < RESULTS_FROM or day.isoweekday() not in spec.draw_weekdays:
        day -= timedelta(days=1)
    while day.isoweekday() not in spec.draw_weekdays:
        day -= timedelta(days=1)
    return day


def can_freeze(target: date, now: datetime) -> bool:
    return now < datetime.combine(target, FREEZE_CUTOFF, tzinfo=PARIS)


def fetch_current_archive(
    dest: Path, *, opener: Callable[[str], bytes] | None = None
) -> Path | None:
    """Download the FDJ archive that grows with each draw. Returns the new file, if new.

    Only works where the FDJ host is reachable (Chris's Mac, not the sandboxes).
    """

    def _open(url: str) -> bytes:
        req = urllib.request.Request(url, headers={"User-Agent": "PredictionLab (recherche perso)"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()

    content = (opener or _open)(CURRENT_ARCHIVE_URL)
    if content[:2] != b"PK":
        raise ValueError("la réponse FDJ n'est pas une archive ZIP")
    digest = sha256_bytes(content)
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"current_{digest[:12]}.zip"
    if path.exists():
        return None
    path.write_bytes(content)
    return path


@dataclass(frozen=True, slots=True)
class Carnet:
    ledger: AppendOnlyLedger

    def records(self) -> list[dict[str, Any]]:
        return list(self.ledger.records())

    def grids(self) -> list[dict[str, Any]]:
        return [r for r in self.records() if r["type"] == "grid"]

    def results(self) -> list[dict[str, Any]]:
        return [r for r in self.records() if r["type"] == "result"]

    def frozen_draws(self) -> set[str]:
        return {r["draw_date"] for r in self.grids()}

    def settled(self) -> set[tuple[str, str]]:
        return {(r["draw_date"], r["logic"]) for r in self.results()}


def freeze_next(
    carnet: Carnet, store: EuroMillionsStore, now: datetime, spec: GameSpec = EM_2016_09
) -> list[dict[str, Any]]:
    """Freeze one grid per logic (and the witness) for the next draw, if still allowed."""
    dates, pools = store.arrays(spec)
    last = dates[-1].astype("datetime64[D]").astype(date)
    target = next_draw_date(max(last, now.astimezone(PARIS).date() - timedelta(days=1)), spec)
    if target.isoformat() in carnet.frozen_draws() or not can_freeze(target, now):
        return []
    view = build_view(spec, dates, pools, as_of=target)
    expected_prev = target - timedelta(days=1)
    while expected_prev.isoweekday() not in spec.draw_weekdays:
        expected_prev -= timedelta(days=1)
    common = {
        "type": "grid",
        "draw_date": target.isoformat(),
        "frozen_at": now.astimezone(UTC).isoformat(timespec="seconds"),
        "history_last_draw": last.isoformat(),
        "history_draws": len(view),
        "history_stale": last < expected_prev,
        "data_fingerprint": dataset_fingerprint(dates, pools),
        "code_version": __version__,
        "spec": spec.key,
    }
    written = []
    policy = TopKPolicy()
    for model in logic_models(spec):
        if model.name == "uniform":
            continue
        ticket = policy.ticket(model.forecast(view, target))
        rec = {
            **common,
            "logic": model.name,
            "balls": list(ticket["main"]),
            "stars": list(ticket["stars"]),
        }
        carnet.ledger.append(rec)
        written.append(rec)
    w = witness_grid(target, spec.pools)
    rec = {**common, "logic": WITNESS, "balls": list(w["main"]), "stars": list(w["stars"])}
    carnet.ledger.append(rec)
    written.append(rec)
    return written


def settle(carnet: Carnet, store: EuroMillionsStore, now: datetime) -> list[dict[str, Any]]:
    """Write a result for every frozen grid whose draw is now in the store."""
    df = store.read()
    by_date = {d.isoformat(): i for i, d in enumerate(df["draw_date"].to_list())}
    done = carnet.settled()
    written = []
    for g in carnet.grids():
        key = (g["draw_date"], g["logic"])
        if key in done or g["draw_date"] not in by_date:
            continue
        i = by_date[g["draw_date"]]
        balls = set(df["main_numbers"][i].to_list())
        stars = set(df["stars_numbers"][i].to_list())
        bh = len(balls & set(g["balls"]))
        sh = len(stars & set(g["stars"]))
        rapports = np.array(
            [[np.nan if v is None else v for v in df["rapports"][i].to_list()]], dtype=np.float64
        )
        pay, rank = grid_payouts(np.array([bh]), np.array([sh]), rapports, df["era"][i])
        rec = {
            "type": "result",
            "draw_date": g["draw_date"],
            "logic": g["logic"],
            "ball_hits": bh,
            "star_hits": sh,
            "rank": int(rank[0]),
            "payout_eur": None if np.isnan(pay[0]) else float(pay[0]),
            "drawn_balls": sorted(balls),
            "drawn_stars": sorted(stars),
            "settled_at": now.astimezone(UTC).isoformat(timespec="seconds"),
        }
        carnet.ledger.append(rec)
        done.add(key)
        written.append(rec)
    return written


def summarise(carnet: Carnet) -> dict[str, Any]:
    """Per logic: draws settled, matches vs the exact law, payout and ROI (fictive)."""
    mean_b, var_b = hypergeometric_matches(EM_2016_09.pool("main"))
    mean_s, var_s = hypergeometric_matches(EM_2016_09.pool("stars"))
    out: dict[str, Any] = {}
    for logic in sorted({r["logic"] for r in carnet.results()}):
        rows = [r for r in carnet.results() if r["logic"] == logic]
        n = len(rows)
        b = np.array([r["ball_hits"] for r in rows], dtype=np.float64)
        s = np.array([r["star_hits"] for r in rows], dtype=np.float64)
        pays = [r["payout_eur"] for r in rows if r["payout_eur"] is not None]
        zb = (b.sum() - n * mean_b) / np.sqrt(n * var_b)
        zs = (s.sum() - n * mean_s) / np.sqrt(n * var_s)
        out[logic] = {
            "draws": n,
            "mean_balls": float(b.mean()),
            "z_balls": float(zb),
            "p_balls": float(2 * stats.norm.sf(abs(zb))),
            "mean_stars": float(s.mean()),
            "z_stars": float(zs),
            "wins": int(sum(r["rank"] > 0 for r in rows)),
            "paid_eur": float(sum(pays)),
            "staked_eur": GRID_PRICE_EUR * n,
            "roi": float(sum(pays) / (GRID_PRICE_EUR * n) - 1) if n else float("nan"),
        }
    return out
