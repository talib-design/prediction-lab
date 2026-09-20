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

# What each method actually does, in the words someone would use to describe it out
# loud. The identifiers are for the code; a reader should never have to decode
# `seasonal_naive_drift` to find out that it means "last year's same month, adjusted
# for how much the level has moved since".
METHOD_LABELS = {
    "naive": "Le mois dernier",
    "seasonal_naive": "Le même mois, l'an dernier",
    "drift": "La tendance longue",
    "seasonal_mean_3": "Ce mois-ci, moyenne des 3 dernières années",
    "seasonal_naive_drift": "L'an dernier, corrigé de la tendance récente",
}
METHOD_EXPLAINS = {
    "naive": "Recopie la dernière valeur connue. Le minimum syndical : toute méthode "
    "qui ne bat pas ça ne sert à rien.",
    "seasonal_naive": "Recopie le même mois de l'année précédente. Connaît le "
    "calendrier, ignore tout du niveau actuel.",
    "drift": "Prolonge la droite qui relie le premier et le dernier point.",
    "seasonal_mean_3": "Moyenne le même mois sur trois ans, pour lisser le bruit "
    "d'une seule année.",
    "seasonal_naive_drift": "Part du même mois l'an dernier, puis corrige de "
    "l'évolution récente du niveau. Calendrier et conjoncture ensemble.",
}


def label_of(model: str) -> str:
    """Human name for a method identifier, falling back to the identifier itself."""
    return METHOD_LABELS.get(model, model)


def explain_of(model: str) -> str:
    return METHOD_EXPLAINS.get(model, "")


def build_report(
    result: BacktestResult,
    series: MonthlySeries,
    *,
    now: datetime | None = None,
    forward: list[Any] | None = None,
    cumulative: dict[str, Any] | None = None,
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
        # A share out of ten, not a percentage. "The model promises its range will
        # contain reality 8 times out of 10; it managed 7.7" is a sentence anyone can
        # check. "80% nominal coverage, 77% empirical" is one only a statistician can.
        horizons.append(
            {
                "horizon": h,
                "n": best.n,
                "label": _horizon_label(h),
                "reference": REFERENCE_MODEL,
                "reference_mase": None if reference is None else round(reference.mase, 4),
                "best": best.model,
                "best_mase": round(best.mase, 4),
                "best_mape": round(best.mape, 4),
                "margin_vs_reference": None if margin is None else round(margin, 4),
                "beats_reference": bool(margin is not None and margin > 0),
                "mape_above_quantisation_floor": bool(best.mape > floor),
                "calibrated_80": best.coverage_80.verdict() == "calibré",
                "best_mae": round(best.mae, 0),
                "best_band_low": round(min(best.lows), 0) if best.lows else None,
                "models": [
                    {
                        **row.summary(),
                        "label": label_of(row.model),
                        "explain": explain_of(row.model),
                        "mae": round(row.mae, 0),
                        "kept_promise": round(row.coverage_80.empirical * 10, 1),
                        "is_reference": row.model == REFERENCE_MODEL,
                    }
                    for row in ranked
                ],
                "trace": {
                    "model": best.model,
                    "label": label_of(best.model),
                    "periods": list(best.periods),
                    "actuals": [round(v) for v in best.actuals],
                    "forecast": [round(v) for v in best.medians],
                    "low": [round(v) for v in best.lows],
                    "high": [round(v) for v in best.highs],
                },
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
        # The months the source has not published. Kept beside the backtest rather
        # than in a separate document, so a reader always sees the forecast next to
        # the measurement of how far that kind of forecast has been wrong before.
        "forward": [{**f.payload(), "label": label_of(f.method)} for f in (forward or [])],
        "cumulative": cumulative,
        "caveats": _caveats(result, floor),
    }


def _horizon_label(h: int) -> str:
    """The horizon as a person would say it, not as a parameter."""
    if h == 1:
        return "Le mois prochain"
    if h < 12:
        return f"Dans {h} mois"
    if h == 12:
        return "Dans un an"
    return f"Dans {h} mois"


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
