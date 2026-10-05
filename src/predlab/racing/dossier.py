"""The weekly dossier: the facts the critic agent reads (docs/METHODOLOGY.md §14).

Python computes, the LLM comments. Every number the critic may quote is in here,
computed the same way each week:

* **carnet** -- the live paper bets, favourite against model, since the start and over
  the last 7 days, and the week's races where the two picks differed;
* **history** -- the replay (walk-forward model on every race since 2024) cut into
  segments: favourite's odds, field size, distance, going, category, quinté, venue,
  quarter, odds of the model's pick when it leaves the favourite. Per segment: races,
  races where the picks differ, model − favourite in euros (1 € gagnant + 1 € placé on
  each) with a 90 % bootstrap interval; segments with fewer than 50 differing races are
  flagged as too small to say anything;
* **calibration** -- the model's own pick: predicted probability against the observed
  win rate, by band;
* **lab** -- champion, history coverage, vault, tests by status, latest conclusions;
* **health** -- backfill progress, carnet volume, errors logged.

The dossier has seen the results. Whatever the critic proposes from it is therefore
judged only on races run *after* the proposal (``Candidate.fresh_from``), never on this
history.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from itertools import pairwise
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from predlab.core.clock import paris_day
from predlab.core.hashing import AppendOnlyLedger
from predlab.core.paths import Paths
from predlab.racing import lab
from predlab.racing import replay as replay_lib
from predlab.racing.carnet import entries as carnet_entries
from predlab.registry.hypotheses import HypothesisRegistry

DISCIPLINES = ("PLAT", "ATTELE", "MONTE")
SMALL = 50  # differing races below which a segment says nothing
LEVEL = 0.90
PAIRS = {"SG": ("SG favori", "SG top marche_plus"), "SP": ("SP favori", "SP top marche_plus")}


# ---------------------------------------------------------------------------- carnet


def _side() -> dict[str, float]:
    return {"stake": 0.0, "returned": 0.0}


def _close(side: dict[str, float]) -> dict[str, Any]:
    stake, ret = side["stake"], side["returned"]
    return {
        "stake": round(stake, 2),
        "returned": round(ret, 2),
        "net": round(ret - stake, 2),
        "roi": round(ret / stake - 1, 4) if stake else None,
    }


def _tally(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Favourite against model on the settled races where both played a bet type."""
    sides = {"favori": _side(), "modèle": _side()}
    races = 0
    for e in items:
        by = {t["strategy"]: t for t in e["tickets"]}
        played = False
        for fav, mod in PAIRS.values():
            if fav in by and mod in by:
                played = True
                for name, t in (("favori", by[fav]), ("modèle", by[mod])):
                    sides[name]["stake"] += t["stake"]
                    sides[name]["returned"] += t["returned"] or 0.0
        races += played
    return {"races": races, **{k: _close(v) for k, v in sides.items()}}


def _strats(e: dict[str, Any]) -> set[str]:
    return {t["strategy"] for t in e["tickets"]}


def _net(t: dict[str, Any] | None) -> float:
    return 0.0 if t is None else round((t["returned"] or 0.0) - t["stake"], 2)


def carnet_part(items: list[dict[str, Any]], today: date) -> dict[str, Any]:
    week_from = today - timedelta(days=7)
    out: dict[str, Any] = {"week": [week_from.isoformat(), (today - timedelta(days=1)).isoformat()]}
    for d in DISCIPLINES:
        mine = [e for e in items if e["discipline"] == d and e["settled"]]
        if not mine:
            continue
        week = [e for e in mine if week_from <= date.fromisoformat(e["day"]) < today]
        differ = []
        for e in week:
            by = {t["strategy"]: t for t in e["tickets"]}
            fav, mod = by.get("SG favori"), by.get("SG top marche_plus")
            if fav is None or mod is None or fav["numbers"] == mod["numbers"]:
                continue
            order = [n for group in (e.get("finish_order") or [])[:3] for n in group]
            differ.append(
                {
                    "day": e["day"],
                    "race_id": e["race_id"],
                    "venue": e.get("venue"),
                    "favori": fav["numbers"],
                    "modèle": mod["numbers"],
                    "arrivée": order,
                    "net_favori": round(_net(fav) + _net(by.get("SP favori")), 2),
                    "net_modèle": round(_net(mod) + _net(by.get("SP top marche_plus")), 2),
                }
            )
        paired = [
            e for e in mine if any(f in _strats(e) and m in _strats(e) for f, m in PAIRS.values())
        ]
        if not paired:
            continue
        out[d] = {
            "since": min(e["day"] for e in paired),
            "all": _tally(mine),
            "week": _tally(week),
            "week_differ": sorted(differ, key=lambda r: (r["day"], r["race_id"])),
        }
    return out


# --------------------------------------------------------------------------- history


def _bins(col: str, edges: list[float], labels: list[str]) -> pl.Expr:
    expr = pl.when(pl.col(col).is_null()).then(pl.lit("inconnu"))
    for hi, label in zip(edges, labels[:-1], strict=True):
        expr = expr.when(pl.col(col) < hi).then(pl.lit(label))
    return expr.otherwise(pl.lit(labels[-1]))


def _top(col: str, df: pl.DataFrame, keep: int, min_races: int) -> pl.Expr:
    counts = df.group_by(col).len().filter(pl.col("len") >= min_races).sort("len", descending=True)
    kept = counts[col].head(keep).to_list()
    return (
        pl.when(pl.col(col).is_in(kept)).then(pl.col(col).cast(pl.Utf8)).otherwise(pl.lit("autre"))
    )


FAV_ODDS = ["< 1,5", "1,5 – 2", "2 – 3", "3 – 5", "≥ 5"]
RUNNERS = ["≤ 8", "9 – 11", "12 – 14", "≥ 15"]
DIST_FLAT = ["< 1 400 m", "1 400 – 1 799 m", "1 800 – 2 399 m", "≥ 2 400 m"]
DIST_TROT = ["< 2 200 m", "2 200 – 2 699 m", "≥ 2 700 m"]
MOD_ODDS = ["< 3", "3 – 5", "5 – 10", "≥ 10"]
MOD_SEGMENT = "cote du choix du modèle (quand il quitte le favori)"
ORDER = {
    "cote du favori": FAV_ODDS,
    "partants": RUNNERS,
    "distance": [*DIST_FLAT, *DIST_TROT],
    "quinté": ["quinté", "autres"],
    "trimestre": ["T1", "T2", "T3", "T4"],
    MOD_SEGMENT: ["même cheval", *MOD_ODDS],
}


def _sorted_rows(name: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Bands in their natural order; categories by volume; « autre » and « inconnu » last."""
    order = ORDER.get(name)

    def key(r: dict[str, Any]) -> tuple[int, float, str]:
        s = r["segment"]
        if s in ("autre", "inconnu"):
            return (2, 0.0, s)
        if order and s in order:
            return (0, float(order.index(s)), s)
        return (1, -float(r["races"]), s)

    return sorted(rows, key=key)


def segment_exprs(df: pl.DataFrame, discipline: str) -> dict[str, pl.Expr]:
    flat = discipline == "PLAT"
    dist = ([1400.0, 1800.0, 2400.0], DIST_FLAT) if flat else ([2200.0, 2700.0], DIST_TROT)
    out = {
        "cote du favori": _bins("fav_odds", [1.5, 2.0, 3.0, 5.0], FAV_ODDS),
        "partants": _bins("declared_runners", [9, 12, 15], RUNNERS),
        "distance": _bins("distance_m", *dist),
        "catégorie": _top("category", df, 8, 200),
        "quinté": pl.when(pl.col("has_quinte")).then(pl.lit("quinté")).otherwise(pl.lit("autres")),
        "hippodrome": _top("venue_name", df, 12, 150),
        "trimestre": pl.concat_str(pl.lit("T"), pl.col("day").dt.quarter().cast(pl.Utf8)),
        MOD_SEGMENT: pl.when(pl.col("fav_number") == pl.col("mod_number"))
        .then(pl.lit("même cheval"))
        .otherwise(_bins("mod_odds", [3.0, 5.0, 10.0], MOD_ODDS)),
    }
    if flat:
        out["terrain"] = _top("going_label", df, 8, 200)
    return out


def _interval(d: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    if len(d) < 2:
        return float("nan"), float("nan")
    idx = rng.integers(0, len(d), size=(1000, len(d)))
    sums = d[idx].sum(axis=1)
    lo, hi = np.quantile(sums, [(1 - LEVEL) / 2, (1 + LEVEL) / 2])
    return float(lo), float(hi)


def _cell(df: pl.DataFrame, rng: np.random.Generator) -> dict[str, Any]:
    d = df["diff"].to_numpy().astype(np.float64)
    differ = int(df["differ"].sum())
    lo, hi = _interval(d, rng)
    return {
        "races": df.height,
        "differ": differ,
        "model_minus_favourite": round(float(d.sum()), 2),
        "low": round(lo, 2),
        "high": round(hi, 2),
        "small": differ < SMALL,
    }


def with_diff(picks: pl.DataFrame) -> pl.DataFrame:
    """Per race: model − favourite in euros, 1 € gagnant + 1 € placé on each (a bet the
    race did not pay counts for neither)."""
    return picks.with_columns(
        (
            (pl.col("mod_SG").fill_null(0.0) + pl.col("mod_SP").fill_null(0.0))
            - (pl.col("fav_SG").fill_null(0.0) + pl.col("fav_SP").fill_null(0.0))
        ).alias("diff"),
        (pl.col("fav_number") != pl.col("mod_number")).cast(pl.Int64).alias("differ"),
    )


def history_part(picks: pl.DataFrame, races: pl.DataFrame, discipline: str) -> dict[str, Any]:
    df = with_diff(picks.join(races, on="race_id", how="left"))
    if df.is_empty():
        return {"races": 0}
    rng = np.random.default_rng(7)
    segments: dict[str, list[dict[str, Any]]] = {}
    for name, expr in segment_exprs(df, discipline).items():
        cut = df.with_columns(expr.alias("_seg"))
        rows = [
            {"segment": str(label), **_cell(part, rng)}
            for (label,), part in sorted(cut.group_by(["_seg"]), key=lambda kv: str(kv[0][0]))
        ]
        segments[name] = _sorted_rows(name, rows)
    calib = []
    won = df.filter(pl.col("mod_SG").is_not_null() & pl.col("mod_p").is_not_null())
    edges = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.01]
    for lo, hi in pairwise(edges):
        band = won.filter((pl.col("mod_p") >= lo) & (pl.col("mod_p") < hi))
        if band.is_empty():
            continue
        calib.append(
            {
                "band": f"{lo:.0%} – {min(hi, 1.0):.0%}",
                "races": band.height,
                "predicted": round(float(band["mod_p"].mean()), 4),  # type: ignore[arg-type]
                "observed": round(float((band["mod_SG"] > 0).mean()), 4),  # type: ignore[arg-type]
            }
        )
    days = df["day"]
    return {
        "first_day": str(days.min()),
        "last_day": str(days.max()),
        **_cell(df, rng),
        "segments": segments,
        "calibration": calib,
    }


def _race_attributes(db_path: Path) -> pl.DataFrame:
    import duckdb

    schema = {
        "race_id": pl.Utf8,
        "distance_m": pl.Float64,
        "going_label": pl.Utf8,
        "category": pl.Utf8,
        "declared_runners": pl.Float64,
        "venue_name": pl.Utf8,
        "has_quinte": pl.Boolean,
    }
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        rows = con.execute(
            f"SELECT {', '.join(schema)} FROM races WHERE country_code = 'FRA'"
        ).fetchall()
    finally:
        con.close()
    return pl.DataFrame(rows, schema=schema, orient="row")


# ------------------------------------------------------------------------------- lab


def lab_part(paths: Paths) -> dict[str, Any]:
    from predlab.racing.champion import EXTENDED, Champion, history_coverage, races_since

    reg = HypothesisRegistry(AppendOnlyLedger(paths.hypotheses))
    current = [h for h in reg.current() if h.experiment] if paths.hypotheses.exists() else []
    results = lab.results(paths.lab)
    out: dict[str, Any] = {}
    for d in DISCIPLINES:
        champ = Champion.load(paths.lab, d)
        protocol = f"obj{champ.current['version']}"
        mine = [h for h in current if h.dataset == d and str(h.experiment).endswith(f":{protocol}")]
        counts = Counter(h.status.value for h in mine)
        latest = sorted(
            (r for r in results.values() if r.get("discipline") == d),
            key=lambda r: r.get("tested_at", ""),
            reverse=True,
        )[:8]
        start = champ.vault_start(EXTENDED)
        out[d] = {
            "champion": {
                "version": champ.current["version"],
                "features": len(champ.features),
                "tau": champ.tau,
                "rules": champ.rules,
                "origin": champ.current.get("origin"),
            },
            "coverage": history_coverage(paths.database, d),
            "vault": {
                "start": start.isoformat(),
                "races": races_since(paths.database, d, start),
                "min_races": EXTENDED.vault_min_races,
                "attempts": len(champ.data.get("attempts", [])),
            },
            "tests": dict(counts),
            "waiting": sorted({h.forward_result or "" for h in mine if h.forward_result}),
            "latest": [
                {
                    k: r.get(k)
                    for k in ("experiment", "label", "kind", "status", "conclusion", "tested_at")
                }
                for r in latest
            ],
        }
    return out


# ---------------------------------------------------------------------------- health


def health_part(paths: Paths, items: list[dict[str, Any]], today: date) -> dict[str, Any]:
    backfill = {}
    for f in sorted(paths.raw_pmu.glob("backfill_done_v2*.json")):
        try:
            days = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        name = f.stem.removeprefix("backfill_done_v2").lstrip("_") or "PLAT"
        backfill[name] = {"days_done": len(days), "oldest": min(days) if days else None}
    week_from = today - timedelta(days=7)
    per_day: dict[str, Counter[str]] = defaultdict(Counter)
    for e in items:
        if week_from <= date.fromisoformat(e["day"]) < today:
            per_day[e["day"]][e["discipline"]] += 1
    errors = 0
    log = paths.logs / "collect.log"
    if log.exists():
        since = week_from.isoformat()
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            if line[:10] >= since and "ERREUR" in line:
                errors += 1
    return {
        "backfill": backfill,
        "carnet_races_per_day": {k: dict(v) for k, v in sorted(per_day.items())},
        "errors_logged_this_week": errors,
    }


# ----------------------------------------------------------------------------- build


def build(paths: Paths, now: datetime) -> dict[str, Any]:
    today = paris_day(now)
    try:
        items = carnet_entries(AppendOnlyLedger(paths.carnet)) if paths.carnet.exists() else []
    except (KeyError, ValueError, TypeError):
        items = []
    history: dict[str, Any] = {}
    if paths.database.exists():
        races = _race_attributes(paths.database)
        for d in DISCIPLINES:
            picks = replay_lib.load_picks(paths.normalized, d)
            if picks is not None and "mod_p" in picks.columns:
                history[d] = history_part(picks, races, d)
    return {
        "generated_at": now.isoformat(timespec="seconds"),
        "day": today.isoformat(),
        "method": (
            "1 € gagnant + 1 € placé sur le favori (plus petite cote à 25 min) et sur le "
            "choix du modèle ; « modèle − favori » en euros, intervalle bootstrap à 90 % "
            f"sur les courses ; un segment de moins de {SMALL} courses où les choix "
            "diffèrent ne dit rien. Historique : reconstitution walk-forward depuis 2024."
        ),
        "carnet": carnet_part(items, today),
        "history": history,
        "lab": lab_part(paths) if paths.database.exists() else {},
        "health": health_part(paths, items, today),
    }


def _eur(x: float | None) -> str:
    return "—" if x is None or x != x else f"{x:+.2f} €".replace(".", ",")


def _pct(x: float | None) -> str:
    return "—" if x is None else f"{x:+.1%}".replace(".", ",")


def to_markdown(rep: dict[str, Any]) -> str:
    lines = [f"# Dossier de la semaine — {rep['day']}", "", rep["method"], ""]
    c = rep["carnet"]
    lines += [f"## Carnet en direct (semaine du {c['week'][0]} au {c['week'][1]})", ""]
    for d in DISCIPLINES:
        if d not in c:
            continue
        x = c[d]
        lines.append(f"### {d}")
        lines.append("")
        lines.append("| Période | Courses | Favori | Modèle |")
        lines.append("|---|---|---|---|")
        for label, t in ((f"depuis le {x['since']}", x["all"]), ("7 derniers jours", x["week"])):
            lines.append(
                f"| {label} | {t['races']} | {_eur(t['favori']['net'])} ({_pct(t['favori']['roi'])})"
                f" | {_eur(t['modèle']['net'])} ({_pct(t['modèle']['roi'])}) |"
            )
        lines.append("")
        if x["week_differ"]:
            lines.append("Courses de la semaine où les choix diffèrent :")
            lines.append("")
            lines.append(
                "| Jour | Course | Hippodrome | Favori | Modèle | Arrivée | Net favori | Net modèle |"
            )
            lines.append("|---|---|---|---|---|---|---|---|")
            for r in x["week_differ"]:
                lines.append(
                    f"| {r['day']} | {r['race_id'].split('/')[1]} | {r['venue'] or ''} | "
                    f"{r['favori']} | {r['modèle']} | {r['arrivée']} | {_eur(r['net_favori'])} | "
                    f"{_eur(r['net_modèle'])} |"
                )
            lines.append("")
    lines += ["## Historique (reconstitution) : où le modèle gagne ou perd face au favori", ""]
    for d, h in rep["history"].items():
        if not h.get("races"):
            continue
        lines.append(
            f"### {d} — {h['races']} courses du {h['first_day']} au {h['last_day']}, "
            f"{h['differ']} où les choix diffèrent : modèle − favori {_eur(h['model_minus_favourite'])} "
            f"(IC 90 % {_eur(h['low'])} à {_eur(h['high'])})"
        )
        lines.append("")
        for name, rows in h["segments"].items():
            lines.append(f"**{name}**")
            lines.append("")
            lines.append("| Segment | Courses | Choix différents | Modèle − favori | IC 90 % |")
            lines.append("|---|---|---|---|---|")
            for r in rows:
                flag = " (trop peu)" if r["small"] else ""
                lines.append(
                    f"| {r['segment']} | {r['races']} | {r['differ']}{flag} | "
                    f"{_eur(r['model_minus_favourite'])} | {_eur(r['low'])} à {_eur(r['high'])} |"
                )
            lines.append("")
        if h["calibration"]:
            lines.append(
                "**Calibration du choix du modèle** (probabilité annoncée / gagne vraiment)"
            )
            lines.append("")
            lines.append("| Bande | Courses | Annoncé | Observé |")
            lines.append("|---|---|---|---|")
            for r in h["calibration"]:
                lines.append(
                    f"| {r['band']} | {r['races']} | "
                    f"{r['predicted']:.1%} | {r['observed']:.1%} |".replace(".", ",")
                )
            lines.append("")
    lines += ["## Labo", ""]
    for d, x in rep["lab"].items():
        ch = x["champion"]
        cov = x["coverage"]
        status = {
            "PROPOSED": "proposés",
            "TESTING": "en test",
            "SUPPORTED": "retenus",
            "REJECTED": "rejetés",
            "INCONCLUSIVE": "non concluants",
        }
        tests = ", ".join(f"{n} {status.get(k, k)}" for k, n in sorted(x["tests"].items()))
        tau = f"{ch['tau']:.2f}".replace(".", ",")
        lines.append(
            f"- **{d}** : Marché+ v{ch['version']} ({ch['features']} facteurs, τ {tau}, "
            f"règles {', '.join(ch['rules']) or 'aucune'}) ; historique 2020-2023 prêt : "
            f"{'oui' if cov.get('ready') else 'non'} ; coffre {x['vault']['races']}/"
            f"{x['vault']['min_races']} courses ; tests : {tests or 'aucun'}."
        )
        for r in x["latest"][:5]:
            lines.append(f"  - {r['experiment']} — {r['status']} : {r['conclusion']}")
    lines += ["", "## Santé des données", ""]
    hl = rep["health"]
    for k, v in hl["backfill"].items():
        lines.append(
            f"- Rattrapage {k} : {v['days_done']} jours complets, le plus ancien {v['oldest']}."
        )
    lines.append(f"- Erreurs consignées cette semaine : {hl['errors_logged_this_week']}.")
    for day, v in hl["carnet_races_per_day"].items():
        lines.append(f"- Carnet {day} : " + ", ".join(f"{k} {n}" for k, n in sorted(v.items())))
    return "\n".join(lines) + "\n"


def write(rep: dict[str, Any], lab_dir: Path) -> tuple[Path, Path]:
    out = lab_dir / "dossier"
    out.mkdir(parents=True, exist_ok=True)
    stem = out / f"dossier_{rep['day']}"
    js, md = stem.with_suffix(".json"), stem.with_suffix(".md")
    js.write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    md.write_text(to_markdown(rep), encoding="utf-8")
    return js, md
