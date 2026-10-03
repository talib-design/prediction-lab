from __future__ import annotations

import copy
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from predlab.core.hashing import AppendOnlyLedger
from predlab.racing.carnet import entries, run_carnet, summarise_entries
from predlab.racing.sources.pmu.client import FetchResult
from predlab.racing.store.raw import RawStore

from .conftest import fixture_bytes

OFF = datetime.fromtimestamp(1790585400, tz=UTC)  # R2C1 of 2026-09-28, 10:50 Paris
MS = lambda t: int(t.timestamp() * 1000)  # noqa: E731


def _programme(final: bool = False) -> bytes:
    doc = json.loads(fixture_bytes("programme_2026-09-28_excerpt.json"))
    course = doc["programme"]["reunions"][1]["courses"][0]
    course["paris"] = [{"typePari": t} for t in ("SIMPLE_GAGNANT", "SIMPLE_PLACE", "TRIO")]
    if final:
        course["statut"] = "ARRIVEE_DEFINITIVE_COMPLETE"
        course["arriveeDefinitive"] = True
        course["ordreArrivee"] = [[4], [2], [1], [3]]
    return json.dumps(doc).encode()


def _participants(late_odds_on_1: bool = False) -> bytes:
    doc = json.loads(fixture_bytes("participants_2026-09-28_R2C1_excerpt.json"))
    base = doc["participants"][0]
    runners: list[dict[str, Any]] = []
    for number, odds in ((1, 5.0), (2, 3.2), (3, 8.0), (4, 1.9)):  # overround 1.16
        r = copy.deepcopy(base)
        r["numPmu"] = number
        r["nom"] = f"CHEVAL {number}"
        r["idCheval"] = f"CHEVAL {number}-M-P"
        r["dernierRapportReference"].update(
            rapport=odds, dateRapport=MS(OFF - timedelta(minutes=30))
        )
        # A later quote, after the horizon: must never be used to decide.
        late = 1.2 if (number == 1 and late_odds_on_1) else odds
        r["dernierRapportDirect"].update(rapport=late, dateRapport=MS(OFF - timedelta(minutes=10)))
        runners.append(r)
    return json.dumps({"participants": runners}).encode()


def _record(store: RawStore, body: bytes, key: str, endpoint: str, at: datetime) -> None:
    store.record(FetchResult("u", 200, body, at), key=key, endpoint=endpoint, purpose="t")


def _run(store: RawStore, ledger: AppendOnlyLedger, now: datetime):
    return run_carnet(store, ledger, now=now, alpha_for=lambda d: 1.2)


def test_tickets_are_frozen_inside_the_window_from_horizon_odds_only(tmp_path: Path) -> None:
    store, ledger = RawStore(tmp_path / "raw"), AppendOnlyLedger(tmp_path / "carnet.jsonl")
    _record(store, _programme(), "programme/2026-09-28", "programme", OFF - timedelta(hours=3))
    _record(
        store,
        _participants(late_odds_on_1=True),
        "participants/2026-09-28/R2C1",
        "participants",
        OFF - timedelta(minutes=8),
    )

    assert _run(store, ledger, OFF - timedelta(minutes=40)).frozen == [], "before the horizon"
    rep = _run(store, ledger, OFF - timedelta(minutes=5))
    assert rep.frozen == ["2026-09-28/R2C1"]
    (entry,) = entries(ledger)
    fav = next(t for t in entry["tickets"] if t["strategy"] == "SG favori")
    assert fav["numbers"] == [4], "the 1.2 quote on no. 1 came after T-25 and is ignored"
    assert {t["strategy"] for t in entry["tickets"]} == {"SG favori", "SP favori"}, (
        "no model parameters here: only the favourite is played"
    )
    assert datetime.fromisoformat(entry["odds_as_of"]) <= OFF - timedelta(minutes=25)

    assert _run(store, ledger, OFF - timedelta(minutes=1)).frozen == [], "frozen once only"


def test_a_race_missed_before_the_off_is_never_backfilled(tmp_path: Path) -> None:
    store, ledger = RawStore(tmp_path / "raw"), AppendOnlyLedger(tmp_path / "carnet.jsonl")
    _record(store, _programme(), "programme/2026-09-28", "programme", OFF - timedelta(hours=3))
    _record(
        store,
        _participants(),
        "participants/2026-09-28/R2C1",
        "participants",
        OFF - timedelta(minutes=8),
    )
    assert _run(store, ledger, OFF + timedelta(minutes=1)).frozen == []
    assert entries(ledger) == []


def test_settlement_uses_the_official_dividends_and_keeps_the_chain(tmp_path: Path) -> None:
    store, ledger = RawStore(tmp_path / "raw"), AppendOnlyLedger(tmp_path / "carnet.jsonl")
    _record(store, _programme(), "programme/2026-09-28", "programme", OFF - timedelta(hours=3))
    _record(
        store,
        _participants(),
        "participants/2026-09-28/R2C1",
        "participants",
        OFF - timedelta(minutes=8),
    )
    _run(store, ledger, OFF - timedelta(minutes=5))
    assert _run(store, ledger, OFF + timedelta(minutes=30)).settled == [], "no dividends yet"

    later = OFF + timedelta(hours=1)
    _record(store, _programme(final=True), "programme/2026-09-28", "programme", later)
    _record(
        store,
        fixture_bytes("rapports_2026-09-28_R2C1_full.json"),
        "rapports/2026-09-28/R2C1",
        "rapports",
        later,
    )
    assert _run(store, ledger, later + timedelta(minutes=5)).settled == ["2026-09-28/R2C1"]

    (entry,) = entries(ledger)
    got = {t["strategy"]: t["returned"] for t in entry["tickets"]}
    assert got["SG favori"] == 7.6 and got["SP favori"] == 1.6
    assert entry["finish_order"] == [[4], [2], [1], [3]]
    ledger.verify()
    rows = {r["strategy"]: r for r in summarise_entries(entries(ledger))}
    assert rows["SG favori"]["races"] == 1 and abs(rows["SG favori"]["roi"] - 6.6) < 1e-9
    assert _run(store, ledger, later + timedelta(minutes=10)).settled == [], "settled once only"


def test_no_ticket_on_an_incoherent_market(tmp_path: Path) -> None:
    store, ledger = RawStore(tmp_path / "raw"), AppendOnlyLedger(tmp_path / "carnet.jsonl")
    _record(store, _programme(), "programme/2026-09-28", "programme", OFF - timedelta(hours=3))
    doc = json.loads(_participants())
    for r in doc[
        "participants"
    ]:  # every quote doubled: 1/odds sums to 0.58, no pool looks like that
        r["dernierRapportReference"]["rapport"] *= 2
    _record(
        store,
        json.dumps(doc).encode(),
        "participants/2026-09-28/R2C1",
        "participants",
        OFF - timedelta(minutes=8),
    )
    rep = _run(store, ledger, OFF - timedelta(minutes=5))
    assert rep.frozen == [] and rep.waiting_market == ["2026-09-28/R2C1"]


def test_model_tickets_are_frozen_with_the_model_probabilities(tmp_path: Path) -> None:
    import numpy as np

    store, ledger = RawStore(tmp_path / "raw"), AppendOnlyLedger(tmp_path / "carnet.jsonl")
    _record(store, _programme(), "programme/2026-09-28", "programme", OFF - timedelta(hours=3))
    _record(
        store,
        _participants(),
        "participants/2026-09-28/R2C1",
        "participants",
        OFF - timedelta(minutes=8),
    )
    seen: list[list[int]] = []

    def model_for(race, card, runners):  # the outsider no. 3 is the model's pick
        seen.append([x.number for x in runners])
        assert [s.number for s in card.starters] == seen[-1], "same order as the card"
        return np.array([0.2, 0.2, 0.5, 0.1]), "model_PLAT_x"

    run_carnet(
        store,
        ledger,
        now=OFF - timedelta(minutes=5),
        alpha_for=lambda d: 1.0,
        model_for=model_for,
    )
    (entry,) = entries(ledger)
    got = {t["strategy"]: t["numbers"] for t in entry["tickets"]}
    assert got["SG top marche_plus"] == [3] and got["SG favori"] == [4]
    assert set(got) == {"SG favori", "SP favori", "SG top marche_plus", "SP top marche_plus"}
    assert ledger.records()[0]["model"]["probabilities"]["3"] == 0.5


def test_a_failing_model_never_blocks_the_other_tickets(tmp_path: Path) -> None:
    store, ledger = RawStore(tmp_path / "raw"), AppendOnlyLedger(tmp_path / "carnet.jsonl")
    _record(store, _programme(), "programme/2026-09-28", "programme", OFF - timedelta(hours=3))
    _record(
        store,
        _participants(),
        "participants/2026-09-28/R2C1",
        "participants",
        OFF - timedelta(minutes=8),
    )

    def broken(race, card, runners):
        raise RuntimeError("base en reconstruction")

    rep = run_carnet(
        store, ledger, now=OFF - timedelta(minutes=5), alpha_for=lambda d: 1.0, model_for=broken
    )
    assert rep.frozen == ["2026-09-28/R2C1"]
    rec = ledger.records()[0]
    assert "base en reconstruction" in rec["model_error"]
    assert not any("marche_plus" in t["strategy"] for t in rec["tickets"])


def test_retired_witnesses_stay_in_the_ledger_but_out_of_every_balance(tmp_path: Path) -> None:
    ledger = AppendOnlyLedger(tmp_path / "carnet.jsonl")
    ledger.append(
        {
            "kind": "freeze",
            "race_id": "2026-09-28/R1C1",
            "day": "2026-09-28",
            "discipline": "PLAT",
            "off_time": "2026-09-28T12:00:00+00:00",
            "frozen_at": "2026-09-28T11:40:00+00:00",
            "odds_as_of": "2026-09-28T11:35:00+00:00",
            "alpha": 1.0,
            "tickets": [
                {
                    "strategy": "SG favori",
                    "bet_type": "SIMPLE_GAGNANT",
                    "numbers": [1],
                    "stake": 1.0,
                },
                {
                    "strategy": "SG hasard",
                    "bet_type": "SIMPLE_GAGNANT",
                    "numbers": [5],
                    "stake": 1.0,
                },
            ],
        }
    )
    ledger.append(
        {"kind": "settle", "race_id": "2026-09-28/R1C1", "settled_at": "x", "returns": [0.0, 12.0]}
    )
    (entry,) = entries(ledger)
    assert [t["strategy"] for t in entry["tickets"]] == ["SG favori"]
    assert entry["tickets"][0]["returned"] == 0.0, "returns stay aligned with their ticket"
    ledger.verify()
