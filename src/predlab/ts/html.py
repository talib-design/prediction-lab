"""A readable interface for a backtest report.

This is a dashboard, not a document: it is scanned, not read top to bottom. So the
order is verdict, then evidence, then limits -- and state is encoded in shape as well
as in number, because "78% coverage against a nominal 80%" is a fact the reader has
to compute, while a marker sitting inside a tolerance band is one they can see.

The one chart that earns its place twice is the coverage gauge. Everyone ships a
forecast line; almost nobody ships a picture of whether their stated uncertainty was
honest. That is the differentiator, so it gets the emphasis.

Colours come from the validated categorical palette (blue for observed, orange for
forecast), with the status hues kept deliberately separate so a calibration verdict
can never be mistaken for a data series.
"""

from __future__ import annotations

import html as _html
import json
from typing import Any

PALETTE = {
    "observed": ("#2a78d6", "#3987e5"),
    "forecast": ("#eb6834", "#d95926"),
    "good": ("#0ca30c", "#0ca30c"),
    "warning": ("#fab219", "#fab219"),
    "critical": ("#d03b3b", "#d03b3b"),
}

_STYLE = """
:root{
  color-scheme: light;
  --page:#f4f3ef; --surface:#fcfcfb; --raised:#ffffff;
  --ink:#0b0b0b; --ink-2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --rule:#d8d7cf; --ring:rgba(11,11,11,.10);
  --observed:#2a78d6; --forecast:#eb6834;
  --good:#0ca30c; --warning:#fab219; --critical:#d03b3b;
  --good-ink:#006300; --critical-ink:#a32020;
  --band:rgba(42,120,214,.07);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    color-scheme: dark;
    --page:#0d0d0d; --surface:#1a1a19; --raised:#212120;
    --ink:#ffffff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --rule:#383835; --ring:rgba(255,255,255,.10);
    --observed:#3987e5; --forecast:#d95926;
    --good-ink:#0ca30c; --critical-ink:#e08080;
    --band:rgba(57,135,229,.10);
  }
}
:root[data-theme="dark"]{
  color-scheme: dark;
  --page:#0d0d0d; --surface:#1a1a19; --raised:#212120;
  --ink:#ffffff; --ink-2:#c3c2b7; --muted:#898781;
  --grid:#2c2c2a; --rule:#383835; --ring:rgba(255,255,255,.10);
  --observed:#3987e5; --forecast:#d95926;
  --good-ink:#0ca30c; --critical-ink:#e08080;
  --band:rgba(57,135,229,.10);
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--page); color:var(--ink);
  font:14px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1080px; margin:0 auto; padding-block:40px 64px; padding-left:20px; padding-right:20px;}
h1,h2,h3{font-family:Newsreader,Georgia,"Times New Roman",serif; font-weight:500; margin:0; text-wrap:balance;}
h1{font-size:34px; line-height:1.15; letter-spacing:-.01em;}
h2{font-size:22px; line-height:1.25;}
h3{font-size:16px; font-family:inherit; font-weight:600;}
.eyebrow{
  font-size:11px; letter-spacing:.09em; text-transform:uppercase;
  color:var(--muted); font-weight:600;
}
.sub{color:var(--ink-2); margin-top:10px; max-width:66ch;}
header{border-bottom:1px solid var(--rule); padding-bottom:26px; margin-bottom:30px;}
.meta{display:flex; flex-wrap:wrap; gap:6px 20px; margin-top:16px; font-size:12.5px; color:var(--muted);}
.meta b{color:var(--ink-2); font-weight:600;}

section{margin-top:40px;}
.section-head{display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; margin-bottom:16px;}
.section-head p{margin:0; color:var(--ink-2); font-size:13px;}

.tiles{display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:1px;
  background:var(--rule); border:1px solid var(--rule); border-radius:10px; overflow:hidden;}
.tile{background:var(--surface); padding:18px 18px 16px;}
.tile .label{font-size:12px; color:var(--muted); margin-bottom:8px;}
.tile .value{font-size:30px; line-height:1; font-weight:600; letter-spacing:-.02em;}
.tile .note{font-size:12px; color:var(--ink-2); margin-top:8px;}

.chart-card{background:var(--surface); border:1px solid var(--rule); border-radius:10px; padding:20px 18px 14px;}
.chart-card figcaption{font-size:12.5px; color:var(--ink-2); margin-top:12px;}
.legend{display:flex; gap:18px; flex-wrap:wrap; font-size:12.5px; color:var(--ink-2); margin-bottom:14px;}
.legend span{display:inline-flex; align-items:center; gap:7px;}
.key{width:14px; height:3px; border-radius:2px; display:inline-block;}
.key.sq{width:12px; height:12px; border-radius:3px;}
svg{display:block; width:100%; height:auto;}
.tick{fill:var(--muted); font-size:11px; font-family:system-ui,sans-serif;}
.tabular{font-variant-numeric:tabular-nums;}

.hcard{background:var(--surface); border:1px solid var(--rule); border-radius:10px;
  padding:20px 18px; margin-top:16px;}
.hcard > header{border:0; padding:0; margin:0 0 14px; display:flex; align-items:baseline;
  gap:12px; flex-wrap:wrap;}
.verdict{font-size:13px; color:var(--ink-2);}
.pill{display:inline-flex; align-items:center; gap:6px; font-size:11.5px; font-weight:600;
  padding:3px 9px; border-radius:999px; border:1px solid var(--ring); white-space:nowrap;}
.pill .dot{width:7px; height:7px; border-radius:50%;}
.pill.ok{color:var(--good-ink);} .pill.ok .dot{background:var(--good);}
.pill.bad{color:var(--critical-ink);} .pill.bad .dot{background:var(--critical);}
.pill.warn{color:var(--ink-2);} .pill.warn .dot{background:var(--warning);}

.table-scroll{overflow-x:auto; margin:0 -18px; padding:0 18px;}
table{border-collapse:collapse; width:100%; min-width:560px; font-size:13px;}
th,td{text-align:right; padding:9px 10px; border-bottom:1px solid var(--grid); white-space:nowrap;}
th:first-child,td:first-child{text-align:left; white-space:normal;}
thead th{font-size:11px; letter-spacing:.05em; text-transform:uppercase; color:var(--muted);
  font-weight:600; border-bottom:1px solid var(--rule);}
tbody tr:last-child td{border-bottom:0;}
tr.best td{background:color-mix(in srgb, var(--observed) 6%, transparent);}

code{font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace; color:var(--ink);}

.gauge{width:132px; height:9px; border-radius:999px; background:var(--grid);
  position:relative; display:inline-block; vertical-align:middle;}
.gauge .target{position:absolute; top:-3px; bottom:-3px; width:2px; background:var(--muted);}
.gauge .fill{position:absolute; top:0; bottom:0; left:0; border-radius:999px;}

.headline{margin:0 0 6px; font-size:15px; line-height:1.5; max-width:72ch;}
.headline strong{font-weight:600;}
.promise-line{margin:0 0 18px; font-size:13.5px; color:var(--ink-2); max-width:72ch;}
.promise-line b{color:var(--ink); font-weight:600; font-variant-numeric:tabular-nums;}
.chart-note{margin:10px 0 0; font-size:12.5px; color:var(--muted);}
.key.dashed{background:repeating-linear-gradient(90deg,var(--forecast) 0 5px,transparent 5px 9px)!important;}
details{margin-top:18px; border-top:1px solid var(--grid); padding-top:6px;}
summary{cursor:pointer; font-size:13px; color:var(--ink-2); padding:8px 0; font-weight:500;}
summary:hover{color:var(--ink);}
summary:focus-visible{outline:2px solid var(--observed); outline-offset:3px; border-radius:4px;}
table{min-width:520px;}
table.fwd{min-width:420px; margin-top:16px;}
table.fwd td:first-child{font-weight:600; font-variant-numeric:tabular-nums;}
td.refused{color:var(--muted); font-style:italic; white-space:normal;}
.untrusted{color:var(--muted); text-decoration:underline dotted; text-underline-offset:3px;}
.m-sub.warn{color:var(--critical-ink); white-space:normal; max-width:36ch; margin-left:auto;}
td{vertical-align:top;}
.m-name{font-weight:600; font-size:13.5px;}
.m-explain{font-size:12px; color:var(--muted); margin-top:4px; max-width:40ch; white-space:normal;}
.m-sub{font-size:11.5px; color:var(--muted); margin-top:4px; font-variant-numeric:normal;}
.num{font-size:15px; font-weight:600; white-space:nowrap;}
.unit{font-size:11.5px; font-weight:400; color:var(--muted);}
.promise{font-size:15px; font-weight:600; margin-bottom:5px;}
.tag{font-size:10.5px; font-weight:600; letter-spacing:.04em; text-transform:uppercase;
  color:var(--muted); border:1px solid var(--ring); border-radius:4px; padding:1px 5px;
  margin-left:6px; vertical-align:1px;}
ul.caveats{margin:0; padding:0; list-style:none; display:grid; gap:12px;}
ul.caveats li{padding-left:20px; position:relative; color:var(--ink-2); max-width:78ch;}
ul.caveats li::before{content:""; position:absolute; left:0; top:8px; width:9px; height:2px;
  background:var(--forecast);}
footer{margin-top:48px; padding-top:18px; border-top:1px solid var(--rule);
  font-size:12px; color:var(--muted); display:flex; gap:16px; flex-wrap:wrap;}
@media (max-width:560px){ h1{font-size:27px} .tile .value{font-size:26px} }
@media (prefers-reduced-motion:reduce){ *{transition:none!important; animation:none!important} }
"""


NBSP = "\N{NO-BREAK SPACE}"
THIN = "\N{NARROW NO-BREAK SPACE}"
"""French typography: a non-breaking space before %, a narrow one as the
thousands separator. Named rather than written literally, because in source they
are indistinguishable from an ordinary space."""


def _esc(text: object) -> str:
    return _html.escape(str(text), quote=True)


def _fmt_pct(x: float, digits: int = 1) -> str:
    return f"{x * 100:.{digits}f}".replace(".", ",") + NBSP + "%"


def _fmt_num(x: float, digits: int = 3) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def _fmt_int(x: float) -> str:
    """Thousands separated the French way, applied to one number only.

    Not a replace over a formatted string: the first version of this file ran
    ``.replace(",", THIN)`` across whole SVG and HTML fragments, which turned the
    commas between SVG path coordinates into spaces -- the series line disappeared
    from the chart -- and flattened every decimal comma in the tables.
    """
    return f"{x:,.0f}".replace(",", THIN)


def _series_chart(periods: list[str], values: list[int], train_end: str) -> str:
    """The series, with the evaluated span marked off from the training span.

    One scale, one series, so no legend box is needed for the line itself -- but the
    training/test split is a second encoding and does get a key. The shaded band is
    what stops a reader assuming the whole curve was scored.
    """
    w, h = 1000, 300
    left, right, top, bottom = 52, 14, 16, 30
    iw, ih = w - left - right, h - top - bottom
    n = len(values)
    vmax = max(values)
    # Round the top of the scale up to a clean number so every tick names a real value.
    step = 5000
    top_v = ((vmax // step) + 1) * step

    def x(i: int) -> float:
        return left + (i / max(1, n - 1)) * iw

    def y(v: float) -> float:
        return top + ih - (v / top_v) * ih

    cut = next((i for i, p in enumerate(periods) if p > train_end), n)

    grid, ticks = [], []
    for v in range(0, top_v + 1, step):
        gy = y(v)
        grid.append(
            f'<line x1="{left}" y1="{gy:.1f}" x2="{w - right}" y2="{gy:.1f}" stroke="var(--grid)" stroke-width="1"/>'
        )
        ticks.append(
            f'<text class="tick" x="{left - 9}" y="{gy + 4:.1f}" text-anchor="end">{v // 1000}k</text>'
        )

    xticks = []
    for i, p in enumerate(periods):
        if p.endswith("-01") and int(p[:4]) % 5 == 0:
            xticks.append(
                f'<text class="tick" x="{x(i):.1f}" y="{h - 10}" text-anchor="middle">{p[:4]}</text>'
            )

    path = " ".join(f"{'M' if i == 0 else 'L'}{x(i):.1f},{y(v):.1f}" for i, v in enumerate(values))
    band = ""
    if cut < n:
        band = (
            f'<rect x="{x(cut):.1f}" y="{top}" width="{w - right - x(cut):.1f}" '
            f'height="{ih}" fill="var(--band)"/>'
        )
    last_i, last_v = n - 1, values[-1]
    return f"""<svg viewBox="0 0 {w} {h}" role="img"
  aria-label="Offres cadre collectées par mois, {periods[0]} à {periods[-1]}. Maximum {vmax} en {periods[values.index(vmax)]}.">
  {band}
  {"".join(grid)}
  <line x1="{left}" y1="{y(0):.1f}" x2="{w - right}" y2="{y(0):.1f}" stroke="var(--rule)" stroke-width="1"/>
  {"".join(ticks)}{"".join(xticks)}
  <path d="{path}" fill="none" stroke="var(--observed)" stroke-width="2"
        stroke-linejoin="round" stroke-linecap="round"/>
  <circle cx="{x(last_i):.1f}" cy="{y(last_v):.1f}" r="4.5" fill="var(--observed)"
          stroke="var(--surface)" stroke-width="2"/>
  <text class="tick" x="{x(last_i) - 8:.1f}" y="{y(last_v) - 10:.1f}" text-anchor="end"
        style="fill:var(--ink);font-weight:600">{_fmt_int(last_v)}</text>
</svg>"""


def _gauge(empirical: float, nominal: float) -> str:
    """Observed coverage against the level it claimed, as a position rather than a number."""
    gap = empirical - nominal
    colour = "var(--good)" if abs(gap) <= 0.05 else "var(--critical)"
    return (
        f'<span class="gauge" role="img" aria-label="couverture observée '
        f'{_fmt_pct(empirical)} pour un nominal de {_fmt_pct(nominal, 0)}">'
        f'<span class="fill" style="width:{min(100.0, empirical * 100):.1f}%;background:{colour}"></span>'
        f'<span class="target" style="left:{nominal * 100:.1f}%"></span></span>'
    )


def _trace_chart(trace: dict[str, Any], months: int = 36) -> str:
    """The model at work: what it predicted, what happened, and the range it promised.

    A score tells a reader whether a method is good. This tells them what it *does* --
    and it is the only place in the report where the uncertainty band is visible as a
    shape rather than as a coverage percentage. Limited to the recent span, because
    139 points of band is a smear, not a picture.
    """
    periods = trace["periods"][-months:]
    actual = trace["actuals"][-months:]
    fc = trace["forecast"][-months:]
    low = trace["low"][-months:]
    high = trace["high"][-months:]
    if not periods:
        return ""

    w, h = 1000, 280
    left, right, top, bottom = 56, 14, 14, 32
    iw, ih = w - left - right, h - top - bottom
    n = len(periods)
    vmax = max(max(high), max(actual))
    step = 5000
    top_v = ((int(vmax) // step) + 1) * step

    def x(i: int) -> float:
        return left + (i / max(1, n - 1)) * iw

    def y(v: float) -> float:
        return top + ih - (v / top_v) * ih

    grid, ticks = [], []
    for v in range(0, top_v + 1, step):
        gy = y(v)
        grid.append(
            f'<line x1="{left}" y1="{gy:.1f}" x2="{w - right}" y2="{gy:.1f}" '
            f'stroke="var(--grid)" stroke-width="1"/>'
        )
        ticks.append(
            f'<text class="tick" x="{left - 9}" y="{gy + 4:.1f}" text-anchor="end">'
            f"{v // 1000}k</text>"
        )
    xticks = [
        f'<text class="tick" x="{x(i):.1f}" y="{h - 11}" text-anchor="middle">'
        f"{_esc(p[:4] if p.endswith('-01') else p[5:7])}</text>"
        for i, p in enumerate(periods)
        if p.endswith(("-01", "-07"))
    ]

    band = (
        "M"
        + " L".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(high))
        + " L"
        + " L".join(f"{x(i):.1f},{y(v):.1f}" for i, v in reversed(list(enumerate(low))))
        + " Z"
    )
    line_a = " ".join(
        f"{'M' if i == 0 else 'L'}{x(i):.1f},{y(v):.1f}" for i, v in enumerate(actual)
    )
    line_f = " ".join(f"{'M' if i == 0 else 'L'}{x(i):.1f},{y(v):.1f}" for i, v in enumerate(fc))
    return f"""<svg viewBox="0 0 {w} {h}" role="img"
  aria-label="Prévision contre réalité sur les {n} derniers mois, avec la fourchette annoncée.">
  {"".join(grid)}
  <path d="{band}" fill="var(--forecast)" fill-opacity="0.13"/>
  <line x1="{left}" y1="{y(0):.1f}" x2="{w - right}" y2="{y(0):.1f}" stroke="var(--rule)" stroke-width="1"/>
  {"".join(ticks)}{"".join(xticks)}
  <path d="{line_f}" fill="none" stroke="var(--forecast)" stroke-width="2"
        stroke-linejoin="round" stroke-dasharray="5 4"/>
  <path d="{line_a}" fill="none" stroke="var(--observed)" stroke-width="2"
        stroke-linejoin="round" stroke-linecap="round"/>
</svg>"""


def _projection_chart(
    periods: list[str], values: list[int], forward: list[dict[str, Any]], months: int = 30
) -> str:
    """Where the series is heading: recent history, then the forecast and its range.

    The published series stops two months before the present, so a chart that ends
    there shows the past and calls it a forecast page. The dashed continuation and
    its band are the answer to the only question a reader came with.
    """
    hist_p = periods[-months:]
    hist_v = values[-months:]
    fwd = [f for f in forward if f.get("median") is not None]
    if not fwd:
        return ""

    w, h = 1000, 300
    left, right, top, bottom = 56, 66, 16, 32
    iw, ih = w - left - right, h - top - bottom
    n = len(hist_v) + len(fwd)
    vmax = max([*hist_v, *[f["high"] for f in fwd]])
    step = 5000
    top_v = ((int(vmax) // step) + 1) * step

    def x(i: int) -> float:
        return left + (i / max(1, n - 1)) * iw

    def y(v: float) -> float:
        return top + ih - (v / top_v) * ih

    grid, ticks = [], []
    for v in range(0, top_v + 1, step):
        gy = y(v)
        grid.append(
            f'<line x1="{left}" y1="{gy:.1f}" x2="{w - right}" y2="{gy:.1f}" '
            f'stroke="var(--grid)" stroke-width="1"/>'
        )
        ticks.append(
            f'<text class="tick" x="{left - 9}" y="{gy + 4:.1f}" text-anchor="end">'
            f"{v // 1000}k</text>"
        )
    xticks = [
        f'<text class="tick" x="{x(i):.1f}" y="{h - 11}" text-anchor="middle">'
        f"{_esc(p[:4] if p.endswith('-01') else p[5:7])}</text>"
        for i, p in enumerate([*hist_p, *[f["period"] for f in fwd]])
        if p.endswith(("-01", "-04", "-07", "-10"))
    ]

    j = len(hist_v) - 1  # the forecast starts from the last published point
    fx = [j, *range(len(hist_v), n)]
    highs = [hist_v[-1], *[f["high"] for f in fwd]]
    lows = [hist_v[-1], *[f["low"] for f in fwd]]
    meds = [hist_v[-1], *[f["median"] for f in fwd]]

    band = (
        "M"
        + " L".join(f"{x(i):.1f},{y(v):.1f}" for i, v in zip(fx, highs, strict=True))
        + " L"
        + " L".join(f"{x(i):.1f},{y(v):.1f}" for i, v in reversed(list(zip(fx, lows, strict=True))))
        + " Z"
    )
    hist = " ".join(f"{'M' if i == 0 else 'L'}{x(i):.1f},{y(v):.1f}" for i, v in enumerate(hist_v))
    proj = "M" + " L".join(f"{x(i):.1f},{y(v):.1f}" for i, v in zip(fx, meds, strict=True))
    split = (x(j) + x(j + 1)) / 2
    last = fwd[-1]
    return f"""<svg viewBox="0 0 {w} {h}" role="img"
  aria-label="Historique récent puis projection jusqu'à {_esc(last["period"])}.">
  {"".join(grid)}
  <path d="{band}" fill="var(--forecast)" fill-opacity="0.15"/>
  <line x1="{split:.1f}" y1="{top}" x2="{split:.1f}" y2="{top + ih}"
        stroke="var(--rule)" stroke-width="1" stroke-dasharray="3 3"/>
  <line x1="{left}" y1="{y(0):.1f}" x2="{w - right}" y2="{y(0):.1f}" stroke="var(--rule)" stroke-width="1"/>
  {"".join(ticks)}{"".join(xticks)}
  <path d="{hist}" fill="none" stroke="var(--observed)" stroke-width="2"
        stroke-linejoin="round" stroke-linecap="round"/>
  <path d="{proj}" fill="none" stroke="var(--forecast)" stroke-width="2"
        stroke-linejoin="round" stroke-dasharray="5 4"/>
  <circle cx="{x(j):.1f}" cy="{y(hist_v[-1]):.1f}" r="4.5" fill="var(--observed)"
          stroke="var(--surface)" stroke-width="2"/>
  <circle cx="{x(n - 1):.1f}" cy="{y(last["median"]):.1f}" r="4.5" fill="var(--forecast)"
          stroke="var(--surface)" stroke-width="2"/>
  <text class="tick" x="{x(n - 1) + 10:.1f}" y="{y(last["median"]) + 4:.1f}"
        style="fill:var(--ink);font-weight:600">{_fmt_int(last["median"])}</text>
  <text class="tick" x="{split - 8:.1f}" y="{top + 12}" text-anchor="end">publié</text>
  <text class="tick" x="{split + 8:.1f}" y="{top + 12}">prévu</text>
</svg>"""


def _projection_section(report: dict[str, Any]) -> str:
    fwd = report.get("forward") or []
    cum = report.get("cumulative")
    if not fwd:
        return ""
    series = report["series"]
    rows = []
    for f in fwd:
        if f.get("median") is None:
            rows.append(
                f"<tr><td>{_esc(f['period'])}</td>"
                f'<td colspan="2" class="refused">Non évalué — {_esc(f["reason"])}</td></tr>'
            )
            continue
        if f.get("interval_trusted", True):
            band = (
                f"{_fmt_int(f['low'])}&nbsp;&ndash;&nbsp;{_fmt_int(f['high'])}"
                f'<div class="m-sub">{_esc(f["label"])}</div>'
            )
        else:
            band = (
                f'<span class="untrusted">{_fmt_int(f["low"])}&nbsp;&ndash;&nbsp;'
                f"{_fmt_int(f['high'])}</span>"
                f'<div class="m-sub warn">Fourchette non garantie&nbsp;: '
                f"{_esc(f['reason'])}</div>"
            )
        rows.append(
            f"<tr><td>{_esc(f['period'])}</td>"
            f'<td class="tabular num">{_fmt_int(f["median"])}'
            f'<span class="unit"> offres</span></td>'
            f'<td class="tabular">{band}</td></tr>'
        )

    total = ""
    if cum:
        evol = (cum["total"] / cum["previous_year"] - 1) if cum["previous_year"] else 0.0
        rng = (
            f" (entre {_fmt_int(cum['low'])} et {_fmt_int(cum['high'])})" if cum.get("low") else ""
        )
        total = (
            f'<p class="headline">Sur l\'année {_esc(cum["year"])} entière&nbsp;: '
            f"<strong>{_fmt_int(cum['total'])} offres</strong>{rng}, dont "
            f"{_fmt_int(cum['published'])} déjà publiées sur {cum['published_months']} "
            f"mois. Soit <strong>{_fmt_pct(evol)}</strong> par rapport à "
            f"{int(cum['year']) - 1}.</p>"
        )

    return f"""<section>
  <div class="section-head"><h2>Où va-t-on&nbsp;?</h2>
    <p>La DARES publie avec {series["publication_lag_months"]}&nbsp;mois de retard&nbsp;:
    au moment d'écrire, {_esc(series["first_unpublished_period"])} n'existe pas encore.
    Voici ce que les méthodes en disent.</p></div>
  <figure class="chart-card" style="margin:0">
    <div class="legend">
      <span><i class="key" style="background:var(--observed)"></i>publié par la DARES</span>
      <span><i class="key dashed" style="background:var(--forecast)"></i>prévision</span>
      <span><i class="key sq" style="background:color-mix(in srgb,var(--forecast) 22%,transparent);
        border:1px solid var(--rule)"></i>fourchette 8&nbsp;fois sur&nbsp;10</span>
    </div>
    {_projection_chart(series["periods"], series["values"], fwd)}
  </figure>
  {total}
  <div class="table-scroll"><table class="fwd">
    <thead><tr><th>Mois</th><th>Prévision</th><th>Fourchette</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table></div>
  <p class="chart-note">Ces prévisions sont enregistrées dans un journal inaltérable
  au moment où elles sont faites. Quand la DARES publiera, l'écart sera mesuré et
  ajouté ici&nbsp;— c'est la seule façon de savoir si elles valent quelque chose.</p>
</section>"""


def _horizon_card(block: dict[str, Any]) -> str:
    best = block["models"][0]
    ref = next((m for m in block["models"] if m["is_reference"]), None)

    if block["beats_reference"] and ref is not None:
        gain = ref["mae"] - best["mae"]
        headline = (
            f"<strong>{_esc(best['label'])}</strong> est la meilleure méthode&nbsp;: elle se "
            f"trompe de {_fmt_int(best['mae'])} offres en moyenne, contre "
            f"{_fmt_int(ref['mae'])} pour la méthode de référence — "
            f"{_fmt_int(gain)} offres d'écart."
        )
    else:
        headline = (
            "Aucune méthode ne fait mieux que la référence. À cet horizon, la série "
            "ne contient rien d'exploitable que le calendrier ne donne déjà."
        )

    promise = best["kept_promise"]
    if block["calibrated_80"]:
        pill = '<span class="pill ok"><span class="dot"></span>fourchette honnête</span>'
        promise_line = (
            f"Elle annonce une fourchette censée contenir la réalité <b>8&nbsp;fois sur "
            f"10</b>. Sur {block['n']} mois testés, elle y arrive "
            f"<b>{_fmt_num(promise, 1)}&nbsp;fois sur&nbsp;10</b>."
        )
    else:
        pill = '<span class="pill bad"><span class="dot"></span>fourchette trompeuse</span>'
        promise_line = (
            f"Elle annonce une fourchette censée contenir la réalité <b>8&nbsp;fois sur "
            f"10</b>. Sur {block['n']} mois testés, elle n'y arrive que "
            f"<b>{_fmt_num(promise, 1)}&nbsp;fois sur&nbsp;10</b> — elle se dit plus "
            "précise qu'elle ne l'est."
        )

    rows = []
    for i, row in enumerate(block["models"]):
        ok = row["coverage_80_verdict"] == "calibré"
        tag = ' <span class="tag">référence</span>' if row["is_reference"] else ""
        rows.append(
            f'<tr class="{"best" if i == 0 else ""}">'
            f'<td><div class="m-name">{_esc(row["label"])}{tag}</div>'
            f'<div class="m-explain">{_esc(row["explain"])}</div></td>'
            f'<td class="tabular num">± {_fmt_int(row["mae"])}<span class="unit"> offres</span>'
            f'<div class="m-sub">soit {_fmt_pct(row["mape"])} d\'écart</div></td>'
            f'<td><div class="promise tabular">{_fmt_num(row["kept_promise"], 1)}'
            f'<span class="unit"> / 10</span></div>{_gauge(row["coverage_80"], 0.80)}'
            f'<div class="m-sub">{"tient sa promesse" if ok else "se surestime"}</div></td>'
            "</tr>"
        )

    chart = _trace_chart(block["trace"])
    return f"""<article class="hcard">
  <header>
    <h3>{_esc(block["label"])}</h3>
    {pill}
  </header>
  <p class="headline">{headline}</p>
  <p class="promise-line">{promise_line}</p>
  <div class="legend">
    <span><i class="key" style="background:var(--observed)"></i>offres réellement collectées</span>
    <span><i class="key dashed" style="background:var(--forecast)"></i>prévision de la méthode</span>
    <span><i class="key sq" style="background:color-mix(in srgb,var(--forecast) 20%,transparent);
      border:1px solid var(--rule)"></i>fourchette annoncée</span>
  </div>
  {chart}
  <p class="chart-note">Les 36 derniers mois du test. Le modèle n'a jamais vu le mois
  qu'il prédit.</p>
  <details>
    <summary>Comparer les cinq méthodes</summary>
    <div class="table-scroll"><table>
      <thead><tr>
        <th>Méthode</th><th>Erreur moyenne</th><th>Fourchette tenue</th>
      </tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table></div>
  </details>
</article>"""


def _body(report: dict[str, Any]) -> str:
    series = report["series"]
    first = report["horizons"][0]
    best = first["models"][0]

    last_value = series["values"][-1]
    tiles = f"""<div class="tiles">
  <div class="tile"><div class="label">Dernier chiffre publié</div>
    <div class="value tabular">{_fmt_int(last_value)}</div>
    <div class="note">offres cadre en {_esc(series["end"])}</div></div>
  <div class="tile"><div class="label">Le mois prochain, on se trompe de</div>
    <div class="value tabular">± {_fmt_int(first["best_mae"])}</div>
    <div class="note">offres en moyenne, soit {_fmt_pct(first["best_mape"])}</div></div>
  <div class="tile"><div class="label">La fourchette annoncée est tenue</div>
    <div class="value tabular">{_fmt_num(best["kept_promise"], 1)}<span
      style="font-size:17px;color:var(--ink-2)"> fois sur 10</span></div>
    <div class="note">la méthode en promet 8 sur 10</div></div>
  <div class="tile"><div class="label">Ce chiffre sort avec</div>
    <div class="value tabular">{series["publication_lag_months"]} mois</div>
    <div class="note">de retard — {_esc(series["first_unpublished_period"])} n'est pas
      encore publié</div></div>
</div>"""

    caveats = "".join(f"<li>{_esc(c)}</li>" for c in report["caveats"])
    cards = "".join(_horizon_card(b) for b in report["horizons"])

    return f"""<div class="wrap">
<header>
  <div class="eyebrow">Prediction Lab · backtest</div>
  <h1>Peut-on prévoir le volume d'offres cadre&nbsp;?</h1>
  <p class="sub">Chaque mois, France Travail collecte des offres d'emploi cadre et la
  DARES en publie le compte&nbsp;— avec deux mois de retard. Cette page teste cinq
  façons simples de deviner ce chiffre avant sa publication, et mesure deux choses&nbsp;:
  de combien elles se trompent, et si elles sont honnêtes sur leur propre marge
  d'erreur.</p>
  <div class="meta">
    <span><b>{series["n"]}</b> mois · {_esc(series["start"])} → {_esc(series["end"])}</span>
    <span>entraînement ≤ <b>{_esc(report["backtest"]["train_end"])}</b></span>
    <span>{_esc(series["source"])}</span>
    <span>{_esc(series["licence"])}</span>
  </div>
</header>

<section>
  <div class="section-head"><h2>En bref</h2>
    <p>Les quatre chiffres qui résument le reste de la page.</p></div>
  {tiles}
</section>

<section>
  <div class="section-head"><h2>Ce qu'on cherche à prévoir</h2>
    <p>Le nombre d'offres cadre collectées chaque mois depuis 1996. Sur la zone
    teintée, les méthodes ont été mises à l'épreuve&nbsp;: elles n'avaient accès à
    aucune de ces données.</p></div>
  <figure class="chart-card" style="margin:0">
    <div class="legend">
      <span><i class="key" style="background:var(--observed)"></i>offres cadre collectées, par mois</span>
      <span><i class="key sq" style="background:var(--band);border:1px solid var(--rule)"></i>période de test</span>
    </div>
    {_series_chart(series["periods"], series["values"], report["backtest"]["train_end"])}
    <figcaption>La chute de mars-mai 2020 (11&nbsp;400 → 4&nbsp;600 offres) est le
    confinement. Elle est conservée dans l'évaluation&nbsp;: une méthode doit être jugée
    sur les mois difficiles aussi.</figcaption>
  </figure>
</section>

{_projection_section(report)}

<section>
  <div class="section-head"><h2>Est-ce fiable&nbsp;?</h2>
    <p>Les prévisions ci-dessus ne valent que ce que valent les méthodes qui les
    produisent. Chaque échéance a donc été testée séparément sur les onze dernières
    années&nbsp;— prévoir le mois prochain et prévoir dans un an sont deux problèmes
    différents.</p></div>
  {cards}
</section>

<section>
  <div class="section-head"><h2>Ce que ces chiffres ne disent pas</h2>
    <p>Écrit pendant que le résultat est bon, parce que c'est le seul moment où on
    l'écrit.</p></div>
  <ul class="caveats">{caveats}</ul>
</section>

<footer>
  <span>predlab {_esc(report["code_version"])}</span>
  <span>généré le {_esc(report["generated_at"])}</span>
  <span>«&nbsp;Erreur moyenne&nbsp;» = écart absolu moyen entre la prévision et le
    chiffre réellement publié</span>
</footer>
</div>"""


FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" '
    'href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;'
    '6..72,500;6..72,600&display=swap">'
)


def render_html(report: dict[str, Any], *, standalone: bool = True) -> str:
    """The report as a page.

    ``standalone`` wraps it in a full document for opening from disk. Without it the
    fragment is what an artifact publish expects, which supplies its own skeleton.
    """
    head = f"<title>Prévision des offres cadre</title>{FONT_LINK}<style>{_STYLE}</style>"
    body = _body(report)
    if not standalone:
        return head + body
    return (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"{head}</head><body>{body}</body></html>"
    )


def render_data_json(report: dict[str, Any]) -> str:
    """The report's numbers, for anyone who wants to re-plot them."""
    return json.dumps(report, ensure_ascii=False, indent=2)
