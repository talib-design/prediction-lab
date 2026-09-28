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
    def audit(self) -> Path:
        return self.root / "audit"

    @property
    def logs(self) -> Path:
        return self.root / "logs"

    @property
    def hypotheses(self) -> Path:
        return self.root / "hypotheses.jsonl"

    def ensure(self) -> Paths:
        for directory in (self.raw_pmu, self.audit, self.logs):
            directory.mkdir(parents=True, exist_ok=True)
        return self


def default_paths() -> Paths:
    """``$PREDLAB_DATA_DIR`` if set, otherwise ``./data`` next to the working directory."""
    return Paths(Path(os.environ.get(ENV_VAR, "data")).resolve())
