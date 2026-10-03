"""Historical replay: what the carnet's two picks would have done on every past race.

The carnet only proves what it froze 25 minutes before the off. This replay answers a
weaker but much bigger question -- "over two years, does the model's pick do better than
the favourite?" -- on every finished race since 2024:

* the favourite is the shortest price among the odds known 25 minutes before the off
  (the same market the carnet uses; the PMU's odds history gives it for past races);
* the model's pick is the starter with the highest walk-forward Marché+ probability: the
  model of each month is fitted on earlier months only, so it never sees the race;
* 1 EUR simple gagnant and 1 EUR simple placé on each, paid at the official dividend.

Both picks are counted on exactly the same races (those the walk-forward model covers),
so the two lines compare. It is a reconstruction, never mixed with the carnet's totals.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import polars as pl

PICKS = {"favori": "Favori", "modèle": "Modèle Marché+"}
BETS = ("SG", "SP")


def picks(frame: pl.DataFrame) -> pl.DataFrame:
    """One row per race: the favourite's and the model's numbers and their returns."""
    df = frame.filter(pl.col("p_model").is_not_null() & pl.col("odds").is_not_null())
    if df.is_empty():
        return pl.DataFrame()
    fav = (
        df.sort(["race_id", "odds", "number"])
        .group_by("race_id", maintain_order=True)
        .first()
        .select(
            "race_id",
            "day",
            pl.col("number").alias("fav_number"),
            pl.col("ret_SG").alias("fav_SG"),
            pl.col("ret_SP").alias("fav_SP"),
        )
    )
    top = (
        df.sort(["race_id", "p_model", "number"], descending=[False, True, False])
        .group_by("race_id", maintain_order=True)
        .first()
        .select(
            "race_id",
            pl.col("number").alias("mod_number"),
            pl.col("ret_SG").alias("mod_SG"),
            pl.col("ret_SP").alias("mod_SP"),
        )
    )
    return fav.join(top, on="race_id").sort("day", "race_id")


def daily(per_race: pl.DataFrame) -> list[dict[str, Any]]:
    """Series in the carnet's shape: one per (pick, bet), points per day with running total."""
    out: list[dict[str, Any]] = []
    if per_race.is_empty():
        return out
    for bet in BETS:
        for pick, col in (("favori", f"fav_{bet}"), ("modèle", f"mod_{bet}")):
            # A race counts for a bet only if it paid that kind of bet (no placé with
            # too few starters, for instance): then both picks have a ticket.
            rows = (
                per_race.filter(pl.col(col).is_not_null())
                .group_by("day")
                .agg(
                    pl.len().alias("races"),
                    pl.col(col).sum().alias("returned"),
                )
                .sort("day")
            )
            cum, points = 0.0, []
            for day, races, returned in rows.iter_rows():
                net = float(returned) - races
                cum += net
                points.append(
                    {
                        "day": day.isoformat(),
                        "races": int(races),
                        "stake": float(races),
                        "returned": round(float(returned), 2),
                        "net": round(net, 2),
                        "cum": round(cum, 2),
                    }
                )
            out.append(
                {
                    "strategy": f"{bet} {pick} (historique)",
                    "label": f"{'Gagnant' if bet == 'SG' else 'Placé'} · {PICKS[pick]}",
                    "bet": bet,
                    "pick": pick,
                    "points": points,
                }
            )
    return out


def summary(per_race: pl.DataFrame) -> dict[str, Any]:
    """How often the model leaves the favourite, and the totals of both picks."""
    if per_race.is_empty():
        return {"races": 0}
    n = per_race.height
    differ = per_race.filter(pl.col("fav_number") != pl.col("mod_number"))
    totals: dict[str, Any] = {}
    for bet in BETS:
        for pick, col in (("favori", f"fav_{bet}"), ("modèle", f"mod_{bet}")):
            r = per_race[col].drop_nulls()
            stake = float(r.len())
            ret = float(r.sum()) if stake else 0.0
            totals[f"{bet} {pick}"] = {
                "bets": int(stake),
                "returned": round(ret, 2),
                "net": round(ret - stake, 2),
                "roi": (ret - stake) / stake if stake else None,
            }
    # On the races where the two picks differ, the whole gap is made there.
    gap: dict[str, Any] = {}
    for bet in BETS:
        d = differ.filter(pl.col(f"fav_{bet}").is_not_null())
        gap[bet] = {
            "races": d.height,
            "favori_net": round(float(d[f"fav_{bet}"].sum()) - d.height, 2),
            "modèle_net": round(float(d[f"mod_{bet}"].sum()) - d.height, 2),
        }
    days = per_race["day"]
    return {
        "races": n,
        "first_day": days.min().isoformat(),  # type: ignore[union-attr]
        "last_day": days.max().isoformat(),  # type: ignore[union-attr]
        "differ": differ.height,
        "differ_share": differ.height / n,
        "totals": totals,
        "when_they_differ": gap,
    }


def build_report(
    frame: pl.DataFrame, discipline: str, now: datetime | None = None
) -> dict[str, Any]:
    per_race = picks(frame)
    return {
        "kind": "replay",
        "generated_at": (now or datetime.now(UTC)).isoformat(timespec="seconds"),
        "discipline": discipline,
        "method": (
            "Favori : plus petite cote connue 25 min avant le départ. Modèle : plus forte "
            "probabilité Marché+ walk-forward (modèle du mois ajusté sur les mois précédents). "
            "1 € gagnant et 1 € placé sur chacun, payés au rapport officiel. Reconstitution, "
            "jamais mêlée au carnet."
        ),
        "summary": summary(per_race),
        "series": daily(per_race),
    }


def write_report(rep: dict[str, Any], runs: Path) -> Path:
    """Only the latest replay is kept: it is recomputed whole every night, and the
    nightly commit would otherwise grow by a full history each day."""
    import shutil

    for old in runs.glob(f"replay_{rep['discipline']}_*") if runs.exists() else []:
        shutil.rmtree(old, ignore_errors=True)
    stamp = rep["generated_at"].replace("-", "").replace(":", "")[:15]
    out = runs / f"replay_{rep['discipline']}_{stamp}Z"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "report.json"
    path.write_text(json.dumps(rep, ensure_ascii=False), encoding="utf-8")
    return path
