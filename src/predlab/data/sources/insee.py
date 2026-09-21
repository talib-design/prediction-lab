"""The INSEE business-climate indicator, as a candidate leading variable.

Verified against the live SDMX service on 2026-09-21:

    endpoint  https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/{idbank}
    idbank    001565530
    title     Indicateur du climat des affaires - Tous secteurs - France métropolitaine
    frequency monthly, 1977-01 onward (1996-01 here, to match the DARES series)
    licence   Licence Ouverte -- attribution to Insee

No API key: this endpoint answers unauthenticated, which is why it was chosen over the
key-gated catalogue API.

WHY THIS VARIABLE AND NOT ANOTHER
=====================================================================================

Elections and geopolitics cannot be modelled here and the arithmetic says so plainly:
367 months of target data contain roughly seven French national elections, so an
effect of unknown sign, size and delay cannot be estimated from them -- the same
power calculation that said detecting a 5% lottery bias would take 385 years. "Tensions
géopolitiques" is worse still: it is a narrative, not a series, so there is nothing to
confront the target with.

The business climate is the opposite case. It is a monthly series running since 1977,
it measures firms' own assessment of their situation -- which is what precedes a hiring
decision -- and, decisively, **it is published ahead of the target**: the August 2026
reading was out on 21 August, while DARES had only published July. A variable that
arrives after the thing it is meant to predict is useless however well it correlates.

THE RULE THAT KEEPS IT HONEST
=====================================================================================

**To forecast month M, only climate readings up to and including M may be used.** The
climate for M is published around the 21st of M; the DARES figure for M appears about
two months later. So the information genuinely exists at forecast time -- and this rule
is the conservative version, since M+1 would often be available too.

Getting this wrong is the classic way a leading indicator manufactures skill: use the
climate of December to forecast December without checking when December's climate was
published, and the backtest reports a model that cannot be run in reality.

And the finding has to survive a test. With 139 evaluation points, a 2-3% improvement
in mean error is well within what noise produces, so an improvement is only reported
as one if a block permutation test says it is.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from pathlib import Path
from xml.etree import ElementTree

from predlab.data.sources.dares import (
    MonthlySeries,
    SeriesIntegrityError,
    SourceFormatError,
    month_index,
    period_of,
)

SDMX_URL = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/{idbank}"
CLIMAT_AFFAIRES = "001565530"
LICENCE = "Licence Ouverte -- Insee"
ATTRIBUTION = "Insee, indicateur du climat des affaires, tous secteurs, France métropolitaine"
PARSER_VERSION = "insee-climat-1"
EXPECTED_HEADER = ("date", "climat_affaires")
TIMEOUT_S = 60
USER_AGENT = "prediction-lab/0.1 (research)"

# The indicator is normalised to a long-run mean of 100 by construction. A value far
# outside this range means the wrong idbank, not an extraordinary economy.
PLAUSIBLE_RANGE = (30.0, 170.0)


def parse_sdmx(xml: bytes | str) -> dict[str, float]:
    """Pull ``TIME_PERIOD -> OBS_VALUE`` out of an SDMX StructureSpecificData message."""
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        raise SourceFormatError(f"the SDMX response did not parse as XML: {exc}") from None
    out: dict[str, float] = {}
    for node in root.iter():
        if not node.tag.endswith("Obs"):
            continue
        period = node.get("TIME_PERIOD")
        raw = node.get("OBS_VALUE")
        if period is None or raw is None:
            continue
        try:
            out[period] = float(raw)
        except ValueError:
            raise SourceFormatError(f"{period} has a non-numeric value {raw!r}") from None
    if not out:
        raise SourceFormatError(
            "the SDMX response contained no observation -- the idbank may have changed"
        )
    return out


def to_series(values: dict[str, float], *, start: str | None = None) -> MonthlySeries:
    """A contiguous monthly series, refusing a gap rather than interpolating one.

    Values are kept as tenths so that :class:`MonthlySeries`, which stores integers,
    does not silently round the indicator to whole points. Callers divide by ten.
    """
    periods = sorted((p for p in values if start is None or p >= start), key=month_index)
    if not periods:
        raise SourceFormatError(f"no observation at or after {start}")
    first, last = month_index(periods[0]), month_index(periods[-1])
    if len(periods) != last - first + 1:
        missing = [period_of(i) for i in range(first, last + 1) if period_of(i) not in values]
        raise SeriesIntegrityError(f"{len(missing)} month(s) missing: {', '.join(missing[:6])}")
    low, high = PLAUSIBLE_RANGE
    for p in periods:
        if not low <= values[p] <= high:
            raise SeriesIntegrityError(
                f"{p} reads {values[p]}, outside the plausible range {PLAUSIBLE_RANGE} "
                "for an indicator normalised to 100 -- wrong idbank?"
            )
    return MonthlySeries(
        periods=tuple(periods),
        values=tuple(round(values[p] * 10) for p in periods),
        parser_version=PARSER_VERSION,
    )


def fetch(idbank: str = CLIMAT_AFFAIRES, *, start: str | None = "1996-01") -> MonthlySeries:
    """Download the indicator. The endpoint needs no key."""
    request = urllib.request.Request(
        SDMX_URL.format(idbank=idbank), headers={"User-Agent": USER_AGENT}
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        raise SourceFormatError(
            f"the INSEE SDMX service refused the request ({exc.code}); idbank {idbank} "
            "may no longer exist"
        ) from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise SourceFormatError(
            f"could not reach bdm.insee.fr ({exc}). Check the network, a proxy, or a firewall."
        ) from None
    return to_series(parse_sdmx(payload), start=start)


def read_csv(path: Path) -> MonthlySeries:
    """Read the canonical two-column CSV."""
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        raise SourceFormatError(f"{path} is empty")
    header = tuple(part.strip() for part in lines[0].split(","))
    if header != EXPECTED_HEADER:
        raise SourceFormatError(f"{path} header is {header}, expected {EXPECTED_HEADER}")
    values: dict[str, float] = {}
    for number, line in enumerate(lines[1:], start=2):
        parts = line.split(",")
        if len(parts) != 2:
            raise SourceFormatError(f"{path} line {number}: expected 2 fields")
        try:
            values[parts[0].strip()] = float(parts[1])
        except ValueError:
            raise SourceFormatError(f"{path} line {number}: {parts[1]!r} is not a number") from None
    return to_series(values)


def write_csv(series: MonthlySeries, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        f"{p},{v / 10:.1f}" for p, v in zip(series.periods, series.values, strict=True)
    )
    path.write_text(",".join(EXPECTED_HEADER) + "\n" + body + "\n", encoding="utf-8")
    return path


def usable_through(target_period: str) -> str:
    """The last climate reading a forecast of ``target_period`` may look at.

    The conservative rule stated in the module docstring, in one place so that no
    model can quietly adopt a looser one.
    """
    return target_period
