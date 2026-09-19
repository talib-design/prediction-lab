"""Turning a backtest into a report a sceptic can audit.

Two rules shape this module.

**Power comes first.** The detection floor is printed before any result, because
"nothing found" only means something once the reader knows what could have been found.

**Observation, anomaly and forecast are never merged.** The descriptive section says
what the history looks like. The predictive section says whether any model helped
predict the next draw. A pattern can be unusual and useless at the same time, and the
report is laid out so that confusing the two takes effort.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from predlab.backtest.engine import BacktestResult
from predlab.core.gamespec import GameSpec
from predlab.eval.metrics import expected_calibration_error
from predlab.eval.power import minimum_detectable_effect, uniformity_monte_carlo
from predlab.eval.uncertainty import (
    benjamini_hochberg,
    block_bootstrap,
    paired_block_permutation_test,
)

REFERENCE_MODEL = "uniform"
DECISION_METRIC = "log_loss"


@dataclass(frozen=True, slots=True)
class ModelSummary:
    model: str
    pool: str
    phase: str
    n_draws: int
    log_loss: float
    log_loss_ci: tuple[float, float]
    brier: float
    mass_lift: float
    mean_matches: float
    calibration_error: float
    difference_vs_reference: float
    p_value_vs_reference: float
    survives_fdr: bool
    verdict: str


def summarise(
    result: BacktestResult,
    *,
    phase: str | None = None,
    n_resamples: int = 2000,
    n_permutations: int = 5000,
    seed: int = 0,
) -> list[ModelSummary]:
    """Compare every model to the reference on every pool, with multiplicity control."""
    reference = result.run_for(REFERENCE_MODEL)
    rows: list[ModelSummary] = []
    raw_p: list[float] = []

    for pool in result.spec.pools:
        for run in result.runs:
            mask = run.mask_for(phase)
            if mask.sum() < 2:
                continue
            series = run.series(pool.name, DECISION_METRIC)[mask]
            ref_series = reference.series(pool.name, DECISION_METRIC)[mask]
            ci = block_bootstrap(series, n_resamples=n_resamples, seed=seed)
            test = paired_block_permutation_test(
                series, ref_series, n_permutations=n_permutations, seed=seed
            )
            ece, _, _, _ = expected_calibration_error(
                run.predicted_probs[pool.name][mask],
                run.outcomes[pool.name][mask].astype(np.float64),
            )
            baseline_mass = pool.k * pool.marginal_probability
            rows.append(
                ModelSummary(
                    model=run.model_name,
                    pool=pool.name,
                    phase=phase or "all",
                    n_draws=int(mask.sum()),
                    log_loss=ci.point,
                    log_loss_ci=(ci.low, ci.high),
                    brier=float(run.series(pool.name, "brier")[mask].mean()),
                    mass_lift=float(
                        run.series(pool.name, "mass_on_drawn")[mask].mean() / baseline_mass
                    ),
                    mean_matches=float(run.matches[pool.name][mask].mean()),
                    calibration_error=ece,
                    difference_vs_reference=test.mean_difference,
                    p_value_vs_reference=test.p_value,
                    survives_fdr=False,
                    verdict=test.verdict(),
                )
            )
            raw_p.append(test.p_value)

    if not rows:
        return rows

    # Every model tested against the reference is another chance at a false positive.
    surviving = benjamini_hochberg(np.array(raw_p), q=0.05)
    return [
        ModelSummary(**{**asdict(row), "survives_fdr": bool(flag)})
        for row, flag in zip(rows, surviving, strict=True)
    ]


def describe_history(
    spec: GameSpec,
    pool_draws: dict[str, np.ndarray],
    *,
    n_simulations: int = 2000,
    seed: int = 0,
) -> dict[str, Any]:
    """Descriptive statistics only. Says nothing about prediction, by construction."""
    out: dict[str, Any] = {}
    for pool in spec.pools:
        draws = pool_draws[pool.name]
        n_draws = len(draws)
        counts = np.bincount(draws.ravel() - pool.low, minlength=pool.size).astype(np.int64)
        statistic, p_value = uniformity_monte_carlo(
            counts, pool, n_draws, n_simulations=n_simulations, seed=seed
        )
        expected = n_draws * pool.marginal_probability
        out[pool.name] = {
            "n_draws": n_draws,
            "expected_count_per_number": expected,
            "observed_min": int(counts.min()),
            "observed_max": int(counts.max()),
            "most_frequent": int(np.argmax(counts)) + pool.low,
            "least_frequent": int(np.argmin(counts)) + pool.low,
            "chi_square_statistic": statistic,
            "monte_carlo_p_value": p_value,
            "uniformity_rejected_at_5pct": p_value < 0.05,
            "counts": counts.tolist(),
        }
    return out


def conclusion(summaries: list[ModelSummary], spec: GameSpec, n_draws: int) -> dict[str, Any]:
    """The verdict, written so that finding nothing is a legitimate outcome."""
    winners = [s for s in summaries if s.survives_fdr and s.verdict == "better"]
    floors = {
        pool.name: minimum_detectable_effect(pool, n_draws, multiplicity_correction=True)
        for pool in spec.pools
    }
    if winners:
        headline = (
            f"{len(winners)} model/pool combination(s) beat the {REFERENCE_MODEL} "
            "reference after false-discovery-rate control. This is a candidate finding, "
            "not a conclusion: it must survive a forward test on draws that did not "
            "exist when the model was written."
        )
    else:
        headline = "No statistically meaningful predictive signal was detected."
    return {
        "headline": headline,
        "reference_model": REFERENCE_MODEL,
        "decision_metric": DECISION_METRIC,
        "candidates": [f"{w.model}/{w.pool}" for w in winners],
        "detection_floor": {
            name: {
                "absolute": f.absolute_effect,
                "relative": f.relative_effect,
                "note": f.describe(),
            }
            for name, f in floors.items()
        },
        "caveat": (
            "A null result here is bounded by statistical power, not by the absence of "
            "any bias. With this many draws only the departures listed under "
            "detection_floor could have been seen at all."
        ),
    }


def build_report(
    result: BacktestResult,
    pool_draws: dict[str, np.ndarray],
    *,
    phase: str | None = None,
    seed: int = 0,
    n_resamples: int = 2000,
    n_permutations: int = 5000,
    n_simulations: int = 2000,
) -> dict[str, Any]:
    """The machine-readable report. :func:`render_markdown` formats the same content."""
    summaries = summarise(
        result,
        phase=phase,
        seed=seed,
        n_resamples=n_resamples,
        n_permutations=n_permutations,
    )
    n_draws = result.n_draws_total
    return {
        "schema": "predlab.report.v1",
        "provenance": result.provenance(),
        "power": {
            pool.name: {
                "uncorrected": asdict(
                    minimum_detectable_effect(pool, n_draws, multiplicity_correction=False)
                ),
                "bonferroni": asdict(
                    minimum_detectable_effect(pool, n_draws, multiplicity_correction=True)
                ),
            }
            for pool in result.spec.pools
        },
        "descriptive": describe_history(
            result.spec, pool_draws, seed=seed, n_simulations=n_simulations
        ),
        "predictive": [asdict(s) for s in summaries],
        "conclusion": conclusion(summaries, result.spec, n_draws),
    }


def render_markdown(report: dict[str, Any]) -> str:
    prov = report["provenance"]
    lines: list[str] = [
        "# Prediction Lab evaluation report",
        "",
        f"**Game:** {prov['game']}  ",
        f"**Generated:** {prov['created_at']}  ",
        f"**Code version:** {prov['code_version']}  ",
        f"**Dataset fingerprint:** `{prov['dataset_fingerprint'][:16]}…`  ",
        f"**Draws in dataset:** {prov['n_draws_total']}  ",
        f"**Selection policy:** {prov['selection_policy']}",
        "",
        "## 1. What could have been detected",
        "",
        "Read this before the results. It bounds what any conclusion below can mean.",
        "",
        "| Pool | Correction | Minimum detectable bias | Relative |",
        "|---|---|---|---|",
    ]
    for pool, entry in report["power"].items():
        for key in ("uncorrected", "bonferroni"):
            f = entry[key]
            lines.append(
                f"| {pool} | {f['correction']} | {f['absolute_effect']:.4f} | "
                f"{f['relative_effect'] * 100:.1f}% |"
            )

    lines += [
        "",
        "## 2. Observation — what the history looks like",
        "",
        "Descriptive only. Nothing in this section is a claim about future draws.",
        "",
        "| Pool | Draws | Expected count | Min | Max | chi2 | Monte-Carlo p | Uniformity rejected |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for pool, d in report["descriptive"].items():
        lines.append(
            f"| {pool} | {d['n_draws']} | {d['expected_count_per_number']:.1f} | "
            f"{d['observed_min']} | {d['observed_max']} | {d['chi_square_statistic']:.2f} | "
            f"{d['monte_carlo_p_value']:.4f} | "
            f"{'yes' if d['uniformity_rejected_at_5pct'] else 'no'} |"
        )

    lines += [
        "",
        "## 3. Forecast — did any model help predict the next draw?",
        "",
        f"Decision metric: **{report['conclusion']['decision_metric']}** (lower is better), "
        f"against the **{report['conclusion']['reference_model']}** reference. "
        "Intervals are moving-block bootstrap; p-values are paired block permutation "
        "tests; the last column applies Benjamini-Hochberg across every comparison.",
        "",
        "| Model | Pool | Phase | n | log loss [95% CI] | Brier | Mass lift | Matches | ECE | vs ref | p | Survives FDR |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in report["predictive"]:
        lo, hi = s["log_loss_ci"]
        lines.append(
            f"| {s['model']} | {s['pool']} | {s['phase']} | {s['n_draws']} | "
            f"{s['log_loss']:.5f} [{lo:.5f}, {hi:.5f}] | {s['brier']:.5f} | "
            f"{s['mass_lift']:.3f} | {s['mean_matches']:.3f} | "
            f"{s['calibration_error']:.4f} | {s['verdict']} | "
            f"{s['p_value_vs_reference']:.4f} | {'yes' if s['survives_fdr'] else 'no'} |"
        )

    concl = report["conclusion"]
    lines += [
        "",
        "## 4. Conclusion",
        "",
        f"**{concl['headline']}**",
        "",
        concl["caveat"],
        "",
        "---",
        "",
        "*Mass lift is the probability the model placed on the numbers that came out, "
        "divided by what assuming fairness would place there; 1.0 means "
        "indistinguishable from assuming fairness. Match count is reported because it "
        "is expected, but under a fair mechanism every legal ticket has the same "
        "expected match count, so it decides nothing.*",
        "",
    ]
    return "\n".join(lines)
