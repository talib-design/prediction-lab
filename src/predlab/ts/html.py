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
tr.ref td:first-child::after{content:" réf"; color:var(--muted); font-size:11px; font-weight:600;}
code{font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace; color:var(--ink);}

.gauge{width:132px; height:9px; border-radius:999px; background:var(--grid);
  position:relative; display:inline-block; vertical-align:middle;}
.gauge .target{position:absolute; top:-3px; bottom:-3px; width:2px; background:var(--muted);}
.gauge .fill{position:absolute; top:0; bottom:0; left:0; border-radius:999px;}

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


def _horizon_card(block: dict[str, Any]) -> str:
    if block["beats_reference"]:
        verdict = (
            f"<code>{_esc(block['best'])}</code> bat la référence de "
            f"{_fmt_num(block['margin_vs_reference'])} MASE"
        )
    else:
        verdict = f"aucun modèle ne bat la référence <code>{_esc(block['reference'])}</code>"
    calib = block["calibrated_80"]
    pill = (
        '<span class="pill ok"><span class="dot"></span>intervalles calibrés</span>'
        if calib
        else '<span class="pill bad"><span class="dot"></span>intervalles mal calibrés</span>'
    )

    rows = []
    for i, row in enumerate(block["models"]):
        classes = []
        if i == 0:
            classes.append("best")
        if row["model"] == block["reference"]:
            classes.append("ref")
        ok = row["coverage_80_verdict"] == "calibré"
        rows.append(
            f'<tr class="{" ".join(classes)}">'
            f"<td><code>{_esc(row['model'])}</code></td>"
            f'<td class="tabular">{_fmt_num(row["mase"])}</td>'
            f'<td class="tabular">{_fmt_pct(row["mape"])}</td>'
            f'<td class="tabular">{_fmt_pct(row["coverage_80"])}</td>'
            f"<td>{_gauge(row['coverage_80'], 0.80)}</td>"
            f'<td><span class="pill {"ok" if ok else "bad"}"><span class="dot"></span>'
            f"{_esc(row['coverage_80_verdict'])}</span></td>"
            f'<td class="tabular">{_fmt_int(row["coverage_80_width"])}</td></tr>'
        )

    return f"""<article class="hcard">
  <header>
    <h3>Horizon {block["horizon"]} mois</h3>
    <span class="verdict">{block["n"]} prévisions évaluées · {verdict}</span>
    {pill}
  </header>
  <div class="table-scroll"><table>
    <thead><tr>
      <th>modèle</th><th>MASE</th><th>MAPE</th><th>couv. 80 %</th>
      <th>vs&nbsp;nominal</th><th>verdict</th><th>largeur</th>
    </tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table></div>
</article>"""


def _body(report: dict[str, Any]) -> str:
    series = report["series"]
    first = report["horizons"][0]
    best = first["models"][0]
    floor = series["quantisation_floor"]

    tiles = f"""<div class="tiles">
  <div class="tile"><div class="label">Meilleur modèle à 1 mois</div>
    <div class="value"><code style="font-size:19px">{_esc(first["best"])}</code></div>
    <div class="note">MASE {_fmt_num(first["best_mase"])} · référence {_fmt_num(first["reference_mase"])}</div></div>
  <div class="tile"><div class="label">Erreur moyenne à 1 mois</div>
    <div class="value tabular">{_fmt_pct(first["best_mape"])}</div>
    <div class="note">plancher de la donnée : {_fmt_pct(floor, 2)}</div></div>
  <div class="tile"><div class="label">Couverture observée</div>
    <div class="value tabular">{_fmt_pct(best["coverage_80"])}</div>
    <div class="note">pour un intervalle annoncé à 80 %</div></div>
  <div class="tile"><div class="label">Retard de publication</div>
    <div class="value tabular">{series["publication_lag_months"]} mois</div>
    <div class="note">premier mois non publié : {_esc(series["first_unpublished_period"])}</div></div>
</div>"""

    caveats = "".join(f"<li>{_esc(c)}</li>" for c in report["caveats"])
    cards = "".join(_horizon_card(b) for b in report["horizons"])

    return f"""<div class="wrap">
<header>
  <div class="eyebrow">Prediction Lab · backtest</div>
  <h1>Offres cadre collectées&nbsp;: ce que la prévision vaut</h1>
  <p class="sub">Évaluation chronologique de cinq méthodes de référence sur la série
  mensuelle de la DARES. Chaque prévision est faite sans que le modèle ait jamais vu
  le mois qu'il prédit, et chacune annonce son incertitude&nbsp;— que ce tableau vérifie.</p>
  <div class="meta">
    <span><b>{series["n"]}</b> mois · {_esc(series["start"])} → {_esc(series["end"])}</span>
    <span>entraînement ≤ <b>{_esc(report["backtest"]["train_end"])}</b></span>
    <span>{_esc(series["source"])}</span>
    <span>{_esc(series["licence"])}</span>
  </div>
</header>

<section>
  <div class="section-head"><h2>Le verdict</h2>
    <p>Ce qu'il faut lire d'abord, y compris quand la réponse est «&nbsp;pas mieux que
    l'évidence&nbsp;».</p></div>
  {tiles}
</section>

<section>
  <div class="section-head"><h2>La série</h2>
    <p>Trente ans d'offres cadre collectées. La zone teintée n'a jamais servi à
    l'entraînement.</p></div>
  <figure class="chart-card" style="margin:0">
    <div class="legend">
      <span><i class="key" style="background:var(--observed)"></i>offres collectées (mensuel, brut)</span>
      <span><i class="key sq" style="background:var(--band);border:1px solid var(--rule)"></i>période évaluée</span>
    </div>
    {_series_chart(series["periods"], series["values"], report["backtest"]["train_end"])}
    <figcaption>Valeurs publiées arrondies à la centaine. La chute de mars-mai 2020 est
    une rupture de régime, conservée dans l'évaluation.</figcaption>
  </figure>
</section>

<section>
  <div class="section-head"><h2>Par horizon</h2>
    <p>Chaque horizon est un problème distinct&nbsp;: les moyenner produirait un chiffre
    qui ne décrit aucun des deux.</p></div>
  {cards}
</section>

<section>
  <div class="section-head"><h2>Ce qui limite ces chiffres</h2>
    <p>Écrit pendant que le résultat est bon, parce que c'est le seul moment où on
    l'écrit.</p></div>
  <ul class="caveats">{caveats}</ul>
</section>

<footer>
  <span>predlab {_esc(report["code_version"])}</span>
  <span>généré le {_esc(report["generated_at"])}</span>
  <span>MASE&nbsp;1,0 = aussi bon que le naïf saisonnier sur l'entraînement</span>
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
