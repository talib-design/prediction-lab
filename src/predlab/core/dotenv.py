"""A small, auditable ``.env`` reader.

Deliberately hand-written rather than pulled from a dependency. This is the one place
in the project that touches credentials, and twenty lines that can be read in full are
easier to trust here than a package nobody on this project has audited.

What it supports, which is what a ``.env`` actually contains:

* ``KEY=value``, with optional whitespace around the ``=``
* a leading ``export ``, because people paste shell snippets
* values wrapped in single or double quotes, which are stripped
* ``#`` comments on their own line, and blank lines

What it deliberately does **not** support: multi-line values, variable interpolation,
and escape sequences. If a value needs any of those, it does not belong in a ``.env``.

One rule that matters more than the parsing: **a variable already set in the real
environment wins.** The file is a convenience for a laptop; CI, a container or a
scheduled task set variables properly, and a stale file must never quietly override
them.
"""

from __future__ import annotations

import os
from pathlib import Path

_QUOTES = ("'", '"')


def parse_dotenv(text: str) -> dict[str, str]:
    """Parse ``.env`` content into a mapping. Malformed lines are skipped, not guessed."""
    values: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        key, separator, value = line.partition("=")
        if not separator:
            continue
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in _QUOTES:
            value = value[1:-1]
        values[key] = value
    return values


def load_dotenv(path: Path | None = None, *, environ: dict[str, str] | None = None) -> list[str]:
    """Load ``path`` into the environment and return the names actually set.

    Variables already present are left alone, so the real environment always wins over
    the file. A missing file is not an error: the project runs without credentials for
    everything except the live collector.
    """
    target = environ if environ is not None else os.environ
    location = path or Path(".env")
    if not location.is_file():
        return []
    applied = []
    for key, value in parse_dotenv(location.read_text(encoding="utf-8")).items():
        if key not in target:
            target[key] = value
            applied.append(key)
    return applied
