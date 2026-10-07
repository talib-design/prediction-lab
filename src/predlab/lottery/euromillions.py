"""EuroMillions: strict reader for the official FDJ archives, and a local draw store.

Source: the six CSV archives published by the FDJ ("service-draw-info" documentations,
see ``data/manifests/euromillions_fdj.json`` for URLs and SHA-256). They cover three
rule eras with *different column layouts and encodings*; this module reads all of them
by column **name** (never by position) and refuses anything it does not understand
rather than guessing.

What is checked on every row (a failure raises :class:`EuroMillionsFormatError`, listing
every offending line, instead of silently dropping or repairing it):

* the date parses (``dd/mm/yyyy``, ``dd/mm/yy`` or ``yyyymmdd``) and falls in an era;
* the French weekday label agrees with the calendar weekday of the date;
* the weekday is one the era draws on;
* the 5 balls and 2 stars are legal for the era (range, distinct);
* the "sorted" columns of the file equal the sorted extraction columns;
* the number of prize ranks matches the era (12 before 2011-05-10, 13 after);
* no draw date appears twice.

Prize data (winners and payout per rank) is optional context for the payout analysis; an
inconsistency there is reported as a *warning* and the value kept as missing, because
it cannot change which numbers were drawn.

Raw archives are never committed (public repository, FDJ reuse terms not stated on the
download page: "Je ne sais pas"). Only the parsed store lives under ``data/normalized``
and it is gitignored too.
"""

from __future__ import annotations

import csv
import io
import json
import re
import unicodedata
import zipfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import numpy as np
import polars as pl

from predlab.core.hashing import sha256_bytes
from predlab.lottery.gamespec import (
    EM_2004_02,
    EUROMILLIONS_ERAS,
    GameSpec,
    euromillions_era_for,
)
from predlab.lottery.store import SourceMutationError

PARSER_VERSION = "em-fdj-1"

FDJ_DOC_BASE = "https://www.sto.api.fdj.fr/anonymous/service-draw-info/v3/documentations/"
_ID = "1a2b3c4d-9876-4562-b3fc-2c963f66"
# (local name, document id suffix, period) as listed on the FDJ EuroMillions download
# page on 2026-10-06. Only the first one changes (it grows with every new draw).
FDJ_ARCHIVES: tuple[tuple[str, str, str], ...] = (
    ("part1", "afe6", "2020-02 ->"),
    ("part2", "afd6", "2019-03 -> 2020-01"),
    ("part3", "afc6", "2016-09 -> 2019-02"),
    ("part4", "afb6", "2014-02 -> 2016-09"),
    ("part5", "afa9", "2011-05 -> 2014-01"),
    ("part6", "afa8", "2004-02 -> 2011-05"),
)
CURRENT_ARCHIVE_URL = FDJ_DOC_BASE + _ID + FDJ_ARCHIVES[0][1]
MAX_RANKS = 13

_WEEKDAYS = {"LUNDI": 1, "MARDI": 2, "MERCREDI": 3, "JEUDI": 4, "VENDREDI": 5, "SAMEDI": 6}
_WEEKDAYS |= {"DIMANCHE": 7, "LU": 1, "MA": 2, "ME": 3, "JE": 4, "VE": 5, "SA": 6, "DI": 7}
_DATE_FORMATS = ("%d/%m/%Y", "%d/%m/%y", "%Y%m%d")
_WINNERS = re.compile(r"nombre_de_gagnant_au_rang(\d+)(?:_euro_millions)?_en_(france|europe)$")
_RAPPORT = re.compile(r"rapport_du_rang(\d+)(?:_euro_millions)?$")
_SORTED = re.compile(r"\d+")


class EuroMillionsFormatError(ValueError):
    """The archive contains something this reader refuses to interpret."""


@dataclass(frozen=True, slots=True)
class EuroMillionsDraw:
    """One draw, numbers in extraction order. Prize tuples have ``MAX_RANKS`` slots."""

    draw_date: date
    weekday: int
    era: str
    main_order: tuple[int, ...]
    stars_order: tuple[int, ...]
    source_id: str
    cycle: str | None
    winners_fr: tuple[int | None, ...]
    winners_eu: tuple[int | None, ...]
    rapports: tuple[float | None, ...]
    source_file: str

    @property
    def main_sorted(self) -> tuple[int, ...]:
        return tuple(sorted(self.main_order))

    @property
    def stars_sorted(self) -> tuple[int, ...]:
        return tuple(sorted(self.stars_order))


@dataclass(slots=True)
class ParseReport:
    """What a parse run saw. Warnings never change the numbers, only the prize columns."""

    files: list[dict[str, object]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    missing_dates: list[date] = field(default_factory=list)

    def summary(self) -> str:
        n = sum(int(f["rows"]) for f in self.files)  # type: ignore[call-overload]
        lines = [f"{len(self.files)} fichier(s), {n} tirages"]
        lines += [
            f"  {f['name']}: {f['rows']} lignes, {f['first']} -> {f['last']}, {f['encoding']}"
            for f in self.files
        ]
        if self.missing_dates:
            shown = ", ".join(d.isoformat() for d in self.missing_dates[:6])
            lines.append(
                f"  {len(self.missing_dates)} date(s) de tirage attendue(s) absente(s): {shown}"
            )
        lines += [f"  attention : {w}" for w in self.warnings[:10]]
        if len(self.warnings) > 10:
            lines.append(f"  … et {len(self.warnings) - 10} autre(s) avertissement(s)")
        return "\n".join(lines)


def _fold(name: str) -> str:
    """Header normalisation: ``numéro_de_tirage`` and its mangled latin-1 form agree."""
    text = unicodedata.normalize("NFKD", name.strip())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _decode(raw: bytes) -> tuple[str, str]:
    try:
        return raw.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        return raw.decode("latin-1"), "latin-1"


def _parse_date(text: str) -> date:
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unreadable date {text!r}")


def _number(text: str) -> float | None:
    text = re.sub(r"[\s\u202f\xa0]+", "", text)
    if text == "":
        return None
    return float(text.replace(",", "."))


def _int_list(text: str) -> tuple[int, ...]:
    return tuple(int(m) for m in _SORTED.findall(text))


def parse_csv(
    content: bytes, source_file: str
) -> tuple[list[EuroMillionsDraw], dict[str, object], list[str]]:
    """Parse one archive CSV. Returns draws, a file summary and prize-data warnings."""
    text, encoding = _decode(content)
    rows = list(csv.reader(io.StringIO(text), delimiter=";"))
    if len(rows) < 2:
        raise EuroMillionsFormatError(f"{source_file}: empty file")
    header = [_fold(h) for h in rows[0]]
    index = {name: i for i, name in enumerate(header) if name}
    needed = ["annee_numero_de_tirage", "jour_de_tirage", "date_de_tirage"]
    needed += [f"boule_{i}" for i in range(1, 6)] + ["etoile_1", "etoile_2"]
    needed += ["boules_gagnantes_en_ordre_croissant", "etoiles_gagnantes_en_ordre_croissant"]
    absent = [c for c in needed if c not in index]
    if absent:
        raise EuroMillionsFormatError(f"{source_file}: missing column(s) {absent}")

    winners_cols: dict[tuple[str, int], int] = {}
    rapport_cols: dict[int, int] = {}
    for name, i in index.items():
        if m := _WINNERS.fullmatch(name):
            winners_cols[(m.group(2), int(m.group(1)))] = i
        elif m := _RAPPORT.fullmatch(name):
            rapport_cols[int(m.group(1))] = i
    n_ranks = max(rapport_cols, default=0)
    if sorted(rapport_cols) != list(range(1, n_ranks + 1)):
        raise EuroMillionsFormatError(f"{source_file}: prize ranks are not contiguous")
    if "devise" in index:
        pass  # checked per row below

    errors: list[str] = []
    warnings: list[str] = []
    draws: list[EuroMillionsDraw] = []
    for line_no, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue
        if len(row) < len(header):
            row = row + [""] * (len(header) - len(row))
        try:
            draws.append(
                _parse_row(
                    row, index, winners_cols, rapport_cols, n_ranks, source_file, warnings, line_no
                )
            )
        except (ValueError, KeyError) as exc:
            errors.append(f"{source_file}:{line_no}: {exc}")
    if errors:
        shown = "\n  ".join(errors[:20])
        more = f"\n  … {len(errors) - 20} more" if len(errors) > 20 else ""
        raise EuroMillionsFormatError(f"{len(errors)} unreadable row(s):\n  {shown}{more}")

    dates = [d.draw_date for d in draws]
    summary: dict[str, object] = {
        "name": source_file,
        "rows": len(draws),
        "first": min(dates).isoformat(),
        "last": max(dates).isoformat(),
        "encoding": encoding,
        "columns": len(header),
        "ranks": n_ranks,
        "sha256": sha256_bytes(content),
    }
    return draws, summary, warnings


def _parse_row(
    row: list[str],
    index: dict[str, int],
    winners_cols: dict[tuple[str, int], int],
    rapport_cols: dict[int, int],
    n_ranks: int,
    source_file: str,
    warnings: list[str],
    line_no: int,
) -> EuroMillionsDraw:
    def cell(name: str) -> str:
        return row[index[name]].strip()

    day = _parse_date(cell("date_de_tirage"))
    spec = euromillions_era_for(day)
    label = cell("jour_de_tirage").upper()
    if label not in _WEEKDAYS:
        raise ValueError(f"unknown weekday label {label!r}")
    if _WEEKDAYS[label] != day.isoweekday():
        raise ValueError(f"weekday label {label!r} disagrees with the date {day} ")
    if day.isoweekday() not in spec.draw_weekdays:
        raise ValueError(f"{day} is a weekday on which era {spec.era} does not draw")

    main = tuple(int(cell(f"boule_{i}")) for i in range(1, 6))
    stars = (int(cell("etoile_1")), int(cell("etoile_2")))
    spec.pool("main").validate_combination(main)
    spec.pool("stars").validate_combination(stars)
    if _int_list(cell("boules_gagnantes_en_ordre_croissant")) != tuple(sorted(main)):
        raise ValueError("sorted-balls column disagrees with the extraction columns")
    if _int_list(cell("etoiles_gagnantes_en_ordre_croissant")) != tuple(sorted(stars)):
        raise ValueError("sorted-stars column disagrees with the extraction columns")
    expected_ranks = 12 if spec.era == EM_2004_02.era else 13
    if n_ranks != expected_ranks:
        raise ValueError(f"{n_ranks} prize ranks in file, era {spec.era} has {expected_ranks}")
    if "devise" in index and cell("devise").lower() != "eur":
        raise ValueError(f"currency {cell('devise')!r}, expected eur")

    winners_fr: list[int | None] = [None] * MAX_RANKS
    winners_eu: list[int | None] = [None] * MAX_RANKS
    rapports: list[float | None] = [None] * MAX_RANKS
    for rank in range(1, n_ranks + 1):
        try:
            fr = _number(row[winners_cols[("france", rank)]])
            eu = _number(row[winners_cols[("europe", rank)]])
            rap = _number(row[rapport_cols[rank]])
        except ValueError:
            warnings.append(f"{source_file}:{line_no} {day}: unreadable prize cell at rank {rank}")
            continue
        winners_fr[rank - 1] = None if fr is None else int(fr)
        winners_eu[rank - 1] = None if eu is None else int(eu)
        if eu is not None and eu > 0 and (rap is None or rap <= 0):
            warnings.append(f"{source_file}:{line_no} {day}: winners at rank {rank} but no payout")
        elif rap is not None and rap > 0:
            rapports[rank - 1] = rap

    cycle = (
        cell("numero_de_tirage_dans_le_cycle") if "numero_de_tirage_dans_le_cycle" in index else ""
    )
    return EuroMillionsDraw(
        draw_date=day,
        weekday=day.isoweekday(),
        era=spec.era,
        main_order=main,
        stars_order=stars,
        source_id=cell("annee_numero_de_tirage"),
        cycle=cycle or None,
        winners_fr=tuple(winners_fr),
        winners_eu=tuple(winners_eu),
        rapports=tuple(rapports),
        source_file=source_file,
    )


def parse_archives(paths: Sequence[Path]) -> tuple[list[EuroMillionsDraw], ParseReport]:
    """Parse several archives (``.zip`` containing one CSV, or bare ``.csv``) together."""
    report = ParseReport()
    by_date: dict[date, EuroMillionsDraw] = {}
    for path in paths:
        for name, content in _members(path):
            draws, summary, warnings = parse_csv(content, name)
            summary["archive"] = path.name
            summary["archive_sha256"] = sha256_bytes(path.read_bytes())
            report.files.append(summary)
            report.warnings += warnings
            for d in draws:
                if d.draw_date in by_date:
                    raise EuroMillionsFormatError(
                        f"draw {d.draw_date} appears in {by_date[d.draw_date].source_file} "
                        f"and in {d.source_file}"
                    )
                by_date[d.draw_date] = d
    ordered = [by_date[k] for k in sorted(by_date)]
    report.missing_dates = _missing_dates(ordered)
    return ordered, report


def _members(path: Path) -> Iterable[tuple[str, bytes]]:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            csvs = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            if len(csvs) != 1:
                raise EuroMillionsFormatError(f"{path.name}: expected one CSV, found {csvs}")
            yield csvs[0], zf.read(csvs[0])
    else:
        yield path.name, path.read_bytes()


def _missing_dates(draws: Sequence[EuroMillionsDraw]) -> list[date]:
    """Calendar dates on which the era draws but the archive has no row."""
    if not draws:
        return []
    have = {d.draw_date for d in draws}
    out: list[date] = []
    day = draws[0].draw_date
    while day <= draws[-1].draw_date:
        spec = euromillions_era_for(day)
        if day.isoweekday() in spec.draw_weekdays and day not in have:
            out.append(day)
        day += timedelta(days=1)
    return out


def verify_era_pools(draws: Sequence[EuroMillionsDraw]) -> dict[str, dict[str, int]]:
    """Empirical check of the era definitions: highest star seen per era, ball coverage."""
    out: dict[str, dict[str, int]] = {}
    for spec in EUROMILLIONS_ERAS:
        mine = [d for d in draws if d.era == spec.era]
        if not mine:
            continue
        stars = [s for d in mine for s in d.stars_order]
        balls = {b for d in mine for b in d.main_order}
        out[spec.era] = {
            "draws": len(mine),
            "max_star": max(stars),
            "expected_max_star": spec.pool("stars").high,
            "distinct_balls": len(balls),
        }
    return out


# --------------------------------------------------------------------------------------
# Store
# --------------------------------------------------------------------------------------

_CONTENT = ("main_order", "stars_order")


@dataclass(frozen=True, slots=True)
class EuroMillionsIngest:
    added: int
    unchanged: int
    payouts_revised: int
    total_after: int
    first_date: str
    last_date: str

    def summary(self) -> str:
        return (
            f"euromillions: {self.total_after} tirages ({self.first_date} -> {self.last_date}); "
            f"ajoutés {self.added}, inchangés {self.unchanged}, gains révisés {self.payouts_revised}"
        )


class EuroMillionsStore:
    """One Parquet file of every draw. Numbers are immutable; payouts may be completed.

    A draw's numbers never change: if the archive disagrees with what is stored the
    ingestion stops (:class:`SourceMutationError`). Winner counts and payouts of the most
    recent draws are the one thing allowed to be filled in later, and the number of
    revisions is reported.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def exists(self) -> bool:
        return self.path.exists()

    def read(self) -> pl.DataFrame:
        if not self.path.exists():
            raise FileNotFoundError(f"{self.path} absent: lancer `predlab lottery ingest` d'abord")
        return pl.read_parquet(self.path).sort("draw_date")

    @staticmethod
    def frame(draws: Sequence[EuroMillionsDraw], provenance: dict[str, str]) -> pl.DataFrame:
        return pl.DataFrame(
            {
                "draw_date": [d.draw_date for d in draws],
                "weekday": [d.weekday for d in draws],
                "era": [d.era for d in draws],
                "main_order": [list(d.main_order) for d in draws],
                "stars_order": [list(d.stars_order) for d in draws],
                "main_numbers": [list(d.main_sorted) for d in draws],
                "stars_numbers": [list(d.stars_sorted) for d in draws],
                "source_id": [d.source_id for d in draws],
                "cycle": [d.cycle for d in draws],
                "winners_fr": [list(d.winners_fr) for d in draws],
                "winners_eu": [list(d.winners_eu) for d in draws],
                "rapports": [list(d.rapports) for d in draws],
                "source_file": [d.source_file for d in draws],
                "retrieved_at": [provenance["retrieved_at"]] * len(draws),
                "parser_version": [PARSER_VERSION] * len(draws),
            },
            schema_overrides={
                "draw_date": pl.Date,
                "weekday": pl.Int8,
                "main_order": pl.List(pl.Int16),
                "stars_order": pl.List(pl.Int16),
                "main_numbers": pl.List(pl.Int16),
                "stars_numbers": pl.List(pl.Int16),
                "winners_fr": pl.List(pl.Int64),
                "winners_eu": pl.List(pl.Int64),
                "rapports": pl.List(pl.Float64),
            },
        )

    def ingest(
        self, draws: Sequence[EuroMillionsDraw], provenance: dict[str, str]
    ) -> EuroMillionsIngest:
        incoming = self.frame(draws, provenance)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            incoming.write_parquet(self.path)
            return self._report(added=len(incoming), unchanged=0, revised=0)

        existing = pl.read_parquet(self.path)
        known = {d: i for i, d in enumerate(existing["draw_date"].to_list())}
        mutated: list[str] = []
        revised = 0
        unchanged = 0
        new_idx: list[int] = []
        revised_rows: dict[date, dict[str, list[object]]] = {}
        for i, d in enumerate(incoming["draw_date"].to_list()):
            j = known.get(d)
            if j is None:
                new_idx.append(i)
                continue
            if any(existing[c][j].to_list() != incoming[c][i].to_list() for c in _CONTENT):
                mutated.append(d.isoformat())
                continue
            prize = ("winners_fr", "winners_eu", "rapports")
            if any(existing[c][j].to_list() != incoming[c][i].to_list() for c in prize):
                revised += 1
                revised_rows[d] = {c: incoming[c][i].to_list() for c in prize}
            else:
                unchanged += 1
        if mutated:
            raise SourceMutationError(
                f"euromillions: {len(mutated)} tirage(s) déjà enregistré(s) diffèrent dans la "
                f"source officielle, par ex. {mutated[:3]}. L'historique n'est pas réécrit."
            )
        merged = existing
        if revised_rows:
            rows = merged.to_dicts()
            for r in rows:
                if r["draw_date"] in revised_rows:
                    r.update(revised_rows[r["draw_date"]])
            merged = pl.DataFrame(rows, schema=existing.schema)
        if new_idx:
            merged = pl.concat([merged, incoming[new_idx]], how="vertical_relaxed")
        merged.sort("draw_date").write_parquet(self.path)
        return self._report(added=len(new_idx), unchanged=unchanged, revised=revised)

    def _report(self, *, added: int, unchanged: int, revised: int) -> EuroMillionsIngest:
        df = self.read()
        dates = df["draw_date"].to_list()
        return EuroMillionsIngest(
            added=added,
            unchanged=unchanged,
            payouts_revised=revised,
            total_after=len(df),
            first_date=dates[0].isoformat(),
            last_date=dates[-1].isoformat(),
        )

    # -- arrays for the engine --------------------------------------------------------

    def arrays(
        self, spec: GameSpec, *, era_only: bool = True
    ) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """``(dates, pool_draws)`` for ``build_view``/``run_backtest``.

        With ``era_only`` the rows are restricted to the spec's date range. The balls-only
        pooled spec (``EM_MAIN_2004``) uses every row.
        """
        df = self.read()
        if era_only:
            df = df.filter(pl.col("draw_date") >= spec.era_start)
            if spec.era_end is not None:
                df = df.filter(pl.col("draw_date") <= spec.era_end)
        dates = np.array(
            [np.datetime64(d, "D") for d in df["draw_date"].to_list()], dtype="datetime64[D]"
        )
        pools: dict[str, np.ndarray] = {}
        for pool in spec.pools:
            col = "main_numbers" if pool.name == "main" else "stars_numbers"
            pools[pool.name] = np.array(df[col].to_list(), dtype=np.int16).reshape(len(df), pool.k)
        return dates, pools


def provenance_now() -> dict[str, str]:
    return {"retrieved_at": datetime.now(UTC).isoformat(timespec="seconds")}


def archive_url(name: str) -> str | None:
    if name.startswith("current"):
        return CURRENT_ARCHIVE_URL
    for local, suffix, _period in FDJ_ARCHIVES:
        if name.startswith(local):
            return FDJ_DOC_BASE + _ID + suffix
    return None


def record_manifest(manifest: Path, report: ParseReport, *, retrieved_at: str) -> int:
    """Append archives not yet recorded (matched on SHA-256). Returns how many were new."""
    known: list[dict[str, object]] = (
        json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []
    )
    seen = {str(e.get("archive_sha256")) for e in known}
    added = 0
    for f in report.files:
        digest = str(f["archive_sha256"])
        if digest in seen:
            continue
        seen.add(digest)
        known.append(
            {
                "archive": f["archive"],
                "archive_sha256": digest,
                "csv": f["name"],
                "csv_sha256": f["sha256"],
                "rows": f["rows"],
                "first_draw": f["first"],
                "last_draw": f["last"],
                "encoding": f["encoding"],
                "columns": f["columns"],
                "prize_ranks": f["ranks"],
                "url": archive_url(str(f["archive"])),
                "recorded_at": retrieved_at,
                "parser_version": PARSER_VERSION,
            }
        )
        added += 1
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(known, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return added
