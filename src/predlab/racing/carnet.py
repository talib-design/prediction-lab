"""The live paper-betting ledger ("carnet"): tickets frozen *before* the off.

A backtest says what *would have* happened. This ledger says what *did* happen to
decisions written down in advance, which nobody -- not the model author, not a bug in
a later version -- can revise. That is the only evidence that counts in the end
(docs/METHODOLOGY.md §5, level 4).

How it works, run after every collection pass (every 5 min):

1. **Freeze.** For each target race whose horizon (T-25 min) has passed but whose
   scheduled off has not, the tickets of each strategy are computed from the odds
   quoted by the horizon -- the backtest's own rule -- and appended to a hash-chained
   ledger with the moment they were written. A race missed (the Mac asleep between
   T-25 and the off) is simply not in the ledger: it is never back-filled.
2. **Settle.** Once the official dividends are captured, each frozen ticket is
   settled with :func:`predlab.racing.betting.settle` and the result appended.

Rules (fixed 2026-09-28, before the first ticket): same stakes as the simulation
(1 EUR per ticket), no staking plan, no account, nothing is ever wagered. Since
2026-10-03 the carnet plays only the favourite and the Marché+ model (``STRATEGIES``).
The ledger holds our decisions and probabilities, not PMU odds: the odds used are
referenced by the hash of the raw captures they came from. It is safe to commit, and
committing it is what gives the "written before the race" claim an outside anchor.
"""

from __future__ import annotations

import fcntl
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

import numpy as np

from predlab.core.clock import paris_day
from predlab.core.hashing import AppendOnlyLedger
from predlab.core.probability import implied_probabilities
from predlab.racing.backtest import DEFAULT_HORIZON_MINUTES
from predlab.racing.betting import (
    SIMPLE_PLACE,
    SIMPLE_WIN,
    Ticket,
    settle,
    simple_strategies,
)
from predlab.racing.domain import Race, Runner
from predlab.racing.events import RaceCard, RaceEvent, RaceOutcome, Starter
from predlab.racing.sources.pmu.client import Endpoint, capture_key
from predlab.racing.sources.pmu.parser import (
    PmuFormatError,
    parse_dividends,
    parse_participants,
    parse_programme_detailed,
)
from predlab.racing.store.raw import Capture, RawStore

CARNET_VERSION = "1"
TARGETS = ("PLAT", "ATTELE", "MONTE")
MODEL = "market_calibrated"
PLUS = "marche_plus"  # racing/marketplus.py, added 2026-09-30

# What the carnet plays, since 2026-10-03 (decision of Chris): the favourite and the
# Marché+ model, to compare the two, in simple gagnant and simple placé. The other
# witnesses played from 2026-09-28 (random picks, "value", tiercé, quinté) are retired:
# their tickets stay in the hash-chained ledger, untouched, but no longer enter any
# balance, chart or summary -- ``entries`` filters them out.
STRATEGIES = (
    "SG favori",
    "SP favori",
    f"SG top {PLUS}",
    f"SP top {PLUS}",
)
RETIRED = (
    "SG hasard",
    "SG valeur market_calibrated",
    "SP hasard",
    "Tiercé favoris",
    "Tiercé hasard",
    "Quinté favoris",
    "Quinté hasard",
    f"SG valeur {PLUS}",
)

# Beside the champion (racing/champion.py, decision of Chris 2026-10-05): after a
# promotion, the version it replaced keeps playing ("ancien modèle"), and a playing rule
# admitted by the lab gets its own line. Played only when they exist; they enter the
# chart and the summary, never the "bilan" totals (favourite + model, as before).
PREV = "marche_plus_prev"
VALUE_RULE = "value105"
OPTIONAL = (f"SG top {PREV}", f"SP top {PREV}", f"SG {VALUE_RULE} {PLUS}")
PLAYED = (*STRATEGIES, *OPTIONAL)

STRATEGY_LABELS = {
    f"SG top {PREV}": "SG ancien modèle",
    f"SP top {PREV}": "SP ancien modèle",
    f"SG {VALUE_RULE} {PLUS}": "SG valeur modèle (p × cote ≥ 1,05)",
    "SG valeur market_calibrated": "SG valeur (marché calibré)",
    f"SG top {PLUS}": "SG modèle",
    f"SP top {PLUS}": "SP modèle",
    f"SG valeur {PLUS}": "SG valeur (modèle)",
}

# Given the race, its card at the horizon and the starters' details: the model's win
# probabilities in card order, and the id of the report its parameters come from.
# An optional third element (dict) says what plays beside the champion: "previous" (the
# replaced version's probabilities), "previous_version", "version", "rules".
ModelFor = Callable[[Race, RaceCard, list[Runner]], tuple[Any, ...] | None]


def strategy_label(name: str) -> str:
    return STRATEGY_LABELS.get(name, name)


def _value_rule(e: Any, f: dict[str, np.ndarray], offered: set[str]) -> list[Any]:
    """Simple gagnant on every starter the champion finds mispriced: p × odds ≥ 1.05."""
    from predlab.racing.betting import SIMPLE_WIN, STAKE, Ticket
    from predlab.racing.champion import VALUE_EDGE

    if SIMPLE_WIN not in offered:
        return []
    odds = np.array([s.odds or 0.0 for s in e.card.starters], dtype=float)
    return [
        Ticket(SIMPLE_WIN, (e.card.starters[int(i)].number,), STAKE[SIMPLE_WIN])
        for i in np.flatnonzero(f[PLUS] * odds >= VALUE_EDGE)
    ]


def _strategies(
    with_model: bool = False, with_previous: bool = False, rules: tuple[str, ...] = ()
) -> dict[str, Any]:
    every = simple_strategies([MODEL, PLUS, PREV])
    out = {n: every[n] for n in STRATEGIES if with_model or PLUS not in n}
    if with_model and with_previous:
        out.update({n: every[n] for n in OPTIONAL if PREV in n})
    if with_model and VALUE_RULE in rules:
        out[f"SG {VALUE_RULE} {PLUS}"] = _value_rule
    return out


@dataclass
class CarnetReport:
    frozen: list[str] = field(default_factory=list)
    settled: list[str] = field(default_factory=list)
    waiting_market: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"carnet : {len(self.frozen)} course(s) figée(s), {len(self.settled)} réglée(s)"
            + (f", {len(self.waiting_market)} sans marché complet" if self.waiting_market else "")
            + (f", {len(self.errors)} erreur(s)" if self.errors else "")
        )


def _latest_ok(captures: list[Capture]) -> Capture | None:
    ok = [c for c in captures if c.ok]
    return max(ok, key=lambda c: c.retrieved_at) if ok else None


def _programme(store: RawStore, index: dict[str, list[Capture]], day: date) -> list[Race]:
    cap = _latest_ok(index.get(capture_key(Endpoint.PROGRAMME, day), []))
    if cap is None:
        return []
    try:
        return parse_programme_detailed(store.read(cap)).races
    except PmuFormatError:
        return []


def _is_target(race: Race) -> bool:
    return (
        race.country_code == "FRA"
        and race.discipline in TARGETS
        and "ANNULEE" not in (race.status or "")
    )


def _card_at_horizon(
    store: RawStore, captures: list[Capture], race: Race, now: datetime, horizon: timedelta
) -> tuple[RaceCard, list[str], list[Runner]] | None:
    """Starters as last seen by ``now``; odds as quoted by the horizon (backtest rule)."""
    usable = sorted(
        (c for c in captures if c.ok and c.retrieved_at <= now), key=lambda c: c.retrieved_at
    )
    if not usable:
        return None
    cutoff = race.off_time - horizon
    runners: list[Runner] = []
    best: dict[int, tuple[datetime, float]] = {}
    used: set[str] = set()
    for cap in usable:
        try:
            parsed = parse_participants(store.read(cap), race.race_id)
        except PmuFormatError:
            continue
        runners = parsed
        for x in parsed:
            for q in (x.odds_reference, x.odds_direct):
                if q is None or q.reported_at > cutoff:
                    continue
                if x.number not in best or q.reported_at > best[x.number][0]:
                    best[x.number] = (q.reported_at, q.odds)
                    if cap.sha256:
                        used.add(cap.sha256)
    starters = tuple(
        Starter(
            number=x.number,
            horse_id=x.identity_key,
            jockey=x.jockey,
            trainer=x.trainer,
            draw=x.draw,
            weight_raw=x.weight_raw,
            age=x.age,
            odds=best[x.number][1] if x.number in best else None,
            odds_reported_at=best[x.number][0] if x.number in best else None,
        )
        for x in runners
        if x.is_runner
    )
    card = RaceCard(
        race_id=race.race_id,
        day=race.day,
        off_time=race.off_time,
        prediction_time=cutoff,
        venue_code=race.venue_code,
        distance_m=race.distance_m,
        going_value=race.going.value if race.going else None,
        category=race.category,
        starters=starters,
    )
    return card, sorted(used), [x for x in runners if x.is_runner]


def _ticket_dict(strategy: str, t: Ticket) -> dict[str, Any]:
    return {
        "strategy": strategy,
        "bet_type": t.bet_type,
        "numbers": list(t.numbers),
        "stake": t.stake,
    }


def freeze_race(
    race: Race,
    card: RaceCard,
    alpha: float | None,
    now: datetime,
    capture_hashes: list[str],
    model: tuple[Any, ...] | None = None,
    model_error: str | None = None,
) -> dict[str, Any]:
    odds = np.array([s.odds for s in card.starters], dtype=float)
    q = implied_probabilities(odds)
    a = alpha if alpha is not None else 1.0
    p = np.power(q, a)
    p = p / p.sum()
    forecasts = {"market": q, MODEL: p}
    parts: list[Any] = list(model) if model is not None else []
    extras: dict[str, Any] = parts[2] if len(parts) > 2 else {}
    if parts:
        forecasts[PLUS] = parts[0]
    if extras.get("previous") is not None:
        forecasts[PREV] = np.asarray(extras["previous"], dtype=float)
    event = RaceEvent(card=card, outcome=RaceOutcome(card.race_id, {}), known_at=race.off_time)
    offered = set(race.bet_types)
    tickets = [
        _ticket_dict(name, t)
        for name, strategy in _strategies(
            with_model=model is not None,
            with_previous=PREV in forecasts,
            rules=tuple(extras.get("rules", ())),
        ).items()
        for t in strategy(event, forecasts, offered)
    ]
    extra: dict[str, Any] = {}
    if model is not None:
        extra["model"] = {
            "name": PLUS,
            "report": parts[1],
            "probabilities": {
                str(s.number): round(float(x), 6)
                for s, x in zip(card.starters, parts[0], strict=True)
            },
        }
        if "version" in extras:
            extra["model"]["version"] = extras["version"]
        if extras.get("rules"):
            extra["model"]["rules"] = list(extras["rules"])
        if PREV in forecasts:
            extra["model"]["previous"] = {
                "version": extras.get("previous_version"),
                "probabilities": {
                    str(s.number): round(float(x), 6)
                    for s, x in zip(card.starters, forecasts[PREV], strict=True)
                },
            }
    elif model_error:
        extra["model_error"] = model_error
    return {
        "kind": "freeze",
        "carnet_version": CARNET_VERSION,
        "race_id": race.race_id,
        "day": race.day.isoformat(),
        "discipline": race.discipline,
        "venue": race.venue_name,
        "has_quinte": race.has_quinte,
        "off_time": race.off_time.isoformat(),
        "frozen_at": now.isoformat(),
        "horizon_minutes": DEFAULT_HORIZON_MINUTES,
        "odds_as_of": max(
            s.odds_reported_at for s in card.starters if s.odds_reported_at
        ).isoformat(),  # type: ignore[type-var]
        "alpha": a,
        "alpha_source": "backtest" if alpha is not None else "défaut (aucun backtest)",
        "probabilities": {
            str(s.number): round(float(x), 6) for s, x in zip(card.starters, p, strict=True)
        },
        "source_captures": capture_hashes,
        "tickets": tickets,
        **extra,
    }


def run_carnet(
    store: RawStore,
    ledger: AppendOnlyLedger,
    *,
    now: datetime,
    alpha_for: Callable[[str], float | None],
    horizon_minutes: float = DEFAULT_HORIZON_MINUTES,
    model_for: ModelFor | None = None,
) -> CarnetReport:
    """One pass, holding an exclusive lock: the collector and a manual run never interleave."""
    ledger.path.parent.mkdir(parents=True, exist_ok=True)
    with ledger.path.open("a") as fh:  # lock the ledger file itself: no stray lock file
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        try:
            return _run_carnet(store, ledger, now, alpha_for, horizon_minutes, model_for)
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def _run_carnet(
    store: RawStore,
    ledger: AppendOnlyLedger,
    now: datetime,
    alpha_for: Callable[[str], float | None],
    horizon_minutes: float,
    model_for: ModelFor | None = None,
) -> CarnetReport:
    report = CarnetReport()
    records = ledger.records()
    frozen = {r["race_id"]: r for r in records if r.get("kind") == "freeze"}
    settled = {r["race_id"] for r in records if r.get("kind") == "settle"}
    index = store.index()
    horizon = timedelta(minutes=horizon_minutes)

    # 1. Freeze: today's races inside their window [off - horizon, off).
    today = paris_day(now)
    for race in _programme(store, index, today):
        if not _is_target(race) or race.race_id in frozen:
            continue
        if not (race.off_time - horizon <= now < race.off_time):
            continue
        key = capture_key(Endpoint.PARTICIPANTS, race.day, race.meeting_number, race.race_number)
        built = _card_at_horizon(store, index.get(key, []), race, now, horizon)
        if built is None or not built[0].starters or not built[0].market_coherent:
            # Incomplete or incoherent quotes: retried at the next pass until the off.
            report.waiting_market.append(race.race_id)
            continue
        model, model_error = None, None
        if model_for is not None:
            try:
                model = model_for(race, built[0], built[2])
            except Exception as exc:  # the model never blocks the other tickets
                model_error = f"{type(exc).__name__}: {exc}"
        try:
            rec = ledger.append(
                freeze_race(
                    race, built[0], alpha_for(race.discipline), now, built[1], model, model_error
                )
            )
        except (ValueError, PmuFormatError) as exc:
            report.errors.append(f"{race.race_id}: {exc}")
            continue
        frozen[race.race_id] = rec
        report.frozen.append(race.race_id)

    # 2. Settle: any frozen race whose official dividends are now stored.
    programmes: dict[date, dict[str, Race]] = {}
    for race_id, rec in frozen.items():
        if race_id in settled:
            continue
        day = date.fromisoformat(rec["day"])
        if day not in programmes:
            programmes[day] = {r.race_id: r for r in _programme(store, index, day)}
        race = programmes[day].get(race_id)
        if race is None:
            continue
        settlement = _settle(store, index, race, rec, now)
        if settlement is not None:
            ledger.append(settlement)
            report.settled.append(race_id)
    return report


def _settle(
    store: RawStore,
    index: dict[str, list[Capture]],
    race: Race,
    frozen: dict[str, Any],
    now: datetime,
) -> dict[str, Any] | None:
    base = {
        "kind": "settle",
        "carnet_version": CARNET_VERSION,
        "race_id": race.race_id,
        "settled_at": now.isoformat(),
    }
    if "ANNULEE" in (race.status or ""):
        return {
            **base,
            "note": "course annulée : mises remboursées",
            "finish_order": None,
            "returns": [t["stake"] for t in frozen["tickets"]],
        }
    cap = _latest_ok(
        index.get(
            capture_key(Endpoint.RAPPORTS, race.day, race.meeting_number, race.race_number), []
        )
    )
    if cap is None or not race.is_final:
        return None
    try:
        dividends = parse_dividends(store.read(cap), race.race_id)
    except PmuFormatError:
        return None
    if not dividends:
        return None
    non_runners = _non_runners(store, index, race)
    returns: list[float] = []
    notes: list[str] = []
    for t in frozen["tickets"]:
        ticket = Ticket(t["bet_type"], tuple(t["numbers"]), float(t["stake"]))
        scratched = set(ticket.numbers) & non_runners
        if scratched and ticket.bet_type in (SIMPLE_WIN, SIMPLE_PLACE):
            returns.append(ticket.stake)  # a simple bet on a non-runner is refunded
            notes.append(f"{t['strategy']} : non-partant {sorted(scratched)}, remboursé")
            continue
        if scratched:
            notes.append(
                f"{t['strategy']} : non-partant {sorted(scratched)}, réglé tel quel (approximation)"
            )
        returns.append(settle(ticket, dividends))
    return {
        **base,
        "finish_order": race.finish_order,
        "dividends_capture": cap.sha256,
        "returns": returns,
        "note": "; ".join(notes) or None,
    }


def _non_runners(store: RawStore, index: dict[str, list[Capture]], race: Race) -> set[int]:
    key = capture_key(Endpoint.PARTICIPANTS, race.day, race.meeting_number, race.race_number)
    cap = _latest_ok(index.get(key, []))
    if cap is None:
        return set()
    try:
        return {
            x.number for x in parse_participants(store.read(cap), race.race_id) if not x.is_runner
        }
    except PmuFormatError:
        return set()


# --------------------------------------------------------------------------- reading


def entries(ledger: AppendOnlyLedger) -> list[dict[str, Any]]:
    """One entry per frozen race, with its settlement merged in when there is one."""
    records = ledger.records()
    settles = {r["race_id"]: r for r in records if r.get("kind") == "settle"}
    out = []
    for r in records:
        if r.get("kind") != "freeze":
            continue
        s = settles.get(r["race_id"])
        tickets = [
            {
                **t,
                "label": strategy_label(t["strategy"]),
                "returned": s["returns"][i] if s else None,
            }
            for i, t in enumerate(r["tickets"])
            if t["strategy"] in PLAYED  # retired witnesses stay in the ledger only
        ]
        out.append(
            {
                "race_id": r["race_id"],
                "day": r["day"],
                "rc": r["race_id"].split("/")[1],
                "discipline": r["discipline"],
                "venue": r.get("venue"),
                "has_quinte": r.get("has_quinte", False),
                "off_time": r["off_time"],
                "frozen_at": r["frozen_at"],
                "odds_as_of": r["odds_as_of"],
                "alpha": r["alpha"],
                "model_probabilities": (r.get("model") or {}).get("probabilities"),
                "tickets": tickets,
                "settled": s is not None,
                "settled_at": s["settled_at"] if s else None,
                "finish_order": s.get("finish_order") if s else None,
                "note": s.get("note") if s else None,
            }
        )
    return out


def summarise_entries(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per strategy, settled races only: same measures as the simulation."""
    from predlab.racing.betting import StrategyLedger
    from predlab.racing.betting import summarise as summarise_ledgers

    played = {t["strategy"] for e in items for t in e["tickets"]}
    names = [*STRATEGIES, *(n for n in OPTIONAL if n in played)]
    ledgers = {name: StrategyLedger(name) for name in names}
    pending: dict[str, int] = dict.fromkeys(names, 0)
    for e in sorted(items, key=lambda e: e["off_time"]):
        by: dict[str, list[dict[str, Any]]] = {}
        for t in e["tickets"]:
            by.setdefault(t["strategy"], []).append(t)
        for name, ts in by.items():
            if name not in ledgers:
                continue
            if not e["settled"]:
                pending[name] += 1
                continue
            led = ledgers[name]
            led.race_ids.append(e["race_id"])
            led.phases.append("live")
            led.stake.append(sum(t["stake"] for t in ts))
            led.returned.append(sum(t["returned"] for t in ts))
            led.tickets.append(len(ts))
    rows = summarise_ledgers(ledgers, None)
    for r in rows:
        r["pending"] = pending[r["strategy"]]
        r["label"] = strategy_label(r["strategy"])
    return rows
