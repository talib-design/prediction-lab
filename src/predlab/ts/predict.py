"""Forward forecasts: the months the source has not published yet.

Two rules separate this from a spreadsheet extrapolation.

**A horizon is only forecast if the backtest showed its interval held.** Producing a
number for a horizon where the stated range covered reality 6 times in 10 instead of
8 is worse than producing nothing: it is a figure carrying a promise the method has
already been measured failing to keep. Such horizons are reported as refused, with
the measurement that refused them.

**The method is chosen by the backtest, per horizon, not picked once.** Different
horizons have different winners on this series -- the calendar-plus-level method
leads one month out, plain persistence five months out -- and pretending otherwise
would mean using a method at a horizon where it was measured to be worse.

Cumulating months needs its own care. Adding the monthly bounds assumes the errors
move together; adding them in quadrature assumes they are independent. Neither is
true, so the cumulative range here is measured instead: the same block length is
walked over the test period and its actual errors are used.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from predlab.data.sources.dares import MonthlySeries, month_index, period_of
from predlab.ts.backtest import BacktestResult
from predlab.ts.forecast import DEFAULT_LEVELS, Forecaster
from predlab.ts.seriesview import build_view

COVERAGE_TOLERANCE = 0.05
"""How far empirical coverage may sit from nominal before a horizon is refused."""


@dataclass(frozen=True, slots=True)
class ForwardForecast:
    """One forecast for one unpublished month, or the refusal to make it."""

    period: str
    horizon: int
    method: str
    method_label: str
    median: float | None
    low: float | None
    high: float | None
    backtest_mae: float
    backtest_coverage: float
    refused: bool
    reason: str = ""

    def payload(self) -> dict[str, object]:
        return {
            "period": self.period,
            "horizon": self.horizon,
            "method": self.method,
            "median": None if self.median is None else round(self.median),
            "low": None if self.low is None else round(self.low),
            "high": None if self.high is None else round(self.high),
            "backtest_mae": round(self.backtest_mae),
            "backtest_coverage": round(self.backtest_coverage, 3),
            "refused": self.refused,
            "reason": self.reason,
        }


def block_error_band(
    result: BacktestResult, block: int, levels: tuple[float, float] = (0.10, 0.90)
) -> tuple[float, float] | None:
    """Empirical error on a sum of ``block`` consecutive months, from the test period.

    Measured rather than derived, because the two available derivations bracket the
    truth from either side: summing the monthly bounds assumes errors move together,
    adding them in quadrature assumes independence, and month-to-month forecast errors
    on this series are neither.
    """
    one = next((r for r in result.results if r.horizon == 1), None)
    if one is None or len(one.actuals) < block * 3:
        return None
    a = np.asarray(one.actuals, dtype=np.float64)
    f = np.asarray(one.medians, dtype=np.float64)
    errors = np.asarray(
        [float(a[i : i + block].sum() - f[i : i + block].sum()) for i in range(len(a) - block + 1)]
    )
    low, high = np.quantile(errors, list(levels))
    return float(low), float(high)


def forward(
    series: MonthlySeries,
    result: BacktestResult,
    forecasters: tuple[Forecaster, ...],
    *,
    until: str,
    levels: tuple[float, ...] = DEFAULT_LEVELS,
) -> list[ForwardForecast]:
    """Forecast every month from just after ``series.end`` through ``until``."""
    by_name = {f.name: f for f in forecasters}
    last = month_index(series.end)
    target = month_index(until)
    if target <= last:
        raise ValueError(f"{until} is already published (series ends {series.end})")

    # A view as_of the first unpublished month contains the whole series and nothing
    # more -- the same object a backtest origin would have produced.
    view = build_view(series, as_of=period_of(last + 1))

    out: list[ForwardForecast] = []
    for h in range(1, target - last + 1):
        period = period_of(last + h)
        ranked = result.for_horizon(h)
        if not ranked:
            out.append(
                ForwardForecast(
                    period,
                    h,
                    "",
                    "",
                    None,
                    None,
                    None,
                    0.0,
                    0.0,
                    True,
                    f"l'horizon {h} n'a pas été évalué",
                )
            )
            continue
        row = ranked[0]
        gap = abs(row.coverage_80.empirical - 0.80)
        if gap > COVERAGE_TOLERANCE:
            out.append(
                ForwardForecast(
                    period,
                    h,
                    row.model,
                    row.model,
                    None,
                    None,
                    None,
                    row.mae,
                    row.coverage_80.empirical,
                    True,
                    f"fourchette non tenue au backtest : "
                    f"{row.coverage_80.empirical:.0%} de couverture pour 80 % annoncés",
                )
            )
            continue
        model = by_name[row.model]
        produced = model.forecast(view, (h,), levels)[0]
        low, high = produced.interval(0.80)
        out.append(
            ForwardForecast(
                period,
                h,
                row.model,
                row.model,
                produced.median(),
                low,
                high,
                row.mae,
                row.coverage_80.empirical,
                False,
            )
        )
    return out
