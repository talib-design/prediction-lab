"""Turning a backtest into something a person can act on.

A report has one job: make the reader able to tell whether the result is any good,
including when the answer is no. Three things decide that, and they are ordered here
by how often they are left out of reports that are trying to sell something.

**Is it better than the obvious thing?** MASE against 1.0, and the reference model
named explicitly. A model presented without its baseline is a model whose baseline
would have won.

**Does it know what it does not know?** Coverage against the nominal level. A point
forecast quoted without this is a claim no one can check.

**What would make it wrong?** The quantisation floor, the regime break, the horizon
at which everything collapses to the same number. Written down while the result is
still good, because that is the only time anyone writes them down.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from predlab import __version__
from predlab.data.sources.dares import (
    ATTRIBUTION,
    LICENCE,
    MonthlySeries,
    next_period,
    publication_lag_months,
    quantisation_floor,
)
from predlab.ts.backtest import BacktestResult

REFERENCE_MODEL = "seasonal_naive"


def build_report(
    result: BacktestResult,
    series: MonthlySeries,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """A machine-readable record of one run, complete enough to be re-checked."""
    moment = now or datetime.now(UTC)
    floor = quantisation_floor(series)

    horizons: list[dict[str, Any]] = []
    for h in result.horizons:
        ranked = result.for_horizon(h)
        reference = result.reference(h)
        best = ranked[0]
        # "Better than the reference" is only worth saying with the margin attached,
        # and only worth believing if it also exceeds the data's own resolution.
        margin = None if reference is None else reference.mase - best.mase
        horizons.append(
            {
                "horizon": h,
                "n": best.n,
                "reference": REFERENCE_MODEL,
                "reference_mase": None if reference is None else round(reference.mase, 4),
                "best": best.model,
                "best_mase": round(best.mase, 4),
                "best_mape": round(best.mape, 4),
                "margin_vs_reference": None if margin is None else round(margin, 4),
                "beats_reference": bool(margin is not None and margin > 0),
                "mape_above_quantisation_floor": bool(best.mape > floor),
                "calibrated_80": best.coverage_80.verdict() == "calibré",
                "models": [row.summary() for row in ranked],
            }
        )

    return {
        "schema": "predlab-ts-report-1",
        "generated_at": moment.isoformat(timespec="seconds"),
        "code_version": __version__,
        "series": {
            "start": result.series_start,
            "end": result.series_end,
            "n": len(series),
            "source": ATTRIBUTION,
            "licence": LICENCE,
            "quantisation_floor": round(floor, 5),
            "publication_lag_months": publication_lag_months(series, moment.date()),
            "first_unpublished_period": next_period(result.series_end),
            "periods": list(series.periods),
            "values": list(series.values),
        },
        "backtest": {
            "train_end": result.train_end,
            "horizons": list(result.horizons),
            "mase_scale": round(result.scale, 2),
        },
        "horizons": horizons,
        "caveats": _caveats(result, floor),
    }


def _caveats(result: BacktestResult, floor: float) -> list[str]:
    """Limits stated while the result still looks good, which is the only useful time."""
    out = [
        f"Les valeurs publiées sont arrondies à la centaine, soit {floor:.2%} du "
        "niveau moyen de la série. Une erreur sous ce seuil n'est pas de la "
        "compétence : elle est sous la résolution de la donnée.",
        "Série brute, non désaisonnalisée. Une partie de la performance de tout "
        "modèle vient du calendrier, pas du marché.",
        "Mars-mai 2020 est une rupture de régime, pas un point aberrant à retirer. "
        "Elle est incluse dans l'évaluation et pèse sur toutes les erreurs moyennes.",
        "Offres collectées par France Travail, pas le marché cadre entier. C'est un "
        "indicateur, pas un recensement.",
        "Le lien entre cette série et les volumes internes Apec n'est pas mesuré et "
        "ne doit pas être affirmé.",
    ]
    # Stated only when true, so that it carries information rather than boilerplate.
    long_h = [h for h in result.horizons if h >= 12]
    if long_h:
        out.append(
            f"À l'horizon {min(long_h)}, le naïf saisonnier se réduit exactement au "
            "naïf — le même mois l'an dernier, douze mois à l'avance, est la dernière "
            "observation. Leurs scores y coïncident par construction, pas par hasard."
        )
    return out


def render_markdown(report: dict[str, Any]) -> str:
    """The same content as prose, for a terminal or a pull request."""
    series = report["series"]
    lines = [
        "# Prévision des offres cadre collectées",
        "",
        f"Série {series['start']} → {series['end']} ({series['n']} mois). "
        f"Entraînement ≤ {report['backtest']['train_end']}.",
        f"Source : {series['source']} — {series['licence']}.",
        "",
        f"Dernier chiffre publié : **{series['end']}**, soit "
        f"{series['publication_lag_months']} mois de retard. Le premier mois non "
        f"publié est **{series['first_unpublished_period']}**.",
        "",
        "## Verdict par horizon",
        "",
    ]
    for block in report["horizons"]:
        verdict = (
            f"**{block['best']}** bat la référence de {block['margin_vs_reference']:+.3f} MASE"
            if block["beats_reference"]
            else f"aucun modèle ne bat la référence (`{block['reference']}`)"
        )
        calib = "intervalles calibrés" if block["calibrated_80"] else "**intervalles mal calibrés**"
        lines += [
            f"### Horizon {block['horizon']} mois — {block['n']} prévisions",
            "",
            f"{verdict} · {calib}.",
            "",
            "| modèle | MASE | MAPE | couv. 80 % | verdict | largeur |",
            "|---|---:|---:|---:|---|---:|",
        ]
        for row in block["models"]:
            mark = " ←réf" if row["model"] == block["reference"] else ""
            lines.append(
                f"| `{row['model']}`{mark} | {row['mase']:.3f} | {row['mape']:.1%} | "
                f"{row['coverage_80']:.1%} | {row['coverage_80_verdict']} | "
                f"{row['coverage_80_width']:,.0f} |"
            )
        lines.append("")

    lines += ["## Ce qui limite ces chiffres", ""]
    lines += [f"- {c}" for c in report["caveats"]]
    lines += ["", f"_predlab {report['code_version']} — {report['generated_at']}_"]
    return "\n".join(lines)


def to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False)
