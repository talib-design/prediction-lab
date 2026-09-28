"""Time, stated once.

Racing is time-sensitive in a way the lottery was not: several races a day, odds that
move by the minute, and a result that becomes knowable at a precise moment. Every
timestamp in this project is therefore timezone-aware and stored in UTC; Paris time
is a display concern and the calendar day a race belongs to.

PMU publishes instants as epoch milliseconds (UTC). ``from_epoch_ms`` is the only
conversion used.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

PARIS = ZoneInfo("Europe/Paris")


def utcnow() -> datetime:
    return datetime.now(UTC)


def from_epoch_ms(value: int | float) -> datetime:
    return datetime.fromtimestamp(float(value) / 1000.0, UTC)


def paris_day(moment: datetime) -> date:
    """The racing day a UTC instant belongs to, in French local time."""
    if moment.tzinfo is None:
        raise ValueError("naive datetime: every instant in this project must carry a timezone")
    return moment.astimezone(PARIS).date()


def paris_midnight(day: date) -> datetime:
    return datetime(day.year, day.month, day.day, tzinfo=PARIS).astimezone(UTC)


def minutes_between(earlier: datetime, later: datetime) -> float:
    return (later - earlier) / timedelta(minutes=1)
