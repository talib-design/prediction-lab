"""End-to-end tests of the thing the project actually claims to do.

Two of these matter more than all the unit tests combined:

* on fair data, the system must conclude that it found nothing;
* on data with a planted bias far above the detection floor, it must find it.

A system that only ever says "no signal" is not careful, it is broken. A system that
finds signal in fair data is worse. Both directions are checked here.
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pytest

from predlab.backtest.engine import BacktestConfig, run_backtest
from predlab.core.gamespec import LOTO_2019_11, GameSpec
from predlab.eval.report import build_report, render_markdown
from predlab.models.baselines import default_baselines
from predlab.models.selection import TopKPolicy

from .conftest import synthetic_draws

START = date(2020, 1, 1)


def biased_draws(
    spec: GameSpec, n: int, rigged_number: int, rate: float, seed: int
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Fair draws, except ``rigged_number`` turns up in a ``rate`` fraction of them."""
    rng = np.random.default_rng(seed)
    dates = np.array(
        [np.datetime64(START + timedelta(days=2 * i), "D") for i in range(n)],
        dtype="datetime64[D]",
    )
    main_pool = spec.pool("main")
    others = np.array([v for v in range(main_pool.low, main_pool.high + 1) if v != rigged_number])
    rows = np.empty((n, main_pool.k), dtype=np.int16)
    for i in range(n):
        if rng.random() < rate:
            rest = rng.choice(others, size=main_pool.k - 1, replace=False)
            rows[i] = np.sort(np.append(rest, rigged_number))
        else:
            rows[i] = np.sort(rng.choice(others, size=main_pool.k, replace=False))
    _, pools = synthetic_draws(spec, n, seed=seed, start=START)
    pools["main"] = rows
    return dates, pools


def evaluate(spec: GameSpec, dates: np.ndarray, pools: dict[str, np.ndarray]) -> dict:
    result = run_backtest(
        spec,
        dates,
        pools,
        default_baselines(spec),
        TopKPolicy(),
        BacktestConfig(min_train_draws=200),
    )
    # Small resample counts: these tests check behaviour, not precision.
    return build_report(
        result, pools, seed=0, n_resamples=250, n_permutations=300, n_simulations=150
    )


def test_fair_data_yields_an_explicit_null_result(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 600, seed=11, start=START)
    report = evaluate(loto, dates, pools)
    assert report["conclusion"]["headline"] == (
        "No statistically meaningful predictive signal was detected."
    )
    assert report["conclusion"]["candidates"] == []
    # The uniformity test's own false-positive rate is checked in test_power.py; a
    # single fair dataset is expected to trip it 5% of the time, so asserting on one
    # here would only produce a flaky test.


def test_the_null_result_is_reported_with_its_power_bound(loto: GameSpec) -> None:
    """A null finding without a detection floor is not a finding."""
    dates, pools = synthetic_draws(loto, 600, seed=12, start=START)
    report = evaluate(loto, dates, pools)
    floor = report["conclusion"]["detection_floor"]["main"]
    assert floor["relative"] > 0
    assert "detection_floor" in report["conclusion"]["caveat"]


def test_a_planted_bias_is_found(loto: GameSpec) -> None:
    """Positive control: the harness must be able to say yes, or its no means nothing."""
    dates, pools = biased_draws(loto, 700, rigged_number=7, rate=0.60, seed=13)
    report = evaluate(loto, dates, pools)
    assert report["descriptive"]["main"]["uniformity_rejected_at_5pct"]
    assert report["descriptive"]["main"]["most_frequent"] == 7
    assert report["conclusion"]["candidates"], "frequency model should beat uniform here"
    assert "candidate finding, not a conclusion" in report["conclusion"]["headline"]


def test_a_model_that_learns_the_bias_puts_mass_on_it(loto: GameSpec) -> None:
    dates, pools = biased_draws(loto, 700, rigged_number=7, rate=0.60, seed=14)
    report = evaluate(loto, dates, pools)
    by_model = {(r["model"], r["pool"]): r for r in report["predictive"]}
    assert by_model[("frequency", "main")]["mass_lift"] > 1.05
    assert by_model[("uniform", "main")]["mass_lift"] == pytest.approx(1.0)


def test_random_and_uniform_stay_indistinguishable(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 500, seed=15, start=START)
    report = evaluate(loto, dates, pools)
    by_model = {(r["model"], r["pool"]): r for r in report["predictive"]}
    assert by_model[("random", "main")]["verdict"] == "indistinguishable"
    assert by_model[("random", "main")]["log_loss"] == by_model[("uniform", "main")]["log_loss"]


def test_observation_and_forecast_are_separate_sections(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 450, seed=16, start=START)
    report = evaluate(loto, dates, pools)
    assert set(report) >= {"power", "descriptive", "predictive", "conclusion", "provenance"}
    assert "counts" in report["descriptive"]["main"]
    assert all("mass_lift" in row for row in report["predictive"])


def test_markdown_renders_power_before_results(loto: GameSpec) -> None:
    dates, pools = synthetic_draws(loto, 450, seed=17, start=START)
    md = render_markdown(evaluate(loto, dates, pools))
    assert md.index("What could have been detected") < md.index("Observation")
    assert md.index("Observation") < md.index("Forecast")
    assert "No statistically meaningful predictive signal was detected." in md


def test_report_is_json_serialisable(loto: GameSpec) -> None:
    import json

    dates, pools = synthetic_draws(LOTO_2019_11, 450, seed=18, start=START)
    report = evaluate(loto, dates, pools)
    assert json.loads(json.dumps(report))["schema"] == "predlab.report.v1"
