"""A forecaster that uses an outside indicator, and the test that judges it.

The model is deliberately the smallest thing that could use the variable at all: take
the best calendar-and-level baseline, and adjust it by how far the business climate
currently sits from its own recent average, scaled by a coefficient fitted on visible
history alone. One parameter. Anything richer would fit noise long before it found
signal, on 139 evaluation points.

Two safeguards are structural rather than advisory.

**Causality, and a correction it forced.** The first version read the climate *of the
month being forecast*. At one month out that is legitimate -- the climate for August is
published on 21 August while DARES has only reached June -- but at six months out it is
not: forecasting January 2027 from a series ending July 2026 would have used January's
climate, which does not exist yet. The backtest would have reported a model that cannot
be run.

The rule that holds at every horizon is the operational one. DARES publishes with a
two-month lag, the climate with none, so at the moment of forecasting the most recent
climate reading available is roughly ``last published DARES month + 2``. Every horizon
therefore uses *that* reading -- the freshest one that will actually exist -- rather
than one chosen relative to the target. At one month out the two coincide; beyond that
they do not, and it is the difference between a measurement and a fiction.

**The fit is inside the loop.** The coefficient is re-estimated at every forecast
origin, from that origin's visible history only. Fitting it once over the whole series
and then "backtesting" would be the ordinary way this kind of result is faked: the
coefficient would already know how the test period turned out.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from predlab.data.sources.dares import MonthlySeries, month_index
from predlab.ts.baselines import NotEnoughHistoryError, _Base
from predlab.ts.forecast import (
    DEFAULT_LEVELS,
    QuantileForecast,
    quantiles_from_relative_residuals,
)
from predlab.ts.seriesview import SEASON, SeriesView

LOOKBACK = 12
"""Months over which the indicator's own reference level is computed."""

PUBLICATION_LEAD = 2
"""How many months ahead of the target series the indicator is available.

DARES publishes with a two-month lag and the business climate with none, so when the
newest DARES figure is for month M, the newest climate reading is for about M+2. This
is the only number that decides which reading a forecast may use, and it is stated
once here rather than assumed at each call site.
"""

MIN_FIT_POINTS = 60
"""Below this, the coefficient is not estimated and the model falls back to its base."""


@dataclass(frozen=True, slots=True)
class Indicator:
    """An exogenous monthly series, addressed by period rather than by index.

    Lookup is by period on purpose: aligning two series by position is how an
    off-by-one becomes a silent one-month look-ahead.
    """

    name: str
    by_period: dict[str, float]

    @classmethod
    def from_series(cls, name: str, series: MonthlySeries, *, scale: float = 0.1) -> Indicator:
        return cls(
            name=name,
            by_period={p: v * scale for p, v in zip(series.periods, series.values, strict=True)},
        )

    def latest_available(self, last_published: str, lead: int) -> str | None:
        """The freshest reading that exists when the target's source is still unpublished.

        ``lead`` is how far ahead of the target series' last published month the
        indicator runs -- two months here, because DARES lags by two and the climate
        does not lag at all. Walking backwards from there means a month the indicator
        has not reached yet degrades to the previous one instead of vanishing.
        """
        idx = month_index(last_published) + lead
        for back in range(lead + 1):
            key = _period(idx - back)
            if key in self.by_period:
                return key
        return None

    def deviation(self, period: str, lookback: int = LOOKBACK) -> float | None:
        """How far the indicator sits above its own average over the previous year.

        Expressed as a deviation rather than a level, because the level of a
        normalised indicator carries no information the seasonal baseline lacks --
        what might carry information is the change.
        """
        idx = month_index(period)
        window = []
        for back in range(1, lookback + 1):
            key = _period(idx - back)
            if key in self.by_period:
                window.append(self.by_period[key])
        here = self.by_period.get(period)
        if here is None or len(window) < lookback:
            return None
        return here - float(np.mean(window))


def _period(idx: int) -> str:
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


@dataclass(frozen=True, slots=True)
class ClimateAdjustedForecaster:
    """``base`` adjusted by the business climate's deviation from its own recent mean.

    ``prediction = base * (1 + beta * deviation)``, with ``beta`` re-fitted at every
    origin by least squares on the base model's own past relative errors against the
    deviation that was observable at the time.
    """

    base: _Base
    indicator: Indicator

    @property
    def name(self) -> str:
        return f"{self.base.name}+climat"

    @property
    def version(self) -> str:
        return "1"

    def _fit(self, view: SeriesView, h: int) -> float:
        """Least-squares coefficient from visible history only. Zero if uninformative.

        Returning exactly zero when there is too little history is what makes this
        model reduce to its base rather than to noise -- and it means a reported gain
        cannot come from the fallback path.
        """
        values = np.asarray(view.values, dtype=np.float64)
        need = self.base._min_history()
        xs: list[float] = []
        ys: list[float] = []
        for cut in range(need, len(values) - h + 1):
            target_idx = month_index(view.start) + cut + h - 1
            target = _period(target_idx)
            # The reading that would have been available at this origin -- not the
            # one belonging to the target month, which at long horizons does not
            # exist yet.
            origin_last = _period(month_index(view.start) + cut - 1)
            asof = self.indicator.latest_available(origin_last, PUBLICATION_LEAD)
            dev = None if asof is None else self.indicator.deviation(asof)
            if dev is None:
                continue
            _ = target
            month = (cut + h - 1) % SEASON + 1
            predicted = self.base._point(values[:cut], h, month)
            if predicted <= 0:
                continue
            xs.append(dev)
            ys.append(float(values[cut + h - 1]) / predicted - 1.0)
        if len(xs) < MIN_FIT_POINTS:
            return 0.0
        x = np.asarray(xs)
        y = np.asarray(ys)
        var = float(np.sum((x - x.mean()) ** 2))
        if var <= 0.0:
            return 0.0
        return float(np.sum((x - x.mean()) * (y - y.mean())) / var)

    def forecast(
        self,
        view: SeriesView,
        horizons: tuple[int, ...],
        levels: tuple[float, ...] = DEFAULT_LEVELS,
    ) -> tuple[QuantileForecast, ...]:
        values = np.asarray(view.values, dtype=np.float64)
        if len(values) < self.base._min_history():
            raise NotEnoughHistoryError(
                f"{self.name} needs at least {self.base._min_history()} observations"
            )
        out: list[QuantileForecast] = []
        for h in horizons:
            period = view.horizon_period(h)
            centre = self.base._point(values, h, view.season_position(h))
            # The freshest reading that exists at forecast time, identical for every
            # horizon. A missing reading means no adjustment, not a guessed one.
            asof = self.indicator.latest_available(view.end, PUBLICATION_LEAD)
            dev = None if asof is None else self.indicator.deviation(asof)
            beta = self._fit(view, h) if dev is not None else 0.0
            adjusted = centre * (1.0 + beta * (dev or 0.0))
            out.append(
                QuantileForecast(
                    period=period,
                    horizon=h,
                    levels=levels,
                    quantiles=quantiles_from_relative_residuals(
                        max(adjusted, 0.0), self.base._insample_ratios(values, h), levels
                    ),
                )
            )
        return tuple(out)
