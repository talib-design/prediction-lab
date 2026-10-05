"""The arena: candidates judged against the champion, for the objective "beat the
favourite by predicting better" (racing/champion.py, docs/METHODOLOGY.md §13).

Per candidate, registered before any result and tested once:

* criterion (a new factor): challenger = champion + the factor, both fitted the same way
  (train, λ chosen on validation). On the test window:
  - filter 1, prediction: per-race log loss challenger − champion, 99 % interval
    entirely below 0 and a gain in every test calendar year;
  - filter 2, money: the challenger's pick returns more per euro than the champion's
    (simple gagnant + simple placé pooled) -- "beats the favourite by more", the
    favourite's return being the same on both sides. A point estimate: an interval on
    money would need years of races; the vault and then the carnet are the safeguards.
* calibration: tau fitted on validation (p ∝ p^tau). Filter 1 only: the pick is
  unchanged by construction, the probabilities become honest (what a value rule needs).
* rule (when to bet): judged on fresh races only (the value threshold was found by
  exploring the whole history on 2026-10-04): return per euro of the rule's simple
  gagnant tickets above the favourite's, on races after that exploration.

A criterion or calibration that passes goes to the vault once (racing/champion.py).

* criterion proposed after looking at results (``Candidate.fresh_from``, the critic
  agent): the same two filters, but on races run from ``fresh_from`` -- and from the day
  after its registration at the earliest -- once ``FRESH_MIN_RACES`` of them exist; the
  champion and the challenger are fitted on everything before. Its vault comes after its
  test races.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

from predlab.core.clock import utcnow
from predlab.eval.uncertainty import block_bootstrap
from predlab.racing import lab
from predlab.racing.champion import VALUE_EDGE, Champion, Window
from predlab.racing.marketplus import LAMBDAS, MIN_TRAIN_RACES, Design, _probs, design, fit
from predlab.registry.hypotheses import Hypothesis, HypothesisRegistry, Status

PROTOCOL = "obj"  # experiment keys: <candidate>:<discipline>:obj<champion version>
RULE_FRESH_FROM = date(2026, 10, 5)  # the value threshold was explored on 2026-10-04
TAU_GRID = tuple(round(0.5 + 0.01 * i, 2) for i in range(101))  # 0.50 → 1.50
FRESH_MIN_RACES = 1000  # races run after a post-hoc criterion's registration

RULE_TEXT = (
    "Règle fixée avant le test (objectif « battre le favori en prévoyant mieux », "
    "2026-10-05) : challenger = champion + ce critère, ajustés de la même façon. Sur la "
    "fenêtre de test : (1) la prévision s'améliore, IC 99 % de l'écart de log loss sous 0 "
    "et gain chaque année ; (2) le cheval choisi rapporte plus par euro que celui du "
    "champion, gagnant + placé. Les deux tenus : un essai unique au coffre, sur des courses "
    "jamais utilisées ; promu s'il prévoit encore mieux et ne perd pas d'argent face au "
    "champion."
)
RULE_TEXT_CALIBRATION = (
    "Règle fixée avant le test (objectif du 2026-10-05) : τ ajusté sur la validation ; "
    "retenu si l'IC 99 % de l'écart de log loss sur le test est sous 0 et le gain présent "
    "chaque année ; puis un essai unique au coffre (log loss encore meilleure)."
)
RULE_TEXT_RULE = (
    "Règle fixée avant le test (objectif du 2026-10-05) : jugée seulement sur des courses "
    f"postérieures au {RULE_FRESH_FROM.isoformat()} ; admise au carnet si le retour par euro "
    "de ses tickets simple gagnant dépasse celui du favori sur au moins le nombre de "
    "courses du coffre."
)


RULE_TEXT_FRESH = (
    "Règle fixée avant le test (critère proposé après avoir vu des résultats, donc jamais "
    "jugé sur eux) : jugé seulement sur les courses courues à partir du {start} et au plus "
    "tôt le lendemain de cet enregistrement, une fois {n} courses atteintes ; challenger = "
    "champion + ce critère, ajustés sur toutes les courses d'avant. (1) IC 99 % de l'écart "
    "de log loss sous 0 ; (2) son choix rapporte plus par euro que celui du champion, "
    "gagnant + placé. Les deux tenus : un essai unique au coffre, sur des courses "
    "postérieures à ce test."
)


def key(candidate: lab.Candidate, discipline: str, version: int = 1) -> str:
    """One experiment per candidate and champion version: after a promotion, the others
    are registered again against the new champion."""
    return f"{candidate.id}:{discipline}:{PROTOCOL}{version}"


def _is_ours(experiment: str) -> bool:
    parts = experiment.split(":")
    return len(parts) == 3 and parts[2].startswith(PROTOCOL)


# ---------------------------------------------------------------------------- frames


def split(frame: pl.DataFrame, window: Window, vault_start: date) -> dict[str, pl.DataFrame]:
    day = pl.col("day")
    return {
        "train": frame.filter(day <= window.train_end),
        "validation": frame.filter((day > window.train_end) & (day <= window.validation_end)),
        "test": frame.filter((day > window.validation_end) & (day <= window.test_end)),
        "vault": frame.filter(day >= vault_start),
    }


def _sorted(df: pl.DataFrame) -> pl.DataFrame:
    return df.sort(["day", "race_id", "number"])


def _fit(
    parts: dict[str, pl.DataFrame], features: tuple[str, ...], lams: tuple[float, ...]
) -> dict[str, Any]:
    means, stds, best, lam = lab._fit_select(parts, features, lams)
    return {
        "features": features,
        "means": means,
        "stds": stds,
        "theta": best["theta"],
        "se": best["se"],
        "lambda": lam,
    }


def _refit(df: pl.DataFrame, model: dict[str, Any]) -> dict[str, Any]:
    """Same features and λ, fitted on ``df`` (everything before the vault)."""
    feats = model["features"]
    x = df.select(feats).to_numpy().astype(np.float64)
    means, stds = x.mean(0), x.std(0)
    stds = np.where(stds > 1e-9, stds, 0.0)
    f = fit(design(df, means, stds, feats), model["lambda"], np.r_[True, stds > 0])
    return {**model, "means": means, "stds": stds, "theta": f["theta"], "se": f["se"]}


def _design(df: pl.DataFrame, model: dict[str, Any]) -> Design:
    return design(df, model["means"], model["stds"], model["features"])


def _log_loss(d: Design, theta: np.ndarray, tau: float) -> np.ndarray:
    p = _probs(d, theta * tau)
    return -np.add.reduceat(d.weight * np.log(np.clip(p, 1e-15, None)), d.starts)


def _tops(d: Design, theta: np.ndarray) -> np.ndarray:
    p = _probs(d, theta)
    ends = np.r_[d.starts[1:], len(p)]
    return np.array([s + int(np.argmax(p[s:e])) for s, e in zip(d.starts, ends, strict=True)])


def _favs(df: pl.DataFrame, d: Design) -> np.ndarray:
    odds = df["odds"].to_numpy().astype(np.float64)
    ends = np.r_[d.starts[1:], len(odds)]
    return np.array([s + int(np.argmin(odds[s:e])) for s, e in zip(d.starts, ends, strict=True)])


def _pick_returns(df: pl.DataFrame, rows: np.ndarray) -> np.ndarray:
    """Per race: (stake, returned) of 1 € gagnant + 1 € placé on the picked row; a bet
    type the race did not pay is not staked."""
    sg = df["ret_SG"].to_numpy()[rows]
    sp = df["ret_SP"].to_numpy()[rows]
    stake = (~np.isnan(sg.astype(float))).astype(float) + (~np.isnan(sp.astype(float))).astype(
        float
    )
    ret = np.nan_to_num(sg.astype(float)) + np.nan_to_num(sp.astype(float))
    return np.c_[stake, ret]


def _roi(sr: np.ndarray) -> float | None:
    stake = float(sr[:, 0].sum())
    return float(sr[:, 1].sum()) / stake - 1.0 if stake else None


def money(
    df: pl.DataFrame, da: Design, theta_a: np.ndarray, db: Design, theta_b: np.ndarray
) -> dict[str, Any]:
    """Pick of model a vs pick of model b vs the favourite, on the same races (``df``
    sorted like the designs)."""
    tops_a, tops_b = _tops(da, theta_a), _tops(db, theta_b)
    a = _pick_returns(df, tops_a)
    b = _pick_returns(df, tops_b)
    fav = _pick_returns(df, _favs(df, da))
    diff = (a[:, 1] - a[:, 0]) - (b[:, 1] - b[:, 0])  # net per race, a − b
    ci = block_bootstrap(diff, n_resamples=1000, seed=1) if len(diff) > 1 else None
    return {
        "races": len(diff),
        "races_where_picks_differ": int(np.sum(tops_a != tops_b)),
        "roi_challenger": _roi(a),
        "roi_champion": _roi(b),
        "roi_favourite": _roi(fav),
        "net_difference": float(diff.sum()),
        "net_difference_low": float(ci.low * len(diff)) if ci else None,
        "net_difference_high": float(ci.high * len(diff)) if ci else None,
    }


def prediction(
    da: Design, ta: np.ndarray, db: Design, tb: np.ndarray, tau_a: float, tau_b: float
) -> dict[str, Any]:
    diff = _log_loss(da, ta, tau_a) - _log_loss(db, tb, tau_b)
    ci = block_bootstrap(diff, n_resamples=2000, level=lab.LEVEL, seed=0)
    years: dict[str, dict[str, float]] = {}
    for y in sorted({int(str(x)[:4]) for x in da.days}):
        sel = np.array([int(str(x)[:4]) == y for x in da.days])
        years[str(y)] = {"races": int(sel.sum()), "difference": float(diff[sel].mean())}
    return {
        "difference": float(diff.mean()),
        "ci_low": ci.low,
        "ci_high": ci.high,
        "level": lab.LEVEL,
        "by_year": years,
        "test_days": [str(da.days[0]), str(da.days[-1])] if len(da.days) else None,
    }


# ------------------------------------------------------------------------- evaluation


def evaluate_criterion(
    parts: dict[str, pl.DataFrame], champ: Champion, column: str
) -> dict[str, Any]:
    base = _fit(parts, champ.features, LAMBDAS)
    chal = _fit(parts, (*champ.features, column), LAMBDAS)
    test = _sorted(parts["test"])
    db, dc = _design(test, base), _design(test, chal)
    pred = prediction(dc, chal["theta"], db, base["theta"], champ.tau, champ.tau)
    mon = money(test, dc, chal["theta"], db, base["theta"])
    beta, se, sd = float(chal["theta"][-1]), float(chal["se"][-1]), float(chal["stds"][-1])
    return {
        **pred,
        "money": mon,
        "lambda": {"champion": base["lambda"], "challenger": chal["lambda"]},
        "beta": beta,
        "beta_low": beta - 2.575829 * se,
        "beta_high": beta + 2.575829 * se,
        "per_sd": float(np.exp(beta)) if sd > 0 else None,
        "races": {k: int(v["race_id"].n_unique()) for k, v in parts.items()},
    }


def fit_tau(d: Design, theta: np.ndarray) -> float:
    losses = [(float(_log_loss(d, theta, t).mean()), t) for t in TAU_GRID]
    return min(losses)[1]


def evaluate_calibration(parts: dict[str, pl.DataFrame], champ: Champion) -> dict[str, Any]:
    base = _fit(parts, champ.features, LAMBDAS)
    tau = fit_tau(_design(_sorted(parts["validation"]), base), base["theta"])
    d = _design(_sorted(parts["test"]), base)
    pred = prediction(d, base["theta"], d, base["theta"], tau, champ.tau)
    return {
        **pred,
        "tau": tau,
        "lambda": {"champion": base["lambda"]},
        "races": {k: int(v["race_id"].n_unique()) for k, v in parts.items()},
    }


def evaluate_rule(
    frame: pl.DataFrame, champ: Champion, window: Window, fresh_from: date, min_races: int
) -> tuple[int, dict[str, Any] | None]:
    """The value rule on races from ``fresh_from``, with the champion fitted on all races
    before them (λ chosen on validation, the champion's tau)."""
    fresh = _sorted(frame.filter(pl.col("day") >= fresh_from))
    n = fresh["race_id"].n_unique()
    if n < min_races:
        return n, None
    parts = split(frame.filter(pl.col("day") < fresh_from), window, fresh_from)
    model = _refit(frame.filter(pl.col("day") < fresh_from), _fit(parts, champ.features, LAMBDAS))
    d = _design(fresh, model)
    p = _probs(d, model["theta"] * champ.tau)
    odds = fresh["odds"].to_numpy().astype(np.float64)
    sg = fresh["ret_SG"].to_numpy().astype(float)
    bets = (p * odds >= VALUE_EDGE) & ~np.isnan(sg)
    fav = _favs(fresh, d)
    fav_sg = sg[fav]
    fav_sg = fav_sg[~np.isnan(fav_sg)]
    roi_rule = float(sg[bets].sum() / bets.sum() - 1.0) if bets.sum() else None
    roi_fav = float(fav_sg.mean() - 1.0) if len(fav_sg) else None
    return n, {
        "races": n,
        "bets": int(bets.sum()),
        "roi_rule": roi_rule,
        "roi_favourite": roi_fav,
        "fresh_from": fresh_from.isoformat(),
        "days": [str(d.days[0]), str(d.days[-1])] if len(d.days) else None,
    }


def evaluate_fresh_criterion(
    frame: pl.DataFrame,
    champ: Champion,
    window: Window,
    column: str,
    start: date,
    min_races: int = FRESH_MIN_RACES,
) -> tuple[int, dict[str, Any] | None]:
    """A post-hoc criterion on races from ``start`` only; champion and challenger fitted
    on every race before (λ chosen on the window's validation)."""
    fresh = _sorted(frame.filter(pl.col("day") >= start))
    n = fresh["race_id"].n_unique()
    if n < min_races:
        return n, None
    before = frame.filter(pl.col("day") < start)
    parts = split(before, window, start)
    base = _refit(before, _fit(parts, champ.features, LAMBDAS))
    chal = _refit(before, _fit(parts, (*champ.features, column), LAMBDAS))
    db, dc = _design(fresh, base), _design(fresh, chal)
    pred = prediction(dc, chal["theta"], db, base["theta"], champ.tau, champ.tau)
    mon = money(fresh, dc, chal["theta"], db, base["theta"])
    beta, se = float(chal["theta"][-1]), float(chal["se"][-1])
    return n, {
        **pred,
        "money": mon,
        "lambda": {"champion": base["lambda"], "challenger": chal["lambda"]},
        "beta": beta,
        "beta_low": beta - 2.575829 * se,
        "beta_high": beta + 2.575829 * se,
        "fresh_from": start.isoformat(),
        "fresh_until": str(fresh["day"].max()),
        "races": {"before": int(before["race_id"].n_unique()), "fresh": n},
    }


def verdict(kind: str, res: dict[str, Any]) -> tuple[Status, str]:
    if kind == "rule":
        rr, rf = res.get("roi_rule"), res.get("roi_favourite")
        if rr is None or rf is None:
            return Status.REJECTED, f"Refusée : aucun pari sur {res['races']} courses."
        span = (
            f"retour {rr:+.1%} sur {res['bets']} paris contre {rf:+.1%} pour le favori "
            f"({res['races']} courses)"
        )
        if rr > rf:
            return Status.SUPPORTED, f"Admise au carnet : {span}."
        return Status.REJECTED, f"Refusée : {span}."
    # A post-hoc criterion is judged on a few months of fresh races: no per-year rule.
    status, text = lab.verdict(res, need_every_year="fresh_from" not in res)
    if status != Status.SUPPORTED:
        return status, text
    span = (
        f"écart de log loss {res['difference']:+.4f} (IC 99 % {res['ci_low']:+.4f} à "
        f"{res['ci_high']:+.4f})"
        + (
            f", sur les courses depuis le {res['fresh_from']}"
            if "fresh_from" in res
            else ", gain chaque année"
        )
    )
    if kind == "calibration":
        return Status.SUPPORTED, f"Retenu : {span}, τ = {res['tau']:.2f}. Essai au coffre."
    m = res["money"]
    gain = (
        f"{m['net_difference']:+.0f} € face au choix du champion sur {m['races']} courses, "
        f"dont {m['races_where_picks_differ']} où les choix diffèrent"
    )
    if m["net_difference"] > 0:
        return (
            Status.SUPPORTED,
            f"Retenu : {span} ; son choix rapporte plus ({gain}). Essai au coffre.",
        )
    return Status.INCONCLUSIVE, (
        f"Prévoit mieux ({span}) mais son choix ne rapporte pas plus ({gain}) : non retenu."
    )


# --------------------------------------------------------------------------- the loop


def _by_experiment(reg: HypothesisRegistry) -> dict[str, Hypothesis]:
    return {h.experiment: h for h in reg.current() if h.experiment}


def version_info(lab_dir: Path, discipline: str) -> tuple[int, set[str], float]:
    champ = Champion.load(lab_dir, discipline)
    return champ.current["version"], set(champ.features), champ.tau


def register(reg: HypothesisRegistry, discipline: str, lab_dir: Path) -> list[str]:
    """Pre-register every catalogue candidate (criteria, calibration, rule) of this
    discipline for the objective, before any test."""
    known = _by_experiment(reg)
    champ_version, in_model, tau = version_info(lab_dir, discipline)
    added = []
    for c in lab.CANDIDATES:
        k = key(c, discipline, champ_version)
        if c.source == "live" or discipline not in c.disciplines or k in known:
            continue
        if c.column in in_model or (c.kind == "calibration" and tau != 1.0):
            continue  # already part of the champion
        rule = {"calibration": RULE_TEXT_CALIBRATION, "rule": RULE_TEXT_RULE}.get(c.kind, RULE_TEXT)
        if c.fresh_from is not None:
            rule = RULE_TEXT_FRESH.format(
                start=c.fresh_from.strftime("%d/%m/%Y"), n=FRESH_MIN_RACES
            )
        reg.add(
            Hypothesis(
                description=f"{c.label} ({discipline}). {c.hypothesis} {rule}",
                origin=c.origin,
                dataset=discipline,
                experiment=k,
                status=Status.PROPOSED,
            )
        )
        added.append(k)
    return added


def _save(lab_dir: Path, experiment: str, payload: dict[str, Any]) -> None:
    out = lab_dir / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{experiment.replace(':', '_')}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )


def _note(reg: HypothesisRegistry, h: Hypothesis, text: str, lines: list[str]) -> None:
    if h.status != Status.TESTING or h.forward_result != text:
        reg.update(h.hypothesis_id, status=Status.TESTING, forward_result=text)
        lines.append(f"{h.experiment} : {text}")


def run(
    reg: HypothesisRegistry,
    frame: pl.DataFrame | None,
    lab_dir: Path,
    discipline: str,
    window: Window,
    *,
    ready: bool,
    max_tests: int = 3,
    now: datetime | None = None,
    rule_window: Window | None = None,
) -> tuple[list[str], dict[str, Any] | None]:
    """Tests whose data is ready, then at most one vault attempt per kind.

    ``frame``: ``load_finished(since=window.since)`` with the candidates' columns and the
    returns (strategies.with_returns); None when the history is not ready. Returns the
    lines to log and, when a version was promoted, the promotion (the caller refits the
    model and freezes the previous parameters)."""
    now = now or utcnow()
    lines: list[str] = []
    champ = Champion.load(lab_dir, discipline)
    if not champ.path.exists():
        champ.save()  # v1 written down, the starting point of the scoreboard
    pending = [
        h
        for h in _by_experiment(reg).values()
        if h.dataset == discipline
        and _is_ours(str(h.experiment))
        and str(h.experiment).endswith(f"{PROTOCOL}{champ.current['version']}")
        and h.status in (Status.PROPOSED, Status.TESTING)
    ]
    rule_window = rule_window or window
    registered = _registered_on(reg)
    if not ready or frame is None:
        for h in pending:
            c = lab.BY_ID.get(str(h.experiment).split(":")[0])
            if c is not None and c.kind == "rule" and frame is not None:
                _rule(reg, h, c, frame, champ, rule_window, lab_dir, discipline, now, lines)
            elif c is not None and c.fresh_from is not None and frame is not None:
                start = _fresh_start(c, registered.get(h.hypothesis_id))
                _fresh(reg, h, c, frame, champ, rule_window, start, lab_dir, discipline, now, lines)
            else:
                _note(reg, h, "En attente de l'historique 2020 de cette discipline.", lines)
        return lines, None
    vault_start = champ.vault_start(window)
    parts = split(frame, window, vault_start)
    if parts["train"]["race_id"].n_unique() < MIN_TRAIN_RACES:
        return lines, None
    done = 0
    for h in pending:
        c = lab.BY_ID.get(str(h.experiment).split(":")[0])
        if c is None:
            continue
        if c.kind == "rule":
            _rule(reg, h, c, frame, champ, rule_window, lab_dir, discipline, now, lines)
            continue
        if c.fresh_from is not None:
            start = _fresh_start(c, registered.get(h.hypothesis_id))
            _fresh(reg, h, c, frame, champ, window, start, lab_dir, discipline, now, lines)
            continue
        if done >= max_tests:
            continue
        elif c.kind == "calibration":
            res = evaluate_calibration(parts, champ)
            done += 1
        else:
            if c.column not in frame.columns:
                continue
            res = evaluate_criterion(parts, champ, c.column)
            done += 1
        _record(reg, h, c, res, champ, lab_dir, discipline, now, lines)
    promotion = attempt_vault(reg, frame, lab_dir, discipline, window, champ, now, lines)
    return lines, promotion


def _record(
    reg: HypothesisRegistry,
    h: Hypothesis,
    c: lab.Candidate,
    res: dict[str, Any],
    champ: Champion,
    lab_dir: Path,
    discipline: str,
    now: datetime,
    lines: list[str],
) -> Status:
    status, text = verdict(c.kind, res)
    payload = {
        "experiment": h.experiment,
        "candidate": c.id,
        "label": c.label,
        "discipline": discipline,
        "kind": c.kind,
        "protocol": PROTOCOL,
        "champion_version": champ.current["version"],
        "tested_at": now.isoformat(timespec="seconds"),
        "status": status.value,
        "conclusion": text,
        **res,
    }
    _save(lab_dir, str(h.experiment), payload)
    summary = (
        f"{res['difference']:+.4f} [{res['ci_low']:+.4f}, {res['ci_high']:+.4f}]"
        if "difference" in res
        else text
    )
    reg.update(h.hypothesis_id, status=status, out_of_sample_result=summary, conclusion=text)
    lines.append(f"{h.experiment} : {text}")
    return status


def _rule(
    reg: HypothesisRegistry,
    h: Hypothesis,
    c: lab.Candidate,
    frame: pl.DataFrame,
    champ: Champion,
    window: Window,
    lab_dir: Path,
    discipline: str,
    now: datetime,
    lines: list[str],
) -> None:
    """A playing rule only needs fresh races and a champion fitted before them: it does
    not wait for the extended history."""
    n, res = evaluate_rule(frame, champ, window, RULE_FRESH_FROM, window.vault_min_races)
    if res is None:
        _note(
            reg,
            h,
            f"En attente de courses fraîches : {n}/{window.vault_min_races} "
            f"depuis le {RULE_FRESH_FROM.strftime('%d/%m/%Y')}.",
            lines,
        )
        return
    if _record(reg, h, c, res, champ, lab_dir, discipline, now, lines) == Status.SUPPORTED:
        champ.admit_rule(c.id)
        champ.save()


def _registered_on(reg: HypothesisRegistry) -> dict[str, date]:
    """Day each hypothesis was first written to the registry (its revision 0)."""
    out: dict[str, date] = {}
    for h in reg.history():
        out.setdefault(h.hypothesis_id, h.created_at.date())
    return out


def _fresh_start(c: lab.Candidate, registered: date | None) -> date:
    assert c.fresh_from is not None
    if registered is None:
        return c.fresh_from
    return max(c.fresh_from, registered + timedelta(days=1))


def _fresh(
    reg: HypothesisRegistry,
    h: Hypothesis,
    c: lab.Candidate,
    frame: pl.DataFrame,
    champ: Champion,
    window: Window,
    start: date,
    lab_dir: Path,
    discipline: str,
    now: datetime,
    lines: list[str],
) -> None:
    """A post-hoc criterion: waits for its fresh races, then is tested once."""
    if c.column not in frame.columns:
        return
    n, res = evaluate_fresh_criterion(
        frame, champ, window, c.column, start, min_races=FRESH_MIN_RACES
    )
    if res is None:
        _note(
            reg,
            h,
            f"En attente de courses fraîches : {n}/{FRESH_MIN_RACES} depuis le "
            f"{start.strftime('%d/%m/%Y')}.",
            lines,
        )
        return
    _record(reg, h, c, res, champ, lab_dir, discipline, now, lines)


def attempt_vault(
    reg: HypothesisRegistry,
    frame: pl.DataFrame,
    lab_dir: Path,
    discipline: str,
    window: Window,
    champ: Champion,
    now: datetime,
    lines: list[str],
) -> dict[str, Any] | None:
    """The best retained criterion or calibration not yet tried goes to the vault once."""
    tried = {a["experiment"] for a in champ.data["attempts"]}
    res_all = lab.results(lab_dir)
    waiting = [
        r
        for exp, r in res_all.items()
        if r.get("protocol") == PROTOCOL
        and r.get("discipline") == discipline
        and r.get("status") == Status.SUPPORTED.value
        and r.get("kind") in ("criterion", "calibration")
        and exp not in tried
        and r.get("champion_version") == champ.current["version"]
    ]
    if not waiting:
        return None
    best = min(waiting, key=lambda r: r["difference"])
    vault_start = champ.vault_start(window)
    if best.get("fresh_until"):  # a post-hoc criterion: its vault comes after its test
        vault_start = max(vault_start, date.fromisoformat(best["fresh_until"]) + timedelta(days=1))
    parts = split(frame, window, vault_start)
    vault = _sorted(parts["vault"])
    n = vault["race_id"].n_unique()
    h = _by_experiment(reg).get(best["experiment"])
    if n < window.vault_min_races:
        lines.append(
            f"{best['experiment']} : retenu, en attente du coffre ({n}/"
            f"{window.vault_min_races} courses jamais utilisées)."
        )
        return None
    before = frame.filter(pl.col("day") < vault_start)
    pre = split(before, window, vault_start)
    base = _refit(before, _fit(pre, champ.features, LAMBDAS))
    if best["kind"] == "calibration":
        chal, tau = base, float(best["tau"])
        features = champ.features
    else:
        c = lab.BY_ID[best["candidate"]]
        features = (*champ.features, c.column)
        chal, tau = _refit(before, _fit(pre, features, LAMBDAS)), champ.tau
    db, dc = _design(vault, base), _design(vault, chal)
    pred = prediction(dc, chal["theta"], db, base["theta"], tau, champ.tau)
    mon = money(vault, dc, chal["theta"], db, base["theta"])
    passed = pred["difference"] < 0 and mon["net_difference"] >= 0
    days = (
        date.fromisoformat(str(vault["day"].min())),
        date.fromisoformat(str(vault["day"].max())),
    )
    result = {"prediction": pred, "money": mon, "races": n}
    champ.record_attempt(best["experiment"], days, result, passed, now)
    if not passed:
        champ.save()
        text = (
            f"Refusé au coffre ({n} courses du {days[0]:%d/%m/%Y} au {days[1]:%d/%m/%Y}) : "
            f"log loss {pred['difference']:+.4f}, argent face au champion "
            f"{mon['net_difference']:+.0f} €."
        )
        if h is not None:
            reg.update(h.hypothesis_id, forward_result=text)
        lines.append(f"{best['experiment']} : {text}")
        return None
    origin = f"{best['label']} (labo, {best['experiment']})"
    promotion = {
        "experiment": best["experiment"],
        "features": list(features),
        "tau": tau,
        "origin": origin,
        "evidence": {"test": best, "vault": result},
    }
    text = (
        f"Promu au coffre ({n} courses) : log loss {pred['difference']:+.4f}, argent face au "
        f"champion {mon['net_difference']:+.0f} €. Devient Marché+ v{champ.current['version'] + 1}."
    )
    if h is not None:
        reg.update(h.hypothesis_id, forward_result=text)
    lines.append(f"{best['experiment']} : {text}")
    champ.save()
    return promotion
