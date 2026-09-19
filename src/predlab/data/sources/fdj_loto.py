"""Ingestion of the official FDJ Loto historical archive.

Provenance, verified 2026-09-19 (see docs/DATA_SOURCES.md):

    https://www.sto.api.fdj.fr/anonymous/service-draw-info/v3/documentations/
    1a2b3c4d-9876-4562-b3fc-2c963f66afp6

A ZIP containing a single file ``loto_201911.csv``: Windows-1252, ``;``-separated,
50 columns of which the last is empty (every line ends with a trailing ``;``), rows
ordered by **descending** draw date.

Design stance: this parser is deliberately brittle about the *header*. If FDJ changes
a column name, adds a column or reorders the file, parsing stops with an explicit
error instead of silently producing a dataset whose columns mean something else. A
silent shift of one column would move ``numero_chance`` into ``boule_5`` and poison
every downstream result. Bump ``PARSER_VERSION`` only after a human has looked at the
change.
"""

from __future__ import annotations

import csv
import io
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from predlab.core.gamespec import GameSpec

PARSER_VERSION = "fdj-loto-1"
ENCODING = "cp1252"
DELIMITER = ";"

SOURCE_URLS: dict[str, str] = {
    "2019-11": (
        "https://www.sto.api.fdj.fr/anonymous/service-draw-info/v3/documentations/"
        "1a2b3c4d-9876-4562-b3fc-2c963f66afp6"
    ),
}

# Exact header of the 2019-11 era file, read from the official archive on 2026-09-19.
EXPECTED_HEADER: tuple[str, ...] = (
    "annee_numero_de_tirage",
    "jour_de_tirage",
    "date_de_tirage",
    "date_de_forclusion",
    "boule_1",
    "boule_2",
    "boule_3",
    "boule_4",
    "boule_5",
    "numero_chance",
    "combinaison_gagnante_en_ordre_croissant",
    "nombre_de_gagnant_au_rang1",
    "rapport_du_rang1",
    "nombre_de_gagnant_au_rang2",
    "rapport_du_rang2",
    "nombre_de_gagnant_au_rang3",
    "rapport_du_rang3",
    "nombre_de_gagnant_au_rang4",
    "rapport_du_rang4",
    "nombre_de_gagnant_au_rang5",
    "rapport_du_rang5",
    "nombre_de_gagnant_au_rang6",
    "rapport_du_rang6",
    "nombre_de_gagnant_au_rang7",
    "rapport_du_rang7",
    "nombre_de_gagnant_au_rang8",
    "rapport_du_rang8",
    "nombre_de_gagnant_au_rang9",
    "rapport_du_rang9",
    "nombre_de_codes_gagnants",
    "rapport_codes_gagnants",
    "codes_gagnants",
    "boule_1_second_tirage",
    "boule_2_second_tirage",
    "boule_3_second_tirage",
    "boule_4_second_tirage",
    "boule_5_second_tirage",
    "promotion_second_tirage",
    "combinaison_gagnant_second_tirage_en_ordre_croissant",
    "nombre_de_gagnant_au_rang_1_second_tirage",
    "rapport_du_rang1_second_tirage",
    "nombre_de_gagnant_au_rang_2_second_tirage",
    "rapport_du_rang2_second_tirage",
    "nombre_de_gagnant_au_rang_3_second_tirage",
    "rapport_du_rang3_second_tirage",
    "nombre_de_gagnant_au_rang_4_second_tirage",
    "rapport_du_rang4_second_tirage",
    "numero_7",
    "devise",
    "",  # trailing delimiter
)

# The weekday column carries trailing padding in the real file ("LUNDI   ").
FRENCH_WEEKDAY_TO_ISO: dict[str, int] = {
    "LUNDI": 1,
    "MARDI": 2,
    "MERCREDI": 3,
    "JEUDI": 4,
    "VENDREDI": 5,
    "SAMEDI": 6,
    "DIMANCHE": 7,
}


class SourceFormatError(RuntimeError):
    """The official file no longer matches the format this parser was written for."""


class DrawIntegrityError(ValueError):
    """A row is internally inconsistent: the source contradicts itself."""


@dataclass(frozen=True, slots=True)
class ParsedDraw:
    """One draw, reduced to what a predictive model may legitimately see.

    Prize and winner columns are read for cross-checking but deliberately not carried
    into the predictive dataset: they describe how many people bet on what, not how
    the balls came out, and keeping them invites post-hoc storytelling.
    """

    draw_key: str
    draw_date: date
    weekday: int
    main_numbers: tuple[int, ...]
    chance_numbers: tuple[int, ...]
    source_draw_id: str


def read_archive(zip_path: Path) -> tuple[str, bytes]:
    """Return ``(member_name, raw_bytes)`` of the single CSV inside the archive."""
    with zipfile.ZipFile(zip_path) as zf:
        members = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if len(members) != 1:
            raise SourceFormatError(
                f"{zip_path.name}: expected exactly one CSV in the archive, found {members}"
            )
        return members[0], zf.read(members[0])


def parse_csv_bytes(raw: bytes, spec: GameSpec) -> list[ParsedDraw]:
    """Parse the official CSV into validated draws, sorted by ascending date.

    Every row is cross-checked against the source's own
    ``combinaison_gagnante_en_ordre_croissant`` column and against the calendar. A row
    that fails either check raises rather than being dropped: a self-contradicting
    official file is news, not noise.
    """
    text = raw.decode(ENCODING)
    reader = csv.reader(io.StringIO(text, newline=""), delimiter=DELIMITER)
    try:
        header = tuple(next(reader))
    except StopIteration:
        raise SourceFormatError("empty file") from None

    if header != EXPECTED_HEADER:
        raise SourceFormatError(_describe_header_drift(header))

    main_pool = spec.pool("main")
    chance_pool = spec.pool("chance")
    idx = {name: i for i, name in enumerate(EXPECTED_HEADER[:-1])}

    draws: list[ParsedDraw] = []
    for line_no, row in enumerate(reader, start=2):
        if not any(cell.strip() for cell in row):
            continue
        if len(row) != len(EXPECTED_HEADER):
            raise SourceFormatError(
                f"line {line_no}: expected {len(EXPECTED_HEADER)} fields, got {len(row)}"
            )
        draws.append(_parse_row(row, idx, spec, main_pool.k, chance_pool.k, line_no))

    _assert_unique_dates(draws)
    draws.sort(key=lambda d: d.draw_date)
    return draws


def _parse_row(
    row: list[str],
    idx: dict[str, int],
    spec: GameSpec,
    n_main: int,
    n_chance: int,
    line_no: int,
) -> ParsedDraw:
    def cell(name: str) -> str:
        return row[idx[name]].strip()

    try:
        draw_date = datetime.strptime(cell("date_de_tirage"), "%d/%m/%Y").date()
    except ValueError as exc:
        raise SourceFormatError(
            f"line {line_no}: unparseable date {cell('date_de_tirage')!r}"
        ) from exc

    if n_chance != 1:
        raise SourceFormatError(
            f"{spec.key}: this parser handles a single chance number, spec asks for {n_chance}"
        )
    main = tuple(sorted(int(cell(f"boule_{i}")) for i in range(1, n_main + 1)))
    chance = (int(cell("numero_chance")),)
    spec.pool("main").validate_combination(main)
    spec.pool("chance").validate_combination(chance)

    # Cross-check 1: the source states the sorted combination itself. Use it.
    declared = cell("combinaison_gagnante_en_ordre_croissant")
    expected = "-".join(str(n) for n in main) + "+" + str(chance[0])
    if declared != expected:
        raise DrawIntegrityError(
            f"line {line_no}: source contradicts itself -- boules give {expected!r} "
            f"but combinaison_gagnante_en_ordre_croissant says {declared!r}"
        )

    # Cross-check 2: the stated weekday must match the calendar.
    stated = cell("jour_de_tirage").upper()
    iso = FRENCH_WEEKDAY_TO_ISO.get(stated)
    if iso is None:
        raise SourceFormatError(f"line {line_no}: unknown weekday {stated!r}")
    if iso != draw_date.isoweekday():
        raise DrawIntegrityError(
            f"line {line_no}: {draw_date} is ISO weekday {draw_date.isoweekday()} "
            f"but the file says {stated}"
        )

    # Cross-check 3: the draw must fall on a day this era actually draws on.
    if iso not in spec.draw_weekdays:
        raise DrawIntegrityError(
            f"line {line_no}: {draw_date} ({stated}) is not a draw day for {spec.key}"
        )
    if not spec.covers(draw_date):
        raise DrawIntegrityError(f"line {line_no}: {draw_date} lies outside era {spec.key}")

    return ParsedDraw(
        draw_key=f"{spec.key}/{draw_date.isoformat()}",
        draw_date=draw_date,
        weekday=iso,
        main_numbers=main,
        chance_numbers=chance,
        # Kept verbatim for traceability only. Its format is NOT stable across the
        # file ("20199133" in 2019, "26111" in 2026), so it is never used as a key.
        source_draw_id=cell("annee_numero_de_tirage"),
    )


def _assert_unique_dates(draws: list[ParsedDraw]) -> None:
    seen: dict[date, int] = {}
    for d in draws:
        seen[d.draw_date] = seen.get(d.draw_date, 0) + 1
    collisions = sorted(day for day, n in seen.items() if n > 1)
    if collisions:
        raise DrawIntegrityError(
            f"{len(collisions)} date(s) carry more than one draw, e.g. {collisions[:3]}. "
            "The canonical key assumes one draw per date for this era; refusing to "
            "deduplicate silently."
        )


def _describe_header_drift(actual: tuple[str, ...]) -> str:
    missing = [c for c in EXPECTED_HEADER if c and c not in actual]
    added = [c for c in actual if c and c not in EXPECTED_HEADER]
    parts = [
        "the official file no longer matches the format this parser was written for",
        f"expected {len(EXPECTED_HEADER)} columns, got {len(actual)}",
    ]
    if missing:
        parts.append(f"missing: {missing}")
    if added:
        parts.append(f"new: {added}")
    parts.append(
        "review the change, then bump PARSER_VERSION -- do not relax this check to "
        "make ingestion pass"
    )
    return "; ".join(parts)


# --------------------------------------------------------------------------------------
# Download
# --------------------------------------------------------------------------------------
# Kept separate from parsing so that the network is never needed to test the parser,
# and so an archive obtained by any other means (a manual curl, a colleague's copy)
# goes through exactly the same validation path.

USER_AGENT = "prediction-lab/0.1 (research; contact via repository)"
DOWNLOAD_TIMEOUT_S = 60


def download_archive(era: str, destination: Path) -> Path:
    """Download one era's ZIP archive to ``destination`` and return its path.

    Requires outbound HTTPS access to ``sto.api.fdj.fr``.
    """
    try:
        url = SOURCE_URLS[era]
    except KeyError:
        raise KeyError(
            f"no recorded official URL for era {era!r}; known: {sorted(SOURCE_URLS)}"
        ) from None

    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=DOWNLOAD_TIMEOUT_S) as response:
        content_type = response.headers.get("Content-Type", "")
        payload = response.read()

    if not payload.startswith(b"PK\x03\x04"):
        raise SourceFormatError(
            f"{url} did not return a ZIP archive (Content-Type: {content_type!r}, "
            f"{len(payload)} bytes). The endpoint may have changed or be rate-limiting."
        )
    destination.write_bytes(payload)
    return destination
