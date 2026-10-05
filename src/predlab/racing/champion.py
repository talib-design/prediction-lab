"""The objective, the champion model and its challengers (docs/METHODOLOGY.md §13).

Objective, fixed on 2026-10-05 (decision of Chris): **beat the favourite by predicting
better**. Concretely, on the same races, the model's pick returns more per euro staked
than the favourite does, in simple gagnant and simple placé.

How a version of the model replaces the one in service:

1. the lab tests one candidate at a time against the champion on the *test* window
   (filter 1: prediction, filter 2: money -- the challenger's pick returns more than the
   champion's, which is "beats the favourite by more" since the favourite term cancels);
2. a candidate that passes both is tried once on the *vault*: races no test has used.
   It is promoted if it still predicts better there and does not lose money against
   the champion. Each attempt consumes the vault: the next attempt waits for fresh races;
3. the promoted version becomes the carnet's "modèle"; the version it replaced keeps
   playing beside it ("ancien modèle"), so the two are compared live on the same races.

A playing rule (bet only when a horse is mispriced: p × odds ≥ 1.05) is judged against
the favourite directly, on the test window then on the vault; one that passes is added
to the carnet as its own line ("valeur modèle").

Windows. The extended history (2020 onwards, decision of 2026-10-05) is used once it is
in place for a discipline: train 2020-2023, validation 2024 (λ), test 2025-01-01 →
2026-03-31, vault from 2026-04-01. Until then nothing new is tested for that discipline.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from predlab.racing.features import MODEL_FEATURES

OBJECTIVE = (
    "Battre le favori en prévoyant mieux : sur les mêmes courses, le cheval choisi par le "
    "modèle rapporte plus, par euro misé, que le favori, en simple gagnant et en simple placé."
)

EXTENDED_START = date(2020, 1, 1)
VAULT_START = date(2026, 4, 1)
VAULT_MIN_RACES = 600
VALUE_EDGE = 1.05


@dataclass(frozen=True)
class Window:
    since: date
    train_end: date
    validation_end: date
    test_end: date
    vault_start: date
    vault_min_races: int = VAULT_MIN_RACES


EXTENDED = Window(
    since=EXTENDED_START,
    train_end=date(2023, 12, 31),
    validation_end=date(2024, 12, 31),
    test_end=date(2026, 3, 31),
    vault_start=VAULT_START,
)


YEARS = (2020, 2021, 2022, 2023)
SHARE = 0.6


# Before the extended history is in place: the model's own split (2024), enough to fit
# the champion the value rule needs; the rule is judged on fresh races anyway.
BASE = Window(
    since=date(2024, 1, 1),
    train_end=date(2024, 6, 30),
    validation_end=date(2024, 12, 31),
    test_end=date(2026, 3, 31),
    vault_start=VAULT_START,
)


def history_coverage(db_path: Path, discipline: str) -> dict[str, Any]:
    """Races per year 2020-2024 and whether the extended history is in place: every year
    2020-2023 must hold at least 60 % of the races of 2024 (2020 had fewer races:
    lockdown). The first race in the base proves nothing: the 2026-09-28 audit stored
    scattered days back to 2013."""
    import duckdb

    per_year: dict[int, int] = {}
    if db_path.exists():
        con = duckdb.connect(str(db_path), read_only=True)
        try:
            rows = con.execute(
                "SELECT year(day), count(*) FROM races WHERE is_final AND country_code = 'FRA' "
                "AND discipline = ? AND year(day) BETWEEN ? AND 2024 GROUP BY 1",
                [discipline, min(YEARS)],
            ).fetchall()
        finally:
            con.close()
        per_year = {int(y): int(n) for y, n in rows}
    ref = per_year.get(2024, 0)
    return {
        "reference_2024": ref,
        "years": {str(y): per_year.get(y, 0) for y in YEARS},
        "share": SHARE,
        "ready": ref > 0 and all(per_year.get(y, 0) >= SHARE * ref for y in YEARS),
    }


def history_ready(db_path: Path, discipline: str) -> bool:
    return bool(history_coverage(db_path, discipline)["ready"])


def races_since(db_path: Path, discipline: str, start: date) -> int:
    """Finished races of the discipline from ``start`` (the vault's supply)."""
    import duckdb

    if not db_path.exists():
        return 0
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        row = con.execute(
            "SELECT count(*) FROM races WHERE is_final AND country_code = 'FRA' "
            "AND discipline = ? AND day >= ?",
            [discipline, start],
        ).fetchone()
    finally:
        con.close()
    return int(row[0]) if row else 0


# --------------------------------------------------------------------------- the store


def _v1() -> dict[str, Any]:
    return {
        "version": 1,
        "features": list(MODEL_FEATURES),
        "tau": 1.0,
        "promoted_at": None,
        "origin": "Marché+ v1 (11 facteurs pré-enregistrés le 2026-09-30)",
        "evidence": None,
    }


class Champion:
    """``data/lab/champion_<DISCIPLINE>.json``: the versions in order, the vault's use,
    the playing rules admitted to the carnet. Written only by the lab."""

    def __init__(self, path: Path, discipline: str, data: dict[str, Any] | None = None):
        self.path = path
        self.discipline = discipline
        self.data = data or {
            "discipline": discipline,
            "objective": OBJECTIVE,
            "versions": [_v1()],
            "attempts": [],
            "vault_used_until": None,
            "rules": [],
        }

    @classmethod
    def load(cls, lab_dir: Path, discipline: str) -> Champion:
        path = lab_dir / f"champion_{discipline}.json"
        if path.exists():
            return cls(path, discipline, json.loads(path.read_text(encoding="utf-8")))
        return cls(path, discipline)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(self.path)

    @property
    def current(self) -> dict[str, Any]:
        return self.data["versions"][-1]

    @property
    def previous(self) -> dict[str, Any] | None:
        return self.data["versions"][-2] if len(self.data["versions"]) > 1 else None

    @property
    def features(self) -> tuple[str, ...]:
        return tuple(self.current["features"])

    @property
    def tau(self) -> float:
        return float(self.current.get("tau", 1.0))

    @property
    def rules(self) -> list[str]:
        return list(self.data.get("rules", []))

    def vault_start(self, window: Window) -> date:
        used = self.data.get("vault_used_until")
        if used is None:
            return window.vault_start
        return max(window.vault_start, date.fromordinal(date.fromisoformat(used).toordinal() + 1))

    def record_attempt(
        self,
        experiment: str,
        vault: tuple[date, date],
        result: dict[str, Any],
        passed: bool,
        now: datetime,
    ) -> None:
        self.data["attempts"].append(
            {
                "experiment": experiment,
                "at": now.isoformat(timespec="seconds"),
                "vault": [vault[0].isoformat(), vault[1].isoformat()],
                "passed": passed,
                "result": result,
            }
        )
        self.data["vault_used_until"] = vault[1].isoformat()

    def promote(
        self,
        *,
        features: tuple[str, ...],
        tau: float,
        origin: str,
        evidence: dict[str, Any],
        now: datetime,
        params_before: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Append the new version. ``params_before``: the fitted parameters of the version
        being replaced, frozen, so it can keep playing beside the new one."""
        if params_before is not None:
            self.current["frozen_params"] = params_before
        new = {
            "version": self.current["version"] + 1,
            "features": list(features),
            "tau": tau,
            "promoted_at": now.isoformat(timespec="seconds"),
            "origin": origin,
            "evidence": evidence,
        }
        self.data["versions"].append(new)
        return new

    def admit_rule(self, rule: str) -> None:
        if rule not in self.data.setdefault("rules", []):
            self.data["rules"].append(rule)
