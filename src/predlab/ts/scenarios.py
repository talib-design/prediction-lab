"""Conditional scenarios: judgement, kept visibly outside the model.

The request that produced this module was to "take into account the elections, the
economy, the geopolitical tensions". Two of those three cannot enter a model built on
367 months, and saying so precisely is more useful than a vague caveat: the period
contains roughly seven French national elections, which is not enough observations to
estimate an effect of unknown sign, size and delay; "geopolitical tension" is not a
series at all, so there is nothing to fit it against.

What can be done is this. State a scenario, state the adjustment it implies, state
what that number rests on, and keep all of it **outside** the forecast rather than
folded into it. Then a reader can accept the measurement and reject the judgement, or
the reverse, which is impossible once the two are added together.

The design rules follow from that one purpose.

**A scenario never changes the recorded forecast.** It produces a separate figure,
carrying its own label. The ledger keeps the measured forecast alone, so the track
record scores the model, not the model plus someone's opinion about the Middle East.

**Every scenario names its author and its basis.** An adjustment with no stated source
is indistinguishable from a number someone liked, and in six months nobody will
remember which it was. A historical analogue is the strongest basis available here and
still only an analogue: 2020 says what a sudden stop did once, not what the next one
will do.

**Probabilities are the author's, and labelled as such.** They are not estimated from
anything and the code never treats them as if they were -- there is no expected value
computed across scenarios, because averaging invented probabilities produces a number
that looks measured and is not.

This is, notably, what Apec itself does: its 2026 figure is a forecast, and the Middle
East is a warning printed next to it, not a variable inside it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

Basis = Literal["historical_analogue", "published_estimate", "expert_judgement"]

BASIS_LABELS: dict[str, str] = {
    "historical_analogue": "Analogue historique",
    "published_estimate": "Estimation publiée",
    "expert_judgement": "Jugement d'expert",
}


class ScenarioError(ValueError):
    """A scenario is missing something that would make it accountable."""


@dataclass(frozen=True, slots=True)
class Scenario:
    """One named alternative to the baseline, with its adjustment and its grounds.

    ``adjustment`` is a multiplicative factor applied to the baseline: 0.85 means
    "15% below". It is a judgement, never a measurement, and everything in this class
    exists to keep that distinction visible six months from now.
    """

    key: str
    name: str
    trigger: str
    adjustment: float
    basis: Basis
    rationale: str
    author: str
    subjective_probability: float | None = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds"))

    def __post_init__(self) -> None:
        if not 0.1 <= self.adjustment <= 3.0:
            raise ScenarioError(
                f"{self.key}: adjustment {self.adjustment} is outside 0.1-3.0; a factor "
                "that extreme is a different series, not a scenario"
            )
        if not self.rationale.strip():
            raise ScenarioError(
                f"{self.key}: a scenario without a stated rationale is a number "
                "someone liked, and in six months nobody will be able to tell"
            )
        if not self.author.strip():
            raise ScenarioError(f"{self.key}: every adjustment must name its author")
        if self.subjective_probability is not None and not (
            0.0 < self.subjective_probability < 1.0
        ):
            raise ScenarioError(
                f"{self.key}: a subjective probability must lie strictly in (0, 1); "
                "certainty is not a scenario"
            )

    @property
    def percent(self) -> float:
        return (self.adjustment - 1.0) * 100.0

    def apply(self, baseline: float) -> float:
        return baseline * self.adjustment

    def payload(self) -> dict[str, object]:
        return {
            "key": self.key,
            "name": self.name,
            "trigger": self.trigger,
            "adjustment": self.adjustment,
            "percent": round(self.percent, 1),
            "basis": self.basis,
            "basis_label": BASIS_LABELS[self.basis],
            "rationale": self.rationale,
            "author": self.author,
            "subjective_probability": self.subjective_probability,
            "created_at": self.created_at,
            "is_judgement": True,
        }


def apply_all(baseline: float, scenarios: list[Scenario]) -> dict[str, object]:
    """Baseline plus one figure per scenario. No expected value is computed.

    Combining scenarios by their stated probabilities would produce a single number
    that looks like a forecast and is an average of guesses. The output is a list on
    purpose: the reader picks the world they think they are in.
    """
    return {
        "baseline": round(baseline),
        "baseline_is_measured": True,
        "scenarios": [{**s.payload(), "value": round(s.apply(baseline))} for s in scenarios],
        "note": (
            "Les scénarios sont des jugements, pas des mesures. Ils n'entrent pas dans "
            "la prévision enregistrée et ne sont pas moyennés : aucune valeur "
            "« espérée » n'est calculée, car moyenner des probabilités inventées "
            "produit un chiffre qui a l'air mesuré et ne l'est pas."
        ),
    }


def default_scenarios(author: str = "Chris") -> list[Scenario]:
    """A starting set, each tied to something that actually happened or was published.

    These are illustrations of the form, not recommendations. The point of the module
    is that whoever puts a number here has to say where it came from.
    """
    return [
        Scenario(
            key="choc_energetique",
            name="Choc énergétique durable",
            trigger="Le conflit au Moyen-Orient débouche sur une crise énergétique "
            "affectant inflation et taux en Europe",
            adjustment=0.88,
            basis="historical_analogue",
            rationale="Entre le pic de septembre 2022 et le creux de l'été 2023, les "
            "offres cadre collectées ont reculé d'environ 12 % sur un an pendant le "
            "précédent choc énergétique. Ce chiffre décrit ce qui s'est passé une fois, "
            "pas ce qui se passera.",
            author=author,
            subjective_probability=0.2,
        ),
        Scenario(
            key="apec_2026",
            name="Reprise conforme à la prévision Apec",
            trigger="Les recrutements cadres progressent de 4 % en 2026 comme l'Apec "
            "l'a publié en avril 2026",
            adjustment=1.04,
            basis="published_estimate",
            rationale="L'Apec prévoit 305 800 recrutements cadres en 2026, +4 % sur "
            "2025. Transposer ce taux aux offres collectées suppose que les deux "
            "grandeurs bougent ensemble — un lien qui n'est pas mesuré à ce jour.",
            author=author,
            subjective_probability=0.35,
        ),
        Scenario(
            key="arret_brutal",
            name="Arrêt brutal",
            trigger="Choc systémique comparable au confinement de mars 2020",
            adjustment=0.55,
            basis="historical_analogue",
            rationale="Mars-mai 2020 : les offres cadre collectées sont passées de "
            "11 400 à 4 600, soit une chute de 60 % en deux mois, avec un retour au niveau "
            "antérieur en environ un an. L'ampleur retenue ici est volontairement plus "
            "faible que l'épisode observé, qui reste le pire de trente ans.",
            author=author,
            subjective_probability=0.05,
        ),
    ]
