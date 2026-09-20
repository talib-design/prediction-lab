"""Forward forecasts: the months the source has not published yet.

Two rules separate this from a spreadsheet extrapolation.

**A range is only promised where the backtest showed the promise was kept.** The
refusal applies to the interval, not to the point. A first version refused the whole
forecast, which produced an inconsistency visible the moment the page was drawn:
November 2026 vanished from the monthly table and therefore from the annual total,
silently understating the year by a whole month. Either a month is forecast or it is
not -- dropping it from one figure while the reader assumes it is in another is the
worst of both. So the point is always produced, the interval carries
``interval_trusted``, and the reader is told which months' ranges are not guaranteed.

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
from datetime import UTC, datetime

import numpy as np

from predlab import __version__
from predlab.core.hashing import AppendOnlyLedger
from predlab.data.sources.dares import MonthlySeries, month_index, period_of
from predlab.ts.backtest import BacktestResult
from predlab.ts.forecast import DEFAULT_LEVELS, Forecaster
from predlab.ts.seriesview import build_view

COVERAGE_TOLERANCE = 0.05
"""How far empirical coverage may sit from nominal before its range is untrusted."""


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
    interval_trusted: bool = True
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
            "interval_trusted": self.interval_trusted,
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
                    interval_trusted=False,
                    reason=f"l'horizon {h} n'a pas été évalué",
                )
            )
            continue
        row = ranked[0]
        model = by_name[row.model]
        produced = model.forecast(view, (h,), levels)[0]
        low, high = produced.interval(0.80)
        trusted = abs(row.coverage_80.empirical - 0.80) <= COVERAGE_TOLERANCE
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
                interval_trusted=trusted,
                reason=""
                if trusted
                else (
                    "au backtest, cette échéance n'a tenu sa fourchette que "
                    f"{row.coverage_80.empirical * 10:.1f} fois sur 10 au lieu de 8"
                ),
            )
        )
    return out


# --------------------------------------------------------------- recording & scoring


class HindsightError(ValueError):
    """Refused to record a "forecast" about a month the source has already published."""


def record(
    ledger: AppendOnlyLedger,
    forecasts: list[ForwardForecast],
    series: MonthlySeries,
    *,
    train_end: str,
    now: datetime | None = None,
) -> int:
    """Write forecasts to the append-only ledger, refusing any that are not forward.

    A forecast only means something if it was written down before the answer was
    available. The ledger is hash-chained and append-only, so a forecast cannot be
    quietly improved after the fact -- and a "forecast" about an already-published
    month is refused outright rather than recorded with a caveat, because a caveat is
    something a later reader can overlook.

    Forecasts whose range is not trusted are recorded too, flagged. A system that
    kept only the predictions it was confident about would show a flattering track
    record made of easy months.
    """
    published = month_index(series.end)
    moment = now or datetime.now(UTC)
    written = 0
    for f in forecasts:
        if month_index(f.period) <= published:
            raise HindsightError(
                f"{f.period} is already published in the series (it ends {series.end}); "
                "recording it as a forecast would be recording a known answer"
            )
        ledger.append(
            {
                **f.payload(),
                "created_at": moment.isoformat(timespec="seconds"),
                "series_end": series.end,
                "train_end": train_end,
                "code_version": __version__,
            }
        )
        written += 1
    return written


@dataclass(frozen=True, slots=True)
class ScoredForecast:
    """A recorded forecast, compared with the value the source published since."""

    period: str
    horizon: int
    method: str
    forecast: float
    low: float
    high: float
    actual: float
    created_at: str

    @property
    def error(self) -> float:
        """Signed: positive means the forecast was too low."""
        return self.actual - self.forecast

    @property
    def absolute_pct(self) -> float:
        return abs(self.error) / self.actual if self.actual else float("nan")

    @property
    def inside(self) -> bool:
        return self.low <= self.actual <= self.high


def score(
    ledger: AppendOnlyLedger, series: MonthlySeries
) -> tuple[list[ScoredForecast], list[dict[str, object]]]:
    """Match recorded forecasts against what has been published since.

    Returns the scored ones and those still waiting for their month. A record with no
    point at all (an unevaluated horizon) carries nothing to score and is skipped, but
    it stays in the ledger, so the record shows what the system declined to predict as
    well as what it got right.
    """
    published = dict(zip(series.periods, series.values, strict=True))
    scored: list[ScoredForecast] = []
    pending: list[dict[str, object]] = []
    for row in ledger.records():
        period = str(row.get("period", ""))
        if row.get("median") is None:
            continue
        actual = published.get(period)
        if actual is None:
            pending.append(row)
            continue
        scored.append(
            ScoredForecast(
                period=period,
                horizon=int(row["horizon"]),
                method=str(row.get("method", "")),
                forecast=float(row["median"]),
                low=float(row["low"]),
                high=float(row["high"]),
                actual=float(actual),
                created_at=str(row.get("created_at", "")),
            )
        )
    return scored, pending


@dataclass(frozen=True, slots=True)
class Scoreboard:
    """The forward track record, in the same terms the backtest reports."""

    n: int
    mae: float = 0.0
    mape: float = 0.0
    bias: float = 0.0
    kept_promise: float = 0.0
    first: str = ""
    last: str = ""


def scoreboard(scored: list[ScoredForecast]) -> Scoreboard:
    """The track record in the same terms the backtest used, so the two compare.

    The backtest says how a method behaved on history. This says how it behaved on
    months nobody had seen when the forecast was written. When the two disagree, the
    second one is right.
    """
    if not scored:
        return Scoreboard(n=0)
    errors = np.asarray([s.error for s in scored], dtype=np.float64)
    return Scoreboard(
        n=len(scored),
        mae=float(np.mean(np.abs(errors))),
        mape=float(np.mean([s.absolute_pct for s in scored])),
        bias=float(np.mean(errors)),
        kept_promise=float(np.mean([s.inside for s in scored]) * 10.0),
        first=min(s.period for s in scored),
        last=max(s.period for s in scored),
    )
