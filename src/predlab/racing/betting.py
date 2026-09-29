"""Fictitious betting, settled against the official PMU dividends.

Same spirit as the lottery experiment: **no real money, no account, no bet placed**.
Tickets are imagined at the prediction horizon and settled afterwards with the
dividends the PMU actually paid. The question is the one the brief asks in money
terms: does any rule, fixed in advance, lose less than the obvious ones -- or even
win -- once the pools' takeout has been paid?

Rules fixed before the first simulation (docs/METHODOLOGY.md §9):

* decisions use only the race card at the horizon (odds quoted by then);
* payouts use the final official dividends: pari-mutuel odds move after the decision,
  and that slippage is part of what is measured;
* one unit per ticket -- 1 EUR for simple and tiercé bets, the 2 EUR base stake for
  the Quinté+; no staking plan, no bankroll management;
* a ticket is only imagined on a bet type the PMU offered on that race (known from the
  dividend table: its presence carries no information about the result);
* a refunded bet type returns the stake;
* no ticket on a race whose quotes do not form one market (``RaceCard.market_coherent``,
  rule added 2026-09-29).

Strategies (every one gets a *favourite* and a *random* control on the same races):

| family | rule |
|---|---|
| ``SG favori`` / ``SG hasard`` | Simple gagnant on the shortest price / a random starter |
| ``SG top <model>`` | Simple gagnant on the model's most likely winner |
| ``SG valeur <model>`` | Simple gagnant on every starter with p × odds ≥ 1.10 |
| ``SP favori`` / ``SP hasard`` / ``SP top <model>`` | Simple placé, same logic, using the Harville place probability |
| ``Tiercé …`` / ``Quinté …`` | one ticket in the model's most likely order, Quinté+ races only |
"""

from __future__ import annotations

import hashlib
import itertools
import unicodedata
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from predlab.eval.uncertainty import suggested_block_size
from predlab.racing.backtest import BacktestResult
from predlab.racing.domain import Dividend
from predlab.racing.events import RaceEvent
from predlab.racing.orders import most_likely_order, places_paid, top_k_probabilities
from predlab.racing.report import discipline_label

VALUE_THRESHOLD = 1.10
SIMPLE_WIN, SIMPLE_PLACE, TIERCE, QUINTE = "SIMPLE_GAGNANT", "SIMPLE_PLACE", "TIERCE", "QUINTE_PLUS"
STAKE = {SIMPLE_WIN: 1.0, SIMPLE_PLACE: 1.0, TIERCE: 1.0, QUINTE: 2.0}


@dataclass(frozen=True, slots=True)
class Ticket:
    bet_type: str
    numbers: tuple[int, ...]
    stake: float


def _norm(label: str) -> str:
    text = unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode().lower()
    return text


def settle(ticket: Ticket, dividends: Sequence[Dividend]) -> float:
    """What the ticket returned, stake included. 0 for a losing ticket."""
    lines = [d for d in dividends if d.bet_type == ticket.bet_type]
    if any(d.refunded for d in lines):
        return ticket.stake
    best = 0.0
    mine = ticket.numbers
    for d in lines:
        combo = d.numbers
        if combo is None:
            continue  # non-runner lines ("13-8-NP")
        label = _norm(d.label)
        if ticket.bet_type in (SIMPLE_WIN, SIMPLE_PLACE):
            hit = combo == mine
        elif "desordre" in label:
            hit = set(combo) == set(mine)
        elif "ordre" in label:
            hit = combo == mine
        elif "bonus" in label:
            hit = set(combo) <= set(mine)
        else:
            hit = False
        if hit:
            best = max(best, ticket.stake * d.per_euro)
    return best


# ------------------------------------------------------------------------ strategies

Strategy = Callable[[RaceEvent, dict[str, np.ndarray], set[str]], list[Ticket]]


def _rng(race_id: str, salt: str) -> np.random.Generator:
    digest = hashlib.sha256(f"{salt}:{race_id}".encode()).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "big"))


def _odds(event: RaceEvent) -> np.ndarray:
    return np.array([s.odds if s.odds else np.inf for s in event.card.starters])


def _numbers(event: RaceEvent, idx: Sequence[int]) -> tuple[int, ...]:
    return tuple(event.card.starters[i].number for i in idx)


def _favourites(event: RaceEvent, k: int) -> list[int]:
    return [int(i) for i in np.argsort(_odds(event), kind="stable")[:k]]


def _random(event: RaceEvent, k: int, salt: str) -> list[int]:
    return [int(i) for i in _rng(event.card.race_id, salt).permutation(event.card.n)[:k]]


def simple_strategies(models: Sequence[str]) -> dict[str, Strategy]:
    out: dict[str, Strategy] = {}

    def single(bet: str, pick: Callable[[RaceEvent, dict[str, np.ndarray]], int]) -> Strategy:
        def strategy(e: RaceEvent, f: dict[str, np.ndarray], offered: set[str]) -> list[Ticket]:
            if bet not in offered:
                return []
            return [Ticket(bet, _numbers(e, [pick(e, f)]), STAKE[bet])]

        return strategy

    out["SG favori"] = single(SIMPLE_WIN, lambda e, f: _favourites(e, 1)[0])
    out["SG hasard"] = single(SIMPLE_WIN, lambda e, f: _random(e, 1, "sg")[0])
    out["SP favori"] = single(SIMPLE_PLACE, lambda e, f: _favourites(e, 1)[0])
    out["SP hasard"] = single(SIMPLE_PLACE, lambda e, f: _random(e, 1, "sp")[0])
    for m in models:
        out[f"SG top {m}"] = single(SIMPLE_WIN, lambda e, f, m=m: int(np.argmax(f[m])))
        out[f"SP top {m}"] = single(
            SIMPLE_PLACE,
            lambda e, f, m=m: int(np.argmax(top_k_probabilities(f[m], places_paid(e.card.n)))),
        )

        def value(
            e: RaceEvent, f: dict[str, np.ndarray], offered: set[str], m: str = m
        ) -> list[Ticket]:
            if SIMPLE_WIN not in offered:
                return []
            edge = f[m] * _odds(e)
            return [
                Ticket(SIMPLE_WIN, _numbers(e, [int(i)]), STAKE[SIMPLE_WIN])
                for i in np.flatnonzero(edge >= VALUE_THRESHOLD)
            ]

        out[f"SG valeur {m}"] = value
    return out


def exotic_strategies(models: Sequence[str]) -> dict[str, Strategy]:
    out: dict[str, Strategy] = {}
    for bet, k, name in ((TIERCE, 3, "Tiercé"), (QUINTE, 5, "Quinté")):

        def make(
            pick: Callable[[RaceEvent, dict[str, np.ndarray]], list[int]], bet: str = bet
        ) -> Strategy:
            def strategy(e: RaceEvent, f: dict[str, np.ndarray], offered: set[str]) -> list[Ticket]:
                # Exotic tickets only on Quinté+ races: the race the public plays.
                if bet not in offered or QUINTE not in offered:
                    return []
                return [Ticket(bet, _numbers(e, pick(e, f)), STAKE[bet])]

            return strategy

        out[f"{name} favoris"] = make(lambda e, f, k=k: _favourites(e, k))
        out[f"{name} hasard"] = make(lambda e, f, k=k, name=name: _random(e, k, name))
        for m in models:
            out[f"{name} {m}"] = make(lambda e, f, k=k, m=m: most_likely_order(f[m], k))
    return out


# ------------------------------------------------------------------------ simulation


@dataclass
class StrategyLedger:
    name: str
    race_ids: list[str] = field(default_factory=list)
    phases: list[str] = field(default_factory=list)
    stake: list[float] = field(default_factory=list)
    returned: list[float] = field(default_factory=list)
    tickets: list[int] = field(default_factory=list)

    def select(self, phase: str | None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        mask = np.array([phase is None or p == phase for p in self.phases], dtype=bool)
        return (
            np.array(self.stake)[mask],
            np.array(self.returned)[mask],
            np.array(self.tickets)[mask],
        )


def simulate(
    result: BacktestResult,
    dividends: dict[str, list[Dividend]],
    strategies: dict[str, Strategy],
) -> dict[str, StrategyLedger]:
    ledgers = {name: StrategyLedger(name) for name in strategies}
    split = result.split
    for event in result.scored_events:
        race_divs = dividends.get(event.card.race_id)
        if not race_divs:
            continue  # no official payout stored: the race cannot be settled
        if not event.card.market_coherent:
            continue  # quotes from a pool not yet formed: no decision is imagined
        offered = {d.bet_type for d in race_divs}
        forecasts = result.forecasts[event.card.race_id]
        phase = split.phase_of(event.card.day) if split else "all"
        for name, strategy in strategies.items():
            tickets = strategy(event, forecasts, offered)
            if not tickets:
                continue
            led = ledgers[name]
            led.race_ids.append(event.card.race_id)
            led.phases.append(phase)
            led.stake.append(sum(t.stake for t in tickets))
            led.returned.append(sum(settle(t, race_divs) for t in tickets))
            led.tickets.append(len(tickets))
    return ledgers


def _roi_interval(
    stake: np.ndarray, returned: np.ndarray, n_resamples: int = 2000, seed: int = 0
) -> tuple[float, float]:
    """Moving-block bootstrap of ROI = Σ returned / Σ stake − 1, blocks of consecutive races."""
    n = len(stake)
    if n < 10:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    b = suggested_block_size(n)
    n_blocks = int(np.ceil(n / b))
    values = np.empty(n_resamples)
    offsets = np.arange(b)
    for r in range(n_resamples):
        starts = rng.integers(0, max(1, n - b + 1), size=n_blocks)
        idx = np.minimum((starts[:, None] + offsets[None, :]).ravel()[:n], n - 1)
        values[r] = returned[idx].sum() / stake[idx].sum() - 1.0
    low, high = np.quantile(values, [0.025, 0.975])
    return float(low), float(high)


def summarise(ledgers: dict[str, StrategyLedger], phase: str | None) -> list[dict[str, Any]]:
    rows = []
    for name, led in ledgers.items():
        stake, returned, tickets = led.select(phase)
        if stake.size == 0:
            rows.append({"strategy": name, "races": 0})
            continue
        total_stake, total_return = float(stake.sum()), float(returned.sum())
        low, high = _roi_interval(stake, returned)
        roi = total_return / total_stake - 1.0
        if np.isnan(low):
            verdict = "échantillon trop petit"
        elif high < 0:
            verdict = "perte significative"
        elif low > 0:
            verdict = "gain significatif"
        else:
            verdict = "indéterminé"
        rows.append(
            {
                "strategy": name,
                "races": int(stake.size),
                "tickets": int(tickets.sum()),
                "stake": total_stake,
                "returned": total_return,
                "net": total_return - total_stake,
                "roi": roi,
                "roi_low": low,
                "roi_high": high,
                "hit_rate": float(np.mean(returned > 0)),
                "largest_share": float(returned.max() / total_return) if total_return > 0 else 0.0,
                "verdict": verdict,
            }
        )
    return rows


def place_calibration(
    result: BacktestResult, model: str, phase: str | None
) -> list[dict[str, Any]]:
    """Harville place probabilities vs observed place rate, by probability bucket."""
    probs: list[float] = []
    hits: list[float] = []
    for event in result.scored_events:
        if phase is not None and result.split and result.split.phase_of(event.card.day) != phase:
            continue
        k = places_paid(event.card.n)
        q = top_k_probabilities(result.forecasts[event.card.race_id][model], k)
        for s, pq in zip(event.card.starters, q, strict=True):
            pos = event.outcome.positions.get(s.number)
            probs.append(float(pq))
            hits.append(float(pos is not None and pos <= k))
    p, y = np.array(probs), np.array(hits)
    rows = []
    edges = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0)
    for lo, hi in itertools.pairwise(edges):
        mask = (p >= lo) & ((p < hi) if hi < 1.0 else (p <= hi))
        if mask.any():
            rows.append(
                {
                    "bucket": f"{lo:.1f}-{hi:.1f}",
                    "n": int(mask.sum()),
                    "mean_forecast": float(p[mask].mean()),
                    "observed": float(y[mask].mean()),
                }
            )
    return rows


# ---------------------------------------------------------------------------- loading


def load_dividends(db_path: Any) -> dict[str, list[Dividend]]:
    import duckdb

    con = duckdb.connect(str(db_path), read_only=True)
    try:
        rows = con.execute(
            "SELECT race_id, bet_type, label, combination, per_euro, base_stake, refunded "
            "FROM dividends"
        ).fetchall()
    finally:
        con.close()
    out: dict[str, list[Dividend]] = {}
    for race_id, bet, label, combo, per_euro, base, refunded in rows:
        out.setdefault(race_id, []).append(
            Dividend(
                race_id=race_id,
                bet_type=bet,
                label=label,
                combination=tuple(t for t in combo.split("-") if t),
                per_euro=per_euro,
                base_stake=base,
                refunded=bool(refunded),
            )
        )
    return out


# ----------------------------------------------------------------------------- report


def _f(x: Any, digits: int = 3, pct: bool = False) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return f"{x * 100:+.1f} %" if pct else f"{x:.{digits}f}"


def build_simulation_report(
    result: BacktestResult,
    ledgers: dict[str, StrategyLedger],
    *,
    n_races_with_dividends: int,
    generated_at: str,
    discipline: str = "PLAT",
) -> dict[str, Any]:
    phases = sorted({p for led in ledgers.values() for p in led.phases})
    decision = "test" if "test" in phases else "all"
    return {
        "generated_at": generated_at,
        "discipline": discipline,
        "code_version": result.code_version,
        "horizon_minutes": result.horizon_minutes,
        "dataset_fingerprint": result.dataset_fingerprint,
        "n_eligible": result.n_eligible,
        "n_races_with_dividends": n_races_with_dividends,
        "value_threshold": VALUE_THRESHOLD,
        "decision_phase": decision,
        "by_phase": {ph: summarise(ledgers, ph) for ph in phases},
        "place_calibration": place_calibration(result, "market_calibrated", decision)
        if _has_model(result, "market_calibrated")
        else [],
    }


def _has_model(result: BacktestResult, name: str) -> bool:
    return any(name in f for f in result.forecasts.values())


def render_simulation_markdown(report: dict[str, Any]) -> str:
    phase = report["decision_phase"]
    lines = [
        f"# Simulation de paris fictifs — {discipline_label(report.get('discipline'))}, hippodromes français",
        "",
        "**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les "
        "rapports officiels du PMU.",
        "",
        f"Généré le {report['generated_at']} · horizon **T-{report['horizon_minutes']:g} min** · "
        f"code {report['code_version']} · empreinte `{report['dataset_fingerprint'][:12]}` · "
        f"courses évaluées : {report['n_eligible']}, dont {report['n_races_with_dividends']} avec "
        f"rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ {report['value_threshold']:.2f}.",
        "",
        "Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). "
        "L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. "
        "« Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.",
        "",
    ]
    order = [phase] + [p for p in report["by_phase"] if p != phase]
    for ph in order:
        rows = report["by_phase"][ph]
        lines += [
            f"## Phase {ph}" + (" (décision)" if ph == phase else ""),
            "",
            "| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |",
            "|---|---:|---:|---:|---:|---|---:|---:|---|",
        ]
        for r in sorted(rows, key=lambda r: -(r.get("roi") if r.get("races") else -9)):
            if not r.get("races"):
                lines.append(f"| {r['strategy']} | 0 | — | — | — | — | — | — | aucun pari |")
                continue
            lines.append(
                f"| {r['strategy']} | {r['races']} | {r['stake']:.0f} | {r['returned']:.0f} | "
                f"{_f(r['roi'], pct=True)} | [{_f(r['roi_low'], pct=True)} ; {_f(r['roi_high'], pct=True)}] | "
                f"{r['hit_rate'] * 100:.1f} % | {r['largest_share'] * 100:.0f} % | {r['verdict']} |"
            )
        lines.append("")
    if report["place_calibration"]:
        lines += [
            "## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place",
            "",
            f"Marché calibré, phase {phase}. Si « prévu » dépasse « observé » sur les fortes "
            "probabilités, Harville surestime les favoris pour les places (biais connu).",
            "",
            "| Tranche | Partants | Prévu | Observé |",
            "|---|---:|---:|---:|",
        ]
        lines += [
            f"| {r['bucket']} | {r['n']} | {r['mean_forecast']:.3f} | {r['observed']:.3f} |"
            for r in report["place_calibration"]
        ]
        lines.append("")
    lines += [
        "## Limites",
        "",
        "- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux "
        "fait partie de ce qui est mesuré.",
        "- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.",
        "- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de "
        "tickets avant qu'un ROI veuille dire quelque chose.",
        "- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » "
        "sur la phase de test, confirmé en conditions réelles, compterait.",
        "",
    ]
    return "\n".join(lines)
