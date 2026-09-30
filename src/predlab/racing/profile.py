"""The winners' profile: how each condition bears on the odds and on the result.

Two families of factors, because they answer different questions:

* **Race conditions** (terrain, temperature, sky, wind, distance, field size) are the
  same for every starter. Someone wins every race, so "more winners when it is cold"
  cannot exist. What can change is *who* wins: whether the favourite wins more or less
  often than its odds said, how long the winner's odds were. That is what is measured.
* **Runner attributes** (starting position, rest, age, sex, weight, distance handicap,
  shoeing, rank in the betting) differ between starters. For each level:

  - *effect on the result*: wins / wins expected by pure chance (Σ 1/field);
  - *effect on the odds*: what the market expected (Σ implied probability) / chance --
    how much the public already backs these runners;
  - *what the odds missed*: wins / what the market expected. Above 1: these runners win
    more than their odds said. This is the only column a bettor could exploit;
  - *top 3 vs odds*: top-3 finishes / the top-3 chances the odds implied (Harville).
    Finishing *ranks* compared with betting ranks would mislead: a favourite can only
    lose places and an outsider only gain some, whatever the factor.

Every ratio carries a 95 % interval (normal approximation of a sum of Bernoulli
draws), and verdicts go through the Benjamini-Yekutieli correction over all levels
shown: with ~60 levels, three or four would look "significant" by chance alone.
Stability compares 2024 with 2025-2026: an effect that flips sign is noise until shown
otherwise. Descriptive only -- the model's inputs were fixed before this was computed
(docs/METHODOLOGY.md §10).
"""

from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
from scipy.stats import norm

from predlab.core.clock import utcnow
from predlab.eval.uncertainty import benjamini_hochberg
from predlab.racing.features import FACTORS, LEVELS, RACE_FACTORS
from predlab.racing.report import discipline_label

SPLIT_DAY = date(2025, 1, 1)
Z = 1.959964
MIN_EXPECTED = 5.0  # below this many expected wins, no verdict and no interval


def _num(x: Any) -> float | None:
    """A polars scalar (mean, median) as a float; None when empty."""
    return None if x is None else float(x)


def _ratio(wins: float, expected: float, variance: float) -> dict[str, Any]:
    if expected < MIN_EXPECTED or variance <= 0:
        return {
            "value": wins / expected if expected > 0 else None,
            "low": None,
            "high": None,
            "p": None,
        }
    sd = math.sqrt(variance)
    z = (wins - expected) / sd
    return {
        "value": wins / expected,
        "low": max(0.0, (wins - Z * sd) / expected),
        "high": (wins + Z * sd) / expected,
        "p": float(2 * norm.sf(abs(z))),
    }


def _stability(sub: pl.DataFrame, numerator: str, denominator: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, part in (
        ("avant_2025", sub.filter(pl.col("day") < SPLIT_DAY)),
        ("depuis_2025", sub.filter(pl.col("day") >= SPLIT_DAY)),
    ):
        e = float(part[denominator].sum()) if part.height else 0.0
        w = float(part[numerator].sum()) if part.height else 0.0
        out[name] = {"ratio": w / e if e > 0 else None, "expected": e}
    a, b = out["avant_2025"], out["depuis_2025"]
    if min(a["expected"], b["expected"]) < MIN_EXPECTED:
        out["verdict"] = "trop peu de données"
    elif (a["ratio"] - 1) * (b["ratio"] - 1) > 0:
        out["verdict"] = "même sens"
    else:
        out["verdict"] = "sens opposés"
    return out


def _runner_level(sub: pl.DataFrame, total: int) -> dict[str, Any]:
    wins = float(sub["won"].sum())
    fair = sub["fair_p"].to_numpy()
    market = sub["market_p"].to_numpy()
    return {
        "runners": sub.height,
        "share": sub.height / total if total else 0.0,
        "races": sub["race_id"].n_unique(),
        "wins": int(wins),
        "win_rate": wins / sub.height if sub.height else None,
        "placed_rate": _num(sub["placed"].mean()),
        "result_vs_chance": _ratio(wins, float(fair.sum()), float((fair * (1 - fair)).sum())),
        "odds_vs_chance": float(market.sum() / fair.sum()) if fair.sum() > 0 else None,
        "missed_by_odds": _ratio(wins, float(market.sum()), float((market * (1 - market)).sum())),
        "top3_vs_odds": _ratio(
            float(sub["placed"].sum()),
            float(sub["exp_top3"].sum()),
            float((sub["exp_top3"] * (1 - sub["exp_top3"])).sum()),
        ),
        "stability": _stability(sub, "won", "market_p"),
    }


def _race_level(sub: pl.DataFrame, total_races: int) -> dict[str, Any]:
    """``sub``: the favourites (one per race) and winners of the races at this level."""
    fav = sub.filter(pl.col("is_fav"))
    win = sub.filter(pl.col("won"))
    p = fav["market_p"].to_numpy()
    races = fav["race_id"].n_unique()
    return {
        "races": races,
        "share": races / total_races if total_races else 0.0,
        "favourite_win_rate": _num(fav["won"].mean()),
        "favourite_expected": float(p.mean()) if len(p) else None,
        "favourite_vs_odds": _ratio(
            float(fav["won"].sum()), float(p.sum()), float((p * (1 - p)).sum())
        ),
        "winner_median_odds": _num(win["odds"].median()),
        "outsider_win_rate": _num((win["odds_rank"] >= 4).mean()),
        "stability": _stability(fav, "won", "market_p"),
    }


def _ordered(levels: list[str], key: str) -> list[str]:
    order = {v: i for i, v in enumerate(LEVELS.get(key, ()))}
    return sorted(levels, key=lambda v: order.get(v, 99))


def build_profile(df: pl.DataFrame, discipline: str) -> dict[str, Any]:
    """``df``: the frame of ``features.load_finished`` for one discipline."""
    total = df.height
    # One favourite per race: the shortest odds (ties: the lowest number).
    df = df.with_columns(
        (
            pl.col("number") == pl.col("number").sort_by(["odds", "number"]).first().over("race_id")
        ).alias("is_fav")
    )
    total_races = df["race_id"].n_unique()
    race_factors, runner_factors = [], []
    tests: list[tuple[dict[str, Any], str]] = []
    for key, label, disciplines in FACTORS:
        if discipline not in disciplines or key not in df.columns:
            continue
        levels = []
        for value in _ordered(df[key].unique().to_list(), key):
            sub = df.filter(pl.col(key) == value)
            if key in RACE_FACTORS:
                stats = _race_level(sub.filter(pl.col("is_fav") | pl.col("won")), total_races)
                tests.append((stats["favourite_vs_odds"], "favourite_vs_odds"))
            else:
                stats = _runner_level(sub, total)
                tests.append((stats["result_vs_chance"], "result_vs_chance"))
                tests.append((stats["missed_by_odds"], "missed_by_odds"))
                tests.append((stats["top3_vs_odds"], "top3_vs_odds"))
            levels.append({"level": value, **stats})
        (race_factors if key in RACE_FACTORS else runner_factors).append(
            {"key": key, "label": label, "levels": levels}
        )
    _verdicts(tests)
    days = df["day"]
    return {
        "kind": "profile",
        "generated_at": utcnow().isoformat(timespec="seconds"),
        "discipline": discipline,
        "discipline_label": discipline_label(discipline),
        "first_day": days.min().isoformat() if total else None,  # type: ignore[union-attr]
        "last_day": days.max().isoformat() if total else None,  # type: ignore[union-attr]
        "n_races": total_races,
        "n_runners": total,
        "split_day": SPLIT_DAY.isoformat(),
        "race_factors": race_factors,
        "runner_factors": runner_factors,
        "tests": len([t for t, _ in tests if t["p"] is not None]),
        "correction": "Benjamini-Yekutieli, taux de fausses découvertes 5 %",
    }


def _verdicts(tests: list[tuple[dict[str, Any], str]]) -> None:
    usable = [t for t, _ in tests if t["p"] is not None]
    survive = benjamini_hochberg(np.array([t["p"] for t in usable])) if usable else []
    for t, s in zip(usable, survive, strict=True):
        if not s:
            t["verdict"] = "="
        else:
            t["verdict"] = "+" if t["value"] > 1 else "−"
    for t, _ in tests:
        t.setdefault("verdict", "?")


# ------------------------------------------------------------------- one race, per horse


def _record(runs: pl.DataFrame) -> dict[str, Any]:
    return {
        "runs": runs.height,
        "wins": int(runs["won"].sum()),
        "top3": int(runs["placed"].sum()),
        "expected_top3": float(runs["exp_top3"].sum()),
    }


def horse_conditions(
    hist: pl.DataFrame, horse_ids: list[str], day: date, conditions: dict[str, str]
) -> dict[str, dict[str, Any]]:
    """For each horse: its runs since 2024 before ``day``, overall and in each of the
    given conditions (``{"going_cat": "Souple", ...}``), with the top-3 finishes the
    odds implied. ``lean`` marks a horse that, per run, beat its odds' top-3 chances by
    at least a quarter more in these conditions than elsewhere (3 runs each at least)."""
    past = hist.filter(pl.col("horse_id").is_in(horse_ids) & (pl.col("day") < day))
    out: dict[str, dict[str, Any]] = {}
    for (horse,), runs in past.group_by("horse_id"):
        entry: dict[str, Any] = {**_record(runs), "conditions": {}}
        for key, value in conditions.items():
            inside = _record(runs.filter(pl.col(key) == value))
            outside = _record(runs.filter(pl.col(key) != value))
            lean = None
            if inside["runs"] >= 3 and outside["runs"] >= 3:
                edge_in = (inside["top3"] - inside["expected_top3"]) / inside["runs"]
                edge_out = (outside["top3"] - outside["expected_top3"]) / outside["runs"]
                if edge_in - edge_out >= 0.25:
                    lean = "+"
                elif edge_out - edge_in >= 0.25:
                    lean = "−"
            entry["conditions"][key] = {
                "level": value,
                **inside,
                "elsewhere": outside,
                "lean": lean,
            }
        out[str(horse)] = entry
    return out


# ------------------------------------------------------------------------------ output


def _pct(x: Any) -> str:
    return "—" if x is None else f"{100 * x:.1f} %"


def _x(r: dict[str, Any]) -> str:
    if r.get("value") is None:
        return "—"
    s = f"×{r['value']:.2f}"
    if r.get("low") is not None:
        s += f" [{r['low']:.2f} ; {r['high']:.2f}]"
    return s + (f" **{r['verdict']}**" if r.get("verdict") in ("+", "−") else "")


def render_markdown(rep: dict[str, Any]) -> str:
    lines = [
        f"# Profil des vainqueurs — {rep['discipline_label']}",
        "",
        f"Généré le {rep['generated_at']} · {rep['n_races']} courses, {rep['n_runners']} partants "
        f"du {rep['first_day']} au {rep['last_day']} · marché à T-25 min · {rep['correction']}.",
        "",
        "Lecture : ×1,00 = aucun effet. **+** / **−** : effet qui survit à la correction pour "
        "tests multiples. Descriptif : rien ici n'est une recommandation de pari.",
        "",
        "## Conditions de course (le favori gagne-t-il plus ou moins que sa cote ?)",
        "",
        "| Facteur | Niveau | Courses | Favori gagnant | Attendu par la cote | Favori vs cote | "
        "Cote médiane du gagnant | Gagnant hors 3 premières cotes | Stabilité |",
        "|---|---|---:|---:|---:|---|---:|---:|---|",
    ]
    for f in rep["race_factors"]:
        for lv in f["levels"]:
            lines.append(
                f"| {f['label']} | {lv['level']} | {lv['races']} | {_pct(lv['favourite_win_rate'])} "
                f"| {_pct(lv['favourite_expected'])} | {_x(lv['favourite_vs_odds'])} "
                f"| {lv['winner_median_odds'] or '—'} | {_pct(lv['outsider_win_rate'])} "
                f"| {lv['stability']['verdict']} |"
            )
    lines += [
        "",
        "## Profil des partants",
        "",
        "| Facteur | Niveau | Partants | Victoires | Résultat vs hasard | Cote vs hasard | "
        "Ce que la cote a raté | Top 3 vs cote | Stabilité |",
        "|---|---|---:|---:|---|---:|---|---|---|",
    ]
    for f in rep["runner_factors"]:
        for lv in f["levels"]:
            lines.append(
                f"| {f['label']} | {lv['level']} | {lv['runners']} | {lv['wins']} "
                f"| {_x(lv['result_vs_chance'])} | ×{lv['odds_vs_chance']:.2f} "
                f"| {_x(lv['missed_by_odds'])} | {_x(lv['top3_vs_odds'])} "
                f"| {lv['stability']['verdict']} |"
            )
    return "\n".join(lines) + "\n"


def write_profile(rep: dict[str, Any], runs: Path) -> Path:
    stamp = rep["generated_at"].replace(":", "").replace("-", "")[:15]
    out = runs / f"profile_{rep['discipline']}_{stamp}Z"
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(
        json.dumps(rep, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    (out / "report.md").write_text(render_markdown(rep), encoding="utf-8")
    return out


def latest(runs: Path, prefix: str, discipline: str) -> dict[str, Any] | None:
    """Most recent ``{prefix}_{discipline}_*/report.json``."""
    best: tuple[str, dict[str, Any]] | None = None
    for f in runs.glob(f"{prefix}_{discipline}_*/report.json") if runs.exists() else []:
        try:
            rep = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if best is None or rep.get("generated_at", "") > best[0]:
            best = (rep.get("generated_at", ""), {**rep, "id": f.parent.name})
    return best[1] if best else None
