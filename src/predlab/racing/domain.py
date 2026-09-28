"""The racing domain, as data.

These objects are what the rest of the project reasons about. They are deliberately
source-neutral: nothing here says "PMU". A parser turns a source's payload into these
objects, so a second source later means a second parser, not a second domain.

Two rules shape every class:

* **Instants are UTC and timezone-aware.** An odds quote without the moment it was
  quoted is worthless for honest evaluation, so ``reported_at`` is mandatory.
* **Nothing is inferred silently.** Where a unit is inferred rather than documented
  (weights, earnings), the raw value is kept next to the derived one.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class OddsQuote(BaseModel, frozen=True):
    """One pari-mutuel win-odds quote for one runner, at one instant.

    ``kind`` is the source's own label (PMU: ``REFERENCE`` or ``DIRECT``). What those
    labels mean in time is **measured, not assumed**: in the samples checked on
    2026-09-28 the REFERENCE quote sat ~30 min before the off and the last DIRECT
    quote ~2 min *after* the scheduled off -- i.e. final odds, unusable by any model
    predicting before the race. See docs/DATA_SOURCES.md.
    """

    kind: str
    odds: float
    reported_at: datetime
    favourite: bool = False
    trend: str | None = None


class GoingMeasure(BaseModel, frozen=True):
    """Penetrometer reading. ``measured_at_local`` is Paris wall-clock time as published."""

    value: float | None
    label: str | None
    measured_at_local: str | None


class WeatherForecast(BaseModel, frozen=True):
    """A forecast, with the moment it was issued. Not an observation."""

    issued_at: datetime | None
    temperature_c: float | None
    wind_force: float | None
    wind_direction: str | None
    sky: str | None


class Race(BaseModel, frozen=True):
    day: date
    meeting_number: int
    race_number: int
    off_time: datetime
    country_code: str
    venue_code: str
    venue_name: str
    name: str | None = None
    discipline: str
    specialty: str | None = None
    category: str | None = None
    age_condition: str | None = None
    sex_condition: str | None = None
    distance_m: int | None = None
    handedness: str | None = None  # "LEFT" | "RIGHT" | None
    declared_runners: int | None = None
    prize_eur: int | None = None
    status: str | None = None
    status_category: str | None = None
    going: GoingMeasure | None = None
    weather: WeatherForecast | None = None
    is_final: bool = False
    finish_order: list[list[int]] | None = None
    incidents: list[dict[str, object]] = Field(default_factory=list)

    @property
    def race_id(self) -> str:
        return f"{self.day.isoformat()}/R{self.meeting_number}C{self.race_number}"

    @property
    def is_finished(self) -> bool:
        return self.is_final or self.status_category == "ARRIVEE"


class Runner(BaseModel, frozen=True):
    race_id: str
    number: int
    name: str
    horse_key: str | None = None
    status: str
    age: int | None = None
    sex: str | None = None
    breed: str | None = None
    draw: int | None = None
    weight_raw: int | None = None
    handicap_value: float | None = None
    jockey: str | None = None
    jockey_changed: bool | None = None
    trainer: str | None = None
    owner: str | None = None
    sire: str | None = None
    dam: str | None = None
    dam_sire: str | None = None
    blinkers: str | None = None
    form: str | None = None
    career_starts: int | None = None
    career_wins: int | None = None
    career_places: int | None = None
    earnings_raw: int | None = None
    finish_position: int | None = None
    odds_reference: OddsQuote | None = None
    odds_direct: OddsQuote | None = None

    @property
    def identity_key(self) -> str | None:
        """Stable horse identity: PMU's ``idCheval`` when published, else rebuilt.

        PMU's key is ``NAME-DAM-SIRE``. It is absent before 2025 but the audit of
        2026-09-28 found it equal to that concatenation in 1 836 of 1 836 checked
        runners, with dam and sire present in every year since 2013.
        """
        if self.horse_key:
            return self.horse_key
        if self.name and self.dam and self.sire:
            return f"{self.name}-{self.dam}-{self.sire}"
        return None

    @property
    def weight_kg(self) -> float | None:
        """Inferred unit: PMU publishes tenths of a kilogram (580 -> 58.0). [hypothesis]"""
        return None if self.weight_raw is None else self.weight_raw / 10.0

    @property
    def is_runner(self) -> bool:
        return self.status == "PARTANT"
