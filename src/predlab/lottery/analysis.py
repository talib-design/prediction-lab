"""EuroMillions historical analysis: the pre-registered tests of families A, B, C and D3.

Every test here was written down, with its statistic and decision rule, in
:mod:`predlab.lottery.hypotheses_em` before this module was run on the real draws. Each
returns a :class:`TestResult`; nothing prints, nothing decides. Decisions (BH within each
sub-family, confirmation on the later half) are applied by :func:`apply_decisions`.

The central tool for the prediction theories (family B) is :func:`causal_selection_test`.
A rule looks only at draws ``< t`` and puts weights ``w`` on numbers; draw ``t`` is then
independent of ``w`` under H0, so the weighted hit count has an *exact* conditional mean and
variance (a k-subset draw). Summing the centred hits over draws gives a martingale, hence a
z statistic whose null is known without simulation and without any tuning.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field, replace
from datetime import date
from itertools import combinations
from typing import Any

import numpy as np
import polars as pl
from scipy import stats

from predlab.lottery.gamespec import NumberPool
from predlab.lottery.power import fair_null_distribution

SPLIT_DATE = date(2020, 1, 1)  # confirmation half: draws on or after this date
BALLS = NumberPool(name="main", low=1, high=50, k=5)


@dataclass(frozen=True, slots=True)
class TestResult:
    test_id: str
    hypothesis: str
    family: str
    label: str
    n_draws: int
    statistic: float
    p_value: float
    observed: float | None = None
    expected: float | None = None
    note: str = ""
    detail: dict[str, Any] = field(default_factory=dict)
    q_value: float | None = None
    decision: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "test_id": self.test_id,
            "hypothesis": self.hypothesis,
            "family": self.family,
            "label": self.label,
            "n_draws": self.n_draws,
            "statistic": self.statistic,
            "p_value": self.p_value,
            "q_value": self.q_value,
            "observed": self.observed,
            "expected": self.expected,
            "decision": self.decision,
            "note": self.note,
            "detail": self.detail,
        }


# --------------------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class EmData:
    """Everything the analysis needs, as arrays sorted by date."""

    dates: np.ndarray  # datetime64[D]
    era: np.ndarray  # str
    weekday: np.ndarray  # int
    main_order: np.ndarray  # (n, 5) extraction order
    main: np.ndarray  # (n, 5) sorted
    stars: np.ndarray  # (n, 2) sorted
    winners_eu: np.ndarray  # (n, 13) float, nan = rank absent / unknown
    rapports: np.ndarray  # (n, 13) float, nan = nobody won / absent

    @classmethod
    def from_frame(cls, df: pl.DataFrame) -> EmData:
        df = df.sort("draw_date")

        def mat(col: str, width: int, dtype: Any) -> np.ndarray:
            rows = df[col].to_list()
            return np.array(
                [[np.nan if v is None else v for v in r] for r in rows], dtype=dtype
            ).reshape(len(df), width)

        return cls(
            dates=np.array(
                [np.datetime64(d, "D") for d in df["draw_date"].to_list()], dtype="datetime64[D]"
            ),
            era=np.array(df["era"].to_list()),
            weekday=df["weekday"].to_numpy().astype(np.int64),
            main_order=mat("main_order", 5, np.int64),
            main=mat("main_numbers", 5, np.int64),
            stars=mat("stars_numbers", 2, np.int64),
            winners_eu=mat("winners_eu", 13, np.float64),
            rapports=mat("rapports", 13, np.float64),
        )

    def __len__(self) -> int:
        return len(self.dates)

    def subset(self, mask: np.ndarray) -> EmData:
        return EmData(**{f: getattr(self, f)[mask] for f in self.__dataclass_fields__})

    def era_mask(self, era: str) -> np.ndarray:
        return self.era == era

    def later_mask(self) -> np.ndarray:
        return self.dates >= np.datetime64(SPLIT_DATE, "D")


def incidence(draws: np.ndarray, pool: NumberPool) -> np.ndarray:
    """``(n, size)`` 0/1 matrix: which numbers came out in each draw."""
    n = len(draws)
    out = np.zeros((n, pool.size), dtype=np.int8)
    out[np.repeat(np.arange(n), pool.k), (draws - pool.low).ravel()] = 1
    return out


# --------------------------------------------------------------------------------------
# Family A -- the mechanism
# --------------------------------------------------------------------------------------


def uniformity_test(
    draws: np.ndarray,
    pool: NumberPool,
    *,
    test_id: str,
    label: str,
    n_simulations: int = 20_000,
    seed: int = 0,
) -> TestResult:
    """A1: Pearson chi-square on counts, Monte-Carlo null of the real k-subset mechanism.

    The scaled asymptotic p-value (X² / ((N-k)/(N-1)) ~ chi²(N-1)) is reported alongside as
    a cross-check; the decision uses the Monte-Carlo one, as pre-registered.
    """
    n = len(draws)
    counts = incidence(draws, pool).sum(axis=0)
    expected = n * pool.marginal_probability
    x2 = float(np.sum((counts - expected) ** 2) / expected)
    scale = (pool.size - pool.k) / (pool.size - 1)
    p_asym = float(stats.chi2.sf(x2 / scale, pool.size - 1))
    if n_simulations > 0:
        null = fair_null_distribution(pool, n, n_simulations=n_simulations, seed=seed)
        p_mc = (int((null >= x2).sum()) + 1) / (n_simulations + 1)
    else:  # control runs only (em-R2): asymptotic p, as registered
        p_mc = p_asym
    dev = (counts - expected) / expected
    return TestResult(
        test_id=test_id,
        hypothesis="em-A1",
        family="A1",
        label=label,
        n_draws=n,
        statistic=x2,
        p_value=p_mc,
        observed=float(np.max(np.abs(dev))),
        expected=None,
        note="observed = plus grand écart relatif d'un numéro à sa fréquence attendue",
        detail={
            "p_asymptotic_scaled": p_asym,
            "n_simulations": n_simulations,
            "expected_per_number": expected,
            "counts": {int(pool.low + i): int(c) for i, c in enumerate(counts)},
        },
    )


def per_number_tests(
    draws: np.ndarray, pool: NumberPool, *, prefix: str, what: str
) -> list[TestResult]:
    """A2: exact two-sided binomial test per number (count ~ Bin(n, k/N) under H0)."""
    n = len(draws)
    counts = incidence(draws, pool).sum(axis=0)
    p0 = pool.marginal_probability
    out = []
    for i, c in enumerate(counts):
        number = pool.low + i
        res = stats.binomtest(int(c), n, p0)
        out.append(
            TestResult(
                test_id=f"A2/{prefix}/{number}",
                hypothesis="em-A2",
                family="A2",
                label=f"{what} {number} ({prefix})",
                n_draws=n,
                statistic=float((c - n * p0) / math.sqrt(n * p0 * (1 - p0))),
                p_value=float(res.pvalue),
                observed=float(c),
                expected=n * p0,
            )
        )
    return out


def position_tests(main_order: np.ndarray) -> list[TestResult]:
    """A3: the ball drawn in position j is uniform on 1..50 (chi², 49 df) with mean 25.5."""
    n = len(main_order)
    out = []
    var_one = (50**2 - 1) / 12
    for j in range(main_order.shape[1]):
        col = main_order[:, j]
        counts = np.bincount(col - 1, minlength=50)
        e = n / 50
        x2 = float(np.sum((counts - e) ** 2) / e)
        out.append(
            TestResult(
                test_id=f"A3/position{j + 1}/uniformity",
                hypothesis="em-A3",
                family="A3",
                label=f"position {j + 1} : uniformité",
                n_draws=n,
                statistic=x2,
                p_value=float(stats.chi2.sf(x2, 49)),
            )
        )
        mean = float(col.mean())
        z = (mean - 25.5) / math.sqrt(var_one / n)
        out.append(
            TestResult(
                test_id=f"A3/position{j + 1}/mean",
                hypothesis="em-A3",
                family="A3",
                label=f"position {j + 1} : moyenne",
                n_draws=n,
                statistic=z,
                p_value=float(2 * stats.norm.sf(abs(z))),
                observed=mean,
                expected=25.5,
            )
        )
    return out


def homogeneity_test(
    draws: np.ndarray,
    labels: np.ndarray,
    pool: NumberPool,
    *,
    test_id: str,
    label: str,
    n_permutations: int = 10_000,
    seed: int = 0,
) -> TestResult:
    """A4: chi² of homogeneity between groups of draws; null by permuting group labels."""
    x = incidence(draws, pool).astype(np.float64)
    groups, codes = np.unique(labels, return_inverse=True)
    col_tot = x.sum(axis=0)
    n = len(x)

    def stat(c: np.ndarray) -> float:
        onehot = np.zeros((len(groups), n))
        onehot[c, np.arange(n)] = 1.0
        table = onehot @ x
        n_g = onehot.sum(axis=1)[:, None]
        expected = n_g * col_tot[None, :] / n
        mask = expected > 0
        return float(np.sum((table[mask] - expected[mask]) ** 2 / expected[mask]))

    observed = stat(codes)
    rng = np.random.default_rng(seed)
    hits = sum(stat(rng.permutation(codes)) >= observed for _ in range(n_permutations))
    return TestResult(
        test_id=test_id,
        hypothesis="em-A4",
        family="A4",
        label=label,
        n_draws=n,
        statistic=observed,
        p_value=(hits + 1) / (n_permutations + 1),
        detail={"groups": {str(g): int((codes == i).sum()) for i, g in enumerate(groups)}},
    )


# --------------------------------------------------------------------------------------
# Family B -- prediction theories, tested causally
# --------------------------------------------------------------------------------------

Rule = Callable[[np.ndarray, int], np.ndarray]
"""``rule(X, t)`` -> weights in [0, 1] per number, using only rows ``X[:t]``."""


def top_weights(score: np.ndarray, m: int) -> np.ndarray:
    """Weights selecting the ``m`` highest scores; ties at the boundary share the rest.

    Fractional ties keep the rule deterministic without an arbitrary tie-break (lowest
    number first would quietly favour low numbers).
    """
    order = np.sort(score)[::-1]
    v = order[m - 1]
    above = score > v
    tied = score == v
    w = above.astype(np.float64)
    remaining = m - int(above.sum())
    w[tied] = remaining / int(tied.sum())
    return w


def hot_rule(window: int, m: int) -> Rule:
    def rule(x: np.ndarray, t: int) -> np.ndarray:
        return top_weights(x[t - window : t].sum(axis=0).astype(np.float64), m)

    return rule


def cold_rule(window: int, m: int) -> Rule:
    def rule(x: np.ndarray, t: int) -> np.ndarray:
        return top_weights(-x[t - window : t].sum(axis=0).astype(np.float64), m)

    return rule


def repeat_rule() -> Rule:
    def rule(x: np.ndarray, t: int) -> np.ndarray:
        return x[t - 1].astype(np.float64)

    return rule


def neighbour_rule() -> Rule:
    def rule(x: np.ndarray, t: int) -> np.ndarray:
        last = x[t - 1].astype(bool)
        near = np.zeros_like(last)
        near[1:] |= last[:-1]
        near[:-1] |= last[1:]
        return (near & ~last).astype(np.float64)

    return rule


def current_gaps(x: np.ndarray, t: int) -> np.ndarray:
    """Draws since each number last appeared, counting back from ``t - 1`` (0 = just out)."""
    seen = x[:t][::-1]
    has = seen.any(axis=0)
    first = np.argmax(seen, axis=0)
    return np.where(has, first, t).astype(np.float64)


def gap_top_rule(m: int) -> Rule:
    def rule(x: np.ndarray, t: int) -> np.ndarray:
        return top_weights(current_gaps(x, t), m)

    return rule


def gap_at_least_rule(threshold: int) -> Rule:
    def rule(x: np.ndarray, t: int) -> np.ndarray:
        return (current_gaps(x, t) >= threshold).astype(np.float64)

    return rule


@dataclass(frozen=True, slots=True)
class SelectionStats:
    hits: float
    expected: float
    variance: float
    n_draws: int

    @property
    def z(self) -> float:
        return (self.hits - self.expected) / math.sqrt(self.variance) if self.variance > 0 else 0.0

    @property
    def p_value(self) -> float:
        return float(2 * stats.norm.sf(abs(self.z)))

    @property
    def ratio(self) -> float:
        return self.hits / self.expected if self.expected > 0 else float("nan")


def selection_stats(
    x: np.ndarray, pool: NumberPool, rule: Rule, start: int, mask: np.ndarray | None = None
) -> SelectionStats:
    """Weighted hits of a causal rule versus their exact null moments.

    Under H0 draw ``t`` is a uniform k-subset independent of ``w_t``, so
    ``E[w·x_t] = p Σw`` and ``Var[w·x_t] = p(1-p) N/(N-1) (Σw² - (Σw)²/N)``.
    """
    p = pool.marginal_probability
    n_num = pool.size
    c = p * (1 - p) * n_num / (n_num - 1)
    hits = expected = variance = 0.0
    used = 0
    for t in range(start, len(x)):
        if mask is not None and not mask[t]:
            continue
        w = rule(x, t)
        sw = float(w.sum())
        if sw == 0:
            continue
        hits += float(w @ x[t])
        expected += p * sw
        variance += c * (float(w @ w) - sw * sw / n_num)
        used += 1
    return SelectionStats(hits=hits, expected=expected, variance=variance, n_draws=used)


def causal_selection_test(
    draws: np.ndarray,
    pool: NumberPool,
    rule: Rule,
    *,
    start: int,
    later: np.ndarray,
    test_id: str,
    hypothesis: str,
    label: str,
) -> TestResult:
    """B: z test of a causal selection rule, with the two halves reported for confirmation."""
    x = incidence(draws, pool)
    whole = selection_stats(x, pool, rule, start)
    early = selection_stats(x, pool, rule, start, ~later)
    late = selection_stats(x, pool, rule, start, later)
    return TestResult(
        test_id=test_id,
        hypothesis=hypothesis,
        family="B",
        label=label,
        n_draws=whole.n_draws,
        statistic=whole.z,
        p_value=whole.p_value,
        observed=whole.hits,
        expected=whole.expected,
        note="observed/expected = sorties pondérées des numéros sélectionnés",
        detail={
            "ratio": whole.ratio,
            "variance": whole.variance,
            # smallest ratio detectable 80 % of the time at 5 % two-sided (no correction)
            "detectable_ratio": 1 + 2.8016 * math.sqrt(whole.variance) / whole.expected
            if whole.expected > 0
            else float("nan"),
            "early": {"n": early.n_draws, "z": early.z, "p": early.p_value, "ratio": early.ratio},
            "late": {"n": late.n_draws, "z": late.z, "p": late.p_value, "ratio": late.ratio},
        },
    )


def family_b(data: EmData) -> list[TestResult]:
    out: list[TestResult] = []
    later = data.later_mask()
    for w in (20, 50, 100, 300):
        out.append(
            causal_selection_test(
                data.main,
                BALLS,
                hot_rule(w, 10),
                start=300,
                later=later,
                test_id=f"B1/balls/hot{w}",
                hypothesis="em-B1",
                label=f"boules chaudes : 10 plus sorties sur {w} tirages",
            )
        )
    for w in (20, 50, 100, 300):
        out.append(
            causal_selection_test(
                data.main,
                BALLS,
                cold_rule(w, 10),
                start=300,
                later=later,
                test_id=f"B2/balls/cold{w}",
                hypothesis="em-B2",
                label=f"boules froides : 10 moins sorties sur {w} tirages",
            )
        )
    out.append(
        causal_selection_test(
            data.main,
            BALLS,
            repeat_rule(),
            start=300,
            later=later,
            test_id="B3/balls/repeat",
            hypothesis="em-B3",
            label="série : boules du tirage précédent",
        )
    )
    out.append(
        causal_selection_test(
            data.main,
            BALLS,
            neighbour_rule(),
            start=300,
            later=later,
            test_id="B3/balls/neighbours",
            hypothesis="em-B3",
            label="série : voisins ±1 des boules du tirage précédent",
        )
    )
    out.append(
        causal_selection_test(
            data.main,
            BALLS,
            gap_top_rule(10),
            start=300,
            later=later,
            test_id="B4/balls/gap-top10",
            hypothesis="em-B4",
            label="retard : 10 boules au plus long retard",
        )
    )
    out.append(
        causal_selection_test(
            data.main,
            BALLS,
            gap_at_least_rule(20),
            start=300,
            later=later,
            test_id="B4/balls/gap-ge20",
            hypothesis="em-B4",
            label="retard : boules absentes depuis au moins 20 tirages",
        )
    )
    era = data.subset(data.era_mask("2016-09"))
    stars = NumberPool(name="stars", low=1, high=12, k=2)
    later_e = era.later_mask()
    for w in (20, 50, 100):
        out.append(
            causal_selection_test(
                era.stars,
                stars,
                hot_rule(w, 3),
                start=100,
                later=later_e,
                test_id=f"B1/stars/hot{w}",
                hypothesis="em-B1",
                label=f"étoiles chaudes : 3 plus sorties sur {w} tirages (2016-09)",
            )
        )
    for w in (20, 50, 100):
        out.append(
            causal_selection_test(
                era.stars,
                stars,
                cold_rule(w, 3),
                start=100,
                later=later_e,
                test_id=f"B2/stars/cold{w}",
                hypothesis="em-B2",
                label=f"étoiles froides : 3 moins sorties sur {w} tirages (2016-09)",
            )
        )
    out.append(
        causal_selection_test(
            era.stars,
            stars,
            repeat_rule(),
            start=100,
            later=later_e,
            test_id="B3/stars/repeat",
            hypothesis="em-B3",
            label="série : étoiles du tirage précédent (2016-09)",
        )
    )
    out.append(
        causal_selection_test(
            era.stars,
            stars,
            gap_top_rule(3),
            start=100,
            later=later_e,
            test_id="B4/stars/gap-top3",
            hypothesis="em-B4",
            label="retard : 3 étoiles au plus long retard (2016-09)",
        )
    )
    return out


# --------------------------------------------------------------------------------------
# Family C -- shape of the draws
# --------------------------------------------------------------------------------------


def all_combinations(size: int = 50, k: int = 5) -> np.ndarray:
    return np.array(list(combinations(range(1, size + 1), k)), dtype=np.int16)


def _consecutive_pairs(s: np.ndarray) -> np.ndarray:
    return (np.diff(s, axis=1) == 1).sum(axis=1)


def _distinct(values: np.ndarray) -> np.ndarray:
    srt = np.sort(values, axis=1)
    return 1 + (np.diff(srt, axis=1) != 0).sum(axis=1)


SHAPE_STATS: dict[str, tuple[str, Callable[[np.ndarray], np.ndarray]]] = {
    "sum": ("somme des 5 boules", lambda s: s.sum(axis=1)),
    "odd": ("nombre de boules impaires", lambda s: (s % 2 == 1).sum(axis=1)),
    "low": ("nombre de boules <= 25", lambda s: (s <= 25).sum(axis=1)),
    "consecutive": ("nombre de paires consécutives", _consecutive_pairs),
    "decades": ("dizaines distinctes", lambda s: _distinct((s - 1) // 10)),
    "last_digits": ("derniers chiffres distincts", lambda s: _distinct(s % 10)),
    "range": ("étendue max-min", lambda s: s.max(axis=1) - s.min(axis=1)),
}


def exact_pmf(values: np.ndarray) -> dict[int, float]:
    support, counts = np.unique(values, return_counts=True)
    total = counts.sum()
    return {int(v): float(c) / float(total) for v, c in zip(support, counts, strict=True)}


def bins_from_pmf(pmf: dict[int, float], n: int, *, target_bins: int = 20) -> list[list[int]]:
    """Group adjacent support points: about ``target_bins`` classes, each expected >= 5."""
    support = sorted(pmf)
    quantum = max(1.0 / target_bins, 5.0 / n)
    bins: list[list[int]] = [[]]
    acc = 0.0
    for v in support:
        bins[-1].append(v)
        acc += pmf[v]
        if acc >= quantum:
            bins.append([])
            acc = 0.0
    if not bins[-1]:
        bins.pop()
    # merge a too-small tail into its neighbour
    while len(bins) > 1 and sum(pmf[v] for v in bins[-1]) * n < 5:
        tail = bins.pop()
        bins[-1].extend(tail)
    return bins


def gof_test(
    observed_values: np.ndarray, pmf: dict[int, float], *, test_id: str, label: str, hypothesis: str
) -> TestResult:
    n = len(observed_values)
    bins = bins_from_pmf(pmf, n)
    obs = np.array([np.isin(observed_values, b).sum() for b in bins], dtype=np.float64)
    exp = np.array([n * sum(pmf[v] for v in b) for b in bins])
    x2 = float(np.sum((obs - exp) ** 2 / exp))
    df = len(bins) - 1
    mean_null = sum(v * p for v, p in pmf.items())
    return TestResult(
        test_id=test_id,
        hypothesis=hypothesis,
        family=test_id.split("/")[0],
        label=label,
        n_draws=n,
        statistic=x2,
        p_value=float(stats.chi2.sf(x2, df)),
        observed=float(np.mean(observed_values)),
        expected=float(mean_null),
        note="observed/expected = moyennes ; test sur toute la distribution",
        detail={"bins": len(bins), "df": df},
    )


def family_c(data: EmData, combos: np.ndarray | None = None) -> list[TestResult]:
    combos = all_combinations() if combos is None else combos
    out = []
    for key, (label, fn) in SHAPE_STATS.items():
        out.append(
            gof_test(
                fn(data.main),
                exact_pmf(fn(combos)),
                test_id=f"C1/balls/{key}",
                label=label,
                hypothesis="em-C1",
            )
        )
    era = data.subset(data.era_mask("2016-09"))
    star_combos = all_combinations(12, 2)
    out.append(
        gof_test(
            era.stars.sum(axis=1),
            exact_pmf(star_combos.sum(axis=1)),
            test_id="C1/stars/sum",
            label="somme des 2 étoiles (2016-09)",
            hypothesis="em-C1",
        )
    )
    consec = int((np.diff(era.stars, axis=1)[:, 0] == 1).sum())
    p_consec = 11 / 66
    res = stats.binomtest(consec, len(era), p_consec)
    out.append(
        TestResult(
            test_id="C1/stars/consecutive",
            hypothesis="em-C1",
            family="C1",
            label="étoiles consécutives (2016-09)",
            n_draws=len(era),
            statistic=float(consec),
            p_value=float(res.pvalue),
            observed=float(consec),
            expected=len(era) * p_consec,
        )
    )
    out.append(repeated_combinations(data.main, data.dates))
    out += serial_tests(data.main.sum(axis=1).astype(np.float64))
    return out


def repeated_combinations(main: np.ndarray, dates: np.ndarray | None = None) -> TestResult:
    """C2: pairs of draws with the same 5 balls versus Poisson(C(n,2)/C(50,5))."""
    n = len(main)
    keys = [tuple(r) for r in np.sort(main, axis=1).tolist()]
    _, counts = np.unique(np.array(keys), axis=0, return_counts=True)
    where: dict[tuple[int, ...], list[str]] = {}
    for i, key in enumerate(keys):
        where.setdefault(key, []).append(str(dates[i]) if dates is not None else str(i))
    repeated = [{"balls": list(k), "dates": v} for k, v in where.items() if len(v) > 1]
    pairs = int(sum(c * (c - 1) // 2 for c in counts))
    lam = n * (n - 1) / 2 / math.comb(50, 5)
    # pairs sharing exactly 4 balls (context only)
    four: dict[tuple[int, ...], int] = {}
    for r in keys:
        for sub in combinations(r, 4):
            four[sub] = four.get(sub, 0) + 1
    share4 = sum(c * (c - 1) // 2 for c in four.values()) - 5 * pairs
    p4 = 5 * 45 / math.comb(50, 5)
    return TestResult(
        test_id="C2/balls/repeats",
        hypothesis="em-C2",
        family="C2",
        label="paires de tirages aux 5 mêmes boules",
        n_draws=n,
        statistic=float(pairs),
        p_value=float(stats.poisson.sf(pairs - 1, lam)),
        observed=float(pairs),
        expected=lam,
        detail={
            "distinct_combinations": len(counts),
            "repeated": repeated,
            "pairs_sharing_exactly_4": share4,
            "expected_pairs_sharing_4": n * (n - 1) / 2 * p4,
        },
    )


def serial_tests(series: np.ndarray, max_lag: int = 10) -> list[TestResult]:
    """C3: lag-1 autocorrelation and Ljung-Box Q(10) on the sum of the balls."""
    n = len(series)
    x = series - series.mean()
    denom = float(x @ x)
    r = np.array([float(x[k:] @ x[:-k]) / denom for k in range(1, max_lag + 1)])
    z1 = (r[0] + 1 / n) * math.sqrt(n)
    q = float(n * (n + 2) * np.sum(r**2 / (n - np.arange(1, max_lag + 1))))
    return [
        TestResult(
            test_id="C3/balls/sum-lag1",
            hypothesis="em-C3",
            family="C3",
            label="autocorrélation de la somme (rang 1)",
            n_draws=n,
            statistic=z1,
            p_value=float(2 * stats.norm.sf(abs(z1))),
            observed=float(r[0]),
            expected=-1 / n,
        ),
        TestResult(
            test_id="C3/balls/sum-ljungbox10",
            hypothesis="em-C3",
            family="C3",
            label="Ljung-Box sur la somme (rangs 1-10)",
            n_draws=n,
            statistic=q,
            p_value=float(stats.chi2.sf(q, max_lag)),
            detail={"autocorrelations": [float(v) for v in r]},
        ),
    ]


# --------------------------------------------------------------------------------------
# Family A assembly
# --------------------------------------------------------------------------------------

ERAS = (("2004-02", 9), ("2011-05", 11), ("2016-09", 12))


def family_a(
    data: EmData, *, n_simulations: int = 20_000, n_permutations: int = 10_000
) -> list[TestResult]:
    out = [
        uniformity_test(
            data.main,
            BALLS,
            test_id="A1/balls/all",
            label="boules, tous tirages",
            n_simulations=n_simulations,
        )
    ]
    for era, top in ERAS:
        sub = data.subset(data.era_mask(era))
        out.append(
            uniformity_test(
                sub.main,
                BALLS,
                test_id=f"A1/balls/{era}",
                label=f"boules, époque {era}",
                n_simulations=n_simulations,
                seed=1,
            )
        )
        stars = NumberPool(name="stars", low=1, high=top, k=2)
        out.append(
            uniformity_test(
                sub.stars,
                stars,
                test_id=f"A1/stars/{era}",
                label=f"étoiles 1-{top}, époque {era}",
                n_simulations=n_simulations,
                seed=2,
            )
        )
    out += per_number_tests(data.main, BALLS, prefix="all", what="boule")
    for era, top in ERAS:
        sub = data.subset(data.era_mask(era))
        stars = NumberPool(name="stars", low=1, high=top, k=2)
        out += per_number_tests(sub.stars, stars, prefix=era, what="étoile")
    out += position_tests(data.main_order)
    out.append(
        homogeneity_test(
            data.main,
            data.era,
            BALLS,
            test_id="A4/balls/eras",
            label="boules : mêmes fréquences dans les 3 époques",
            n_permutations=n_permutations,
        )
    )
    for era, top in ERAS[1:]:
        sub = data.subset(data.era_mask(era))
        out.append(
            homogeneity_test(
                sub.main,
                sub.weekday,
                BALLS,
                test_id=f"A4/balls/weekday-{era}",
                label=f"boules : mardi = vendredi ({era})",
                n_permutations=n_permutations,
            )
        )
        stars = NumberPool(name="stars", low=1, high=top, k=2)
        out.append(
            homogeneity_test(
                sub.stars,
                sub.weekday,
                stars,
                test_id=f"A4/stars/weekday-{era}",
                label=f"étoiles : mardi = vendredi ({era})",
                n_permutations=n_permutations,
            )
        )
    return out


# --------------------------------------------------------------------------------------
# Decisions
# --------------------------------------------------------------------------------------


def bh_adjust(p_values: Sequence[float]) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values (q-values), step-up, independent form."""
    p = np.asarray(p_values, dtype=np.float64)
    m = len(p)
    order = np.argsort(p)
    ranked = p[order] * m / np.arange(1, m + 1)
    adj = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(m)
    out[order] = np.minimum(adj, 1.0)
    return out


def apply_decisions(results: list[TestResult], q: float = 0.05) -> list[TestResult]:
    """BH within each sub-family; family B/C effects also need the later half to agree."""
    out: list[TestResult] = []
    families = sorted({r.family for r in results})
    for fam in families:
        group = [r for r in results if r.family == fam]
        qs = bh_adjust([r.p_value for r in group])
        for r, qv in zip(group, qs, strict=True):
            if qv >= q:
                decision = "rien de détecté"
            elif fam == "B":
                late = r.detail["late"]
                same_sign = np.sign(late["z"]) == np.sign(r.statistic)
                decision = (
                    "signal confirmé sur la 2e moitié"
                    if same_sign and late["p"] < 0.05
                    else "signal non confirmé sur la 2e moitié"
                )
            else:
                decision = "écart détecté"
            out.append(replace(r, q_value=float(qv), decision=decision))
    return out


def multiplicity_summary(results: list[TestResult]) -> dict[str, dict[str, float]]:
    """Per family: tests run, nominal p < 0.05, expected by chance, BH survivors."""
    summary: dict[str, dict[str, float]] = {}
    for fam in sorted({r.family for r in results}):
        group = [r for r in results if r.family == fam]
        summary[fam] = {
            "tests": len(group),
            "nominal_p_lt_0_05": sum(r.p_value < 0.05 for r in group),
            "expected_by_chance": 0.05 * len(group),
            "bh_survivors": sum((r.q_value or 1.0) < 0.05 for r in group),
        }
    return summary


# --------------------------------------------------------------------------------------
# Whole battery, and the pure-chance control (em-R2)
# --------------------------------------------------------------------------------------


def run_battery(
    data: EmData,
    *,
    n_simulations: int = 20_000,
    n_permutations: int = 10_000,
    combos: np.ndarray | None = None,
) -> list[TestResult]:
    """Families A, B and C on one history, decisions applied."""
    results = family_a(data, n_simulations=n_simulations, n_permutations=n_permutations)
    results += family_b(data)
    results += family_c(data, combos)
    return apply_decisions(results)


def fair_history(data: EmData, rng: np.random.Generator) -> EmData:
    """Same dates, eras and weekdays as ``data``, numbers drawn 100 % at random."""
    n = len(data)
    order = np.argsort(rng.random((n, 50)), axis=1)[:, :5] + 1
    stars = np.empty((n, 2), dtype=np.int64)
    for era, top in ERAS:
        mask = data.era == era
        m = int(mask.sum())
        stars[mask] = np.argsort(rng.random((m, top)), axis=1)[:, :2] + 1
    return EmData(
        dates=data.dates,
        era=data.era,
        weekday=data.weekday,
        main_order=order.astype(np.int64),
        main=np.sort(order, axis=1).astype(np.int64),
        stars=np.sort(stars, axis=1),
        winners_eu=np.full_like(data.winners_eu, np.nan),
        rapports=np.full_like(data.rapports, np.nan),
    )


@dataclass(frozen=True, slots=True)
class ControlVerdict:
    histories: int
    tests_per_history: int
    nominal_rate: float
    histories_with_survivor: dict[str, float]
    ks_p_family_b: float
    passed: bool
    reasons: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "histories": self.histories,
            "tests_per_history": self.tests_per_history,
            "nominal_rate": self.nominal_rate,
            "histories_with_survivor": self.histories_with_survivor,
            "ks_p_family_b": self.ks_p_family_b,
            "passed": self.passed,
            "reasons": self.reasons,
        }


def control_chunk(
    data: EmData,
    indices: range,
    *,
    seed: int = 20261006,
    combos: np.ndarray | None = None,
    progress: Callable[[int], None] | None = None,
) -> dict[str, Any]:
    """em-R2 on synthetic histories ``indices`` (history h uses seed ``[seed, h]``).

    Split in chunks so the control can run in short sessions; :func:`judge_control`
    merges the chunks. Same seeds -> same histories, whatever the chunking.
    """
    combos = all_combinations() if combos is None else combos
    all_p: list[float] = []
    b_p: list[float] = []
    survivors: dict[str, int] = {}
    n_tests = 0
    for h in indices:
        fake = fair_history(data, np.random.default_rng([seed, h]))
        res = run_battery(fake, n_simulations=0, n_permutations=1_000, combos=combos)
        n_tests = len(res)
        all_p += [r.p_value for r in res]
        b_p += [r.p_value for r in res if r.family == "B"]
        for fam in sorted({r.family for r in res}):
            hit = any((r.q_value or 1.0) < 0.05 for r in res if r.family == fam)
            survivors[fam] = survivors.get(fam, 0) + int(hit)
        if progress:
            progress(h)
    return {
        "seed": seed,
        "start": indices.start,
        "stop": indices.stop,
        "histories": len(indices),
        "n_tests": n_tests,
        "p_values": all_p,
        "b_p_values": b_p,
        "survivors": survivors,
    }


def judge_control(chunks: Sequence[dict[str, Any]]) -> ControlVerdict:
    """Apply the registered em-R2 criteria to merged chunks."""
    covered = sorted(i for c in chunks for i in range(c["start"], c["stop"]))
    if len(covered) != len(set(covered)):
        raise ValueError("overlapping control chunks")
    histories = len(covered)
    all_p = np.array([p for c in chunks for p in c["p_values"]])
    b_p = [p for c in chunks for p in c["b_p_values"]]
    fams = sorted({f for c in chunks for f in c["survivors"]})
    surv = {f: sum(c["survivors"].get(f, 0) for c in chunks) / histories for f in fams}
    rate = float(np.mean(all_p < 0.05))
    ks = float(stats.kstest(b_p, "uniform").pvalue)
    reasons = []
    if not 0.03 <= rate <= 0.07:
        reasons.append(f"part globale de p < 0,05 = {rate:.3f}, hors [0,03 ; 0,07]")
    for fam, frac in surv.items():
        if frac > 0.08:
            reasons.append(f"sous-famille {fam} : {frac:.1%} des historiques avec un survivant BH")
    if ks <= 0.01:
        reasons.append(f"p de la famille B non uniformes (KS p = {ks:.4f})")
    return ControlVerdict(
        histories=histories,
        tests_per_history=int(chunks[0]["n_tests"]) if chunks else 0,
        nominal_rate=rate,
        histories_with_survivor=surv,
        ks_p_family_b=ks,
        passed=not reasons,
        reasons=reasons,
    )


# --------------------------------------------------------------------------------------
# D3 -- popularity of numbers and payouts (exploratory, not part of the R2 battery)
# --------------------------------------------------------------------------------------


def popularity_tests(
    era: EmData, *, threshold: int = 31, min_coverage: float = 0.95
) -> list[TestResult]:
    """log(rapport of rank r) regressed on the number of balls <= ``threshold``.

    Under "players favour dates", a draw with many low balls has more winners per rank,
    hence a lower payout per winner. Ranks whose payout is missing in more than 5 % of
    draws are skipped. OLS slope with its classical standard error; Spearman's rho is
    reported as a check that does not assume linearity.
    """
    low = (era.main <= threshold).sum(axis=1).astype(np.float64)
    out = []
    for rank in range(2, 14):
        y = era.rapports[:, rank - 1]
        ok = np.isfinite(y) & (y > 0)
        if ok.mean() < min_coverage:
            continue
        x, ly = low[ok], np.log(y[ok])
        design = np.column_stack([np.ones_like(x), x])
        beta, *_ = np.linalg.lstsq(design, ly, rcond=None)
        resid = ly - design @ beta
        n = len(ly)
        sigma2 = float(resid @ resid) / (n - 2)
        se = math.sqrt(sigma2 / float(((x - x.mean()) ** 2).sum()))
        t = float(beta[1] / se)
        sp = stats.spearmanr(x, ly)
        rho, rho_p = float(sp[0]), float(sp[1])  # type: ignore[arg-type]
        out.append(
            TestResult(
                test_id=f"D3/rank{rank}",
                hypothesis="em-D3",
                family="D3",
                label=f"rang {rank} : rapport selon le nombre de boules <= {threshold}",
                n_draws=n,
                statistic=t,
                p_value=float(2 * stats.t.sf(abs(t), n - 2)),
                observed=float(math.expm1(beta[1])),
                expected=0.0,
                note="observed = variation relative du rapport par boule <= 31 en plus",
                detail={"spearman_rho": rho, "spearman_p": rho_p},
            )
        )
    return out
