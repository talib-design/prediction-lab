"""Where things live on disk.

One place, so that a test can redirect everything with an environment variable and
nothing writes into the repository by accident.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ENV_VAR = "PREDLAB_DATA_DIR"


@dataclass(frozen=True, slots=True)
class Paths:
    root: Path

    @property
    def raw(self) -> Path:
        """Raw captures, one sub-folder per source. Never committed: see DATA_SOURCES.md."""
        return self.root / "raw"

    @property
    def raw_pmu(self) -> Path:
        return self.raw / "pmu"

    @property
    def normalized(self) -> Path:
        """Typed tables rebuilt from raw. Contain PMU data: never committed."""
        return self.root / "normalized"

    @property
    def database(self) -> Path:
        return self.root / "racing.duckdb"

    @property
    def runs(self) -> Path:
        """Backtest reports: aggregates only, safe to commit."""
        return self.root / "runs"

    @property
    def audit(self) -> Path:
        return self.root / "audit"

    @property
    def logs(self) -> Path:
        return self.root / "logs"

    @property
    def hypotheses(self) -> Path:
        return self.root / "hypotheses.jsonl"

    @property
    def carnet(self) -> Path:
        """Live paper-betting ledger: our decisions only, hash-chained, safe to commit."""
        return self.root / "carnet.jsonl"

    @property
    def banc(self) -> Path:
        """Strategy bench: its panel of strategies and its own live ledger (decisions only)."""
        return self.root / "banc"

    @property
    def lab(self) -> Path:
        """The lab: pre-registered criterion tests and studies (our outputs only)."""
        return self.root / "lab"

    @property
    def raw_euromillions(self) -> Path:
        """FDJ EuroMillions archives. Never committed (reuse terms unknown)."""
        return self.raw / "euromillions_fdj"

    @property
    def euromillions_store(self) -> Path:
        return self.normalized / "euromillions_draws.parquet"

    @property
    def manifests(self) -> Path:
        """Provenance of raw archives (URL, SHA-256, rows): metadata only, safe to commit."""
        return self.root / "manifests"

    @property
    def lottery(self) -> Path:
        """EuroMillions forward ledger and reports: our own outputs, safe to commit."""
        return self.root / "lottery"

    def ensure(self) -> Paths:
        for directory in (self.raw_pmu, self.audit, self.logs):
            directory.mkdir(parents=True, exist_ok=True)
        return self


def default_paths() -> Paths:
    """``$PREDLAB_DATA_DIR`` if set, otherwise ``./data`` next to the working directory."""
    return Paths(Path(os.environ.get(ENV_VAR, "data")).resolve())
