"""The lab: new criteria for Marché+, each tested once by a rule written before the test.

How the model "learns" a new criterion without fooling itself
-------------------------------------------------------------
Marché+ re-fits its weights every night, but its list of criteria is fixed: a model
free to pick among hundreds of candidates always finds coincidences (the bench saw it:
0 of 200 combinations found on 2024 held on 2025-2026). So a new criterion goes through
this lab instead:

1. **registered first** -- the candidate, its definition and the decision rule are
   appended to the hypothesis registry (hash-chained, committed by the nightly git pass)
   *before* any result exists;
2. **tested once** -- challenger = Marché+ v1 + the candidate, base = Marché+ v1, both
   fitted by the same procedure on the same races; compared on races neither has seen;
3. **decided by the rule**, recorded whatever the outcome, never retested under the same
   name (a revised definition is a new candidate).

Decision rule (docs/METHODOLOGY.md §12), on the per-race log loss difference
challenger − base on the test races:

* SUPPORTED   the 99 % interval is entirely below 0 *and* the gain holds in every test
              calendar year (99 %, not 95 %: several candidates share one test window);
* REJECTED    the 99 % interval is entirely above 0 (the criterion makes it worse);
* INCONCLUSIVE otherwise -- "we could not see it" is not "it is not there".

A SUPPORTED criterion is not wired into the live model automatically: it becomes the
proposal for the next model version, and the carnet then judges that version on races
nobody has seen.

Two kinds of candidates:

* ``history``: computable from the race card and past performances for every race since
  2024. Split = the model's pre-registered one (train 2024 H1, validation 2024 H2 for λ,
  test 2025 onwards).
* ``live``: needs the odds *movement* before the off. The PMU history only keeps one
  pre-off quote (about 30 min before) and the final one, so the movement exists only for
  races the collector followed live (Mac awake). Evaluated once ``min_races`` such races
  exist: first 60 % (by date) to fit, last 40 % to test.

The "agent" is this nightly loop: it registers every candidate of the catalogue that is
not yet in the registry, and runs the pending tests whose data is ready. New candidates
are added to the catalogue in code review (by Chris or Claude), never generated and
tested in the same breath.
"""

from __future__ import annotations

import json
import math
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from predlab.core.clock import utcnow
from predlab.eval.uncertainty import block_bootstrap
from predlab.racing.backtest import PREREGISTERED_SPLIT
from predlab.racing.features import HISTORY_START, K_PEOPLE, MODEL_FEATURES
from predlab.racing.marketplus import LAMBDAS, MIN_TRAIN_RACES, design, fit, race_log_loss
from predlab.registry.hypotheses import Hypothesis, HypothesisRegistry, Origin, Status

LEVEL = 0.99
LIVE_LAMBDA = 1000.0
LIVE_TRAIN_SHARE = 0.6
EARLY_WINDOW = (120, 45)  # minutes before the off: the "early" quote of the movement

# ---------------------------------------------------------------------------- catalogue


@dataclass(frozen=True)
class Candidate:
    id: str
    label: str
    hypothesis: str
    disciplines: tuple[str, ...]
    origin: Origin
    source: str = "history"  # or "live"
    expr: Callable[[], pl.Expr] | None = None
    min_races: int = 1000  # live candidates only
    # "criterion": a new factor for the model; "calibration": the champion's
    # probabilities made honest (p ∝ p^tau); "rule": when to bet (racing/champion.py).
    kind: str = "criterion"
    # Set for a criterion proposed after looking at results (the critic agent, the weekly
    # dossier): it is judged only on races run from this day on -- and never before the
    # day after its registration -- never on the history it was found in (arena.py).
    fresh_from: date | None = None

    @property
    def column(self) -> str:
        return f"c_{self.id}"


def _musique_tokens() -> pl.Expr:
    return pl.col("musique").fill_null("").str.extract_all(r"[0-9DATRS][a-z]").list.head(5)


CANDIDATES: tuple[Candidate, ...] = (
    Candidate(
        "drift",
        "Mouvement de cote avant le départ",
        "Un cheval dont la cote baisse entre 2 h et 45 min avant le départ (l'argent arrive "
        "dessus) gagne plus souvent que sa cote à 25 min ne le dit. Mesure : log q à T-25 "
        "moins log q de la première cote relevée entre T-120 et T-45 (probabilités "
        "normalisées par course).",
        ("PLAT", "ATTELE", "MONTE"),
        Origin.FOLK_HEURISTIC,
        source="live",
        min_races=1000,
    ),
    Candidate(
        "class_drop",
        "Descend de catégorie",
        "Un cheval qui court pour une allocation plus faible qu'à sa dernière course est "
        "sous-estimé. Mesure : log(allocation précédente / allocation du jour), bornée à ±2.",
        ("PLAT", "ATTELE", "MONTE"),
        Origin.FOLK_HEURISTIC,
        expr=lambda: (
            (pl.col("h_last_prize_eur") / pl.col("prize_eur"))
            .log()
            .clip(-2.0, 2.0)
            .fill_null(0.0)
            .fill_nan(0.0)
        ),
    ),
    Candidate(
        "dist_change",
        "Change de distance",
        "Un changement de distance marqué par rapport à la dernière course pénalise plus "
        "que le marché ne le pense. Mesure : |distance − distance précédente| en km.",
        ("PLAT", "ATTELE", "MONTE"),
        Origin.FOLK_HEURISTIC,
        expr=lambda: (
            ((pl.col("distance_m") - pl.col("h_last_distance_m")).abs() / 1000.0)
            .cast(pl.Float64)
            .fill_null(0.0)
        ),
    ),
    Candidate(
        "blinkers_first",
        "Met des oeillères",
        "Un cheval qui met des oeillères alors qu'il n'en portait pas progresse plus que "
        "le marché ne l'anticipe.",
        ("PLAT",),
        Origin.FOLK_HEURISTIC,
        expr=lambda: (pl.col("blinkers_change") == "Met des oeillères").cast(pl.Float64),
    ),
    Candidate(
        "jockey_change",
        "Changement de jockey",
        "Un changement de jockey (signalé par le PMU) dit quelque chose que la cote n'a pas "
        "entièrement intégré.",
        ("PLAT", "ATTELE", "MONTE"),
        Origin.FOLK_HEURISTIC,
        expr=lambda: pl.col("jockey_changed").cast(pl.Float64).fill_null(0.0),
    ),
    Candidate(
        "duo",
        "Réussite du duo jockey-entraîneur",
        "Le duo jockey-entraîneur a sa propre réussite, au-delà de celle de chacun. Mesure : "
        "log des victoires sur victoires attendues du duo depuis 2024, lissé.",
        ("PLAT", "ATTELE", "MONTE"),
        Origin.FOLK_HEURISTIC,
        expr=lambda: (
            (pl.col("jt_wins").fill_null(0) + K_PEOPLE)
            / (pl.col("jt_exp").fill_null(0.0) + K_PEOPLE)
        ).log(),
    ),
    Candidate(
        "musique_top3",
        "Régularité dans la musique",
        "La part de places dans les 3 premiers sur les 5 dernières courses de la musique "
        "(qui remonte avant 2024) ajoute à la forme mesurée depuis 2024.",
        ("PLAT", "ATTELE", "MONTE"),
        Origin.FOLK_HEURISTIC,
        expr=lambda: (
            pl.col("mus_top3").fill_null(0).cast(pl.Float64)
            / pl.col("mus_n").fill_null(0).clip(1, None).cast(pl.Float64)
        ),
    ),
    Candidate(
        "deferre4",
        "Déferré des quatre pieds (trot)",
        "Au trot, un cheval déferré des quatre pieds va plus vite que ne le dit sa cote.",
        ("ATTELE", "MONTE"),
        Origin.FOLK_HEURISTIC,
        expr=lambda: (
            pl.col("shoeing")
            .fill_null("")
            .str.contains("DEFERRE_ANTERIEURS_POSTERIEURS")
            .cast(pl.Float64)
        ),
    ),
    Candidate(
        "dq_rate",
        "Fautes passées (trot)",
        "Au trot, un cheval souvent disqualifié (D dans la musique) gagne moins que sa cote "
        "ne le dit. Mesure : part de D sur les 5 dernières courses.",
        ("ATTELE", "MONTE"),
        Origin.FOLK_HEURISTIC,
        expr=lambda: (
            _musique_tokens()
            .list.eval(pl.element().str.starts_with("D"))
            .list.sum()
            .cast(pl.Float64)
            / _musique_tokens().list.len().clip(1, None).cast(pl.Float64)
        ),
    ),
)

# Added 2026-10-05 with the objective "beat the favourite" (racing/champion.py), before
# any of them was looked at against results.
CANDIDATES = (
    *CANDIDATES,
    Candidate(
        "logq2",
        "Biais favori-outsider non linéaire",
        "Le marché ne se trompe pas de la même façon sur les favoris et sur les outsiders : "
        "un terme en carré de log q (probabilité de la cote) corrige une erreur que la "
        "correction en puissance actuelle ne capte pas.",
        ("PLAT", "ATTELE", "MONTE"),
        Origin.LITERATURE,
        expr=lambda: (pl.col("log_q") ** 2).fill_null(0.0).fill_nan(0.0),
    ),
    Candidate(
        "fls_field",
        "Biais de la cote selon la taille du champ",
        "Le biais favori-outsider change avec le nombre de partants : log q × (partants − 10) "
        "/ 5 laisse le modèle corriger davantage la cote dans les grands champs.",
        ("PLAT", "ATTELE", "MONTE"),
        Origin.LITERATURE,
        expr=lambda: (
            (pl.col("log_q") * (pl.col("n").cast(pl.Float64) - 10.0) / 5.0)
            .fill_null(0.0)
            .fill_nan(0.0)
        ),
    ),
    Candidate(
        "last_win",
        "A gagné sa dernière course",
        "Un cheval qui vient de gagner est surjoué par le public : il gagne moins souvent que "
        "sa cote ne le dit. Mesure : 1 si la musique commence par une victoire.",
        ("PLAT", "ATTELE", "MONTE"),
        Origin.FOLK_HEURISTIC,
        expr=lambda: (pl.col("mus_last") == 1).cast(pl.Float64).fill_null(0.0),
    ),
    Candidate(
        "young",
        "Jeune cheval en progrès",
        "Les chevaux de 2 et 3 ans (4 ans et moins au trot) progressent vite d'une course à "
        "l'autre, plus vite que la cote ne l'intègre.",
        ("PLAT", "ATTELE", "MONTE"),
        Origin.FOLK_HEURISTIC,
        expr=lambda: (
            pl.when(pl.col("discipline") == "PLAT")
            .then(pl.col("age") <= 3)
            .otherwise(pl.col("age") <= 4)
            .cast(pl.Float64)
            .fill_null(0.0)
        ),
    ),
    Candidate(
        "trainer_opinion",
        "Avis de l'entraîneur",
        "Au trot, le PMU publie avant la course l'avis de l'entraîneur (positif, neutre ou "
        "négatif). Le public n'en tient pas assez compte : un avis positif gagne plus souvent, "
        "un avis négatif moins souvent, que la cote ne le dit. Mesure : +1 positif, −1 négatif, "
        "0 neutre ou absent. Ajouté le 2026-10-05 sans aucun regard sur les résultats "
        "(seulement sa présence : 82 à 100 % des partants du trot depuis 2024, positif ou "
        "négatif pour 11 à 18 %).",
        ("ATTELE", "MONTE"),
        Origin.HUMAN,
        expr=lambda: (
            pl.when(pl.col("trainer_opinion") == "POSITIF")
            .then(1.0)
            .when(pl.col("trainer_opinion") == "NEGATIF")
            .then(-1.0)
            .otherwise(0.0)
        ),
    ),
    Candidate(
        "calibration",
        "Calibrer les probabilités du modèle",
        "Les probabilités de Marché+ sont trop confiantes sur ses meilleurs choix (annoncé "
        "61 %, réalisé 52 %). Une correction p ∝ p^τ, τ ajusté sur la validation, rend la "
        "prévision plus juste. Elle ne change pas le cheval choisi, seulement sa probabilité.",
        ("PLAT", "ATTELE", "MONTE"),
        Origin.HUMAN,
        kind="calibration",
    ),
    Candidate(
        "value105",
        "Ne jouer que les chevaux mal cotés",
        "Parier en simple gagnant seulement quand probabilité du modèle × cote ≥ 1,05 rapporte "
        "plus, par euro misé, que le favori. Seuil trouvé en explorant tout l'historique le "
        "2026-10-04 : jugé uniquement sur des courses postérieures à cette exploration.",
        ("PLAT", "ATTELE", "MONTE"),
        Origin.HUMAN,
        kind="rule",
    ),
)

BY_ID = {c.id: c for c in CANDIDATES}


def key(candidate: Candidate, discipline: str) -> str:
    return f"{candidate.id}:{discipline}"


RULE = (
    "Règle fixée avant le test : challenger = Marché+ v1 + ce critère, comparé à Marché+ v1 "
    "ajusté de la même façon, sur des courses qu'aucun des deux n'a vues. Retenu si "
    "l'intervalle à 99 % de l'écart de log loss est entièrement sous 0 et si le gain tient "
    "chaque année de test ; rejeté s'il est entièrement au-dessus ; sinon non concluant."
)


# -------------------------------------------------------------------------- evaluation


def early_quotes(db_path: Path, discipline: str, since: date = HISTORY_START) -> pl.DataFrame:
    """First quote of each starter between T-120 and T-45 (races followed live only)."""
    import duckdb

    hi, lo = EARLY_WINDOW
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        rows = con.execute(
            """
            SELECT o.race_id, CAST(o.number AS BIGINT), arg_min(o.odds, o.reported_at)
            FROM odds o JOIN races r USING (race_id)
            WHERE r.is_final AND r.country_code = 'FRA' AND r.discipline = ? AND r.day >= ?
              AND o.odds > 1
              AND o.reported_at BETWEEN r.off_time - to_minutes(CAST(? AS BIGINT))
                                    AND r.off_time - to_minutes(CAST(? AS BIGINT))
            GROUP BY o.race_id, o.number
            """,
            [discipline, since, hi, lo],
        ).fetchall()
    finally:
        con.close()
    return pl.DataFrame(
        rows,
        schema={"race_id": pl.Utf8, "number": pl.Int64, "odds_early": pl.Float64},
        orient="row",
    )


def with_drift(frame: pl.DataFrame, early: pl.DataFrame) -> pl.DataFrame:
    """Races where every starter has an early quote, with ``c_drift``."""
    df = frame.join(early, on=["race_id", "number"], how="left")
    complete = df.group_by("race_id").agg(pl.col("odds_early").is_not_null().all().alias("ok"))
    df = df.join(complete.filter("ok").select("race_id"), on="race_id")
    q = 1.0 / pl.col("odds_early")
    return df.with_columns(
        (pl.col("log_q") - (q / q.sum().over("race_id")).log()).alias("c_drift")
    ).drop("odds_early")


def add_candidates(frame: pl.DataFrame, discipline: str) -> pl.DataFrame:
    """Every history candidate's column for this discipline."""
    exprs = [
        c.expr().alias(c.column)
        for c in CANDIDATES
        if c.source == "history"
        and c.kind == "criterion"
        and c.expr is not None
        and discipline in c.disciplines
    ]
    return frame.with_columns(exprs) if exprs else frame


def _fit_select(
    parts: dict[str, pl.DataFrame], features: tuple[str, ...], lams: tuple[float, ...]
) -> tuple[np.ndarray, np.ndarray, dict[str, Any], float]:
    """Standardise on train, fit each λ, keep the best on validation (or the only λ)."""
    x = parts["train"].select(features).to_numpy().astype(np.float64)
    means, stds = x.mean(0), x.std(0)
    stds = np.where(stds > 1e-9, stds, 0.0)
    mask = np.r_[True, stds > 0]
    d_train = design(parts["train"], means, stds, features)
    if len(lams) == 1 or "validation" not in parts:
        best = fit(d_train, lams[0], mask)
        return means, stds, best, lams[0]
    d_val = design(parts["validation"], means, stds, features)
    tries = [
        (float(race_log_loss(d_val, (f := fit(d_train, lam, mask))["theta"]).mean()), lam, f)
        for lam in lams
    ]
    _, lam, best = min(tries, key=lambda t: t[0])
    return means, stds, best, lam


def compare(parts: dict[str, pl.DataFrame], column: str, lams: tuple[float, ...]) -> dict[str, Any]:
    """Base vs base + ``column`` on ``parts["test"]``, per-race log loss difference."""
    base = MODEL_FEATURES
    chal = (*MODEL_FEATURES, column)
    mb, sb, fb, lb = _fit_select(parts, base, lams)
    mc, sc, fc, lc = _fit_select(parts, chal, lams)
    db = design(parts["test"], mb, sb, base)
    dc = design(parts["test"], mc, sc, chal)
    diff = race_log_loss(dc, fc["theta"]) - race_log_loss(db, fb["theta"])
    ci = block_bootstrap(diff, n_resamples=2000, level=LEVEL, seed=0)
    years: dict[str, dict[str, float]] = {}
    for y in sorted({int(str(d)[:4]) for d in dc.days}):
        sel = np.array([int(str(d)[:4]) == y for d in dc.days])
        years[str(y)] = {"races": int(sel.sum()), "difference": float(diff[sel].mean())}
    beta, se = float(fc["theta"][-1]), float(fc["se"][-1])
    sd = float(sc[-1])
    return {
        "races": {k: int(v["race_id"].n_unique()) for k, v in parts.items()},
        "test_days": [str(dc.days[0]), str(dc.days[-1])] if len(dc.days) else None,
        "lambda": {"base": lb, "challenger": lc},
        "difference": float(diff.mean()),
        "ci_low": ci.low,
        "ci_high": ci.high,
        "level": LEVEL,
        "by_year": years,
        "beta": beta,
        "beta_low": beta - 2.575829 * se,
        "beta_high": beta + 2.575829 * se,
        "per_sd": math.exp(beta) if sd > 0 else None,
        "sd": sd,
    }


def verdict(res: dict[str, Any], need_every_year: bool) -> tuple[Status, str]:
    d, lo, hi = res["difference"], res["ci_low"], res["ci_high"]
    years_ok = all(v["difference"] < 0 for v in res["by_year"].values())
    span = f"écart {d:+.4f} (IC 99 % {lo:+.4f} à {hi:+.4f})"
    if hi < 0 and (years_ok or not need_every_year):
        return Status.SUPPORTED, f"Retenu : {span}. Proposé pour la prochaine version du modèle."
    if hi < 0:
        return Status.INCONCLUSIVE, f"Gain global ({span}) mais pas chaque année : non retenu."
    if lo > 0:
        return Status.REJECTED, f"Rejeté : le critère dégrade la prévision, {span}."
    if abs(d) < 0.0005 and hi - lo < 0.003:
        return (
            Status.INCONCLUSIVE,
            f"Aucun gain mesurable : {span}. Probablement déjà dans la cote.",
        )
    return Status.INCONCLUSIVE, f"Pas de différence démontrée : {span}."


def evaluate_history(frame: pl.DataFrame, candidate: Candidate) -> dict[str, Any] | None:
    """None when the train window is too small (the discipline's history is not ready)."""
    s = PREREGISTERED_SPLIT
    parts = {
        "train": frame.filter(pl.col("day") <= s.train_end),
        "validation": frame.filter(
            (pl.col("day") > s.train_end) & (pl.col("day") <= s.validation_end)
        ),
        "test": frame.filter(pl.col("day") > s.validation_end),
    }
    if (
        parts["train"]["race_id"].n_unique() < MIN_TRAIN_RACES
        or parts["test"]["race_id"].n_unique() < 300
    ):
        return None
    return compare(parts, candidate.column, LAMBDAS)


def evaluate_live(frame: pl.DataFrame, candidate: Candidate) -> tuple[int, dict[str, Any] | None]:
    """(eligible races, result or None while fewer than ``min_races``)."""
    races = frame.select("race_id", "day").unique().sort("day", "race_id")
    n = races.height
    if n < candidate.min_races:
        return n, None
    cut = races["race_id"][: int(n * LIVE_TRAIN_SHARE)].to_list()
    train = frame.filter(pl.col("race_id").is_in(cut))
    test = frame.filter(~pl.col("race_id").is_in(cut))
    return n, compare({"train": train, "test": test}, candidate.column, (LIVE_LAMBDA,))


# ---------------------------------------------------------------------------- the loop


def _current_by_experiment(reg: HypothesisRegistry) -> dict[str, Hypothesis]:
    return {h.experiment: h for h in reg.current() if h.experiment}


SUPERSEDED = (
    "Remplacé avant tout test par le protocole « battre le favori » du 2026-10-05 "
    "(racing/champion.py) : le même critère y est réenregistré contre le champion, sur "
    "l'historique étendu à 2020."
)


def register(reg: HypothesisRegistry, discipline: str) -> list[str]:
    """Protocol 1 (2026-10-03), kept for the live candidate only: the odds movement, judged
    on races followed live. Every other candidate goes through racing/arena.py."""
    known = _current_by_experiment(reg)
    added = []
    for c in CANDIDATES:
        if c.source != "live" or discipline not in c.disciplines or key(c, discipline) in known:
            continue
        reg.add(
            Hypothesis(
                description=f"{c.label} ({discipline}). {c.hypothesis} {RULE}",
                origin=c.origin,
                dataset=discipline,
                experiment=key(c, discipline),
                status=Status.PROPOSED,
            )
        )
        added.append(key(c, discipline))
    return added


def _save(lab_dir: Path, name: str, payload: dict[str, Any]) -> None:
    out = lab_dir / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name.replace(':', '_')}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8"
    )


def run_pending(
    reg: HypothesisRegistry,
    frame: pl.DataFrame,
    db_path: Path,
    lab_dir: Path,
    discipline: str,
    *,
    max_tests: int = 3,
    now: datetime | None = None,
) -> list[str]:
    """Run the registered tests whose data is ready; at most ``max_tests`` per call.

    ``frame`` is ``load_finished(db_path, discipline)``. Returns one line per test run or
    progress update.
    """
    now = now or utcnow()
    lines: list[str] = []
    pending = []
    for h in _current_by_experiment(reg).values():
        if h.dataset != discipline or h.status not in (Status.PROPOSED, Status.TESTING):
            continue
        parts = str(h.experiment).split(":")
        c = BY_ID.get(parts[0])
        if len(parts) == 2 and c is not None and c.source != "live":
            # Protocol-1 history test never run: superseded, said so in the registry.
            reg.update(h.hypothesis_id, status=Status.INCONCLUSIVE, conclusion=SUPERSEDED)
            lines.append(f"{h.experiment} : remplacé par le protocole « battre le favori »")
            continue
        if len(parts) == 2:
            pending.append(h)
    if not pending:
        return lines
    hist = add_candidates(frame, discipline)
    live: pl.DataFrame | None = None
    done = 0
    for h in pending:
        if done >= max_tests:
            break
        c = BY_ID.get(str(h.experiment).split(":")[0])
        if c is None:
            continue
        if c.source == "live":
            if live is None:
                live = with_drift(frame, early_quotes(db_path, discipline))
            n, res = evaluate_live(live, c)
            if res is None:
                note = f"En attente de données : {n}/{c.min_races} courses suivies en direct."
                if h.status != Status.TESTING or h.forward_result != note:
                    reg.update(h.hypothesis_id, status=Status.TESTING, forward_result=note)
                    lines.append(f"{h.experiment} : {note}")
                continue
            status, text = verdict(res, need_every_year=False)
        else:
            res = evaluate_history(hist, c)
            if res is None:
                continue  # history not ready for this discipline: stays PROPOSED
            status, text = verdict(res, need_every_year=True)
        payload = {
            "experiment": h.experiment,
            "candidate": c.id,
            "label": c.label,
            "discipline": discipline,
            "source": c.source,
            "tested_at": now.isoformat(timespec="seconds"),
            "status": status.value,
            "conclusion": text,
            **res,
        }
        _save(lab_dir, str(h.experiment), payload)
        reg.update(
            h.hypothesis_id,
            status=status,
            out_of_sample_result=f"{res['difference']:+.4f} [{res['ci_low']:+.4f}, {res['ci_high']:+.4f}] sur {res['races']['test']} courses",
            conclusion=text,
        )
        lines.append(f"{h.experiment} : {text}")
        done += 1
    return lines


def results(lab_dir: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for f in sorted((lab_dir / "results").glob("*.json")) if (lab_dir / "results").exists() else []:
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        out[r["experiment"]] = r
    return out


# ------------------------------------------------------------------- favourites study

FAV_BANDS = (
    (1.0, 1.5, "< 1,5"),
    (1.5, 2.0, "1,5 – 2"),
    (2.0, 3.0, "2 – 3"),
    (3.0, 5.0, "3 – 5"),
    (5.0, math.inf, "≥ 5"),
)
FAV_HYPOTHESIS = (
    "Les très gros favoris (cote < 1,5 à 25 min du départ) rapportent plus qu'ils ne "
    "coûtent en simple gagnant. Règle fixée avant de regarder : sur toutes les courses "
    "depuis 2024, soutenue si l'intervalle à 95 % du retour sur mise est au-dessus de 0, "
    "rejetée s'il est en dessous, sinon non concluante."
)


def _mean_ci(x: np.ndarray) -> tuple[float | None, float | None, float | None]:
    if len(x) < 2:
        return (float(x.mean()) if len(x) else None, None, None)
    m, se = float(x.mean()), float(x.std(ddof=1) / math.sqrt(len(x)))
    return m, m - 1.959964 * se, m + 1.959964 * se


def _wilson(k: int, n: int) -> tuple[float | None, float | None]:
    if n == 0:
        return None, None
    z, p = 1.959964, k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def favourites_study(frame: pl.DataFrame, discipline: str) -> dict[str, Any]:
    """The favourite of each race (shortest price at T-25) by price band: how often it
    wins and places, against what its odds promised, and what 1 EUR on it returned.

    ``frame`` needs ``ret_SG`` / ``ret_SP`` (strategies.with_returns)."""
    fav = (
        frame.sort(["race_id", "odds", "number"])
        .group_by("race_id", maintain_order=True)
        .first()
        .select("race_id", "day", "odds", "market_p", "won", "placed", "ret_SG", "ret_SP")
    )
    rows = []
    for lo, hi, label in (*FAV_BANDS, (1.0, math.inf, "Tous les favoris")):
        b = fav.filter((pl.col("odds") >= lo) & (pl.col("odds") < hi))
        n = b.height
        wins = int(b["won"].sum()) if n else 0
        placed = int(b["placed"].sum()) if n else 0
        wl, wh = _wilson(wins, n)
        sg = (b["ret_SG"].drop_nulls().to_numpy() - 1.0) if n else np.zeros(0)
        sp = (b["ret_SP"].drop_nulls().to_numpy() - 1.0) if n else np.zeros(0)
        rsg, rsg_l, rsg_h = _mean_ci(sg)
        rsp, rsp_l, rsp_h = _mean_ci(sp)
        rows.append(
            {
                "band": label,
                "races": n,
                "win_rate": wins / n if n else None,
                "win_low": wl,
                "win_high": wh,
                "implied": float(b["market_p"].mean()) if n else None,  # type: ignore[arg-type]
                "place_rate": placed / n if n else None,
                "roi_sg": rsg,
                "roi_sg_low": rsg_l,
                "roi_sg_high": rsg_h,
                "roi_sp": rsp,
                "roi_sp_low": rsp_l,
                "roi_sp_high": rsp_h,
                "lost": n - wins,
            }
        )
    days = fav["day"]
    return {
        "kind": "favourites",
        "discipline": discipline,
        "generated_at": utcnow().isoformat(timespec="seconds"),
        "first_day": days.min().isoformat() if fav.height else None,  # type: ignore[union-attr]
        "last_day": days.max().isoformat() if fav.height else None,  # type: ignore[union-attr]
        "bands": rows,
    }


def study_favourites(
    reg: HypothesisRegistry, frame: pl.DataFrame, lab_dir: Path, discipline: str
) -> dict[str, Any]:
    """Refresh the study (descriptive, every night) and settle its one hypothesis once."""
    rep = favourites_study(frame, discipline)
    lab_dir.mkdir(parents=True, exist_ok=True)
    (lab_dir / f"favourites_{discipline}.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    exp = f"favoris_lt_1.5:{discipline}"
    known = _current_by_experiment(reg)
    if exp not in known:
        known[exp] = reg.add(
            Hypothesis(
                description=f"Très gros favoris ({discipline}). {FAV_HYPOTHESIS}",
                origin=Origin.HUMAN,
                dataset=discipline,
                experiment=exp,
            )
        )
    h = known[exp]
    band = rep["bands"][0]
    if h.status == Status.PROPOSED and band["races"] >= 100 and band["roi_sg_low"] is not None:
        lo, hi, roi = band["roi_sg_low"], band["roi_sg_high"], band["roi_sg"]
        span = f"retour {roi:+.1%} (IC 95 % {lo:+.1%} à {hi:+.1%}) sur {band['races']} courses ; ils perdent {band['lost']} fois"
        status = Status.SUPPORTED if lo > 0 else Status.REJECTED if hi < 0 else Status.INCONCLUSIVE
        reg.update(
            h.hypothesis_id,
            status=status,
            out_of_sample_result=span,
            conclusion=(
                "Soutenue : "
                if status == Status.SUPPORTED
                else "Rejetée : "
                if status == Status.REJECTED
                else "Non concluante : "
            )
            + span
            + ".",
        )
    return rep
