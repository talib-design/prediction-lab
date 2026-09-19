"""Scoring a probabilistic forecast against what actually came out.

Four quantities, and it is worth being precise about what each can and cannot show.

``log_loss`` and ``brier`` are **proper** scoring rules on the marginals: a model
minimises them by reporting what it actually believes. They are the decision criteria.

``mass_on_drawn`` is the total probability the model had placed on the numbers that
came out. Under a fair mechanism its expectation is exactly ``k * k / size`` for every
model, which makes it a readable "did it do better than chance" figure. It is *not*
proper -- a model could inflate it by concentrating mass -- so it is a diagnostic.

``matches`` is the count of correctly predicted numbers. It is reported because people
expect it, and it is the weakest of the four: every legal ticket has the same expected
match count under fairness, so a difference in matches between two models is almost
entirely sampling noise. It never decides anything here.

All four are scored on marginals, not on the joint distribution over combinations.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from predlab.models.base import Forecast, PoolForecast


@dataclass(frozen=True, slots=True)
class PoolScore:
    """Scores for one pool on one draw."""

    pool: str
    log_loss: float
    brier: float
    mass_on_drawn: float
    baseline_mass: float

    @property
    def mass_lift(self) -> float:
        """Ratio of realised probability mass to what a fair-mechanism model gets.

        1.0 means "indistinguishable from assuming fairness" on this draw.
        """
        return self.mass_on_drawn / self.baseline_mass


def score_pool(pf: PoolForecast, drawn: np.ndarray) -> PoolScore:
    """Score one pool's forecast against the numbers actually drawn."""
    pf.pool.validate_combination(tuple(int(n) for n in np.sort(drawn)))
    y = pf.outcome_vector(drawn)
    p = pf.inclusion_probs
    return PoolScore(
        pool=pf.pool.name,
        log_loss=float(-np.mean(y * np.log(p) + (1.0 - y) * np.log1p(-p))),
        brier=float(np.mean((p - y) ** 2)),
        mass_on_drawn=float(p[y > 0].sum()),
        baseline_mass=pf.pool.k * pf.pool.marginal_probability,
    )


def score_forecast(forecast: Forecast, drawn: dict[str, np.ndarray]) -> dict[str, PoolScore]:
    return {name: score_pool(pf, drawn[name]) for name, pf in forecast.pools.items()}


def count_matches(ticket: tuple[int, ...], drawn: np.ndarray) -> int:
    return len(set(ticket) & {int(n) for n in drawn})


def expected_calibration_error(
    probabilities: np.ndarray, outcomes: np.ndarray, n_bins: int = 10
) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """Binned calibration of per-number predictions.

    Returns ``(ece, bin_centres, empirical_rate, bin_counts)``. Bins with no
    observations are reported as NaN rather than silently dropped, because an empty
    bin is information: the model never made a prediction in that range.
    """
    if probabilities.shape != outcomes.shape:
        raise ValueError("probabilities and outcomes must have the same shape")
    p = probabilities.ravel()
    y = outcomes.ravel()
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1], right=False), 0, n_bins - 1)

    centres = np.full(n_bins, np.nan)
    empirical = np.full(n_bins, np.nan)
    counts = np.zeros(n_bins, dtype=np.int64)
    ece = 0.0
    for b in range(n_bins):
        mask = idx == b
        counts[b] = int(mask.sum())
        if counts[b] == 0:
            continue
        centres[b] = float(p[mask].mean())
        empirical[b] = float(y[mask].mean())
        ece += counts[b] / len(p) * abs(empirical[b] - centres[b])
    return ece, centres, empirical, counts
