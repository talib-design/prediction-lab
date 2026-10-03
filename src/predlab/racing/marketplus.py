"""Marché+ : the market's odds, corrected by the factors it may have under-weighted.

For each starter ``i`` of a race::

    score_i = α · log q_i + Σ_k β_k · x_ik        p_i = exp(score_i) / Σ_j exp(score_j)

``q`` is the market's implied probability at T-25 min and ``x`` the pre-registered
factors of ``features.MODEL_FEATURES`` (docs/METHODOLOGY.md §10), standardised on the
training window. With every β = 0 this *is* the calibrated market (p ∝ q^α), so each
β reads directly as "what this factor adds to the odds": β > 0, the runners high on
this factor win more than their odds said.

Fitting is exact (Newton's method on the conditional likelihood, a ridge penalty λ on
the β only). The procedure is fixed in advance:

1. fit on the **train** window for each λ of ``LAMBDAS``;
2. keep the λ with the best log loss on the **validation** window;
3. report that model on the **test** window, against the calibrated market fitted on
   the same train window -- the only comparison that decides;
4. refit with that λ on everything released, for the live carnet.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
from scipy.stats import norm

from predlab.backtest.splits import TimeSplit
from predlab.core.clock import utcnow
from predlab.eval.uncertainty import block_bootstrap
from predlab.racing.features import FEATURE_LABELS, MODEL_FEATURES
from predlab.racing.report import discipline_label

NAME = "marche_plus"
VERSION = "1"
LAMBDAS = (1.0, 10.0, 100.0, 1000.0)
MIN_TRAIN_RACES = 300
Z = 1.959964


@dataclass
class Design:
    """Rows sorted by race; ``starts[r]`` is the first row of race ``r``."""

    z: np.ndarray  # (n, d): column 0 is log q, then the standardised features
    weight: np.ndarray  # (n,): 1/k for each of k co-winners, else 0
    starts: np.ndarray  # (races,)
    race_of: np.ndarray  # (n,)
    race_ids: list[str]
    days: np.ndarray  # (races,) datetime64[D]


def design(
    df: pl.DataFrame,
    means: np.ndarray,
    stds: np.ndarray,
    features: tuple[str, ...] = MODEL_FEATURES,
) -> Design:
    """``features`` defaults to the model's own; the lab passes a challenger's list."""
    df = df.sort(["day", "race_id", "number"])
    x = df.select(features).to_numpy().astype(np.float64)
    x = np.where(stds > 0, (x - means) / np.where(stds > 0, stds, 1.0), 0.0)
    logq = df["log_q"].to_numpy().astype(np.float64)[:, None]
    race = df["race_id"].to_numpy()
    starts = np.flatnonzero(np.r_[True, race[1:] != race[:-1]])
    race_of = np.repeat(np.arange(len(starts)), np.diff(np.r_[starts, len(race)]))
    won = df["won"].to_numpy().astype(np.float64) if "won" in df.columns else np.zeros(len(df))
    k = np.add.reduceat(won, starts) if len(starts) else np.zeros(0)
    weight = np.where(won > 0, won / np.maximum(k[race_of], 1.0), 0.0)
    return Design(
        z=np.hstack([logq, x]),
        weight=weight,
        starts=starts,
        race_of=race_of,
        race_ids=[str(r) for r in race[starts]],
        days=df["day"].to_numpy()[starts] if len(starts) else np.zeros(0, "datetime64[D]"),
    )


def _probs(d: Design, theta: np.ndarray) -> np.ndarray:
    s = d.z @ theta
    top = np.maximum.reduceat(s, d.starts)
    e = np.exp(s - top[d.race_of])
    return e / np.add.reduceat(e, d.starts)[d.race_of]


def race_log_loss(d: Design, theta: np.ndarray) -> np.ndarray:
    """Per race: −Σ w log p_winner (dead heats share the weight)."""
    p = _probs(d, theta)
    return -np.add.reduceat(d.weight * np.log(np.clip(p, 1e-15, None)), d.starts)


def fit(d: Design, lam: float, mask: np.ndarray | None = None, iters: int = 50) -> dict[str, Any]:
    """Penalised maximum likelihood by Newton. ``mask`` freezes coefficients at 0."""
    dim = d.z.shape[1]
    active = np.ones(dim, bool) if mask is None else mask.copy()
    active[0] = True
    theta = np.zeros(dim)
    theta[0] = 1.0
    pen = np.full(dim, lam)
    pen[0] = 0.0
    info = np.eye(dim)
    for _ in range(iters):
        p = _probs(d, theta)
        zp = d.z * p[:, None]
        mean_z = np.add.reduceat(zp, d.starts, axis=0)  # (races, d)
        wins_z = np.add.reduceat(d.z * d.weight[:, None], d.starts, axis=0)
        grad = (wins_z - mean_z * np.add.reduceat(d.weight, d.starts)[:, None]).sum(0)
        grad -= pen * theta
        # Every race has total winner weight 1: the Fisher information below is exact.
        info = d.z.T @ zp - mean_z.T @ mean_z + np.diag(pen)
        a = np.flatnonzero(active)
        step = np.zeros(dim)
        step[a] = np.linalg.solve(info[np.ix_(a, a)], grad[a])
        theta += step
        if np.max(np.abs(step)) < 1e-8:
            break
    cov = np.zeros((dim, dim))
    a = np.flatnonzero(active)
    cov[np.ix_(a, a)] = np.linalg.inv(info[np.ix_(a, a)])
    return {"theta": theta, "se": np.sqrt(np.clip(np.diag(cov), 0, None)), "lambda": lam}


def _split(df: pl.DataFrame, split: TimeSplit) -> dict[str, pl.DataFrame]:
    return {
        "train": df.filter(pl.col("day") <= split.train_end),
        "validation": df.filter(
            (pl.col("day") > split.train_end) & (pl.col("day") <= split.validation_end)
        ),
        "test": df.filter(pl.col("day") > split.validation_end),
    }


def _compare(d: Design, model: np.ndarray, reference: np.ndarray) -> dict[str, Any]:
    if len(d.starts) < 2:
        return {"races": len(d.starts)}
    lm, lr = race_log_loss(d, model), race_log_loss(d, reference)
    diff = lm - lr
    ci = block_bootstrap(diff, n_resamples=1000, seed=0)
    return {
        "races": len(d.starts),
        "log_loss_model": float(lm.mean()),
        "log_loss_market": float(lr.mean()),
        "difference": float(diff.mean()),
        "ci_low": ci.low,
        "ci_high": ci.high,
        "verdict": "meilleur que le marché"
        if ci.high < 0
        else ("pire que le marché" if ci.low > 0 else "pas de différence démontrée"),
    }


def _bets(d: Design, theta: np.ndarray, frame: pl.DataFrame, dividends: pl.DataFrame | None):
    """Simple win and place on the model's top pick vs the favourite, 1 EUR each."""
    if dividends is None or len(d.starts) == 0:
        return None
    df = frame.sort(["day", "race_id", "number"])
    p = _probs(d, theta)
    q = d.z[:, 0]
    numbers = df["number"].to_numpy()
    top_model = np.array(
        [
            s + int(np.argmax(p[s:e]))
            for s, e in zip(d.starts, np.r_[d.starts[1:], len(p)], strict=True)
        ]
    )
    top_fav = np.array(
        [
            s + int(np.argmax(q[s:e]))
            for s, e in zip(d.starts, np.r_[d.starts[1:], len(p)], strict=True)
        ]
    )
    odds = df["odds"].to_numpy()
    value_rows = np.flatnonzero(p * odds >= 1.10)
    pay: dict[tuple[str, str], dict[str, float]] = {}
    for race_id, bet, combo, per_euro in dividends.iter_rows():
        pay.setdefault((race_id, bet), {})[combo] = float(per_euro)
    out: dict[str, Any] = {}
    races = np.array(d.race_ids)
    for name, bet, rows in (
        ("SG modèle", "SIMPLE_GAGNANT", top_model),
        ("SG favori", "SIMPLE_GAGNANT", top_fav),
        ("SP modèle", "SIMPLE_PLACE", top_model),
        ("SP favori", "SIMPLE_PLACE", top_fav),
        ("SG valeur modèle", "SIMPLE_GAGNANT", value_rows),
    ):
        stake, ret = [], []
        for r in rows:
            table = pay.get((str(races[d.race_of[r]]), bet))
            if table is None:
                continue
            stake.append(1.0)
            ret.append(table.get(str(numbers[r]), 0.0))
        if len(stake) < 20:
            out[name] = {"bets": len(stake)}
            continue
        net = np.array(ret) - 1.0
        ci = block_bootstrap(net, n_resamples=1000, seed=1)
        out[name] = {
            "bets": len(stake),
            "stake": float(sum(stake)),
            "returned": float(sum(ret)),
            "roi": float(net.mean()),
            "roi_low": ci.low,
            "roi_high": ci.high,
            "hit_rate": float(np.mean(np.array(ret) > 0)),
        }
    return out


def run(
    df: pl.DataFrame,
    discipline: str,
    split: TimeSplit,
    dividends: pl.DataFrame | None = None,
) -> dict[str, Any] | None:
    """The whole pre-registered procedure. None when the train window is too small."""
    parts = _split(df, split)
    if parts["train"]["race_id"].n_unique() < MIN_TRAIN_RACES:
        return None
    x_train = parts["train"].select(MODEL_FEATURES).to_numpy().astype(np.float64)
    means, stds = x_train.mean(0), x_train.std(0)
    stds = np.where(stds > 1e-9, stds, 0.0)
    mask = np.r_[True, stds > 0]
    d = {k: design(v, means, stds) for k, v in parts.items()}

    market = fit(d["train"], 0.0, mask=np.r_[True, np.zeros(len(MODEL_FEATURES), bool)])
    tries = []
    for lam in LAMBDAS:
        f = fit(d["train"], lam, mask)
        tries.append((float(race_log_loss(d["validation"], f["theta"]).mean()), lam, f))
    _, best_lam, best = min(tries, key=lambda t: t[0])

    coefficients = []
    for i, name in enumerate(("log_q", *MODEL_FEATURES)):
        b, se = float(best["theta"][i]), float(best["se"][i])
        active = bool(mask[i])
        row: dict[str, Any] = {
            "feature": name,
            "label": FEATURE_LABELS[name],
            "active": active,
            "beta": b,
            "low": b - Z * se if active else None,
            "high": b + Z * se if active else None,
            "p": float(2 * norm.sf(abs(b / se))) if active and se > 0 else None,
        }
        if i > 0 and active:
            # Win odds multiplied by exp(β) for one standard deviation more of the factor.
            row["per_sd"] = math.exp(b)
            row["sd"] = float(stds[i - 1])
        coefficients.append(row)

    live = fit(design(df, means, stds), best_lam, mask)
    report = {
        "kind": "model",
        "model": NAME,
        "version": VERSION,
        "generated_at": utcnow().isoformat(timespec="seconds"),
        "discipline": discipline,
        "discipline_label": discipline_label(discipline),
        "split": {
            "train_end": split.train_end.isoformat(),
            "validation_end": split.validation_end.isoformat(),
        },
        "races": {k: len(v.starts) for k, v in d.items()},
        "lambda": best_lam,
        "validation_by_lambda": [{"lambda": lam, "log_loss": ll} for ll, lam, _ in tries],
        "market_alpha": float(market["theta"][0]),
        "coefficients": coefficients,
        "validation": _compare(d["validation"], best["theta"], market["theta"]),
        "test": _compare(d["test"], best["theta"], market["theta"]),
        "test_bets": _bets(d["test"], best["theta"], parts["test"], dividends),
        "params": {
            "features": list(MODEL_FEATURES),
            "means": means.tolist(),
            "stds": stds.tolist(),
            "theta": live["theta"].tolist(),
            "lambda": best_lam,
            "fitted_through": df["day"].max().isoformat(),  # type: ignore[union-attr]
        },
    }
    return report


def predict(params: dict[str, Any], frame: pl.DataFrame) -> np.ndarray:
    """Win probabilities for the rows of one race, in ``frame`` order."""
    if list(params["features"]) != list(MODEL_FEATURES):
        raise ValueError("paramètres d'une autre version du modèle")
    means, stds = np.array(params["means"]), np.array(params["stds"])
    x = frame.select(MODEL_FEATURES).to_numpy().astype(np.float64)
    x = np.where(stds > 0, (x - means) / np.where(stds > 0, stds, 1.0), 0.0)
    z = np.hstack([frame["log_q"].to_numpy().astype(np.float64)[:, None], x])
    s = z @ np.array(params["theta"])
    e = np.exp(s - s.max())
    return e / e.sum()


def load_dividends(db_path: Path) -> pl.DataFrame | None:
    import duckdb

    con = duckdb.connect(str(db_path), read_only=True)
    try:
        rows = con.execute(
            "SELECT race_id, bet_type, combination, per_euro FROM dividends "
            "WHERE bet_type IN ('SIMPLE_GAGNANT', 'SIMPLE_PLACE') AND NOT refunded"
        ).fetchall()
    except duckdb.Error:
        return None
    finally:
        con.close()
    return pl.DataFrame(
        rows,
        schema={
            "race_id": pl.Utf8,
            "bet_type": pl.Utf8,
            "combination": pl.Utf8,
            "per_euro": pl.Float64,
        },
        orient="row",
    )


# ------------------------------------------------------------------------------ output


def render_markdown(rep: dict[str, Any]) -> str:
    def f(x: Any, d: int = 4) -> str:
        return "—" if x is None else f"{x:.{d}f}"

    lines = [
        f"# Modèle Marché+ — {rep['discipline_label']}",
        "",
        f"Généré le {rep['generated_at']} · courses : apprentissage {rep['races']['train']}, "
        f"réglage {rep['races']['validation']}, test {rep['races']['test']} · λ = {rep['lambda']:g}"
        f" · α du marché seul = {rep['market_alpha']:.3f}.",
        "",
        "## Ce que chaque facteur ajoute à la cote (fenêtre d'apprentissage)",
        "",
        "Effet = chances de gagner multipliées par ce nombre pour un écart-type de plus du facteur, "
        "*à cote égale*. ×1,00 : la cote l'avait déjà intégré.",
        "",
        "| Facteur | β | IC 95 % | Effet par écart-type | p |",
        "|---|---:|---|---:|---:|",
    ]
    for c in rep["coefficients"]:
        if not c["active"]:
            lines.append(f"| {c['label']} | — | inactif (aucune variation) | — | — |")
            continue
        lines.append(
            f"| {c['label']} | {f(c['beta'], 3)} | [{f(c['low'], 3)} ; {f(c['high'], 3)}] "
            f"| {'—' if 'per_sd' not in c else f'×{c["per_sd"]:.3f}'} | {f(c['p'], 3)} |"
        )
    for phase, title in (("validation", "Réglage"), ("test", "Test (décision)")):
        v = rep[phase]
        if "difference" not in v:
            continue
        lines += [
            "",
            f"## {title} : log loss par course (plus bas = mieux)",
            "",
            f"Modèle {f(v['log_loss_model'])} · marché calibré {f(v['log_loss_market'])} · "
            f"différence {f(v['difference'])} [{f(v['ci_low'])} ; {f(v['ci_high'])}] sur "
            f"{v['races']} courses → **{v['verdict']}**.",
        ]
    bets = rep.get("test_bets") or {}
    if bets:
        lines += [
            "",
            "## Test : paris fictifs à 1 €",
            "",
            "| Stratégie | Paris | ROI | IC 95 % | Taux de réussite |",
            "|---|---:|---:|---|---:|",
        ]
        for name, b in bets.items():
            if "roi" not in b:
                lines.append(f"| {name} | {b['bets']} | — | — | — |")
                continue
            lines.append(
                f"| {name} | {b['bets']} | {100 * b['roi']:+.1f} % | [{100 * b['roi_low']:+.1f} % ; "
                f"{100 * b['roi_high']:+.1f} %] | {100 * b['hit_rate']:.1f} % |"
            )
    return "\n".join(lines) + "\n"


def write_model(rep: dict[str, Any], runs: Path) -> Path:
    stamp = rep["generated_at"].replace(":", "").replace("-", "")[:15]
    out = runs / f"model_{rep['discipline']}_{stamp}Z"
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(
        json.dumps(rep, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    (out / "report.md").write_text(render_markdown(rep), encoding="utf-8")
    return out


def latest_params(runs: Path, discipline: str) -> dict[str, Any] | None:
    from predlab.racing.profile import latest

    rep = latest(runs, "model", discipline)
    if rep is None or rep.get("version") != VERSION:
        return None
    return {**rep["params"], "report": rep["id"]}


def fitted_until(params: dict[str, Any]) -> date:
    return date.fromisoformat(params["fitted_through"])


def model_for_paths(runs: Path, database: Path) -> Any:
    """The carnet's ``model_for``: latest parameters of the discipline, history from the
    database as of its last nightly build, starters in card order. None without a model."""
    from predlab.racing.features import history, live_frame

    cache: dict[str, dict[str, Any] | None] = {}

    def model_for(race: Any, card: Any, runners: list[Any]) -> tuple[np.ndarray, str] | None:
        if race.discipline not in cache:
            cache[race.discipline] = latest_params(runs, race.discipline)
        params = cache[race.discipline]
        if params is None or not database.exists():
            return None
        by_number = {x.number: x for x in runners}
        ordered = [by_number[s.number] for s in card.starters]
        odds = {s.number: s.odds for s in card.starters}
        frame = live_frame(race, ordered, odds, history(database, race.discipline))
        return predict(params, frame), str(params["report"])

    return model_for
