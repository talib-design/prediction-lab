"""One row per starter: race conditions, the runner, the market, and its past.

Shared by the factor profile (``racing/profile.py``) and the Marché+ model
(``racing/marketplus.py``), for history and for a live race alike, so the two can never
compute a factor differently.

* **Conditions** are grouped into plain-language levels (terrain, temperature, sky,
  wind, starting position, distance, field size, rest, age, sex, weight, distance
  handicap, shoeing, rank in the betting). The thresholds are fixed here, before any
  result was looked at (2026-09-30), and never tuned.
* **The market** is the normalised implied probability from the last quote reported by
  the horizon (T-25 min), as in the backtest. A race enters only if its market is
  complete and coherent (docs/METHODOLOGY.md §9).
* **The past** of a horse, jockey or trainer is read with an as-of join on the race
  *day*, excluding that day: a runner never sees a result from its own day or later
  (the ``result_known_at`` rule of ``events.py``). One function builds it, whether the
  target is a race from 2024 or the race that starts in 25 minutes.

Measures of a finished run:

* ``won``, ``placed`` (top 3), ``exp_top3`` -- the chance of a top-3 finish the odds
  implied (Harville), so "top 3 vs odds" is free of the rank effect below;
* ``gain`` -- places gained on the betting: rank in the betting minus finishing rank
  (unplaced counts as last). +2 means it finished two places better than its odds
  said; ``gain_pct`` is the same divided by (field - 1).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from predlab.racing.events import MAX_OVERROUND, MIN_OVERROUND

HISTORY_START = date(2024, 1, 1)
HORIZON_MINUTES = 25

# Columns every raw frame carries, whether it comes from the database or a live race.
RAW_SCHEMA: dict[str, Any] = {
    "race_id": pl.Utf8,
    "day": pl.Date,
    "discipline": pl.Utf8,
    "venue_code": pl.Utf8,
    "distance_m": pl.Int64,
    "going_label": pl.Utf8,
    "going_value": pl.Float64,
    "temperature_c": pl.Float64,
    "wind_force": pl.Float64,
    "sky": pl.Utf8,
    "number": pl.Int64,
    "horse_id": pl.Utf8,
    "jockey": pl.Utf8,
    "trainer": pl.Utf8,
    "draw": pl.Int64,
    "weight_raw": pl.Int64,
    "age": pl.Int64,
    "sex": pl.Utf8,
    "shoeing": pl.Utf8,
    "handicap_distance": pl.Int64,
    "odds": pl.Float64,
    "position": pl.Int64,
    "finished": pl.Boolean,
    # Added 2026-09-30 for the strategy bench (racing/strategies.py). All pre-race: the
    # musique was checked on 2026-09-28 not to contain the race it is published for.
    "venue_name": pl.Utf8,
    "category": pl.Utf8,
    "prize_eur": pl.Int64,
    "musique": pl.Utf8,
    "blinkers": pl.Utf8,
    "jockey_changed": pl.Boolean,
}

# The factors of the profile, in display order: column, French name, which disciplines.
FACTORS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("going_cat", "Terrain", ("PLAT",)),
    ("temp_band", "Température", ("PLAT", "ATTELE", "MONTE")),
    ("sky_cat", "Ciel", ("PLAT", "ATTELE", "MONTE")),
    ("wind_band", "Vent", ("PLAT", "ATTELE", "MONTE")),
    ("draw_band", "Position au départ", ("PLAT", "ATTELE", "MONTE")),
    ("dist_band", "Distance", ("PLAT", "ATTELE", "MONTE")),
    ("field_band", "Taille du peloton", ("PLAT", "ATTELE", "MONTE")),
    ("rest_band", "Repos depuis la dernière course", ("PLAT", "ATTELE", "MONTE")),
    ("age_band", "Âge", ("PLAT", "ATTELE", "MONTE")),
    ("sex_cat", "Sexe", ("PLAT", "ATTELE", "MONTE")),
    ("weight_band", "Poids porté", ("PLAT",)),
    ("recul_band", "Recul (handicap de distance)", ("ATTELE", "MONTE")),
    ("shoeing_cat", "Ferrure", ("ATTELE", "MONTE")),
    ("odds_band", "Rang dans la cote", ("PLAT", "ATTELE", "MONTE")),
)

# Every level each factor can take, in display order. A test checks ``derive`` never
# produces a label missing from here.
LEVELS: dict[str, tuple[str, ...]] = {
    "going_cat": (
        "PSF (sable fibré)",
        "Bon ou sec",
        "Bon souple",
        "Souple",
        "Très souple",
        "Lourd ou collant",
        "Non mesuré",
    ),
    "temp_band": (
        "Froid (< 10 °C)",
        "Frais (10-17 °C)",
        "Doux (17-24 °C)",
        "Chaud (≥ 24 °C)",
        "Inconnue",
    ),
    "sky_cat": ("Ensoleillé", "Nuageux ou couvert", "Pluie ou averses", "Autre", "Inconnu"),
    "wind_band": ("Faible (< 10)", "Modéré (10-25)", "Fort (≥ 25)", "Inconnu"),
    "draw_band": ("Intérieur (1er tiers)", "Milieu", "Extérieur (dernier tiers)", "Inconnue"),
    "dist_band": (
        "Sprint (< 1 400 m)",
        "Mile (1 400-1 900 m)",
        "Classique (1 900-2 400 m)",
        "Tenue (≥ 2 400 m)",
        "Courte (< 2 200 m)",
        "Moyenne (2 200-2 700 m)",
        "Longue (≥ 2 700 m)",
        "Inconnue",
    ),
    "field_band": ("Petit (≤ 8)", "Moyen (9-13)", "Grand (≥ 14)", "Inconnu"),
    "rest_band": (
        "≤ 14 jours",
        "15-30 jours",
        "31-90 jours",
        "Rentrée (> 90 jours)",
        "Première course connue",
    ),
    "age_band": ("2-3 ans", "4 ans", "5 ans", "6-7 ans", "8 ans et +", "Inconnu"),
    "sex_cat": ("Mâle", "Femelle", "Hongre", "Inconnu"),
    "weight_band": (
        "Plus léger (≤ −1,5 kg)",
        "Dans la moyenne",
        "Plus lourd (≥ +1,5 kg)",
        "Inconnu",
    ),
    "recul_band": ("Sans recul", "25 m", "50 m et +", "Inconnu"),
    "shoeing_cat": ("Déferré des 4", "Déferré partiel", "Protégé", "Ferré (ou non publié)"),
    "odds_band": ("Favori", "2e-3e cote", "4e-6e cote", "7e cote et au-delà", "Non cotée"),
}

# Race-level factors: one value per race (used to describe "these conditions").
RACE_FACTORS = ("going_cat", "temp_band", "sky_cat", "wind_band", "dist_band", "field_band")

# The Marché+ inputs, pre-registered on 2026-09-30 (docs/METHODOLOGY.md §10) before any
# model was fitted. ``log_q`` is the market; every other column is a correction to it.
MODEL_FEATURES: tuple[str, ...] = (
    "f_form",
    "f_going",
    "f_temp",
    "f_new",
    "f_rest",
    "f_jockey",
    "f_trainer",
    "f_draw",
    "f_draw_sprint",
    "f_weight",
    "f_recul",
)

FEATURE_LABELS = {
    "log_q": "Cote (marché)",
    "f_form": "Forme : places gagnées sur la cote, courses passées",
    "f_going": "Préférence du cheval pour ce terrain",
    "f_temp": "Préférence du cheval pour cette température",
    "f_new": "Aucune course connue depuis 2024",
    "f_rest": "Repos (log des jours depuis la dernière course)",
    "f_jockey": "Jockey / driver : victoires vs cote",
    "f_trainer": "Entraîneur : victoires vs cote",
    "f_draw": "Position au départ (0 = intérieur, 1 = extérieur)",
    "f_draw_sprint": "Position au départ, sprints du plat",
    "f_weight": "Poids porté vs moyenne de la course (kg)",
    "f_recul": "Recul au trot (par 25 m)",
}

# Shrinkage: a horse with n runs on a terrain gets sum / (n + k). Fixed, not tuned.
K_FORM, K_PREF, K_PEOPLE = 2.0, 3.0, 3.0


# --------------------------------------------------------------------------- loading


def _market_filter(df: pl.DataFrame) -> pl.DataFrame:
    """Keep races whose every starter is quoted and whose quotes form one market."""
    per_race = df.group_by("race_id").agg(
        pl.col("odds").is_null().any().alias("_missing"),
        (pl.col("odds") <= 1.0).any().alias("_bad"),
        (1.0 / pl.col("odds")).sum().alias("_overround"),
    )
    ok = per_race.filter(
        ~pl.col("_missing")
        & ~pl.col("_bad")
        & pl.col("_overround").is_between(MIN_OVERROUND, MAX_OVERROUND)
    ).select("race_id")
    return df.join(ok, on="race_id", how="semi")


def load_finished(db_path: Path, discipline: str, *, since: date = HISTORY_START) -> pl.DataFrame:
    """Finished races of one discipline since ``since``, coherent markets only, with every
    derived column (conditions, measures, history features)."""
    import duckdb

    con = duckdb.connect(str(db_path), read_only=True)
    try:
        cur = con.execute(
            """
            WITH q AS (
                SELECT o.race_id, o.number, arg_max(o.odds, o.reported_at) AS odds
                FROM odds o JOIN races r USING (race_id)
                WHERE r.is_final AND r.country_code = 'FRA' AND r.discipline = ?
                  AND r.day >= ?
                  AND o.reported_at <= r.off_time - to_minutes(CAST(? AS BIGINT))
                GROUP BY o.race_id, o.number
            )
            SELECT r.race_id, r.day, r.discipline, r.venue_code,
                   CAST(r.distance_m AS BIGINT) AS distance_m,
                   r.going_label, r.going_value, r.temperature_c, r.wind_force, r.sky,
                   CAST(u.number AS BIGINT) AS number, u.horse_id, u.jockey, u.trainer,
                   CAST(u.draw AS BIGINT) AS draw, CAST(u.weight_raw AS BIGINT) AS weight_raw,
                   CAST(u.age AS BIGINT) AS age, u.sex, u.shoeing,
                   CAST(u.handicap_distance AS BIGINT) AS handicap_distance,
                   q.odds, CAST(u.finish_position AS BIGINT) AS position, TRUE AS finished,
                   r.venue_name, r.category, CAST(r.prize_eur AS BIGINT) AS prize_eur,
                   u.form AS musique, u.blinkers, u.jockey_changed
            FROM runners u JOIN races r USING (race_id)
            LEFT JOIN q ON q.race_id = u.race_id AND q.number = u.number
            WHERE r.is_final AND r.country_code = 'FRA' AND r.discipline = ?
              AND r.day >= ? AND u.status = 'PARTANT'
            """,
            [discipline, since, HORIZON_MINUTES, discipline, since],
        )
        rows = cur.fetchall()  # no pyarrow in this project: plain rows, typed below
    finally:
        con.close()
    df = pl.DataFrame(rows, schema=RAW_SCHEMA, orient="row")
    df = _market_filter(df)
    # A race needs a winner to say anything about who wins.
    has_winner = df.group_by("race_id").agg((pl.col("position") == 1).any().alias("w"))
    df = df.join(has_winner.filter("w").select("race_id"), on="race_id", how="semi")
    frame = derive(df)
    return with_history(frame, frame)


@lru_cache(maxsize=6)
def _cached(db_path: str, mtime: float, discipline: str) -> pl.DataFrame:
    return load_finished(Path(db_path), discipline)


def history(db_path: Path, discipline: str) -> pl.DataFrame:
    """``load_finished``, cached until the database file changes (nightly rebuild)."""
    return _cached(str(db_path), db_path.stat().st_mtime, discipline)


def live_frame(
    race: Any, runners: list[Any], odds: Mapping[int, float | None], hist: pl.DataFrame
) -> pl.DataFrame:
    """The same row, for a race not yet run: ``race`` is a domain ``Race``, ``runners``
    its starters, ``odds`` the quotes at the horizon."""
    rows = []
    going, weather = race.going, race.weather
    for x in runners:
        rows.append(
            {
                "race_id": race.race_id,
                "day": race.day,
                "discipline": race.discipline,
                "venue_code": race.venue_code,
                "distance_m": race.distance_m,
                "going_label": going.label if going else None,
                "going_value": going.value if going else None,
                "temperature_c": weather.temperature_c if weather else None,
                "wind_force": weather.wind_force if weather else None,
                "sky": weather.sky if weather else None,
                "number": x.number,
                "horse_id": x.identity_key,
                "jockey": x.jockey,
                "trainer": x.trainer,
                "draw": x.draw,
                "weight_raw": x.weight_raw,
                "age": x.age,
                "sex": x.sex,
                "shoeing": x.shoeing,
                "handicap_distance": x.handicap_distance,
                "odds": odds.get(x.number),
                "position": None,
                "finished": False,
                "venue_name": race.venue_name,
                "category": race.category,
                "prize_eur": race.prize_eur,
                "musique": x.form,
                "blinkers": x.blinkers,
                "jockey_changed": x.jockey_changed,
            }
        )
    df = pl.DataFrame(rows, schema=RAW_SCHEMA)
    return with_history(derive(df), hist)


# --------------------------------------------------------------------------- derived


def _going_cat() -> pl.Expr:
    label = pl.col("going_label").str.to_lowercase().str.strip_chars()
    value = pl.col("going_value")
    by_label = (
        pl.when(label.str.starts_with("psf"))
        .then(pl.lit("PSF (sable fibré)"))
        .when(label.is_in(["bon léger", "léger", "bon", "sec", "très sec"]))
        .then(pl.lit("Bon ou sec"))
        .when(label == "bon souple")
        .then(pl.lit("Bon souple"))
        .when(label == "souple")
        .then(pl.lit("Souple"))
        .when(label == "très souple")
        .then(pl.lit("Très souple"))
        .when(label.is_in(["collant", "lourd", "très lourd"]))
        .then(pl.lit("Lourd ou collant"))
    )
    by_value = (
        pl.when(value <= 3.25)
        .then(pl.lit("Bon ou sec"))
        .when(value <= 3.45)
        .then(pl.lit("Bon souple"))
        .when(value <= 3.75)
        .then(pl.lit("Souple"))
        .when(value <= 4.15)
        .then(pl.lit("Très souple"))
        .when(value.is_not_null())
        .then(pl.lit("Lourd ou collant"))
    )
    return pl.coalesce(by_label, by_value, pl.lit("Non mesuré"))


def _bands(col: str, edges: list[float], labels: list[str], missing: str) -> pl.Expr:
    """``labels[i]`` for values below ``edges[i]``; the last label above every edge."""
    c = pl.col(col)
    expr = pl.when(c.is_null()).then(pl.lit(missing))
    for edge, label in zip(edges, labels[:-1], strict=True):
        expr = expr.when(c < edge).then(pl.lit(label))
    return expr.otherwise(pl.lit(labels[-1]))


def _sky_cat() -> pl.Expr:
    s = pl.col("sky").str.to_lowercase()
    return (
        pl.when(s.is_null())
        .then(pl.lit("Inconnu"))
        .when(s.str.contains("pluie|pluies|averse|ondée|orag|bruine|neige"))
        .then(pl.lit("Pluie ou averses"))
        .when(s.is_in(["soleil", "ensoleillé", "dégagé", "ciel dégagé"]))
        .then(pl.lit("Ensoleillé"))
        .when(s.str.contains("nuag|couvert|voilé|brume|brouillard"))
        .then(pl.lit("Nuageux ou couvert"))
        .otherwise(pl.lit("Autre"))
    )


def derive(df: pl.DataFrame) -> pl.DataFrame:
    """Everything computable from the race itself: market, measures, condition levels."""
    race = "race_id"
    n = pl.len().over(race)
    df = df.with_columns(
        n.cast(pl.Int64).alias("n"),
        ((1.0 / pl.col("odds")) / (1.0 / pl.col("odds")).sum().over(race)).alias("market_p"),
        pl.col("odds").rank("average").over(race).alias("odds_rank"),
        pl.col("draw").rank("average").over(race).alias("draw_rank"),
        (pl.col("weight_raw") / 10.0).alias("weight_kg"),
        (pl.col("handicap_distance") - pl.col("handicap_distance").min().over(race)).alias(
            "recul_m"
        ),
    )
    finish_rank = (
        pl.when(pl.col("position").is_not_null()).then(pl.col("position")).otherwise(pl.col("n"))
    )
    spread = pl.max_horizontal(pl.col("n") - 1, pl.lit(1))
    df = df.with_columns(
        (pl.col("position") == 1).fill_null(False).alias("won"),
        (pl.col("position") <= 3).fill_null(False).alias("placed"),
        pl.when(pl.col("finished"))
        .then(pl.col("odds_rank") - finish_rank)
        .otherwise(None)
        .alias("gain"),
        ((pl.col("draw_rank") - 1) / spread).alias("draw_pct"),
        (pl.col("weight_kg") - pl.col("weight_kg").mean().over(race)).alias("weight_diff"),
        (1.0 / pl.col("n")).alias("fair_p"),
    )
    df = df.with_columns((pl.col("gain") / spread).alias("gain_pct"))
    df = _with_exp_top3(df)
    plat = pl.col("discipline") == "PLAT"
    dist = pl.col("distance_m")
    df = df.with_columns(
        _going_cat().alias("going_cat"),
        _bands(
            "temperature_c",
            [10, 17, 24],
            ["Froid (< 10 °C)", "Frais (10-17 °C)", "Doux (17-24 °C)", "Chaud (≥ 24 °C)"],
            "Inconnue",
        ).alias("temp_band"),
        _sky_cat().alias("sky_cat"),
        _bands(
            "wind_force", [10, 25], ["Faible (< 10)", "Modéré (10-25)", "Fort (≥ 25)"], "Inconnu"
        ).alias("wind_band"),
        pl.when(pl.col("draw_pct").is_null())
        .then(pl.lit("Inconnue"))
        .when(pl.col("draw_pct") < 1 / 3)
        .then(pl.lit("Intérieur (1er tiers)"))
        .when(pl.col("draw_pct") <= 2 / 3)
        .then(pl.lit("Milieu"))
        .otherwise(pl.lit("Extérieur (dernier tiers)"))
        .alias("draw_band"),
        pl.when(dist.is_null())
        .then(pl.lit("Inconnue"))
        .when(plat & (dist < 1400))
        .then(pl.lit("Sprint (< 1 400 m)"))
        .when(plat & (dist < 1900))
        .then(pl.lit("Mile (1 400-1 900 m)"))
        .when(plat & (dist < 2400))
        .then(pl.lit("Classique (1 900-2 400 m)"))
        .when(plat)
        .then(pl.lit("Tenue (≥ 2 400 m)"))
        .when(dist < 2200)
        .then(pl.lit("Courte (< 2 200 m)"))
        .when(dist < 2700)
        .then(pl.lit("Moyenne (2 200-2 700 m)"))
        .otherwise(pl.lit("Longue (≥ 2 700 m)"))
        .alias("dist_band"),
        _bands("n", [9, 14], ["Petit (≤ 8)", "Moyen (9-13)", "Grand (≥ 14)"], "Inconnu").alias(
            "field_band"
        ),
        _bands(
            "age", [4, 5, 6, 8], ["2-3 ans", "4 ans", "5 ans", "6-7 ans", "8 ans et +"], "Inconnu"
        ).alias("age_band"),
        pl.col("sex")
        .replace_strict(
            {"MALES": "Mâle", "FEMELLES": "Femelle", "HONGRES": "Hongre"},
            default="Inconnu",
            return_dtype=pl.Utf8,
        )
        .alias("sex_cat"),
        pl.when(pl.col("weight_diff").is_null())
        .then(pl.lit("Inconnu"))
        .when(pl.col("weight_diff") <= -1.5)
        .then(pl.lit("Plus léger (≤ −1,5 kg)"))
        .when(pl.col("weight_diff") >= 1.5)
        .then(pl.lit("Plus lourd (≥ +1,5 kg)"))
        .otherwise(pl.lit("Dans la moyenne"))
        .alias("weight_band"),
        pl.when(pl.col("recul_m").is_null())
        .then(pl.lit("Inconnu"))
        .when(pl.col("recul_m") <= 0)
        .then(pl.lit("Sans recul"))
        .when(pl.col("recul_m") <= 25)
        .then(pl.lit("25 m"))
        .otherwise(pl.lit("50 m et +"))
        .alias("recul_band"),
        pl.when(pl.col("shoeing").is_null())
        .then(pl.lit("Ferré (ou non publié)"))
        .when(pl.col("shoeing").str.contains("DEFERRE_ANTERIEURS_POSTERIEURS"))
        .then(pl.lit("Déferré des 4"))
        .when(pl.col("shoeing").str.contains("DEFERR"))
        .then(pl.lit("Déferré partiel"))
        .otherwise(pl.lit("Protégé"))
        .alias("shoeing_cat"),
        pl.when(pl.col("odds_rank").is_null())
        .then(pl.lit("Non cotée"))
        .when(pl.col("odds_rank") < 1.5)
        .then(pl.lit("Favori"))
        .when(pl.col("odds_rank") < 3.5)
        .then(pl.lit("2e-3e cote"))
        .when(pl.col("odds_rank") < 6.5)
        .then(pl.lit("4e-6e cote"))
        .otherwise(pl.lit("7e cote et au-delà"))
        .alias("odds_band"),
    )
    return _with_card_extras(df)


def _with_card_extras(df: pl.DataFrame) -> pl.DataFrame:
    """Levels read from the race card itself, added 2026-09-30 for the strategy bench."""
    # Musique, most recent first: "1p4p(25)0pDp" -> positions 1, 4, 10+, disqualified.
    # A real token is one position character followed by the discipline letter; year
    # markers such as "(24)" or a bare "24" before a token are skipped by that rule.
    tokens = pl.col("musique").fill_null("").str.extract_all(r"[0-9DATRS][a-z]").list.head(5)
    pos = tokens.list.eval(
        pl.element()
        .str.slice(0, 1)
        .replace_strict({str(d): d for d in range(1, 10)}, default=10, return_dtype=pl.Int64)
    )
    df = df.with_columns(
        pos.alias("mus_pos"),
        pos.list.len().alias("mus_n"),
    ).with_columns(
        pl.col("mus_pos").list.first().alias("mus_last"),
        pl.col("mus_pos").list.eval(pl.element() <= 3).list.sum().alias("mus_top3"),
    )
    cat = pl.col("category").fill_null("")
    return df.with_columns(
        pl.when(pl.col("mus_n") == 0)
        .then(pl.lit("Aucune course (musique vide)"))
        .when(pl.col("mus_last") == 1)
        .then(pl.lit("Gagnant de sa dernière course"))
        .when(pl.col("mus_last") <= 3)
        .then(pl.lit("2e-3e la dernière fois"))
        .when(pl.col("mus_last") <= 9)
        .then(pl.lit("4e-9e la dernière fois"))
        .otherwise(pl.lit("Non placé ou arrêté la dernière fois"))
        .alias("mus_last_band"),
        pl.when(pl.col("mus_n") == 0)
        .then(pl.lit("Aucune course (musique vide)"))
        .when(pl.col("mus_top3") >= 3)
        .then(pl.lit("Régulier : 3 top 3 ou plus sur 5"))
        .when(pl.col("mus_top3") >= 1)
        .then(pl.lit("Parfois placé : 1-2 top 3 sur 5"))
        .otherwise(pl.lit("Aucun top 3 sur ses dernières courses"))
        .alias("mus_form_band"),
        pl.when(cat.str.contains("GROUPE"))
        .then(pl.lit("Groupe (I à III)"))
        .when(cat.str.contains("HANDICAP"))
        .then(pl.lit("Handicap"))
        .when(cat.str.contains("RECLAMER"))
        .then(pl.lit("À réclamer"))
        .when(cat.str.contains("CONDITION"))
        .then(pl.lit("Course à conditions"))
        .otherwise(pl.lit("Autre ou inconnue"))
        .alias("category_cat"),
        _bands(
            "odds",
            [3, 5, 8, 13, 21],
            ["Cote < 3", "Cote 3 à 5", "Cote 5 à 8", "Cote 8 à 13", "Cote 13 à 21", "Cote ≥ 21"],
            "Non cotée",
        ).alias("odds_range"),
        pl.col("blinkers")
        .replace_strict(
            {
                "SANS_OEILLERES": "Sans oeillères",
                "OEILLERES_AUSTRALIENNES": "Oeillères australiennes",
                "OEILLERES_CLASSIQUE": "Oeillères classiques",
            },
            default="Inconnu",
            return_dtype=pl.Utf8,
        )
        .alias("blinkers_cat"),
        pl.when(pl.col("jockey_changed"))
        .then(pl.lit("Changement de jockey annoncé"))
        .otherwise(pl.lit("Jockey prévu"))
        .alias("jockey_change_cat"),
        pl.col("venue_name").fill_null("Inconnu").alias("venue"),
    )


def harville_top3(p: np.ndarray) -> np.ndarray:
    """P(finish in the first 3) for each runner under Harville, vectorised.

    Same numbers as ``orders.top_k_probabilities(p, 3)`` (a test checks it), in
    O(n²) array operations instead of Python loops: it runs on every race since 2024.
    """
    p = np.asarray(p, dtype=np.float64)
    if p.size <= 3:
        return np.ones_like(p)
    rest = 1.0 - p
    second = p * ((p / rest).sum() - p / rest)
    den = rest[:, None] - p[None, :]  # 1 - p_j - p_m
    with np.errstate(divide="ignore", invalid="ignore"):
        a = np.where(den > 0, (p[:, None] * p[None, :]) / (rest[:, None] * den), 0.0)
    np.fill_diagonal(a, 0.0)
    third = p * (a.sum() - a.sum(1) - a.sum(0))
    return np.minimum(p + second + third, 1.0)


def _with_exp_top3(df: pl.DataFrame) -> pl.DataFrame:
    df = df.with_row_index("_i").sort(["race_id", "number"])
    race = df["race_id"].to_numpy()
    q = df["market_p"].to_numpy().astype(np.float64)
    out = np.full(len(q), np.nan)
    if len(q):
        starts = np.flatnonzero(np.r_[True, race[1:] != race[:-1]])
        for s, e in zip(starts, np.r_[starts[1:], len(q)], strict=True):
            if not np.isnan(q[s:e]).any():
                out[s:e] = harville_top3(q[s:e])
    return df.with_columns(pl.Series("exp_top3", out).fill_nan(None)).sort("_i").drop("_i")


# --------------------------------------------------------------------------- history

_HISTORY_KEYS: dict[str, tuple[str, ...]] = {
    "h": ("horse_id",),
    "hg": ("horse_id", "going_cat"),
    "ht": ("horse_id", "temp_band"),
    "j": ("jockey",),
    "t": ("trainer",),
    "jt": ("jockey", "trainer"),
}
# What a horse's last run looked like (distance, prize, blinkers): its latest day.
_LAST_OF_HORSE = ("distance_m", "prize_eur", "blinkers")


def _cumulative(hist: pl.DataFrame, keys: tuple[str, ...], prefix: str) -> pl.DataFrame:
    """Per key and day: running totals *including* that day (the join excludes it)."""
    daily = (
        hist.filter(pl.all_horizontal(pl.col(k).is_not_null() for k in keys))
        .group_by([*keys, "day"])
        .agg(
            pl.len().alias("n"),
            pl.col("gain_pct").sum().alias("gain"),
            pl.col("gain").sum().alias("places"),
            pl.col("won").sum().alias("wins"),
            pl.col("market_p").sum().alias("exp"),
            pl.col("placed").sum().alias("top3"),
            pl.col("exp_top3").sum().alias("exp3"),
            *(
                [pl.col(c).last().alias(f"last_{c}") for c in _LAST_OF_HORSE]
                if prefix == "h"
                else []
            ),
        )
        .sort("day")
    )
    cum = [
        pl.col(c).cum_sum().over(list(keys)).alias(f"{prefix}_{c}")
        for c in ("n", "gain", "places", "wins", "exp", "top3", "exp3")
    ]
    extra = (
        [pl.col(f"last_{c}").alias(f"h_last_{c}") for c in _LAST_OF_HORSE] if prefix == "h" else []
    )
    return daily.select(*keys, "day", *cum, *extra, pl.col("day").alias(f"{prefix}_last"))


def with_history(targets: pl.DataFrame, hist: pl.DataFrame) -> pl.DataFrame:
    """Add, for each target runner, its past strictly before the target's day."""
    out = targets.with_row_index("_row").sort("day")
    finished = hist.filter(pl.col("finished"))
    for prefix, keys in _HISTORY_KEYS.items():
        right = _cumulative(finished, keys, prefix)
        out = out.join_asof(
            right,
            on="day",
            by=list(keys),
            strategy="backward",
            allow_exact_matches=False,
            check_sortedness=False,
        )
    out = out.sort("_row").drop("_row")
    days = (pl.col("day") - pl.col("h_last")).dt.total_days()
    out = out.with_columns(days.alias("days_since"))
    out = out.with_columns(
        _bands(
            "days_since",
            [15, 31, 91],
            ["≤ 14 jours", "15-30 jours", "31-90 jours", "Rentrée (> 90 jours)"],
            "Première course connue",
        ).alias("rest_band")
    )
    return add_model_features(_with_history_bands(out))


def _people_band(prefix: str, who: str, min_exp: float) -> pl.Expr:
    wins, exp = pl.col(f"{prefix}_wins").fill_null(0), pl.col(f"{prefix}_exp").fill_null(0.0)
    ratio = wins / exp
    return (
        pl.when(exp < min_exp)
        .then(pl.lit(f"{who} peu connu"))
        .when(ratio >= 1.2)
        .then(pl.lit(f"{who} en réussite (≥ ×1,2 vs cote)"))
        .when(ratio <= 0.8)
        .then(pl.lit(f"{who} en difficulté (≤ ×0,8 vs cote)"))
        .otherwise(pl.lit(f"{who} dans la norme"))
    )


def _with_history_bands(df: pl.DataFrame) -> pl.DataFrame:
    """Levels built on the past (strictly before the race day), for the strategy bench."""
    dist = pl.col("distance_m") - pl.col("h_last_distance_m")
    prize = pl.col("prize_eur") / pl.col("h_last_prize_eur")
    was = pl.col("h_last_blinkers").fill_null("SANS_OEILLERES")
    now = pl.col("blinkers").fill_null("SANS_OEILLERES")
    first = pl.col("h_n").is_null()
    excess = (pl.col("hg_top3") - pl.col("hg_exp3")) / pl.col("hg_n")
    return df.with_columns(
        pl.when(first)
        .then(pl.lit("Première course connue"))
        .when(dist.is_null())
        .then(pl.lit("Distance inconnue"))
        .when(dist <= -200)
        .then(pl.lit("Raccourcit (≥ 200 m)"))
        .when(dist >= 200)
        .then(pl.lit("Rallonge (≥ 200 m)"))
        .otherwise(pl.lit("Même distance"))
        .alias("dist_change"),
        pl.when(first)
        .then(pl.lit("Première course connue"))
        .when(prize.is_null() | prize.is_nan())
        .then(pl.lit("Allocation inconnue"))
        .when(prize <= 0.75)
        .then(pl.lit("Descend de niveau (allocation −25 %)"))
        .when(prize >= 1.33)
        .then(pl.lit("Monte de niveau (allocation +33 %)"))
        .otherwise(pl.lit("Même niveau"))
        .alias("class_change"),
        pl.when(first)
        .then(pl.lit("Première course connue"))
        .when((was == "SANS_OEILLERES") & (now != "SANS_OEILLERES"))
        .then(pl.lit("Met des oeillères"))
        .when((was != "SANS_OEILLERES") & (now == "SANS_OEILLERES"))
        .then(pl.lit("Retire ses oeillères"))
        .otherwise(pl.lit("Équipement inchangé"))
        .alias("blinkers_change"),
        _people_band("j", "Jockey", 5.0).alias("jockey_form"),
        _people_band("t", "Entraîneur", 5.0).alias("trainer_form"),
        _people_band("jt", "Duo jockey-entraîneur", 2.0).alias("duo_form"),
        pl.when(pl.col("going_cat") == "Non mesuré")
        .then(pl.lit("Terrain non mesuré"))
        .when(pl.col("hg_n").fill_null(0) < 2)
        .then(pl.lit("Peu d'expérience de ce terrain"))
        .when(excess >= 0.2)
        .then(pl.lit("Réussit sur ce terrain"))
        .when(excess <= -0.2)
        .then(pl.lit("Échoue sur ce terrain"))
        .otherwise(pl.lit("Neutre sur ce terrain"))
        .alias("going_lean"),
    )


def add_model_features(df: pl.DataFrame) -> pl.DataFrame:
    def shrunk(prefix: str, k: float) -> pl.Expr:
        return pl.col(f"{prefix}_gain").fill_null(0.0) / (pl.col(f"{prefix}_n").fill_null(0) + k)

    def ae(prefix: str) -> pl.Expr:
        return (
            (pl.col(f"{prefix}_wins").fill_null(0) + K_PEOPLE)
            / (pl.col(f"{prefix}_exp").fill_null(0.0) + K_PEOPLE)
        ).log()

    sprint = (pl.col("discipline") == "PLAT") & (pl.col("distance_m") < 1400)
    draw = (pl.col("draw_pct") - 0.5).fill_null(0.0).fill_nan(0.0)
    return df.with_columns(
        pl.col("market_p").log().alias("log_q"),
        shrunk("h", K_FORM).alias("f_form"),
        pl.when(pl.col("going_cat") == "Non mesuré")
        .then(0.0)
        .otherwise(shrunk("hg", K_PREF))
        .alias("f_going"),
        pl.when(pl.col("temp_band") == "Inconnue")
        .then(0.0)
        .otherwise(shrunk("ht", K_PREF))
        .alias("f_temp"),
        pl.col("h_n").is_null().cast(pl.Float64).alias("f_new"),
        pl.col("days_since").clip(1, 365).cast(pl.Float64).log1p().fill_null(0.0).alias("f_rest"),
        ae("j").alias("f_jockey"),
        ae("t").alias("f_trainer"),
        draw.alias("f_draw"),
        pl.when(sprint).then(draw).otherwise(0.0).alias("f_draw_sprint"),
        pl.col("weight_diff").fill_null(0.0).fill_nan(0.0).alias("f_weight"),
        (pl.col("recul_m").fill_null(0) / 25.0).cast(pl.Float64).alias("f_recul"),
    )


def rest_log(days: float) -> float:
    """Exposed for tests: the ``f_rest`` transform."""
    return math.log1p(min(max(days, 1.0), 365.0))
