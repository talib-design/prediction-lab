"""The DARES series of job offers collected by France Travail, split by qualification.

Verified against the live Opendatasoft API on 2026-09-20:

    dataset  dares_offres_collectees_satisfaites_france_travail_brutes_mens
    base     https://data.dares.travail-emploi.gouv.fr/api/explore/v2.1/catalog/datasets
    licence  Licence Ouverte v2.0 (``lov2``) -- redistribution permitted with attribution
    records  95 736, of which 367 are the monthly cadre series used here
    coverage 1996-01 .. 2026-07, monthly, no gap
    catalogue https://www.data.gouv.fr/datasets/offres-collectees-et-satisfaites-par-france-travail-brutes-mensuelles

WHY THIS SERIES MATTERS TO THIS PROJECT
=====================================================================================

It is the *same concept* as the live collector -- offers collected by France Travail --
published by the statistical service of the ministry, broken down by qualification, so
``Cadres`` is available directly rather than by proxy. Three consequences:

1. **A target that exists today.** 367 real monthly observations, against which a
   forecasting engine can be built and backtested now, instead of waiting months for
   the live series to mature.
2. **An external check on the live collector.** If the API counts, corrected for
   expiry, do not track this series, the collector is measuring a platform artefact
   rather than the labour market. That is a falsifiable claim, and this is what makes
   it falsifiable.
3. **A forecasting problem with a real user.** DARES publishes with roughly a six-week
   lag -- 2026-07 was the latest figure on 2026-09-20. Predicting the figure before it
   is published is a nowcast of an official statistic, which is a defensible thing to
   build, unlike "predicting the job market" in the abstract.

THE TWO PROPERTIES THAT BOUND WHAT CAN BE CLAIMED
=====================================================================================

**Counts are rounded to the nearest hundred.** Every value in the series is a multiple
of 100, so on a level near 12 000 the published figure carries roughly +/-0.4% of
quantisation. A forecast error below that is not skill; it is below the resolution of
the data. Any reported accuracy has to be read against this floor.

**The series is raw, not seasonally adjusted** (``type_de_donnees = "Brutes"``). The
seasonal swing is large -- August collapses every year -- so a model that ignores
seasonality will be beaten by one that only knows the month, and a naive baseline that
looks impressive on this series may just be reciting the calendar. The seasonal naive
baseline exists to make that explicit.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path

API_BASE = "https://data.dares.travail-emploi.gouv.fr/api/explore/v2.1/catalog/datasets"
DATASET = "dares_offres_collectees_satisfaites_france_travail_brutes_mens"
LICENCE = "Licence Ouverte v2.0 (lov2)"
ATTRIBUTION = "DARES, offres collectées et satisfaites par France Travail (brutes, mensuelles)"
PARSER_VERSION = "dares-offres-1"

# The exact filter that isolates the cadre series. Spelled out rather than built from
# parts, because a silently mistyped modality returns an empty set instead of an error.
CADRE_FILTER = (
    'qualification="Cadres"'
    ' and type_d_emploi="Total"'
    ' and type_d_offre_d_emploi="Offres d\'emploi collectées"'
)
EXPECTED_HEADER = ("date", "nombre_d_offres_d_emploi")
FIRST_PERIOD = "1996-01"
TIMEOUT_S = 60
USER_AGENT = "prediction-lab/0.1 (research)"


class SourceFormatError(RuntimeError):
    """The source did not have the shape this parser was written against."""


class SeriesIntegrityError(RuntimeError):
    """The series itself is not what a monthly series must be."""


@dataclass(frozen=True, slots=True)
class MonthlySeries:
    """A contiguous monthly series. Contiguity is enforced, not assumed.

    ``periods`` are ``YYYY-MM`` strings in ascending order and ``values`` line up with
    them by index. A gap would silently shift every lag in a seasonal model, so it is
    an error rather than something to fill.
    """

    periods: tuple[str, ...]
    values: tuple[int, ...]
    parser_version: str = PARSER_VERSION

    def __post_init__(self) -> None:
        if len(self.periods) != len(self.values):
            raise SeriesIntegrityError(f"{len(self.periods)} periods but {len(self.values)} values")

    def __len__(self) -> int:
        return len(self.values)

    @property
    def start(self) -> str:
        return self.periods[0]

    @property
    def end(self) -> str:
        return self.periods[-1]


def month_index(period: str) -> int:
    """``YYYY-MM`` to a month number, so that contiguity is one subtraction."""
    try:
        year, month = (int(part) for part in period.split("-"))
    except ValueError:
        raise SourceFormatError(f"not a YYYY-MM period: {period!r}") from None
    if not 1 <= month <= 12:
        raise SourceFormatError(f"month out of range in {period!r}")
    return year * 12 + (month - 1)


def period_of(index: int) -> str:
    """Inverse of :func:`month_index`."""
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def next_period(period: str) -> str:
    """The month after ``period``. Used to name the first unpublished month."""
    return period_of(month_index(period) + 1)


def parse_rows(rows: list[dict[str, object]]) -> MonthlySeries:
    """Turn API or CSV rows into a series, refusing anything that is not one.

    Four checks, each guarding a failure that would be invisible downstream: an empty
    result (a mistyped filter modality returns nothing, not an error), a missing or
    non-integer value, a duplicate period, and a gap in the months.
    """
    if not rows:
        raise SourceFormatError(
            "the query returned no row. A mistyped modality in the filter returns an "
            "empty set rather than an error -- check CADRE_FILTER against the API's "
            "facet values."
        )

    seen: dict[str, int] = {}
    for row in rows:
        period = row.get("date")
        raw = row.get("nombre_d_offres_d_emploi")
        if not isinstance(period, str):
            raise SourceFormatError(f"row without a usable date: {row!r}")
        if raw is None:
            raise SeriesIntegrityError(f"{period} has no value")
        if not isinstance(raw, int | float | str):
            raise SourceFormatError(f"{period} has a non-numeric value {raw!r}")
        try:
            value = int(raw)
        except (TypeError, ValueError):
            raise SourceFormatError(f"{period} has a non-integer value {raw!r}") from None
        if value < 0:
            raise SeriesIntegrityError(f"{period} has a negative count {value}")
        if period in seen:
            raise SeriesIntegrityError(f"{period} appears twice")
        seen[period] = value

    ordered = sorted(seen, key=month_index)
    first, last = month_index(ordered[0]), month_index(ordered[-1])
    expected = last - first + 1
    if len(ordered) != expected:
        missing = [period_of(i) for i in range(first, last + 1) if period_of(i) not in seen]
        raise SeriesIntegrityError(
            f"{len(missing)} month(s) missing between {ordered[0]} and {ordered[-1]}: "
            f"{', '.join(missing[:6])}{' …' if len(missing) > 6 else ''}"
        )
    return MonthlySeries(periods=tuple(ordered), values=tuple(seen[p] for p in ordered))


def read_csv(path: Path) -> MonthlySeries:
    """Read the canonical two-column CSV written by :func:`write_csv`."""
    text = path.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise SourceFormatError(f"{path} is empty")
    header = tuple(part.strip() for part in lines[0].split(","))
    if header != EXPECTED_HEADER:
        raise SourceFormatError(
            f"{path} header is {header}, expected {EXPECTED_HEADER}. The file was "
            "written by a different version of this parser, or by hand."
        )
    rows: list[dict[str, object]] = []
    for number, line in enumerate(lines[1:], start=2):
        parts = line.split(",")
        if len(parts) != 2:
            raise SourceFormatError(f"{path} line {number}: expected 2 fields, got {len(parts)}")
        rows.append({"date": parts[0].strip(), "nombre_d_offres_d_emploi": parts[1].strip()})
    return parse_rows(rows)


def write_csv(series: MonthlySeries, path: Path) -> Path:
    """Write the canonical form: two columns, ascending, no thousands separator."""
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        f"{period},{value}" for period, value in zip(series.periods, series.values, strict=True)
    )
    path.write_text(",".join(EXPECTED_HEADER) + "\n" + body + "\n", encoding="utf-8")
    return path


def export_url(where: str = CADRE_FILTER) -> str:
    """The export URL for one filtered slice, ascending by period."""
    params = urllib.parse.urlencode(
        {
            "where": where,
            "select": "date,nombre_d_offres_d_emploi",
            "order_by": "date asc",
        }
    )
    return f"{API_BASE}/{DATASET}/exports/json?{params}"


def fetch(where: str = CADRE_FILTER) -> MonthlySeries:
    """Download the series. Needs network; the CLI falls back to the stored CSV."""
    request = urllib.request.Request(
        export_url(where), headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise SourceFormatError(
            f"the DARES export refused the request ({exc.code}). The dataset id or a "
            "filter modality may have changed."
        ) from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise SourceFormatError(
            f"could not reach {API_BASE} ({exc}). Check the network, a proxy, or a firewall."
        ) from None
    if not isinstance(payload, list):
        raise SourceFormatError(f"expected a JSON array, got {type(payload).__name__}")
    return parse_rows(payload)


def quantisation_floor(series: MonthlySeries) -> float:
    """Relative size of the rounding step at the series' own scale.

    Values are published rounded to the nearest hundred. A forecast error below this
    is not skill -- it is below the resolution of the data, and saying so is the
    difference between an honest accuracy claim and a misleading one.
    """
    if not series.values:
        raise SeriesIntegrityError("empty series has no scale")
    mean = sum(series.values) / len(series.values)
    return 100.0 / mean


def is_rounded_to_hundred(series: MonthlySeries) -> bool:
    """Whether every value is a multiple of 100, as the source publishes them."""
    return all(value % 100 == 0 for value in series.values)


def publication_lag_months(series: MonthlySeries, today: date) -> int:
    """How many months separate the last published figure from the current month.

    This is the size of the gap a nowcast would have to fill, and therefore the
    horizon any forecast of this series has to cover before it is of any use.
    """
    return today.year * 12 + (today.month - 1) - month_index(series.end)
