"""Synthetic histories whose truth is known by construction.

Every null result this project produces rests on an unstated claim: that the harness
*could* have found a signal if one were there. Until now that claim was supported by a
single crude positive control. This module exists to replace the claim with a
measurement.

Each generator returns a :class:`BenchmarkCase` carrying its own ground truth -- is
there a signal, on which numbers, how large, over which stretch of history, and
crucially whether it is **predictive** of future draws or merely visible in past ones.
Those last two are different questions and the benchmark suite keeps them apart, the
same way the report does.

Exactness matters here. A generator that plants "roughly a 10% bias" cannot calibrate
anything, because the measured detection rate could not be attributed to the planted
effect rather than to the generator's own drift. So biases are planted with a
construction whose inclusion probabilities are exact in closed form.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np

from predlab.core.gamespec import GameSpec, NumberPool

DEFAULT_START = date(2006, 1, 2)


@dataclass(frozen=True, slots=True)
class GroundTruth:
    """What is actually true about a synthetic history.

    ``visible`` and ``predictive`` are deliberately separate. A pattern can be present
    in the history and useless for the next draw -- that is the whole point of the
    seductive-false-pattern family -- and a benchmark that collapsed the two would be
    unable to catch the harness confusing them.
    """

    visible: bool
    predictive: bool
    biased_numbers: tuple[int, ...]
    relative_effect: float
    planted_probability: float | None
    active_from: int | None
    active_until: int | None
    note: str

    @property
    def expected_verdict(self) -> str:
        return "signal" if self.predictive else "no_signal"


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    """A synthetic history plus the answer the harness ought to reach."""

    name: str
    family: str
    spec: GameSpec
    dates: np.ndarray
    pool_draws: dict[str, np.ndarray]
    truth: GroundTruth
    snooped_number: int | None = None

    def __len__(self) -> int:
        return len(self.dates)


def draw_dates(spec: GameSpec, n: int, start: date = DEFAULT_START) -> np.ndarray:
    """``n`` consecutive dates on this game's real draw weekdays."""
    out: list[np.datetime64] = []
    day = start
    while len(out) < n:
        if day.isoweekday() in spec.draw_weekdays:
            out.append(np.datetime64(day, "D"))
        day += timedelta(days=1)
    return np.array(out, dtype="datetime64[D]")


def _fair_rows(pool: NumberPool, n: int, rng: np.random.Generator) -> np.ndarray:
    """``n`` draws of ``k`` distinct numbers, uniformly at random."""
    keys = rng.random((n, pool.size))
    chosen = np.argpartition(keys, pool.k - 1, axis=1)[:, : pool.k]
    return np.sort(chosen, axis=1).astype(np.int16) + pool.low


def _biased_rows(
    pool: NumberPool, n: int, number: int, relative_effect: float, rng: np.random.Generator
) -> tuple[np.ndarray, float]:
    """Draws where ``number`` has an exactly specified inclusion probability.

    Construction: with probability ``p`` include ``number`` and fill the remaining
    ``k - 1`` slots uniformly from the other numbers; otherwise fill all ``k`` slots
    from the other numbers. Then

        P(number drawn) = p                                   exactly,
        P(any other i)  = (k - p) / (size - 1)                exactly,

    and the two sum to ``k`` as they must. Weighted sampling without replacement would
    have been easier to write and would *not* give an exact inclusion probability,
    which would make the resulting power curve uninterpretable.
    """
    if not pool.contains(number):
        raise ValueError(f"{number} is not in pool {pool.name}")
    probability = pool.marginal_probability * (1.0 + relative_effect)
    if not 0.0 < probability < 1.0:
        raise ValueError(f"relative_effect {relative_effect} gives p={probability}")

    others = np.array([v for v in range(pool.low, pool.high + 1) if v != number])
    include = rng.random(n) < probability

    rows = np.empty((n, pool.k), dtype=np.int16)
    keys = rng.random((n, len(others)))
    order = np.argsort(keys, axis=1)
    for i in range(n):
        if include[i]:
            rest = others[order[i, : pool.k - 1]]
            rows[i] = np.sort(np.append(rest, number))
        else:
            rows[i] = np.sort(others[order[i, : pool.k]])
    return rows, probability


def _assemble(
    spec: GameSpec, main_rows: np.ndarray, n: int, rng: np.random.Generator
) -> dict[str, np.ndarray]:
    """Attach fair draws for every pool other than ``main``."""
    pools = {"main": main_rows}
    for pool in spec.pools:
        if pool.name != "main":
            pools[pool.name] = _fair_rows(pool, n, rng)
    return pools


# --------------------------------------------------------------------------------------
# A. Pure randomness
# --------------------------------------------------------------------------------------


def pure_random(spec: GameSpec, n: int, seed: int = 0) -> BenchmarkCase:
    """A fair mechanism. Expected verdict: no signal.

    Run many of these and the rate at which the harness cries signal *is* its
    false-positive rate on realistic data -- a number no amount of reasoning about the
    code can substitute for.
    """
    rng = np.random.default_rng(seed)
    return BenchmarkCase(
        name=f"pure_random_n{n}_s{seed}",
        family="A_pure_random",
        spec=spec,
        dates=draw_dates(spec, n),
        pool_draws=_assemble(spec, _fair_rows(spec.pool("main"), n, rng), n, rng),
        truth=GroundTruth(
            visible=False,
            predictive=False,
            biased_numbers=(),
            relative_effect=0.0,
            planted_probability=None,
            active_from=None,
            active_until=None,
            note="Fair mechanism throughout. Any detection is a false positive.",
        ),
    )


# --------------------------------------------------------------------------------------
# B. Weak hidden signal
# --------------------------------------------------------------------------------------


def weak_bias(
    spec: GameSpec, n: int, relative_effect: float, number: int = 7, seed: int = 0
) -> BenchmarkCase:
    """One number biased by an exactly known relative amount, throughout.

    The workhorse of the suite. Sweeping ``relative_effect`` around the analytic
    detection floor turns the power analysis from algebra into a measured property of
    the instrument.
    """
    rng = np.random.default_rng(seed)
    pool = spec.pool("main")
    rows, probability = _biased_rows(pool, n, number, relative_effect, rng)
    return BenchmarkCase(
        name=f"weak_bias_r{relative_effect:.3f}_n{n}_s{seed}",
        family="B_weak_signal",
        spec=spec,
        dates=draw_dates(spec, n),
        pool_draws=_assemble(spec, rows, n, rng),
        truth=GroundTruth(
            visible=True,
            predictive=True,
            biased_numbers=(number,),
            relative_effect=relative_effect,
            planted_probability=probability,
            active_from=0,
            active_until=n,
            note=(
                f"Number {number} drawn with p={probability:.5f} instead of "
                f"{pool.marginal_probability:.5f}; every other number sits at "
                f"{(pool.k - probability) / (pool.size - 1):.5f}."
            ),
        ),
    )


# --------------------------------------------------------------------------------------
# C. Disappearing signal
# --------------------------------------------------------------------------------------


def disappearing_signal(
    spec: GameSpec,
    n: int,
    relative_effect: float,
    number: int = 7,
    ends_at: float = 0.5,
    seed: int = 0,
) -> BenchmarkCase:
    """A real bias that stops partway through, then never returns.

    Tests whether the harness reports a dead effect as live. A full-history frequency
    model will keep believing in it long after it is gone; a short rolling window
    should recover faster. Neither is "correct" -- what matters is that the report does
    not present a stale effect as a current one.
    """
    rng = np.random.default_rng(seed)
    pool = spec.pool("main")
    cut = int(n * ends_at)
    biased, probability = _biased_rows(pool, cut, number, relative_effect, rng)
    rows = np.vstack([biased, _fair_rows(pool, n - cut, rng)])
    return BenchmarkCase(
        name=f"disappearing_r{relative_effect:.3f}_n{n}_s{seed}",
        family="C_disappearing",
        spec=spec,
        dates=draw_dates(spec, n),
        pool_draws=_assemble(spec, rows, n, rng),
        truth=GroundTruth(
            visible=True,
            predictive=False,
            biased_numbers=(number,),
            relative_effect=relative_effect,
            planted_probability=probability,
            active_from=0,
            active_until=cut,
            note=(
                f"Number {number} biased for the first {cut} draws only. Visible in the "
                "history, useless for the last draw. Claiming predictive power at the "
                "end of this series is the error being tested for."
            ),
        ),
    )


# --------------------------------------------------------------------------------------
# D. Regime change
# --------------------------------------------------------------------------------------


def regime_change(
    spec: GameSpec,
    n: int,
    relative_effect: float,
    before: int = 7,
    after: int = 31,
    switch_at: float = 0.5,
    seed: int = 0,
) -> BenchmarkCase:
    """The bias moves from one number to another partway through.

    Harder than a disappearing signal: a model that averages over all history ends up
    believing in two half-strength biases, neither of which is current. The pooled view
    is wrong in a way that looks like weak evidence for both.
    """
    rng = np.random.default_rng(seed)
    pool = spec.pool("main")
    cut = int(n * switch_at)
    first, probability = _biased_rows(pool, cut, before, relative_effect, rng)
    second, _ = _biased_rows(pool, n - cut, after, relative_effect, rng)
    return BenchmarkCase(
        name=f"regime_change_r{relative_effect:.3f}_n{n}_s{seed}",
        family="D_regime_change",
        spec=spec,
        dates=draw_dates(spec, n),
        pool_draws=_assemble(spec, np.vstack([first, second]), n, rng),
        truth=GroundTruth(
            visible=True,
            predictive=True,
            biased_numbers=(before, after),
            relative_effect=relative_effect,
            planted_probability=probability,
            active_from=cut,
            active_until=n,
            note=(
                f"Number {before} biased for the first {cut} draws, then {after} for the "
                f"rest. Only {after} is predictive at the end; a full-history model will "
                f"split its belief between the two."
            ),
        ),
    )


# --------------------------------------------------------------------------------------
# E. Seductive false pattern
# --------------------------------------------------------------------------------------


def seductive_false_pattern(
    spec: GameSpec, n: int, train_fraction: float = 0.5, seed: int = 0
) -> BenchmarkCase:
    """Entirely fair data, plus the pattern a snooper would have found in it.

    Nothing is planted. The seduction is in the analysis, not the data: the number that
    happened to come up most often in the first half is recorded as ``snooped_number``,
    exactly as an over-eager search would have "discovered" it. In a fair series that
    number carries no information about the second half.

    This is the most direct test of whether the chronological split and the multiplicity
    control do their job, because the tempting finding is generated the same way real
    spurious findings are: by looking.
    """
    rng = np.random.default_rng(seed)
    pool = spec.pool("main")
    rows = _fair_rows(pool, n, rng)
    cut = int(n * train_fraction)
    counts = np.bincount(rows[:cut].ravel() - pool.low, minlength=pool.size)
    snooped = int(np.argmax(counts)) + pool.low
    return BenchmarkCase(
        name=f"seductive_n{n}_s{seed}",
        family="E_seductive",
        spec=spec,
        dates=draw_dates(spec, n),
        pool_draws=_assemble(spec, rows, n, rng),
        truth=GroundTruth(
            visible=False,
            predictive=False,
            biased_numbers=(),
            relative_effect=0.0,
            planted_probability=None,
            active_from=None,
            active_until=None,
            note=(
                f"Fair throughout. Number {snooped} led the first {cut} draws by chance "
                "alone; confirming it on the remainder would be the failure this case "
                "exists to catch."
            ),
        ),
        snooped_number=snooped,
    )
