from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from predlab.api.app import create_app
from predlab.core.hashing import AppendOnlyLedger
from predlab.core.paths import Paths
from predlab.racing.sources.pmu.client import FetchResult
from predlab.racing.store.normalized import build
from predlab.racing.store.raw import RawStore

from .conftest import fixture_bytes

T = datetime(2026, 9, 28, 8, 0, tzinfo=UTC)


@pytest.fixture
def lab(tmp_path: Path) -> Paths:
    paths = Paths(tmp_path)
    paths.ensure()
    store = RawStore(paths.raw_pmu)
    store.record(
        FetchResult("u", 200, fixture_bytes("programme_2026-09-28_excerpt.json"), T),
        key="programme/2026-09-28",
        endpoint="programme",
        purpose="programme",
    )
    for minutes in (0, 5):
        store.record(
            FetchResult(
                "u",
                200,
                fixture_bytes("participants_2026-09-28_R2C1_excerpt.json"),
                T + timedelta(minutes=minutes),
            ),
            key="participants/2026-09-28/R2C1",
            endpoint="participants",
            purpose="snapshot",
        )
    store.record(
        FetchResult(
            "u", 200, fixture_bytes("rapports_2026-09-28_R2C1_full.json"), T + timedelta(hours=8)
        ),
        key="rapports/2026-09-28/R2C1",
        endpoint="rapports",
        purpose="result",
    )
    build(store, paths.normalized, paths.database)
    run = paths.runs / "backtest_PLAT_T25_20260928T100000Z"
    run.mkdir(parents=True)
    (run / "report.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-09-28T10:00:00+00:00",
                "discipline": "PLAT",
                "alpha": 1.2,
                "n_eligible": 3,
            }
        ),
        encoding="utf-8",
    )
    return paths


def test_day_lists_target_races_with_snapshot_counts(lab: Paths) -> None:
    client = TestClient(create_app(lab))
    body = client.get("/api/races", params={"day": "2026-09-28"}).json()
    rcs = {r["rc"]: r for r in body["races"]}
    assert set(rcs) <= {"R1C1", "R2C1"} and "R2C1" in rcs
    assert rcs["R2C1"]["snapshots"] == 2
    assert all(r["discipline"] in ("PLAT", "ATTELE", "MONTE") for r in body["races"])


def test_race_detail_has_market_and_is_read_only(lab: Paths) -> None:
    client = TestClient(create_app(lab))
    body = client.get("/api/races/2026-09-28/R2C1").json()
    assert body["race"]["rc"] == "R2C1"
    assert body["calibration_alpha"] == 1.2
    assert body["runners"], "runners from the latest capture"
    series = body["runners"][0]["odds_series"]
    assert len(series) == len({p["t"] for p in series}), "quotes deduplicated across captures"
    assert any(d["bet_type"] == "SIMPLE_GAGNANT" for d in body["dividends"])
    assert client.get("/api/races/2026-09-28/R9C9").status_code == 404
    assert client.post("/api/races").status_code == 405


def test_market_probabilities_sum_to_one_when_complete(lab: Paths) -> None:
    body = TestClient(create_app(lab)).get("/api/races/2026-09-28/R2C1").json()
    ps = [r["market_p"] for r in body["runners"] if r["market_p"] is not None]
    if ps:  # the excerpt may not quote every starter; then no market is shown at all
        assert abs(sum(ps) - 1) < 1e-9


def test_status_reports_and_horse(lab: Paths) -> None:
    client = TestClient(create_app(lab))
    status = client.get("/api/status").json()
    assert status["captures"] == 4 and status["database"]["exists"]
    assert [b["discipline"] for b in status["backfill"]] == ["PLAT", "ATTELE", "MONTE"]
    reports = client.get("/api/reports").json()["reports"]
    assert reports[0]["id"] == "backtest_PLAT_T25_20260928T100000Z"
    assert client.get("/api/reports/..%2F..%2Fsecrets").status_code == 404
    assert client.get("/api/nope").status_code == 404, "unknown API routes never fall to the UI"
    horse = client.get("/api/horses/EAST AND WEST-LIVINGINAFANTASY-TERRITORIES").json()
    assert horse["horse"]["sire"] == "TERRITORIES" and len(horse["runs"]) == 1
    assert client.get("/api/hypotheses").json() == {"hypotheses": []}


def test_dashboard_skips_a_port_held_by_another_app() -> None:
    import socket

    from predlab.cli import bind_loopback

    other = bind_loopback(8765)  # stands in for the app already on the port
    other.listen()
    try:
        ours = bind_loopback(other.getsockname()[1])
        try:
            assert ours.getsockname()[1] != other.getsockname()[1]
            assert ours.getsockname()[0] == "127.0.0.1"
        finally:
            ours.close()
    finally:
        other.close()
    assert isinstance(other, socket.socket)


def test_carnet_endpoint_is_empty_then_reports_integrity(lab: Paths) -> None:
    client = TestClient(create_app(lab))
    body = client.get("/api/carnet").json()
    assert body["races"] == 0 and body["integrity_error"] is None
    assert {r["strategy"] for r in body["summary"]} == {
        "SG favori",
        "SP favori",
        "SG top marche_plus",
        "SP top marche_plus",
    }
    lab.carnet.write_text('{"kind": "freeze", "prev_hash": "x", "record_hash": "y"}\n')
    assert client.get("/api/carnet").json()["integrity_error"]


def test_status_survives_a_base_built_by_an_older_version(lab: Paths) -> None:
    import duckdb

    con = duckdb.connect(str(lab.database))
    con.execute("DROP TABLE dividends")
    con.close()
    db = TestClient(create_app(lab)).get("/api/status").json()["database"]
    assert db["dividends"] is None and db["missing_tables"] == ["dividends"]


def test_day_list_tells_what_the_lab_played(lab: Paths) -> None:
    body = TestClient(create_app(lab)).get("/api/races", params={"day": "2026-09-28"}).json()
    states = {r["rc"]: r["carnet"] for r in body["races"]}
    r2c1 = states["R2C1"]
    assert r2c1["state"] == "missed", "run long after the day: no ticket was frozen"
    assert r2c1["freeze_at"] < r2c1.get("frozen_at", "9999") or "frozen_at" not in r2c1


def test_carnet_periods_are_consistent(lab: Paths) -> None:
    body = TestClient(create_app(lab)).get("/api/carnet/periods").json()
    assert [p["key"] for p in body["periods"]] == ["day", "week", "month", "all"]
    assert set(body["streak"]) == {"current", "best", "ahead", "behind", "same"}
    assert "days" in body
    assert [(s["bet"], s["pick"]) for s in body["series"]] == [
        ("SG", "favori"),
        ("SP", "favori"),
        ("SG", "modèle"),
        ("SP", "modèle"),
    ]
    for p in body["periods"]:
        for side in ("model", "favori"):
            assert p[side]["net"] == p[side]["returned"] - p[side]["stake"]
        assert p["diff"] == p["model"]["net"] - p["favori"]["net"]
        assert p["differ"] <= p["races"]


def test_ahead_streak_skips_level_days_and_breaks_on_a_day_behind() -> None:
    from predlab.api.app import _ahead_streak

    states = ("ahead", "same", "ahead", "ahead", "behind", "ahead", "same", "ahead", "same")
    days = [{"state": s} for s in states]
    assert _ahead_streak(days) == {"current": 2, "best": 3, "ahead": 5, "behind": 1, "same": 3}
    assert _ahead_streak([])["current"] == 0
    assert _ahead_streak([{"state": "same"}])["current"] == 0, "level is not ahead"
    assert _ahead_streak([{"state": "ahead"}, {"state": "behind"}])["best"] == 1


def test_state_is_decided_to_the_cent() -> None:
    from predlab.api.app import _state

    assert _state(0.1 + 0.2 - 0.3) == "same"
    assert _state(0.01) == "ahead" and _state(-0.01) == "behind"


def test_profile_endpoints_answer_before_any_nightly_report(lab: Paths) -> None:
    client = TestClient(create_app(lab))
    body = client.get("/api/profile", params={"discipline": "PLAT"}).json()
    assert body["profile"] is None and body["model"] is None
    assert client.get("/api/profile", params={"discipline": "LOTO"}).status_code == 404
    race = client.get("/api/races/2026-09-28/R2C1/profile")
    assert race.status_code == 200
    assert set(race.json()) >= {"conditions", "horses", "profile", "model"}
    assert client.get("/api/races/2026-09-28/R9C9/profile").status_code == 404
    detail = client.get("/api/races/2026-09-28/R2C1").json()
    assert detail["model"] is None and all(r["model_p"] is None for r in detail["runners"])


def test_latest_profile_report_is_served(lab: Paths) -> None:
    rep = {
        "kind": "profile",
        "generated_at": "2026-09-30T02:00:00+00:00",
        "discipline": "PLAT",
        "race_factors": [],
        "runner_factors": [],
    }
    out = lab.runs / "profile_PLAT_20260930T020000Z"
    out.mkdir(parents=True)
    (out / "report.json").write_text(json.dumps(rep), encoding="utf-8")
    client = TestClient(create_app(lab))
    body = client.get("/api/profile").json()
    assert body["profile"]["id"] == "profile_PLAT_20260930T020000Z"
    kinds = {r["id"]: r["kind"] for r in client.get("/api/reports").json()["reports"]}
    assert kinds["profile_PLAT_20260930T020000Z"] == "profile"


def test_banc_endpoint_before_and_after_a_panel(lab: Paths) -> None:
    client = TestClient(create_app(lab))
    empty = client.get("/api/banc").json()
    assert empty["strategies"] == [] and empty["totals"]["all"]["tickets"] == 0
    (lab.banc).mkdir(parents=True, exist_ok=True)
    (lab.banc / "panel.json").write_text(
        json.dumps(
            {
                "strategies": [
                    {
                        "id": "fav",
                        "discipline": "PLAT",
                        "bet": "SG",
                        "criteria": {"odds_band": "Favori"},
                        "label": "Rang dans la cote : Favori",
                        "reference": True,
                        "origin": "référence",
                        "eliminated_at": None,
                        "exploration": {},
                        "confirmation": None,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    body = client.get("/api/banc").json()
    (s,) = body["strategies"]
    assert s["status"] == "référence" and s["live"]["bets"] == 0
    assert s["criteria_list"][0]["label"] == "Rang dans la cote"
    assert client.get("/api/races/2026-09-28/R2C1").json()["banc"] is None


def test_series_compare_favourite_and_model_on_the_same_races(lab: Paths) -> None:
    from predlab.api.app import Lab, _series

    def freeze(race: str, strategies: list[str]) -> list[dict]:
        tickets = [
            {
                "strategy": s,
                "bet_type": "SIMPLE_GAGNANT" if s.startswith("SG") else "SIMPLE_PLACE",
                "numbers": [1],
                "stake": 1.0,
            }
            for s in strategies
        ]
        return [
            {
                "kind": "freeze",
                "race_id": race,
                "day": "2026-09-30",
                "discipline": "PLAT",
                "off_time": "2026-09-30T12:00:00+00:00",
                "frozen_at": "x",
                "odds_as_of": "x",
                "alpha": 1.0,
                "tickets": tickets,
            },
            {"kind": "settle", "race_id": race, "settled_at": "x", "returns": [2.0] * len(tickets)},
        ]

    ledger = AppendOnlyLedger(lab.carnet)
    for rec in freeze(
        "2026-09-30/R1C1", ["SG favori", "SP favori", "SG top marche_plus", "SP top marche_plus"]
    ) + freeze(
        "2026-09-30/R2C1",
        ["SG favori", "SP favori"],  # a trot race: no model, not compared
    ):
        ledger.append(rec)
    series = {s["strategy"]: s["points"] for s in _series(Lab(lab))}
    assert series["SG favori"][0]["races"] == 1 and series["SG top marche_plus"][0]["races"] == 1
    assert series["SG favori"][0]["cum"] == 1.0
    assert "SG top marche_plus_prev" not in series, "side lines appear once they have played"
    for rec in freeze(
        "2026-09-30/R3C1", ["SG favori", "SG top marche_plus", "SG top marche_plus_prev"]
    ):
        ledger.append(rec)
    picks = {s["strategy"]: s["pick"] for s in _series(Lab(lab))}
    assert picks["SG top marche_plus_prev"] == "ancien"
    body = TestClient(create_app(lab)).get("/api/carnet/periods").json()
    every = body["periods"][-1]
    assert every["races"] == 2, "R2C1 (favourite only) is not a duel"
    assert every["model"]["stake"] == 3.0 and every["favori"]["stake"] == 3.0, (
        "the former version is a side line, not the model"
    )
    assert every["start"] == "2026-09-30" and every["differ"] == 0


def test_duels_pair_per_bet_type_and_tell_different_choices(lab: Paths) -> None:
    from predlab.api.app import Lab, _duel_days, _duels, _periods

    def rec(race: str, day: str, tickets: list[tuple[str, int, float]]) -> list[dict]:
        return [
            {
                "kind": "freeze",
                "race_id": f"{day}/{race}",
                "day": day,
                "discipline": "PLAT",
                "off_time": f"{day}T12:00:00+00:00",
                "frozen_at": "x",
                "odds_as_of": "x",
                "alpha": 1.0,
                "tickets": [
                    {
                        "strategy": s,
                        "bet_type": "SIMPLE_GAGNANT" if s.startswith("SG") else "SIMPLE_PLACE",
                        "numbers": [n],
                        "stake": 1.0,
                    }
                    for s, n, _ in tickets
                ],
            },
            {
                "kind": "settle",
                "race_id": f"{day}/{race}",
                "settled_at": "x",
                "returns": [r for *_, r in tickets],
            },
        ]

    ledger = AppendOnlyLedger(lab.carnet)
    for r in (
        # Same horse: level.
        rec("R1C1", "2026-10-01", [("SG favori", 3, 2.5), ("SG top marche_plus", 3, 2.5)]),
        # Different horses, the model's wins: ahead by 4.
        rec("R1C1", "2026-10-02", [("SG favori", 1, 0.0), ("SG top marche_plus", 5, 4.0)]),
        # SP played by the favourite only: only the SG pair counts.
        rec(
            "R1C2",
            "2026-10-02",
            [("SG favori", 2, 0.0), ("SG top marche_plus", 2, 0.0), ("SP favori", 2, 1.3)],
        ),
    ):
        for x in r:
            ledger.append(x)
    duels = _duels(Lab(lab))
    assert [d["differ"] for d in duels] == [False, True, False]
    assert duels[2]["favori"]["stake"] == 1.0, "the unpaired SP ticket stays out"
    assert duels[1]["model"]["numbers"] == [5] and duels[1]["favori"]["numbers"] == [1]
    assert duels[1]["model"]["win"] is True and duels[1]["favori"]["win"] is False
    assert duels[1]["model"]["net"] == 3.0 and duels[1]["favori"]["net"] == -1.0
    rows = TestClient(create_app(lab)).get("/api/carnet").json()["entries"]
    by = {r["race_id"]: r["duel"] for r in rows}
    assert (
        by["2026-10-02/R1C1"]["differ"] is True and by["2026-10-02/R1C2"]["model"]["stake"] == 1.0
    )
    days = _duel_days(duels)
    assert [d["state"] for d in days] == ["same", "ahead"]
    assert days[1]["diff"] == 4.0 and days[1]["differ"] == 1
    (every,) = [p for p in _periods(duels, date(2026, 10, 2)) if p["key"] == "all"]
    assert every["start"] == "2026-10-01" and every["races"] == 3 and every["differ"] == 1
    assert every["model"]["net"] == 3.5 and every["favori"]["net"] == -0.5
    assert every["diff"] == 4.0 and every["pending_stake"] == 0.0
