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
        return self.root / "raw" / "fdj"

    @property
    def processed(self) -> Path:
        return self.root / "processed"

    @property
    def runs(self) -> Path:
        return self.root / "runs"

    @property
    def manifest(self) -> Path:
        return self.raw / "MANIFEST.json"

    @property
    def predictions(self) -> Path:
        return self.root / "predictions.jsonl"

    @property
    def hypotheses(self) -> Path:
        return self.root / "hypotheses.jsonl"

    @property
    def offers(self) -> Path:
        return self.root / "offers.jsonl"

    def ensure(self) -> Paths:
        for directory in (self.raw, self.processed, self.runs):
            directory.mkdir(parents=True, exist_ok=True)
        return self


def default_paths() -> Paths:
    """``$PREDLAB_DATA_DIR`` if set, otherwise ``./data`` next to the working directory."""
    return Paths(Path(os.environ.get(ENV_VAR, "data")).resolve())
