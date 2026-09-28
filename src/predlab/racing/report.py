"""The backtest report: power first, then scores, then the comparison that decides.

Same discipline as the lottery report: a reader must be able to tell, from the report
alone, whether a result is good -- including when the honest answer is "we cannot
tell yet". Every comparison is against ``market_calibrated`` (docs/METHODOLOGY.md §5),
on the same races, with a block-bootstrap interval, a paired block-permutation
p-value and Benjamini-Yekutieli control over all comparisons in the report.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from predlab.eval.uncertainty import (
    benjamini_hochberg,
    block_bootstrap,
    paired_block_permutation_test,
)
from predlab.racing.backtest import BacktestResult, ModelRun, calibration_error, calibration_table

REFERENCE = "market_calibrated"
Z_POWER = 1.96 + 0.84  # two-sided 5 %, 80 % power


def _phase_mask(run: ModelRun, phase: str) -> np.ndarray:
    return np.array([p == phase for p in run.phases], dtype=bool)


def _runner_mask(run: ModelRun, phase: str) -> np.ndarray:
    return np.array([p == phase for p in run.runner_phases], dtype=bool)


def decision_phase(result: BacktestResult) -> str:
    phases = set(result.runs[0].phases) if result.runs else set()
    return "test" if "test" in phases else ("all" if "all" in phases else "validation")


def summarise(result: BacktestResult) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for phase in sorted(set(result.runs[0].phases)) if result.runs else []:
        rows = []
        for run in result.runs:
            m, rm = _phase_mask(run, phase), _runner_mask(run, phase)
            probs, ys = np.array(run.probs)[rm], np.array(run.outcomes)[rm]
            rows.append(
                {
                    "model": run.name,
                    "n_races": int(m.sum()),
                    "log_loss": float(np.mean(run.series("log_loss")[m])),
                    "brier": float(np.mean(run.series("brier")[m])),
                    "top1": float(np.mean(run.series("top1")[m])),
                    "mrr": float(np.mean(run.series("rr")[m])),
                    "calibration_error": calibration_error(probs, ys),
                }
            )
        out[phase] = rows
    return out


def compare(result: BacktestResult, phase: str, reference: str = REFERENCE) -> list[dict[str, Any]]:
    ref = result.run(reference)
    mask = _phase_mask(ref, phase)
    base = ref.series("log_loss")[mask]
    rows: list[dict[str, Any]] = []
    for run in result.runs:
        if run.name == reference:
            continue
        model = run.series("log_loss")[_phase_mask(run, phase)]
        diff = model - base
        n = len(diff)
        if n < 10:
            rows.append({"model": run.name, "n_races": n, "verdict": "échantillon trop petit"})
            continue
        ci = block_bootstrap(diff)
        test = paired_block_permutation_test(model, base)
        sd = float(np.std(diff, ddof=1))
        rows.append(
            {
                "model": run.name,
                "n_races": n,
                "mean_difference": float(diff.mean()),
                "ci_low": ci.low,
                "ci_high": ci.high,
                "p_value": test.p_value,
                "sd_difference": sd,
                "minimum_detectable_effect": Z_POWER * sd / np.sqrt(n),
                "races_for_0_01": int(np.ceil((Z_POWER * sd / 0.01) ** 2)),
            }
        )
    tested = [r for r in rows if "p_value" in r]
    if tested:
        survive = benjamini_hochberg(np.array([r["p_value"] for r in tested]), dependent=True)
        for r, ok in zip(tested, survive, strict=True):
            r["survives_fdr"] = bool(ok)
            if ok and r["ci_high"] < 0:
                r["verdict"] = "meilleur que la référence"
            elif ok and r["ci_low"] > 0:
                r["verdict"] = "moins bon que la référence"
            else:
                r["verdict"] = "non distinguable de la référence"
    return rows


def build_report(result: BacktestResult, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    phase = decision_phase(result)
    calib = {}
    for name in ("market", REFERENCE):
        try:
            run = result.run(name)
        except KeyError:
            continue
        rm = _runner_mask(run, phase)
        calib[name] = calibration_table(np.array(run.probs)[rm], np.array(run.outcomes)[rm])
    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "code_version": result.code_version,
        "horizon_minutes": result.horizon_minutes,
        "split": result.split.as_dict() if result.split else None,
        "dataset_fingerprint": result.dataset_fingerprint,
        "n_events": result.n_events,
        "n_eligible": result.n_eligible,
        "decision_phase": phase,
        "reference": REFERENCE,
        "models": [{"name": r.name, "version": r.version, "config": r.config} for r in result.runs],
        "summary": summarise(result),
        "comparisons": compare(result, phase),
        "calibration": calib,
        **(extra or {}),
    }


def _f(x: Any, digits: int = 4) -> str:
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{digits}f}"


def render_markdown(report: dict[str, Any]) -> str:
    phase = report["decision_phase"]
    lines = [
        "# Backtest — plat, hippodromes français",
        "",
        f"Généré le {report['generated_at']} · horizon **T-{report['horizon_minutes']:g} min** · "
        f"code {report['code_version']} · empreinte `{report['dataset_fingerprint'][:12]}`",
        "",
        f"Courses chargées : {report['n_events']} · courses évaluées (cotes complètes à l'horizon) : "
        f"{report['n_eligible']} · phase de décision : **{phase}** · référence : `{report['reference']}`.",
        "",
        "## 1. Puissance",
        "",
        "Avant tout résultat : quel écart ce jeu de données permet-il de voir ?",
        "",
        "| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |",
        "|---|---:|---:|---:|---:|",
    ]
    for c in report["comparisons"]:
        if "sd_difference" in c:
            lines.append(
                f"| {c['model']} | {c['n_races']} | {_f(c['sd_difference'])} | "
                f"{_f(c['minimum_detectable_effect'])} | {c['races_for_0_01']} |"
            )
    lines += ["", "## 2. Scores par phase", ""]
    for ph, rows in report["summary"].items():
        lines += [
            f"### {ph}",
            "",
            "| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        for r in sorted(rows, key=lambda r: r["log_loss"]):
            lines.append(
                f"| {r['model']} | {r['n_races']} | {_f(r['log_loss'])} | {_f(r['brier'])} | "
                f"{_f(r['top1'], 3)} | {_f(r['mrr'], 3)} | {_f(r['calibration_error'])} |"
            )
        lines.append("")
    lines += [
        f"## 3. Comparaison à la référence (phase {phase})",
        "",
        "Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % "
        "par bootstrap en blocs, p par permutation appariée en blocs, correction "
        "Benjamini–Yekutieli sur toutes les lignes.",
        "",
        "| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |",
        "|---|---:|---:|---|---:|---|---|",
    ]
    for c in report["comparisons"]:
        if "mean_difference" not in c:
            lines.append(f"| {c['model']} | {c['n_races']} | — | — | — | — | {c['verdict']} |")
            continue
        lines.append(
            f"| {c['model']} | {c['n_races']} | {_f(c['mean_difference'])} | "
            f"[{_f(c['ci_low'])} ; {_f(c['ci_high'])}] | {_f(c['p_value'])} | "
            f"{'oui' if c['survives_fdr'] else 'non'} | {c['verdict']} |"
        )
    lines += ["", "## 4. Calibration du marché (niveau partant)", ""]
    for name, rows in report["calibration"].items():
        lines += [
            f"**{name}**",
            "",
            "| Tranche | Partants | Prévu | Observé |",
            "|---|---:|---:|---:|",
        ]
        lines += [
            f"| {r['bucket']} | {r['n']} | {_f(r['mean_forecast'], 3)} | {_f(r['observed'], 3)} |"
            for r in rows
        ]
        lines.append("")
    if "alpha" in report:
        lines += [
            f"Exposant de calibration du marché (dernier ajustement) : **α = {_f(report['alpha'], 3)}** "
            f"({report.get('alpha_refits', 0)} ajustements). α > 1 : le marché sous-estime les favoris.",
            "",
        ]
    lines += [
        "## 5. Limites",
        "",
        "- Départ **programmé**, pas réel : un retard décale l'horizon effectif.",
        "- Horodatage des cotes = celui publié par le PMU, pris pour vrai.",
        "- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.",
        "- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.",
        "",
    ]
    return "\n".join(lines)


def write_report(report: dict[str, Any], directory: Path) -> tuple[Path, Path]:
    stamp = report["generated_at"].replace(":", "").replace("-", "").replace("+0000", "Z")
    out = directory / f"backtest_T{report['horizon_minutes']:g}_{stamp}"
    out.mkdir(parents=True, exist_ok=True)
    md, js = out / "report.md", out / "report.json"
    md.write_text(render_markdown(report), encoding="utf-8")
    js.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return md, js
