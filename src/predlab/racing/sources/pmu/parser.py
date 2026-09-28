"""Parsing PMU turfinfo JSON into domain objects.

Written against payloads read on 2026-09-28 (see ``tests/fixtures/pmu/README.md``).
The feed is undocumented, so the stance is the one the FDJ parser took:

* **strict on what the project depends on** -- a missing race number, off time or
  discipline raises :class:`PmuFormatError` naming the exact path, instead of producing
  a race that silently lacks its identity;
* **lenient on everything else** -- an optional field that disappears becomes ``None``,
  and unknown new fields are ignored. Their presence rate is what the audit measures.

Parsing never touches the network and never mutates the raw bytes: it can be re-run
over every stored capture whenever this file changes (``predlab racing parse-check``).
"""

from __future__ import annotations

import json
from typing import Any

from predlab.core.clock import from_epoch_ms, paris_day
from predlab.racing.domain import GoingMeasure, OddsQuote, Race, Runner, WeatherForecast

_HANDEDNESS = {"CORDE_DROITE": "RIGHT", "CORDE_GAUCHE": "LEFT"}


class PmuFormatError(ValueError):
    """The payload does not have the shape this parser was written against."""


def _load(raw: bytes | str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    try:
        doc = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise PmuFormatError(f"not valid JSON: {exc}") from exc
    if not isinstance(doc, dict):
        raise PmuFormatError("top level is not a JSON object")
    return doc


def _kinds(kind: type | tuple[type, ...]) -> tuple[type, ...]:
    return kind if isinstance(kind, tuple) else (kind,)


def _req(obj: dict[str, Any], key: str, kind: type | tuple[type, ...], path: str) -> Any:
    if key not in obj or obj[key] is None:
        raise PmuFormatError(f"{path}.{key}: required field is missing")
    value = obj[key]
    kinds = _kinds(kind)
    # bool is an int subclass; a boolean where a number is required is a format change.
    if isinstance(value, bool) and bool not in kinds:
        raise PmuFormatError(f"{path}.{key}: expected {kind}, got bool")
    if not isinstance(value, kinds):
        raise PmuFormatError(f"{path}.{key}: expected {kind}, got {type(value).__name__}")
    return value


def _opt(obj: dict[str, Any], key: str, kind: type | tuple[type, ...]) -> Any:
    value = obj.get(key)
    kinds = _kinds(kind)
    if value is None:
        return None
    if isinstance(value, bool) and bool not in kinds:
        return None
    return value if isinstance(value, kinds) else None


def _decimal(text: object) -> float | None:
    """PMU writes some measures as French decimals in strings: ``"3,8"``."""
    if isinstance(text, (int, float)) and not isinstance(text, bool):
        return float(text)
    if not isinstance(text, str) or not text.strip():
        return None
    try:
        return float(text.strip().replace(",", "."))
    except ValueError:
        return None


# --------------------------------------------------------------------------- programme


def parse_programme(raw: bytes | str | dict[str, Any]) -> list[Race]:
    """All races of one programme day, every country and discipline."""
    doc = _load(raw)
    programme = _req(doc, "programme", dict, "$")
    day = paris_day(from_epoch_ms(_req(programme, "date", int, "$.programme")))
    reunions = _req(programme, "reunions", list, "$.programme")

    races: list[Race] = []
    for i, reunion in enumerate(reunions):
        rpath = f"$.programme.reunions[{i}]"
        if not isinstance(reunion, dict):
            raise PmuFormatError(f"{rpath}: not an object")
        hippodrome = _req(reunion, "hippodrome", dict, rpath)
        pays = _req(reunion, "pays", dict, rpath)
        weather = _weather(reunion.get("meteo"))
        for j, course in enumerate(_req(reunion, "courses", list, rpath)):
            races.append(_race(course, f"{rpath}.courses[{j}]", day, hippodrome, pays, weather))
    return races


def _race(
    course: Any,
    path: str,
    day: Any,
    hippodrome: dict[str, Any],
    pays: dict[str, Any],
    weather: WeatherForecast | None,
) -> Race:
    if not isinstance(course, dict):
        raise PmuFormatError(f"{path}: not an object")
    going_raw = course.get("penetrometre")
    going = None
    if isinstance(going_raw, dict):
        going = GoingMeasure(
            value=_decimal(going_raw.get("valeurMesure")),
            label=_opt(going_raw, "intitule", str) or None,
            measured_at_local=_opt(going_raw, "heureMesure", str),
        )
    order = course.get("ordreArrivee")
    finish_order = None
    if isinstance(order, list) and all(
        isinstance(group, list) and all(isinstance(n, int) for n in group) for group in order
    ):
        finish_order = [list(group) for group in order]
    incidents = [x for x in course.get("incidents") or [] if isinstance(x, dict)]
    return Race(
        day=day,
        meeting_number=_req(course, "numReunion", int, path),
        race_number=_req(course, "numOrdre", int, path),
        off_time=from_epoch_ms(_req(course, "heureDepart", int, path)),
        country_code=_req(pays, "code", str, f"{path}(pays)"),
        venue_code=_req(hippodrome, "code", str, f"{path}(hippodrome)"),
        venue_name=_opt(hippodrome, "libelleCourt", str) or "",
        name=_opt(course, "libelle", str),
        discipline=_req(course, "discipline", str, path),
        specialty=_opt(course, "specialite", str),
        category=_opt(course, "categorieParticularite", str),
        age_condition=_opt(course, "conditionAge", str),
        sex_condition=_opt(course, "conditionSexe", str),
        distance_m=_opt(course, "distance", int),
        handedness=_HANDEDNESS.get(_opt(course, "corde", str) or ""),
        declared_runners=_opt(course, "nombreDeclaresPartants", int),
        prize_eur=_opt(course, "montantPrix", int),
        status=_opt(course, "statut", str),
        status_category=_opt(course, "categorieStatut", str),
        going=going,
        weather=weather,
        is_final=bool(course.get("arriveeDefinitive") or course.get("isArriveeDefinitive")),
        finish_order=finish_order,
        incidents=incidents,
    )


def _weather(meteo: Any) -> WeatherForecast | None:
    if not isinstance(meteo, dict):
        return None
    issued = _opt(meteo, "datePrevision", int)
    return WeatherForecast(
        issued_at=from_epoch_ms(issued) if issued is not None else None,
        temperature_c=_decimal(meteo.get("temperature")),
        wind_force=_decimal(meteo.get("forceVent")),
        wind_direction=_opt(meteo, "directionVent", str),
        sky=_opt(meteo, "nebulositeLibelleCourt", str),
    )


# ------------------------------------------------------------------------ participants


def parse_participants(raw: bytes | str | dict[str, Any], race_id: str) -> list[Runner]:
    doc = _load(raw)
    items = _req(doc, "participants", list, "$")
    runners = []
    for i, p in enumerate(items):
        path = f"$.participants[{i}]"
        if not isinstance(p, dict):
            raise PmuFormatError(f"{path}: not an object")
        gains_raw = p.get("gainsParticipant")
        gains: dict[str, Any] = gains_raw if isinstance(gains_raw, dict) else {}
        runners.append(
            Runner(
                race_id=race_id,
                number=_req(p, "numPmu", int, path),
                name=_req(p, "nom", str, path),
                status=_req(p, "statut", str, path),
                horse_key=_opt(p, "idCheval", str),
                age=_opt(p, "age", int),
                sex=_opt(p, "sexe", str),
                breed=_opt(p, "race", str),
                draw=_opt(p, "placeCorde", int),
                weight_raw=_opt(p, "handicapPoids", int),
                handicap_value=_decimal(p.get("handicapValeur")),
                jockey=_opt(p, "driver", str),
                jockey_changed=_opt(p, "driverChange", bool),
                trainer=_opt(p, "entraineur", str),
                owner=_opt(p, "proprietaire", str),
                sire=_opt(p, "nomPere", str),
                dam=_opt(p, "nomMere", str),
                dam_sire=_opt(p, "nomPereMere", str),
                blinkers=_opt(p, "oeilleres", str),
                form=_opt(p, "musique", str),
                career_starts=_opt(p, "nombreCourses", int),
                career_wins=_opt(p, "nombreVictoires", int),
                career_places=_opt(p, "nombrePlaces", int),
                earnings_raw=_opt(gains, "gainsCarriere", int),
                finish_position=_opt(p, "ordreArrivee", int),
                odds_reference=_quote(p.get("dernierRapportReference")),
                odds_direct=_quote(p.get("dernierRapportDirect")),
            )
        )
    return runners


def _quote(obj: Any) -> OddsQuote | None:
    """An odds quote is kept only if it has both a usable price and a timestamp."""
    if not isinstance(obj, dict):
        return None
    odds = _decimal(obj.get("rapport"))
    stamp = _opt(obj, "dateRapport", int)
    if odds is None or odds <= 1.0 or stamp is None:
        return None
    return OddsQuote(
        kind=_opt(obj, "typeRapport", str) or "UNKNOWN",
        odds=odds,
        reported_at=from_epoch_ms(stamp),
        favourite=bool(obj.get("favoris")),
        trend=_opt(obj, "indicateurTendance", str),
    )
