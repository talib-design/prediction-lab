"""Local, append-only store of immutable draw observations.

A draw that has happened is a fact. Once recorded it is never rewritten. When the
official archive is downloaded again -- which happens every time a new draw lands --
the store compares the incoming rows against what it already holds and reports three
things separately: rows that are new, rows that are unchanged, and rows whose content
*differs from what was previously recorded*. The third category is the interesting
one. It means the official source was edited retroactively, and it must surface as an
alert rather than be absorbed silently.

Storage is Parquet. At this scale (thousands of rows) a database would be ceremony;
what matters is a typed, columnar file with a schema that fails loudly.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import polars as pl

from predlab.core.gamespec import GameSpec
from predlab.data.sources.fdj_loto import ParsedDraw

STORE_SCHEMA_VERSION = 1

CONTENT_COLUMNS = ("draw_date", "weekday", "main_numbers", "chance_numbers")


class SourceMutationError(RuntimeError):
    """The official source changed a draw that had already been recorded."""


@dataclass(frozen=True, slots=True)
class IngestReport:
    """What one ingestion run actually did. Printed, logged, and worth reading."""

    game_key: str
    added: int
    unchanged: int
    mutated: tuple[str, ...]
    total_after: int
    first_date: str | None
    last_date: str | None

    def summary(self) -> str:
        lines = [
            f"{self.game_key}: {self.total_after} draws ({self.first_date} -> {self.last_date})",
            f"  added {self.added}, unchanged {self.unchanged}",
        ]
        if self.mutated:
            lines.append(f"  !! {len(self.mutated)} previously recorded draw(s) changed upstream")
        return "\n".join(lines)


def _frame(draws: Sequence[ParsedDraw], spec: GameSpec, provenance: dict[str, str]) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "draw_key": [d.draw_key for d in draws],
            "draw_date": [d.draw_date for d in draws],
            "weekday": [d.weekday for d in draws],
            "main_numbers": [list(d.main_numbers) for d in draws],
            "chance_numbers": [list(d.chance_numbers) for d in draws],
            "source_draw_id": [d.source_draw_id for d in draws],
            "game": [spec.game] * len(draws),
            "era": [spec.era] * len(draws),
            "official_source": [provenance["official_source"]] * len(draws),
            "source_hash": [provenance["source_hash"]] * len(draws),
            "retrieved_at": [provenance["retrieved_at"]] * len(draws),
            "parser_version": [provenance["parser_version"]] * len(draws),
        },
        schema_overrides={
            "draw_date": pl.Date,
            "weekday": pl.Int8,
            "main_numbers": pl.List(pl.Int16),
            "chance_numbers": pl.List(pl.Int16),
        },
    )


class DrawStore:
    """One Parquet file per game era."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def path_for(self, spec: GameSpec) -> Path:
        return self.root / f"{spec.game}_{spec.era}.parquet"

    def exists(self, spec: GameSpec) -> bool:
        return self.path_for(spec).exists()

    def read(self, spec: GameSpec) -> pl.DataFrame:
        path = self.path_for(spec)
        if not path.exists():
            raise FileNotFoundError(
                f"no dataset for {spec.key}; run `predlab data fetch {spec.game}` first"
            )
        return pl.read_parquet(path).sort("draw_date")

    def ingest(
        self,
        spec: GameSpec,
        draws: Sequence[ParsedDraw],
        provenance: dict[str, str],
        *,
        allow_mutation: bool = False,
    ) -> IngestReport:
        """Merge ``draws`` into the store without ever rewriting recorded history."""
        incoming = _frame(draws, spec, provenance)
        path = self.path_for(spec)
        path.parent.mkdir(parents=True, exist_ok=True)

        if not path.exists():
            incoming.write_parquet(path)
            return self._report(spec, added=len(incoming), unchanged=0, mutated=())

        existing = pl.read_parquet(path)
        known = set(existing["draw_key"].to_list())

        new_rows = incoming.filter(~pl.col("draw_key").is_in(list(known)))
        overlap_keys = [k for k in incoming["draw_key"].to_list() if k in known]

        mutated = self._detect_mutations(existing, incoming, overlap_keys)
        if mutated and not allow_mutation:
            raise SourceMutationError(
                f"{spec.key}: {len(mutated)} already-recorded draw(s) differ in the "
                f"official source, e.g. {mutated[:3]}. History is not rewritten "
                "automatically. Investigate, then re-run with --allow-mutation to "
                "record a corrected observation."
            )

        merged = pl.concat([existing, new_rows], how="vertical_relaxed").sort("draw_date")
        merged.write_parquet(path)
        return self._report(
            spec,
            added=len(new_rows),
            unchanged=len(overlap_keys) - len(mutated),
            mutated=mutated,
        )

    @staticmethod
    def _detect_mutations(
        existing: pl.DataFrame, incoming: pl.DataFrame, overlap_keys: list[str]
    ) -> tuple[str, ...]:
        if not overlap_keys:
            return ()
        cols = ["draw_key", *CONTENT_COLUMNS]
        left = existing.filter(pl.col("draw_key").is_in(overlap_keys)).select(cols).sort("draw_key")
        right = (
            incoming.filter(pl.col("draw_key").is_in(overlap_keys)).select(cols).sort("draw_key")
        )
        differing = [
            key
            for key, a, b in zip(
                left["draw_key"].to_list(),
                left.select(CONTENT_COLUMNS).rows(),
                right.select(CONTENT_COLUMNS).rows(),
                strict=True,
            )
            if a != b
        ]
        return tuple(differing)

    def _report(
        self, spec: GameSpec, *, added: int, unchanged: int, mutated: tuple[str, ...]
    ) -> IngestReport:
        df = self.read(spec)
        dates = df["draw_date"].to_list()
        return IngestReport(
            game_key=spec.key,
            added=added,
            unchanged=unchanged,
            mutated=mutated,
            total_after=len(df),
            first_date=dates[0].isoformat() if dates else None,
            last_date=dates[-1].isoformat() if dates else None,
        )

    def arrays(self, spec: GameSpec) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """Return ``(dates, pool_draws)`` ready for :func:`predlab.core.historyview.build_view`."""
        df = self.read(spec)
        dates = np.array(
            [np.datetime64(d, "D") for d in df["draw_date"].to_list()], dtype="datetime64[D]"
        )
        pools: dict[str, np.ndarray] = {}
        for pool in spec.pools:
            column = "main_numbers" if pool.name == "main" else "chance_numbers"
            pools[pool.name] = np.array(df[column].to_list(), dtype=np.int16).reshape(
                len(df), pool.k
            )
        return dates, pools


class ArchiveManifest:
    """Provenance record for every raw archive ever downloaded.

    Tracked in git on purpose: it is the audit trail that lets a future reader check
    which bytes produced which dataset.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[dict[str, str]]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def record(self, *, url: str, filename: str, sha256: str, n_bytes: int, era: str) -> None:
        entries = self.load()
        entries.append(
            {
                "era": era,
                "url": url,
                "filename": filename,
                "sha256": sha256,
                "bytes": str(n_bytes),
                "retrieved_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "schema_version": str(STORE_SCHEMA_VERSION),
            }
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
