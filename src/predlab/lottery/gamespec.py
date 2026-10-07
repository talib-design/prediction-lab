"""Game definitions.

A ``GameSpec`` describes the *mechanics* of one lottery era: which pools of numbers
are drawn, how many from each, and on which weekdays. Nothing here is game-specific
code -- Loto, EuroMillions and Keno are all data.

Eras matter. The French Loto has changed format several times, and pooling draws
across a format change is a methodological error, not an approximation. Each era is
therefore a separate ``GameSpec`` and the data store keeps them apart.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

MONDAY, TUESDAY, WEDNESDAY, FRIDAY, SATURDAY = 1, 2, 3, 5, 6


@dataclass(frozen=True, slots=True)
class NumberPool:
    """One pool of integers drawn without replacement.

    ``low`` and ``high`` are inclusive. ``k`` numbers are drawn from the pool.
    """

    name: str
    low: int
    high: int
    k: int

    def __post_init__(self) -> None:
        if self.low < 1:
            raise ValueError(f"{self.name}: low must be >= 1, got {self.low}")
        if self.high < self.low:
            raise ValueError(f"{self.name}: high < low")
        if not 1 <= self.k <= self.size:
            raise ValueError(f"{self.name}: k={self.k} out of range for size {self.size}")

    @property
    def size(self) -> int:
        """Number of distinct values in the pool."""
        return self.high - self.low + 1

    @property
    def marginal_probability(self) -> float:
        """P(a given number is drawn) under a fair mechanism: k / size.

        This constant is the reason match-count metrics are nearly useless for
        comparing models: under uniformity every ticket has the same expected
        number of matches, namely ``k * marginal_probability``.
        """
        return self.k / self.size

    def contains(self, value: int) -> bool:
        return self.low <= value <= self.high

    def validate_combination(self, numbers: tuple[int, ...]) -> None:
        """Raise ``ValueError`` unless ``numbers`` is a legal draw for this pool."""
        if len(numbers) != self.k:
            raise ValueError(f"{self.name}: expected {self.k} numbers, got {len(numbers)}")
        if len(set(numbers)) != self.k:
            raise ValueError(f"{self.name}: numbers must be distinct, got {numbers}")
        out_of_range = [n for n in numbers if not self.contains(n)]
        if out_of_range:
            raise ValueError(f"{self.name}: {out_of_range} outside [{self.low}, {self.high}]")


@dataclass(frozen=True, slots=True)
class GameSpec:
    """One game, in one rule era."""

    game: str
    era: str
    era_start: date
    era_end: date | None
    pools: tuple[NumberPool, ...]
    draw_weekdays: frozenset[int]
    source_verified: bool
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.pools:
            raise ValueError("a game must have at least one pool")
        names = [p.name for p in self.pools]
        if len(set(names)) != len(names):
            raise ValueError(f"duplicate pool names: {names}")
        if not self.draw_weekdays <= frozenset(range(1, 8)):
            raise ValueError("draw_weekdays must be ISO weekdays 1..7")

    @property
    def key(self) -> str:
        """Stable identifier, e.g. ``loto/2019-11``."""
        return f"{self.game}/{self.era}"

    def pool(self, name: str) -> NumberPool:
        for p in self.pools:
            if p.name == name:
                return p
        raise KeyError(f"no pool named {name!r} in {self.key}")

    def covers(self, day: date) -> bool:
        """True if ``day`` falls inside this era's date range."""
        if day < self.era_start:
            return False
        return self.era_end is None or day <= self.era_end


# --------------------------------------------------------------------------------------
# Verified specs
# --------------------------------------------------------------------------------------
# The values below were read from the official FDJ archive on 2026-09-19, not from
# memory: every ball in the 1075 draws of the current-era file lies in [1, 49] and every
# numero_chance in [1, 10]; the weekday column contains exactly MONDAY/WEDNESDAY/SATURDAY.
# See docs/DATA_SOURCES.md for the full provenance record.

LOTO_2019_11 = GameSpec(
    game="loto",
    era="2019-11",
    era_start=date(2019, 11, 4),
    era_end=None,
    pools=(
        NumberPool(name="main", low=1, high=49, k=5),
        NumberPool(name="chance", low=1, high=10, k=1),
    ),
    draw_weekdays=frozenset({MONDAY, WEDNESDAY, SATURDAY}),
    source_verified=True,
    notes=(
        "Mechanics empirically confirmed against the official archive covering "
        "2019-11-06 to 2026-09-16. Earlier eras (1976, 2008, 2017, 2019-02) exist in "
        "the FDJ archive but their mechanics have NOT been verified and are "
        "deliberately not defined here."
    ),
)

# --------------------------------------------------------------------------------------
# EuroMillions (FDJ archive, 6 files downloaded 2026-10-06, 1987 draws 2004-02-13 ->
# 2026-10-06). The star pool changed twice, so pooling across eras would be an error:
#
# * 2004-02 .. 2011-05-06: stars 1-9, Friday only, 12 prize ranks;
# * 2011-05-10 .. 2016-09-23: stars 1-11, Tuesday + Friday, 13 prize ranks;
# * 2016-09-24 on (first draw in the data: Tuesday 2016-09-27): stars 1-12.
#
# Era dates are the *rule* dates (Wikipedia, "EuroMillions"); the data agrees with them:
# no star above 9 before 2011-05-10, none above 11 before 2016-09-27, and the highest
# star of each era is reached (checked by ``verify_era_pools`` at load time).
# --------------------------------------------------------------------------------------

_EM_MAIN = NumberPool(name="main", low=1, high=50, k=5)

EM_2004_02 = GameSpec(
    game="euromillions",
    era="2004-02",
    era_start=date(2004, 2, 13),
    era_end=date(2011, 5, 9),
    pools=(_EM_MAIN, NumberPool(name="stars", low=1, high=9, k=2)),
    draw_weekdays=frozenset({FRIDAY}),
    source_verified=True,
    notes="Friday-only draws. 378 draws in the FDJ file, 2004-02-13 to 2011-05-06.",
)

EM_2011_05 = GameSpec(
    game="euromillions",
    era="2011-05",
    era_start=date(2011, 5, 10),
    era_end=date(2016, 9, 23),
    pools=(_EM_MAIN, NumberPool(name="stars", low=1, high=11, k=2)),
    draw_weekdays=frozenset({TUESDAY, FRIDAY}),
    source_verified=True,
    notes="Tuesday draws added with the 11-star pool. 562 draws, 2011-05-10 to 2016-09-23.",
)

EM_2016_09 = GameSpec(
    game="euromillions",
    era="2016-09",
    era_start=date(2016, 9, 24),
    era_end=None,
    pools=(_EM_MAIN, NumberPool(name="stars", low=1, high=12, k=2)),
    draw_weekdays=frozenset({TUESDAY, FRIDAY}),
    source_verified=True,
    notes="12-star pool, current format. First draw in the data: Tuesday 2016-09-27.",
)

EUROMILLIONS_ERAS: tuple[GameSpec, ...] = (EM_2004_02, EM_2011_05, EM_2016_09)

# Balls-only view over every draw since 2004. The ball pool (5 of 1-50) has not changed,
# so pooling is legitimate *if* the balls behave the same across eras; the analysis
# tests that homogeneity explicitly instead of assuming it. Not a rule era: it is not
# part of EUROMILLIONS_ERAS and never used to partition dates.
EM_MAIN_2004 = GameSpec(
    game="euromillions",
    era="main-2004",
    era_start=date(2004, 2, 13),
    era_end=None,
    pools=(_EM_MAIN,),
    draw_weekdays=frozenset({TUESDAY, FRIDAY}),
    source_verified=True,
    notes="Balls only, all 1987 draws since 2004-02-13 (pooled view, see analysis).",
)

REGISTRY: dict[str, GameSpec] = {
    LOTO_2019_11.key: LOTO_2019_11,
    **{spec.key: spec for spec in EUROMILLIONS_ERAS},
    EM_MAIN_2004.key: EM_MAIN_2004,
}
DEFAULT_ERA: dict[str, str] = {"loto": LOTO_2019_11.era, "euromillions": EM_2016_09.era}


def euromillions_era_for(day: date) -> GameSpec:
    """The EuroMillions era a draw date belongs to.

    Dates before the first draw (2004-02-13) have no era and raise ``ValueError``.
    """
    for spec in EUROMILLIONS_ERAS:
        if spec.covers(day):
            return spec
    raise ValueError(f"no EuroMillions era covers {day}")


def get_spec(game: str, era: str | None = None) -> GameSpec:
    """Look up a verified game spec. Unknown or unverified eras raise ``KeyError``."""
    if era is None:
        try:
            era = DEFAULT_ERA[game]
        except KeyError:
            raise KeyError(f"unknown game {game!r}; known games: {sorted(DEFAULT_ERA)}") from None
    try:
        return REGISTRY[f"{game}/{era}"]
    except KeyError:
        raise KeyError(
            f"no verified spec for {game!r} era {era!r}; known: {sorted(REGISTRY)}"
        ) from None
