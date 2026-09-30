"""The strategy bench ("banc d'essai"): look for a combination of criteria that pays.

Asked by Chris on 2026-09-30: bet, fictitiously and without limit, on every coming race
with strategies built from what the lab learned, to find one that returns more than it
stakes (target: +10 %). A strategy is **criteria + a bet type + 1 EUR per ticket**:
"simple gagnant on every starter that is 5 years old and 2nd-3rd in the betting". Never
a staking plan, never a real bet.

Testing thousands of combinations manufactures winners by chance, so the bench works in
three stages, each on data the previous one never saw:

1. **Exploration** (races up to 2024-12-31): every combination of one to three criteria
   among ``DIMENSIONS`` is settled against the official dividends. Combinations with at
   least ``MIN_BETS`` tickets are ranked by the lower bound of their return; the best
   ``TOP`` per bet type are kept. The Marché+ criteria use a walk-forward model: each
   month is scored by a model fitted on earlier months only.
2. **Confirmation** (races since 2025-01-01, read once per strategy, when it enters the
   bench): return with its 95 % interval, one-sided test "return > 0", Benjamini-
   Yekutieli over the batch. Survivors are *confirmée*.
3. **Live**: every strategy of the bench not eliminated plays every coming race, frozen
   at T-25 min like the carnet, in its own ledger (``data/banc/ledger.jsonl``) with its
   own balance, never mixed with the carnet's. Status, from live tickets only:
   *gagnante* after ``WIN_BETS`` tickets if even the low end of its return interval is
   above zero; *éliminée* (for good) after ``KILL_BETS`` tickets if even the high end is
   below −5 %; *en test* otherwise.

Nothing is deleted: an eliminated strategy stays listed with its record, and the bench
file's history is in git.
"""

from __future__ import annotations

import fcntl
import hashlib
import itertools
import json
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
from scipy.stats import norm

from predlab.core.clock import paris_day
from predlab.core.hashing import AppendOnlyLedger
from predlab.eval.uncertainty import benjamini_hochberg
from predlab.racing.betting import SIMPLE_PLACE, SIMPLE_WIN, Ticket, settle
from predlab.racing.domain import Race, Runner
from predlab.racing.events import RaceCard

BANC_VERSION = "1"
EXPLORATION_END = date(2024, 12, 31)
CONFIRMATION_START = date(2025, 1, 1)
MIN_BETS = 200  # exploration: fewer tickets than this say nothing
TOP = 100  # per bet type and discipline, per exploration: breadth means more live tickets
MAX_SIZE = 3  # criteria per strategy
WIN_BETS, KILL_BETS = 300, 100
KILL_ROI = -0.05
TARGET_ROI = 0.10  # Chris's target
Z = 1.959964

BETS = {"SG": SIMPLE_WIN, "SP": SIMPLE_PLACE}
BET_LABEL = {"SG": "Simple gagnant", "SP": "Simple placé"}
ALL = ("PLAT", "ATTELE", "MONTE")

# Criteria the bench may combine: frame column, French name, disciplines.
DIMENSIONS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("odds_band", "Rang dans la cote", ALL),
    ("odds_range", "Cote", ALL),
    ("model_rank_band", "Classement Marché+", ALL),
    ("model_edge_band", "Valeur selon Marché+", ALL),
    ("age_band", "Âge", ALL),
    ("sex_cat", "Sexe", ALL),
    ("weight_band", "Poids porté", ("PLAT",)),
    ("rest_band", "Repos", ALL),
    ("draw_band", "Position au départ", ALL),
    ("dist_band", "Distance", ALL),
    ("field_band", "Taille du peloton", ALL),
    ("going_cat", "Terrain", ("PLAT",)),
    ("temp_band", "Température", ALL),
    ("sky_cat", "Ciel", ALL),
    ("category_cat", "Type de course", ALL),
    ("venue", "Hippodrome", ALL),
    ("mus_last_band", "Dernière course", ALL),
    ("mus_form_band", "Régularité récente", ALL),
    ("dist_change", "Distance vs dernière course", ALL),
    ("class_change", "Niveau vs dernière course", ALL),
    ("blinkers_change", "Oeillères vs dernière course", ALL),
    ("blinkers_cat", "Oeillères", ALL),
    ("jockey_change_cat", "Changement de jockey", ALL),
    ("jockey_form", "Jockey", ALL),
    ("trainer_form", "Entraîneur", ALL),
    ("duo_form", "Duo jockey-entraîneur", ALL),
    ("going_lean", "Le cheval sur ce terrain", ("PLAT",)),
    ("recul_band", "Recul", ("ATTELE", "MONTE")),
    ("shoeing_cat", "Ferrure", ("ATTELE", "MONTE")),
)
DIM_LABEL = {k: v for k, v, _ in DIMENSIONS}

# Levels that mean "we don't know": never a criterion.
UNKNOWN = {
    "Inconnu",
    "Inconnue",
    "Non mesuré",
    "Non cotée",
    "Modèle indisponible",
    "Terrain non mesuré",
    "Distance inconnue",
    "Allocation inconnue",
    "Autre ou inconnue",
}


def dimensions(discipline: str) -> list[str]:
    return [k for k, _, ds in DIMENSIONS if discipline in ds]


# ------------------------------------------------------------------- model criteria


def model_bands(df: pl.DataFrame) -> pl.DataFrame:
    """Marché+ as criteria: its rank in the race and its "value" p × odds."""
    p = pl.col("p_model")
    edge = p * pl.col("odds")
    rank = p.rank("ordinal", descending=True).over("race_id")
    return df.with_columns(
        pl.when(p.is_null())
        .then(pl.lit("Modèle indisponible"))
        .when(rank == 1)
        .then(pl.lit("1er de Marché+"))
        .when(rank <= 3)
        .then(pl.lit("2e-3e de Marché+"))
        .otherwise(pl.lit("4e et au-delà pour Marché+"))
        .alias("model_rank_band"),
        pl.when(p.is_null())
        .then(pl.lit("Modèle indisponible"))
        .when(edge < 0.75)
        .then(pl.lit("Cote trop basse (p × cote < 0,75)"))
        .when(edge < 0.9)
        .then(pl.lit("Cote un peu basse (0,75-0,9)"))
        .when(edge < 1.05)
        .then(pl.lit("Cote juste (0,9-1,05)"))
        .otherwise(pl.lit("Cote généreuse (p × cote ≥ 1,05)"))
        .alias("model_edge_band"),
    )


def walk_forward_model(frame: pl.DataFrame, lam: float, min_races: int = 300) -> pl.DataFrame:
    """``p_model`` for every row, from a Marché+ fitted on earlier months only."""
    from predlab.racing.features import MODEL_FEATURES
    from predlab.racing.marketplus import design, fit, predict

    frame = frame.with_columns(pl.col("day").dt.truncate("1mo").alias("_month"))
    months = sorted(frame["_month"].unique().to_list())
    parts = []
    for m in months:
        past = frame.filter(pl.col("day") < m)
        now = frame.filter(pl.col("_month") == m)
        if past["race_id"].n_unique() < min_races:
            parts.append(now.with_columns(pl.lit(None, pl.Float64).alias("p_model")))
            continue
        x = past.select(MODEL_FEATURES).to_numpy().astype(np.float64)
        means, stds = x.mean(0), x.std(0)
        stds = np.where(stds > 1e-9, stds, 0.0)
        mask = np.r_[True, stds > 0]
        theta = fit(design(past, means, stds), lam, mask)["theta"]
        params = {
            "features": list(MODEL_FEATURES),
            "means": means.tolist(),
            "stds": stds.tolist(),
            "theta": theta.tolist(),
        }
        probs = np.zeros(now.height)
        order = now.with_row_index("_i")
        for (_,), race in order.group_by("race_id"):
            probs[race["_i"].to_numpy()] = predict(params, race)
        parts.append(now.with_columns(pl.Series("p_model", probs)))
    return model_bands(pl.concat(parts).drop("_month"))


# ------------------------------------------------------------------------- returns


def load_simple_dividends(db_path: Path) -> pl.DataFrame:
    """One row per paying (race, bet, number): what 1 EUR returned."""
    import duckdb

    con = duckdb.connect(str(db_path), read_only=True)
    try:
        rows = con.execute(
            "SELECT race_id, bet_type, combination, per_euro FROM dividends "
            "WHERE bet_type IN ('SIMPLE_GAGNANT', 'SIMPLE_PLACE') AND NOT refunded"
        ).fetchall()
    finally:
        con.close()
    out = []
    for race_id, bet, combo, per_euro in rows:
        try:
            number = int(str(combo).strip("-"))
        except ValueError:
            continue
        out.append((race_id, bet, number, float(per_euro)))
    return pl.DataFrame(
        out,
        schema={
            "race_id": pl.Utf8,
            "bet_type": pl.Utf8,
            "number": pl.Int64,
            "per_euro": pl.Float64,
        },
        orient="row",
    )


def with_returns(frame: pl.DataFrame, dividends: pl.DataFrame) -> pl.DataFrame:
    """``ret_SG`` / ``ret_SP``: what 1 EUR on this starter returned; null when the race has
    no dividend of that kind (then no ticket of that kind is counted)."""
    for code, bet in BETS.items():
        d = dividends.filter(pl.col("bet_type") == bet)
        races = d.select("race_id").unique().with_columns(pl.lit(True).alias(f"has_{code}"))
        pay = d.group_by("race_id", "number").agg(pl.col("per_euro").max().alias(f"pay_{code}"))
        frame = (
            frame.join(races, on="race_id", how="left")
            .join(pay, on=["race_id", "number"], how="left")
            .with_columns(
                pl.when(pl.col(f"has_{code}"))
                .then(pl.col(f"pay_{code}").fill_null(0.0))
                .otherwise(None)
                .alias(f"ret_{code}")
            )
            .drop(f"has_{code}", f"pay_{code}")
        )
    return frame


# --------------------------------------------------------------------------- stats


def summarise_returns(returns: np.ndarray) -> dict[str, Any]:
    """Return on 1 EUR tickets, with a 95 % interval and the one-sided p of "> 0"."""
    n = len(returns)
    if n == 0:
        return {
            "bets": 0,
            "stake": 0.0,
            "returned": 0.0,
            "net": 0.0,
            "roi": None,
            "low": None,
            "high": None,
            "p": None,
        }
    net = returns - 1.0
    roi = float(net.mean())
    se = float(net.std(ddof=1) / math.sqrt(n)) if n > 1 else float("inf")
    return {
        "bets": n,
        "stake": float(n),
        "returned": float(returns.sum()),
        "net": float(net.sum()),
        "roi": roi,
        "low": roi - Z * se if n > 1 else None,
        "high": roi + Z * se if n > 1 else None,
        "p": float(norm.sf(roi / se)) if n > 1 and se > 0 else None,
    }


def strategy_id(discipline: str, bet: str, criteria: dict[str, str]) -> str:
    key = json.dumps([discipline, bet, sorted(criteria.items())], ensure_ascii=False)
    return hashlib.sha256(key.encode()).hexdigest()[:10]


def label(criteria: dict[str, str]) -> str:
    return " · ".join(f"{DIM_LABEL.get(k, k)} : {v}" for k, v in sorted(criteria.items()))


def matches(df: pl.DataFrame, criteria: dict[str, str]) -> pl.DataFrame:
    expr = pl.lit(True)
    for k, v in criteria.items():
        expr = expr & (pl.col(k) == v)
    return df.filter(expr)


# ----------------------------------------------------------------------- exploration


def _span(frame: pl.DataFrame) -> tuple[date, date]:
    days = frame["day"].sort().to_list()
    return days[0], days[-1]


def halves(frame: pl.DataFrame) -> list[tuple[date, date]]:
    days: list[date] = frame["day"].sort().to_list()
    if not days:
        return []
    mid = days[len(days) // 2]
    return [(days[0], mid), (mid + timedelta(days=1), days[-1])]


def years(frame: pl.DataFrame) -> list[tuple[date, date]]:
    ys = sorted({d.year for d in frame["day"].to_list()})
    return [(date(y, 1, 1), date(y, 12, 31)) for y in ys]


def explore(
    frame: pl.DataFrame,
    discipline: str,
    *,
    periods: list[tuple[date, date]] | None = None,
    max_size: int = MAX_SIZE,
    min_bets: int = MIN_BETS,
    min_period_bets: int = 40,
    top: int = TOP,
) -> list[dict[str, Any]]:
    """Best combinations on ``frame``, per bet type.

    A combination is kept only if it pays in *every period* (by default the two halves
    of the window), with at least ``min_period_bets`` tickets in each: a single lucky
    longshot can lift a whole window, rarely every part of it. Survivors are ranked by
    the lower bound of their return over the whole window.
    """
    periods = periods if periods is not None else halves(frame)
    dims = [d for d in dimensions(discipline) if d in frame.columns]
    per = pl.lit(-1)
    for i, (a, b) in enumerate(periods):
        per = pl.when(pl.col("day").is_between(a, b)).then(pl.lit(i)).otherwise(per)
    frame = frame.with_columns(
        per.alias("_per"),
        *(~pl.col(d).is_in(list(UNKNOWN)).alias(f"_k_{d}") for d in dims),
    )
    aggs = []
    for code in BETS:
        r = pl.col(f"ret_{code}")
        aggs += [
            r.is_not_null().sum().alias(f"n_{code}"),
            r.sum().alias(f"s_{code}"),
            (r * r).sum().alias(f"sq_{code}"),
        ]
        for i in range(len(periods)):
            inside = pl.col("_per") == i
            aggs += [
                (inside & r.is_not_null()).sum().alias(f"n{i}_{code}"),
                r.filter(inside).sum().alias(f"s{i}_{code}"),
            ]
    found: list[dict[str, Any]] = []
    for size in range(1, max_size + 1):
        for combo in itertools.combinations(dims, size):
            agg = (
                frame.filter(pl.all_horizontal(pl.col(f"_k_{d}") for d in combo))
                .group_by(list(combo))
                .agg(aggs)
            )
            for code in BETS:
                n, s, s2 = pl.col(f"n_{code}"), pl.col(f"s_{code}"), pl.col(f"sq_{code}")
                steady = pl.lit(True)
                for i in range(len(periods)):
                    ni, si = pl.col(f"n{i}_{code}"), pl.col(f"s{i}_{code}")
                    steady = steady & (ni >= min_period_bets) & (si / ni > 1)
                stats = agg.filter((n >= min_bets) & steady).with_columns(
                    (s / n - 1).alias("roi"),
                    ((s2 / n - (s / n) ** 2) / n).sqrt().alias("se"),
                    *(
                        (pl.col(f"s{i}_{code}") / pl.col(f"n{i}_{code}") - 1).alias(f"r{i}")
                        for i in range(len(periods))
                    ),
                )
                for row in stats.iter_rows(named=True):
                    se = row["se"]
                    found.append(
                        {
                            "bet": code,
                            "criteria": {d: row[d] for d in combo},
                            "bets": row[f"n_{code}"],
                            "roi": row["roi"],
                            "periods": [
                                {
                                    "from": a.isoformat(),
                                    "to": b.isoformat(),
                                    "bets": row[f"n{i}_{code}"],
                                    "roi": row[f"r{i}"],
                                }
                                for i, (a, b) in enumerate(periods)
                            ],
                            "low": row["roi"] - Z * se,
                            "high": row["roi"] + Z * se,
                        }
                    )
    # The same tickets reached by more criteria (a level every row has, a redundant pair)
    # count once: keep the shortest description.
    unique: dict[tuple[Any, ...], dict[str, Any]] = {}
    for f in sorted(found, key=lambda f: len(f["criteria"])):
        unique.setdefault((f["bet"], f["bets"], round(f["roi"], 9), round(f["high"], 9)), f)
    found = list(unique.values())
    out = []
    for code in BETS:
        ranked = sorted((f for f in found if f["bet"] == code), key=lambda f: -f["low"])
        out.extend(ranked[:top])
    return out


def confirm(candidates: list[dict[str, Any]], frame: pl.DataFrame) -> list[dict[str, Any]]:
    """Each candidate on the confirmation window, once, with BY over the batch."""
    rows = []
    for c in candidates:
        sel = matches(frame, c["criteria"])
        r = sel[f"ret_{c['bet']}"].drop_nulls().to_numpy().astype(np.float64)
        rows.append(summarise_returns(r))
    usable = [i for i, s in enumerate(rows) if s["p"] is not None]
    survive = benjamini_hochberg(np.array([rows[i]["p"] for i in usable])) if usable else []
    for i, s in zip(usable, survive, strict=True):
        rows[i]["verdict"] = "confirmée" if s and rows[i]["roi"] > 0 else "non confirmée"
    for s in rows:
        s.setdefault("verdict", "trop peu de paris")
    return rows


# ---------------------------------------------------------------------------- panel


@dataclass
class Panel:
    path: Path
    strategies: list[dict[str, Any]] = field(default_factory=list)
    updated_at: str | None = None
    gauge: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> Panel:
        if not path.exists():
            return cls(path)
        doc = json.loads(path.read_text(encoding="utf-8"))
        return cls(path, doc.get("strategies", []), doc.get("updated_at"), doc.get("gauge", {}))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        doc = {
            "banc_version": BANC_VERSION,
            "updated_at": self.updated_at,
            "gauge": self.gauge,
            "strategies": self.strategies,
        }
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.path)

    def ids(self) -> set[str]:
        return {s["id"] for s in self.strategies}

    def active(self, discipline: str) -> list[dict[str, Any]]:
        return [
            s
            for s in self.strategies
            if s["discipline"] == discipline and s.get("eliminated_at") is None
        ]


REFERENCES = ({"odds_band": "Favori"},)


def _entry(
    c: dict[str, Any],
    discipline: str,
    now: datetime,
    origin: str,
    window: tuple[date, date],
    confirmation: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "id": strategy_id(discipline, c["bet"], c["criteria"]),
        "discipline": discipline,
        "bet": c["bet"],
        "criteria": c["criteria"],
        "label": label(c["criteria"]),
        "reference": bool(c.get("reference")),
        "origin": origin,
        "added_at": now.isoformat(timespec="seconds"),
        "exploration": {
            "from": window[0].isoformat(),
            "to": window[1].isoformat(),
            "bets": c["bets"],
            "roi": c["roi"],
            "low": c["low"],
            "high": c["high"],
            "periods": c.get("periods"),
        },
        "confirmation": confirmation,
        "eliminated_at": None,
    }


def update_panel(
    panel: Panel, frame: pl.DataFrame, discipline: str, now: datetime, **explore_options: Any
) -> list[dict[str, Any]]:
    """Two searches, then add every newcomer to the bench. Returns the newcomers.

    * **Strict** -- explored on 2024, confirmed once on 2025-2026. It also measures how
      much of what "works" one year still works the next: the *gauge* of the panel.
      Only confirmed strategies enter the bench from here.
    * **Every year** -- explored on all the history, kept only if it paid in *each*
      calendar year separately. No window is left to confirm it: live races judge it.
    """
    added: list[dict[str, Any]] = []
    known = panel.ids()

    def add(c: dict[str, Any], origin: str, window: tuple[date, date], conf: Any) -> None:
        sid = strategy_id(discipline, c["bet"], c["criteria"])
        if sid in known:
            return
        entry = _entry(c, discipline, now, origin, window, conf)
        panel.strategies.append(entry)
        added.append(entry)
        known.add(sid)

    exploration = frame.filter(pl.col("day") <= EXPLORATION_END)
    confirmation = frame.filter(pl.col("day") >= CONFIRMATION_START)
    if exploration.height:
        strict = explore(exploration, discipline, **explore_options)
        verdicts = confirm(strict, confirmation)
        panel.gauge[discipline] = {
            "at": now.isoformat(timespec="seconds"),
            "tested": len(strict),
            "confirmed": sum(v["verdict"] == "confirmée" for v in verdicts),
            "exploration_roi": float(np.mean([c["roi"] for c in strict])) if strict else None,
            "confirmation_roi": float(np.mean([v["roi"] for v in verdicts if v["roi"] is not None]))
            if strict
            else None,
        }
        window = _span(exploration)
        for c, v in zip(strict, verdicts, strict=True):
            if v["verdict"] == "confirmée":
                add(
                    c,
                    "vérifiée sur 2025-2026",
                    window,
                    {"since": CONFIRMATION_START.isoformat(), **v},
                )

    if frame.height:
        window = _span(frame)
        steady = explore(frame, discipline, periods=years(frame), **explore_options)
        for c in steady:
            add(c, "régulière chaque année", window, None)
        for ref in REFERENCES:
            for code in BETS:
                sel = matches(frame, ref)[f"ret_{code}"].drop_nulls().to_numpy()
                s = summarise_returns(sel.astype(np.float64))
                add(
                    {
                        "bet": code,
                        "criteria": dict(ref),
                        "reference": True,
                        "bets": s["bets"],
                        "roi": s["roi"],
                        "low": s["low"],
                        "high": s["high"],
                    },
                    "référence",
                    window,
                    None,
                )
    panel.updated_at = now.isoformat(timespec="seconds")
    return added


def apply_eliminations(panel: Panel, live: dict[str, dict[str, Any]], now: datetime) -> list[str]:
    """Eliminate, for good, the strategies whose live return is clearly below −5 %."""
    out = []
    for s in panel.strategies:
        if s.get("eliminated_at") or s.get("reference"):
            continue
        st = live.get(s["id"])
        if st and st["bets"] >= KILL_BETS and st["high"] is not None and st["high"] < KILL_ROI:
            s["eliminated_at"] = now.isoformat(timespec="seconds")
            out.append(s["id"])
    return out


def status(s: dict[str, Any], live: dict[str, Any] | None) -> str:
    if s.get("eliminated_at"):
        return "éliminée"
    if s.get("reference"):
        return "référence"
    if live and live["bets"] >= WIN_BETS and live["low"] is not None and live["low"] > 0:
        return "gagnante"
    return "en test"


# ----------------------------------------------------------------------------- live

FrameFor = Callable[[Race, RaceCard, list[Runner]], pl.DataFrame]


@dataclass
class BancReport:
    frozen: list[str] = field(default_factory=list)
    tickets: int = 0
    settled: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"banc : {len(self.frozen)} course(s) figée(s), {self.tickets} ticket(s), "
            f"{len(self.settled)} réglée(s)"
            + (f", {len(self.errors)} erreur(s)" if self.errors else "")
        )


def tickets_for(panel: Panel, race: Race, frame: pl.DataFrame) -> list[list[Any]]:
    """[strategy id, bet code, number] for every strategy's matching starters."""
    offered = set(race.bet_types)
    out: list[list[Any]] = []
    for s in panel.active(race.discipline):
        if BETS[s["bet"]] not in offered:
            continue
        for number in matches(frame, s["criteria"])["number"].to_list():
            out.append([s["id"], s["bet"], int(number)])
    return out


def run_banc(
    store: Any,
    ledger: AppendOnlyLedger,
    panel: Panel,
    *,
    now: datetime,
    frame_for: FrameFor,
    horizon_minutes: float = 25.0,
) -> BancReport:
    """One pass: freeze the races inside [off − horizon, off), settle the finished ones."""
    from predlab.racing import carnet as c

    ledger.path.parent.mkdir(parents=True, exist_ok=True)
    report = BancReport()
    with ledger.path.open("a") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        try:
            records = ledger.records()
            frozen = {r["race_id"]: r for r in records if r.get("kind") == "freeze"}
            settled = {r["race_id"] for r in records if r.get("kind") == "settle"}
            index = store.index()
            horizon = timedelta(minutes=horizon_minutes)
            for race in c._programme(store, index, paris_day(now)):
                if not c._is_target(race) or race.race_id in frozen:
                    continue
                if not (race.off_time - horizon <= now < race.off_time):
                    continue
                if not panel.active(race.discipline):
                    continue
                key = c.capture_key(
                    c.Endpoint.PARTICIPANTS, race.day, race.meeting_number, race.race_number
                )
                built = c._card_at_horizon(store, index.get(key, []), race, now, horizon)
                if built is None or not built[0].starters or not built[0].market_coherent:
                    continue
                try:
                    frame = frame_for(race, built[0], built[2])
                    tickets = tickets_for(panel, race, frame)
                except Exception as exc:  # one race never blocks the others
                    report.errors.append(f"{race.race_id}: {type(exc).__name__}: {exc}")
                    continue
                rec = ledger.append(
                    {
                        "kind": "freeze",
                        "banc_version": BANC_VERSION,
                        "race_id": race.race_id,
                        "day": race.day.isoformat(),
                        "discipline": race.discipline,
                        "off_time": race.off_time.isoformat(),
                        "frozen_at": now.isoformat(),
                        "odds_as_of": max(
                            s.odds_reported_at for s in built[0].starters if s.odds_reported_at
                        ).isoformat(),  # type: ignore[type-var]
                        "source_captures": built[1],
                        "tickets": tickets,
                    }
                )
                frozen[race.race_id] = rec
                report.frozen.append(race.race_id)
                report.tickets += len(tickets)

            programmes: dict[date, dict[str, Race]] = {}
            for race_id, rec in frozen.items():
                if race_id in settled:
                    continue
                day = date.fromisoformat(rec["day"])
                if day not in programmes:
                    programmes[day] = {r.race_id: r for r in c._programme(store, index, day)}
                race = programmes[day].get(race_id)
                if race is None:
                    continue
                out = _settle(store, index, race, rec, now)
                if out is not None:
                    ledger.append(out)
                    report.settled.append(race_id)
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    return report


def _settle(store: Any, index: Any, race: Race, rec: dict[str, Any], now: datetime):
    from predlab.racing import carnet as c

    base = {
        "kind": "settle",
        "banc_version": BANC_VERSION,
        "race_id": race.race_id,
        "settled_at": now.isoformat(),
    }
    if "ANNULEE" in (race.status or ""):
        return {**base, "note": "course annulée", "returns": [1.0 for _ in rec["tickets"]]}
    cap = c._latest_ok(
        index.get(
            c.capture_key(c.Endpoint.RAPPORTS, race.day, race.meeting_number, race.race_number),
            [],
        )
    )
    if cap is None or not race.is_final:
        return None
    try:
        dividends = c.parse_dividends(store.read(cap), race.race_id)
    except c.PmuFormatError:
        return None
    if not dividends:
        return None
    scratched = c._non_runners(store, index, race)
    returns = []
    for _sid, bet, number in rec["tickets"]:
        if number in scratched:
            returns.append(1.0)  # a simple bet on a non-runner is refunded
        else:
            returns.append(settle(Ticket(BETS[bet], (number,), 1.0), dividends))
    return {**base, "finish_order": race.finish_order, "returns": returns}


# ---------------------------------------------------------------------------- reading


def live_returns(ledger: AppendOnlyLedger) -> tuple[dict[str, list[float]], dict[str, Any]]:
    """Per strategy, the returns of its settled live tickets; plus per-day totals and
    pending counts for the bench's own balance."""
    records = ledger.records()
    settles = {r["race_id"]: r for r in records if r.get("kind") == "settle"}
    per: dict[str, list[float]] = {}
    days: dict[str, dict[str, float]] = {}
    pending: dict[str, int] = {}
    for r in records:
        if r.get("kind") != "freeze":
            continue
        s = settles.get(r["race_id"])
        for i, (sid, _bet, _n) in enumerate(r["tickets"]):
            if s is None:
                pending[sid] = pending.get(sid, 0) + 1
                continue
            ret = float(s["returns"][i])
            per.setdefault(sid, []).append(ret)
            d = days.setdefault(r["day"], {"stake": 0.0, "returned": 0.0, "tickets": 0})
            d["stake"] += 1.0
            d["returned"] += ret
            d["tickets"] += 1
    return per, {
        "days": days,
        "pending": pending,
        "races": len([r for r in records if r.get("kind") == "freeze"]),
    }


def live_stats(ledger: AppendOnlyLedger) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    per, meta = live_returns(ledger)
    return {k: summarise_returns(np.array(v)) for k, v in per.items()}, meta


# ------------------------------------------------------------------------- wiring


def frame_for_paths(runs: Path, database: Path) -> FrameFor:
    """Live criteria for a race: features as of yesterday's build, Marché+ on the card."""
    from predlab.racing.features import history, live_frame
    from predlab.racing.marketplus import latest_params, predict

    cache: dict[str, dict[str, Any] | None] = {}

    def frame_for(race: Race, card: RaceCard, runners: list[Runner]) -> pl.DataFrame:
        if race.discipline not in cache:
            cache[race.discipline] = latest_params(runs, race.discipline)
        by_number = {x.number: x for x in runners}
        ordered = [by_number[s.number] for s in card.starters]
        odds = {s.number: s.odds for s in card.starters}
        frame = live_frame(race, ordered, odds, history(database, race.discipline))
        params = cache[race.discipline]
        p = predict(params, frame) if params else None
        return model_bands(
            frame.with_columns(pl.Series("p_model", p, dtype=pl.Float64))
            if p is not None
            else frame.with_columns(pl.lit(None, pl.Float64).alias("p_model"))
        )

    return frame_for


def build_frame(database: Path, runs: Path, discipline: str) -> pl.DataFrame:
    """Every finished race since 2024 with criteria, walk-forward Marché+ and returns."""
    from predlab.racing.features import load_finished
    from predlab.racing.profile import latest

    rep = latest(runs, "model", discipline)
    lam = float(rep["lambda"]) if rep else 1000.0
    frame = walk_forward_model(load_finished(database, discipline), lam)
    return with_returns(frame, load_simple_dividends(database))
