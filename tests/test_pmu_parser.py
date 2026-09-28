from __future__ import annotations

import json
from datetime import UTC, date, datetime

import pytest

from predlab.core.clock import minutes_between
from predlab.racing.sources.pmu.parser import PmuFormatError, parse_participants, parse_programme

from .conftest import fixture_bytes


def _races():
    return {
        r.race_id: r for r in parse_programme(fixture_bytes("programme_2026-09-28_excerpt.json"))
    }


def test_programme_day_is_the_paris_calendar_day() -> None:
    races = _races()
    assert {r.day for r in races.values()} == {date(2026, 9, 28)}


def test_flat_race_fields_are_read() -> None:
    race = _races()["2026-09-28/R2C1"]
    assert race.discipline == "PLAT"
    assert race.country_code == "FRA"
    assert race.venue_code == "CRA"
    assert race.off_time == datetime(2026, 9, 28, 8, 50, tzinfo=UTC)
    assert race.distance_m == 1300
    assert race.handedness == "RIGHT"
    assert race.age_condition == "DEUX_ANS"
    assert race.declared_runners == 9
    assert race.prize_eur == 14600
    assert race.going is not None
    assert race.going.value == pytest.approx(3.8), "French decimal '3,8' must parse"
    assert race.going.label == "Très souple"
    assert not race.is_finished


def test_weather_is_a_forecast_with_its_issue_time() -> None:
    race = _races()["2026-09-28/R1C1"]
    assert race.weather is not None
    assert race.weather.issued_at == datetime(2026, 9, 28, 0, 18, tzinfo=UTC)
    assert race.weather.temperature_c == 21
    assert race.handedness == "LEFT"


def test_a_missing_identity_field_fails_loudly_with_its_path() -> None:
    doc = json.loads(fixture_bytes("programme_2026-09-28_excerpt.json"))
    del doc["programme"]["reunions"][1]["courses"][0]["heureDepart"]
    with pytest.raises(PmuFormatError, match=r"reunions\[1\]\.courses\[0\]\.heureDepart"):
        parse_programme(doc)


def test_a_type_change_fails_loudly() -> None:
    doc = json.loads(fixture_bytes("programme_2026-09-28_excerpt.json"))
    doc["programme"]["reunions"][0]["courses"][0]["numOrdre"] = "1"
    with pytest.raises(PmuFormatError, match="numOrdre"):
        parse_programme(doc)


def test_garbage_is_refused() -> None:
    with pytest.raises(PmuFormatError):
        parse_programme(b"<html>maintenance</html>")


def test_runner_fields_are_read() -> None:
    [runner] = parse_participants(
        fixture_bytes("participants_2026-09-28_R2C1_excerpt.json"), "2026-09-28/R2C1"
    )
    assert runner.name == "EAST AND WEST"
    assert runner.horse_key == "EAST AND WEST-LIVINGINAFANTASY-TERRITORIES"
    assert (runner.sire, runner.dam, runner.dam_sire) == (
        "TERRITORIES",
        "LIVINGINAFANTASY",
        "MONSUN",
    )
    assert runner.draw == 1
    assert runner.weight_kg == pytest.approx(58.0)
    assert runner.jockey == "T.BACHELOT"
    assert runner.trainer == "S.WATTEL (S)"
    assert runner.form == "4p7p"
    assert runner.earnings_raw == 315100
    assert runner.is_runner


def test_odds_quotes_keep_their_timestamps() -> None:
    [runner] = parse_participants(fixture_bytes("participants_2026-09-28_R2C1_excerpt.json"), "x")
    assert runner.odds_reference is not None and runner.odds_direct is not None
    assert runner.odds_reference.odds == 6.3
    assert runner.odds_reference.reported_at == datetime(2026, 9, 28, 8, 20, 5, tzinfo=UTC)
    assert runner.odds_direct.odds == 5.7
    assert runner.odds_direct.reported_at == datetime(2026, 9, 28, 8, 41, 38, tzinfo=UTC)


def test_finished_race_result_and_incidents() -> None:
    [race] = parse_programme(fixture_bytes("programme_2026-09-27_R1C1_partial.json"))
    assert race.is_final and race.is_finished
    assert race.finish_order is not None and race.finish_order[0] == [4]
    assert {i["type"] for i in race.incidents} == {
        "NON_PARTANT",
        "DISQUALIFIE_POUR_ALLURE_IRREGULIERE",
    }

    runners = parse_participants(
        fixture_bytes("participants_2026-09-27_R1C1_partial.json"), race.race_id
    )
    by_number = {r.number: r for r in runners}
    assert by_number[4].finish_position == 1
    assert not by_number[6].is_runner
    assert by_number[5].finish_position is None, "disqualified: no position"


def test_last_direct_quote_can_postdate_the_off() -> None:
    """The leakage trap, pinned: 'last direct odds' were quoted after the scheduled off."""
    [race] = parse_programme(fixture_bytes("programme_2026-09-27_R1C1_partial.json"))
    runners = parse_participants(
        fixture_bytes("participants_2026-09-27_R1C1_partial.json"), race.race_id
    )
    runner = next(r for r in runners if r.number == 4)
    assert runner.odds_direct is not None and runner.odds_reference is not None
    assert minutes_between(race.off_time, runner.odds_direct.reported_at) > 0
    assert minutes_between(race.off_time, runner.odds_reference.reported_at) < -30


def test_a_quote_without_timestamp_is_dropped() -> None:
    doc = {
        "participants": [
            {"numPmu": 1, "nom": "X", "statut": "PARTANT", "dernierRapportDirect": {"rapport": 4.0}}
        ]
    }
    [runner] = parse_participants(doc, "r")
    assert runner.odds_direct is None
