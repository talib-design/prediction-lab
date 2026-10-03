import { type ReactNode, useEffect, useMemo, useRef, useState } from "react";
import { api, type CarnetSeries } from "../lib/api";
import { euros, shortDay } from "../lib/format";
import { useApi } from "../lib/hooks";
import { Segmented } from "./ui";

/** Running total of fictitious bets, one point per day: favourite vs Marché+.
 *
 *  - main lines: favourite solid, model dashed and drawn on top, so when the model picks the
 *    favourite (identical results) both stay visible instead of one hiding the other;
 *  - optional overlay (thin dotted, same colours): the same two picks recalculated on every
 *    race. It covers many more races, so with it the scale switches to return on stakes (%);
 *  - optional period selector, stock-chart style: the totals restart at the window's start. */

type Mode = "ALL" | "SG" | "SP";
type Pick = "favori" | "modèle";
type Range = "1w" | "1m" | "3m" | "6m" | "1y" | "all";

const PICKS = [
  { pick: "favori", label: "Favori", color: "var(--series-favori)", dash: undefined },
  { pick: "modèle", label: "Modèle", color: "var(--series-model)", dash: "7 5" },
] as const;

const RANGES: { value: Range; label: string; days: number }[] = [
  { value: "1w", label: "1S", days: 7 },
  { value: "1m", label: "1M", days: 31 },
  { value: "3m", label: "3M", days: 92 },
  { value: "6m", label: "6M", days: 183 },
  { value: "1y", label: "1A", days: 366 },
  { value: "all", label: "Tout", days: Infinity },
];

const MONTHS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."];

type Point = { day: string; races: number; stake: number; net: number; cum: number; cumStake: number };
type Lines = Record<Pick, Point[]>;

const signed = (x: number) => `${x >= 0 ? "+" : "−"}${euros(Math.abs(x))}`;
const signedPct = (x: number) => `${x >= 0 ? "+" : "−"}${Math.abs(x).toFixed(1).replace(".", ",")} %`;
const DAY_MS = 86_400_000;
const dayNum = (d: string) => Date.parse(`${d}T00:00:00Z`) / DAY_MS;

/** One line per pick for the chosen bet type ("ALL" adds win and place day by day), from
 *  ``from`` on, with running totals restarting there. */
function lines(series: CarnetSeries[], mode: Mode, from: string | null): Lines {
  const out: Lines = { favori: [], modèle: [] };
  for (const pick of ["favori", "modèle"] as const) {
    const byDay = new Map<string, Point>();
    for (const s of series) {
      if (s.pick !== pick || (mode !== "ALL" && s.bet !== mode)) continue;
      for (const p of s.points) {
        if (from && p.day < from) continue;
        const d = byDay.get(p.day) ?? { day: p.day, races: 0, stake: 0, net: 0, cum: 0, cumStake: 0 };
        d.races = Math.max(d.races, p.races);
        d.stake += p.stake;
        d.net += p.net;
        byDay.set(p.day, d);
      }
    }
    let cum = 0;
    let cumStake = 0;
    out[pick] = [...byDay.values()]
      .sort((a, b) => a.day.localeCompare(b.day))
      .map((p) => {
        cum += p.net;
        cumStake += p.stake;
        return { ...p, cum, cumStake };
      });
  }
  return out;
}

function edgeDay(series: CarnetSeries[], which: "first" | "last"): string | null {
  let out: string | null = null;
  for (const s of series) {
    const d = which === "first" ? s.points[0]?.day : s.points[s.points.length - 1]?.day;
    if (d && (!out || (which === "first" ? d < out : d > out))) out = d;
  }
  return out;
}

function niceTicks(lo: number, hi: number, n: number): number[] {
  const span = hi - lo || 1;
  const raw = span / n;
  const pow = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 5, 10].map((k) => k * pow).find((s) => s >= raw) ?? raw;
  const out: number[] = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(Math.round(v * 100) / 100);
  if (!out.includes(0) && lo <= 0 && hi >= 0) out.push(0);
  return out.sort((a, b) => a - b);
}

/** Day labels: dd/mm on short spans, month starts ("mars 25") on long ones. */
function xLabels(days: string[], narrow: boolean): { i: number; text: string }[] {
  const max = narrow ? 4 : 9;
  const span = days.length ? dayNum(days[days.length - 1]!) - dayNum(days[0]!) : 0;
  if (span <= 75) {
    const every = Math.max(1, Math.ceil(days.length / max));
    return days
      .map((d, i) => ({ i, text: shortDay(d).slice(0, 5) }))
      .filter((_, i) => i % every === 0 || i === days.length - 1);
  }
  const starts: { i: number; text: string }[] = [];
  let prev = "";
  days.forEach((d, i) => {
    const ym = d.slice(0, 7);
    if (ym !== prev && i > 0) starts.push({ i, text: `${MONTHS[Number(d.slice(5, 7)) - 1]} ${d.slice(2, 4)}` });
    prev = ym;
  });
  const every = Math.max(1, Math.ceil(starts.length / max));
  return starts.filter((_, k) => k % every === 0);
}

export function BetsChart({
  series,
  height = 280,
  overlay,
  overlayOn = false,
  onOverlay,
  ranges = false,
  note,
}: {
  series: CarnetSeries[];
  height?: number;
  /** The same picks recalculated on every race (thin dotted lines). */
  overlay?: CarnetSeries[] | null;
  overlayOn?: boolean;
  onOverlay?: (on: boolean) => void;
  /** Show the period selector (1S … Tout). */
  ranges?: boolean;
  note?: ReactNode;
}) {
  const [mode, setMode] = useState<Mode>("ALL");
  const [range, setRange] = useState<Range>("all");
  const [hover, setHover] = useState<number | null>(null);
  // Drawn at the container's real width so text stays at its true size on phone and desktop.
  const wrap = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(760);

  const showOverlay = overlayOn && !!overlay && overlay.length > 0;
  const unit: "eur" | "pct" = showOverlay ? "pct" : "eur";
  const first = edgeDay(series, "first");
  const last = edgeDay(series, "last");
  const spanDays = first && last ? dayNum(last) - dayNum(first) : 0;
  const choices = RANGES.filter((r) => r.value === "all" || r.days < spanDays + 1);
  const active = choices.some((c) => c.value === range) ? range : "all";
  const from = useMemo(() => {
    const r = RANGES.find((x) => x.value === active)!;
    if (!last || !Number.isFinite(r.days)) return null;
    return new Date((dayNum(last) - r.days + 1) * DAY_MS).toISOString().slice(0, 10);
  }, [active, last]);

  const data = useMemo(() => lines(series, mode, from), [series, mode, from]);
  const extra = useMemo(
    () => (showOverlay && overlay ? lines(overlay, mode, from ?? first) : null),
    [showOverlay, overlay, mode, from, first],
  );
  const days = useMemo(() => {
    const all = [...data.favori, ...data.modèle, ...(extra ? [...extra.favori, ...extra.modèle] : [])];
    return [...new Set(all.map((p) => p.day))].sort();
  }, [data, extra]);

  const ready = days.length >= 2;
  useEffect(() => {
    const el = wrap.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => e && setWidth(Math.max(300, Math.round(e.contentRect.width))));
    ro.observe(el);
    return () => ro.disconnect();
  }, [ready]);

  const val = (p: Point) => (unit === "pct" ? (p.cumStake ? (p.cum / p.cumStake) * 100 : 0) : p.cum);
  const fmtVal = (v: number) => (unit === "pct" ? signedPct(v) : signed(v));

  const controls = (
    <div className="row" style={{ justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
      <div className="legend" aria-label="Légende">
        {PICKS.map((k) => (
          <span key={k.pick}>
            <svg width="26" height="10" aria-hidden>
              <line x1="1" x2="25" y1="5" y2="5" stroke={k.color} strokeWidth={3} strokeDasharray={k.dash} strokeLinecap="round" />
            </svg>
            {k.label}
          </span>
        ))}
        {showOverlay && (
          <span>
            <svg width="26" height="10" aria-hidden>
              <line x1="1" x2="25" y1="5" y2="5" stroke="var(--ink-2)" strokeWidth={1.75} strokeDasharray="1.5 3.5" strokeLinecap="round" />
            </svg>
            toutes les courses (recalculé)
          </span>
        )}
      </div>
      <div className="row" style={{ gap: 8, flexWrap: "wrap" }}>
        {onOverlay && (
          <label className="small check">
            <input type="checkbox" checked={overlayOn} onChange={(e) => onOverlay(e.target.checked)} /> Toutes les courses
            (recalculé)
          </label>
        )}
        <Segmented<Mode>
          label="Type de pari"
          value={mode}
          onChange={setMode}
          options={[
            { value: "ALL", label: "Gagnant + placé" },
            { value: "SG", label: "Gagnant" },
            { value: "SP", label: "Placé" },
          ]}
        />
      </div>
    </div>
  );

  const rangeBar =
    ranges && choices.length > 1 ? (
      <div className="range-bar" role="group" aria-label="Période">
        {choices.map((r) => (
          <button key={r.value} aria-pressed={r.value === active} onClick={() => setRange(r.value)}>
            {r.label}
          </button>
        ))}
      </div>
    ) : null;

  if (!ready)
    return (
      <div className="stack" style={{ gap: 10 }}>
        {controls}
        <p className="small muted" style={{ margin: 0 }}>
          La courbe apparaît après deux jours de paris réglés.
        </p>
        {rangeBar}
      </div>
    );

  const W = width;
  const narrow = W < 520;
  const H = narrow ? Math.round(height * 0.8) : height;
  const m = { top: 16, right: narrow ? 104 : extra ? 168 : 128, bottom: 28, left: narrow ? 48 : 60 };
  const iw = W - m.left - m.right;
  const ih = H - m.top - m.bottom;
  const groups: { pts: Point[]; k: (typeof PICKS)[number]; thin: boolean }[] = [
    ...(extra ? PICKS.map((k) => ({ pts: extra[k.pick], k, thin: true })) : []),
    ...PICKS.map((k) => ({ pts: data[k.pick], k, thin: false })),
  ];
  const vals = groups.flatMap((g) => g.pts.map(val));
  const lo0 = Math.min(0, ...vals);
  const hi0 = Math.max(0, ...vals);
  const pad = Math.max(unit === "pct" ? 2 : 1, (hi0 - lo0) * 0.1);
  const lo = lo0 - pad;
  const hi = hi0 + pad;
  const x = (i: number) => m.left + (i / (days.length - 1)) * iw;
  const y = (v: number) => m.top + ih - ((v - lo) / (hi - lo)) * ih;
  const idx = new Map(days.map((d, i) => [d, i]));
  const ticks = niceTicks(lo, hi, 5);
  const markers = days.length <= 45;
  const same =
    data.favori.length === data.modèle.length &&
    data.favori.length > 0 &&
    data.favori.every((p, i) => Math.abs(p.cum - (data.modèle[i]?.cum ?? NaN)) < 1e-9);

  // End labels, nudged apart when lines finish close together.
  const ends = groups
    .map((g) => {
      const lp = g.pts[g.pts.length - 1];
      return lp ? { g, last: lp, ly: y(val(lp)) } : null;
    })
    .filter((e): e is NonNullable<typeof e> => e !== null)
    .sort((a, b) => a.ly - b.ly);
  for (let pass = 0; pass < 3; pass++)
    for (let i = 1; i < ends.length; i++)
      if (ends[i]!.ly - ends[i - 1]!.ly < 15) {
        const mid = (ends[i]!.ly + ends[i - 1]!.ly) / 2;
        ends[i - 1]!.ly = mid - 7.5;
        ends[i]!.ly = mid + 7.5;
      }

  const onMove = (e: React.MouseEvent<SVGRectElement>) => {
    const r = (e.currentTarget.ownerSVGElement as SVGSVGElement).getBoundingClientRect();
    const px = ((e.clientX - r.left) / r.width) * W;
    const i = Math.round(((px - m.left) / iw) * (days.length - 1));
    setHover(Math.max(0, Math.min(days.length - 1, i)));
  };
  const hd = hover == null ? null : days[hover]!;
  const hx = hover == null ? 0 : x(hover);

  const tipRows = (pts: Lines, suffix: string) =>
    PICKS.map((k) => {
      const p = pts[k.pick].find((q) => q.day === hd);
      return (
        <div key={k.pick + suffix} className="tip-row">
          <i style={{ background: k.color, opacity: suffix ? 0.55 : 1 }} />
          <span>
            {k.label}
            {suffix}
          </span>
          {p ? (
            <span className="num">
              {fmtVal(val(p))} <span className="muted">(jour {signed(p.net)}, {p.races} c.)</span>
            </span>
          ) : (
            <span className="muted">pas joué</span>
          )}
        </div>
      );
    });

  return (
    <div className="stack" style={{ gap: 10 }}>
      {controls}
      <div className="bets-svg-wrap" ref={wrap}>
        <svg
          className="chart"
          viewBox={`0 0 ${W} ${H}`}
          width={W}
          height={H}
          role="img"
          aria-label={`Gains cumulés par jour, favori et modèle${unit === "pct" ? ", en retour sur mise" : ""}`}
        >
          {ticks.map((v) => (
            <g key={v}>
              <line x1={m.left} x2={m.left + iw} y1={y(v)} y2={y(v)} className={v === 0 ? "zero" : "grid"} />
              <text x={m.left - 8} y={y(v) + 4} textAnchor="end">
                {v === 0
                  ? unit === "pct"
                    ? "0 %"
                    : "0 €"
                  : `${v > 0 ? "+" : "−"}${Math.abs(v)} ${unit === "pct" ? "%" : "€"}`}
              </text>
            </g>
          ))}
          {xLabels(days, narrow).map(({ i, text }) => (
            <text key={i} x={x(i)} y={H - 8} textAnchor="middle">
              {text}
            </text>
          ))}
          {groups.map(({ pts, k, thin }) => (
            <g key={k.pick + (thin ? "-all" : "")} opacity={thin ? 0.75 : 1}>
              <polyline
                points={pts.map((p) => `${x(idx.get(p.day)!)},${y(val(p))}`).join(" ")}
                fill="none"
                stroke={k.color}
                strokeWidth={thin ? 1.75 : days.length > 200 ? 2 : 3}
                strokeDasharray={thin ? "1.5 3.5" : k.dash}
                strokeLinejoin="round"
                strokeLinecap="round"
              />
              {markers &&
                !thin &&
                pts.map((p) => (
                  <circle key={p.day} cx={x(idx.get(p.day)!)} cy={y(val(p))} r={k.dash ? 3 : 4.5} fill={k.color} className="ring" />
                ))}
            </g>
          ))}
          {ends.map(({ g, last: lp, ly }) => (
            <text
              key={g.k.pick + (g.thin ? "-all" : "")}
              x={x(idx.get(lp.day)!) + 10}
              y={ly + 4}
              className="end-label"
              opacity={g.thin ? 0.75 : 1}
            >
              {narrow ? fmtVal(val(lp)) : `${g.k.label}${g.thin ? " (toutes)" : ""} ${fmtVal(val(lp))}`}
            </text>
          ))}
          {hd && <line x1={hx} x2={hx} y1={m.top} y2={m.top + ih} className="crosshair" pointerEvents="none" />}
          <rect x={m.left} y={m.top} width={iw} height={ih} fill="transparent" onMouseMove={onMove} onMouseLeave={() => setHover(null)} />
        </svg>
        {hd && (
          <div
            className="chart-tip"
            style={{ left: `${(hx / W) * 100}%`, transform: hx > W * 0.55 ? "translateX(calc(-100% - 12px))" : "translateX(12px)" }}
          >
            <strong>{shortDay(hd)}</strong>
            {tipRows(data, "")}
            {extra && tipRows(extra, " (toutes)")}
          </div>
        )}
      </div>
      {rangeBar}

      <p className="small muted" style={{ margin: 0 }}>
        {same && !extra ? "Les deux courbes sont confondues : le modèle a choisi le favori sur toutes ces courses. " : ""}
        {unit === "pct" ? "Retour sur mise cumulé, depuis le début de la période affichée. " : ""}
        {note}
      </p>

      <details className="small">
        <summary className="muted">Voir les chiffres jour par jour</summary>
        <div className="table-wrap" style={{ maxHeight: 320, overflowY: "auto" }}>
          <table className="compact">
            <thead>
              <tr>
                <th>Jour</th>
                <th className="r">Courses</th>
                <th className="r">Favori (jour → cumul)</th>
                <th className="r">Modèle (jour → cumul)</th>
              </tr>
            </thead>
            <tbody>
              {[...days].reverse().map((d) => {
                const f = data.favori.find((q) => q.day === d);
                const mo = data.modèle.find((q) => q.day === d);
                return (
                  <tr key={d}>
                    <td>{shortDay(d)}</td>
                    <td className="r num">{f?.races ?? mo?.races ?? "—"}</td>
                    <td className="r num">{f ? `${signed(f.net)} → ${signed(f.cum)}` : "—"}</td>
                    <td className="r num">{mo ? `${signed(mo.net)} → ${signed(mo.cum)}` : "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}

/** The carnet's curve, with the option to add the same picks recalculated on every race of
 *  the same days (the races the Mac missed included): played vs "what it would have been". */
export function CarnetBetsChart({ series }: { series: CarnetSeries[] }) {
  const [on, setOn] = useState(false);
  const since = edgeDay(series, "first") ?? undefined;
  const load = useApi(
    () => (on ? api.replay("ALL", since) : Promise.resolve(null)),
    `carnet-overlay-${on}-${since}`,
  );
  const overlay = load.state === "ready" ? (load.data?.report?.series ?? []) : null;
  return (
    <BetsChart
      series={series}
      overlay={overlay}
      overlayOn={on}
      onOverlay={setOn}
      note={
        on && overlay && overlay.length === 0 ? (
          "Pas encore de reconstitution : elle est calculée chaque nuit."
        ) : on ? (
          <>
            Pointillés fins : favori et modèle recalculés sur toutes les courses de ces jours, jouées ou non (base mise à
            jour la nuit, donc jusqu'à hier).{" "}
          </>
        ) : (
          "Comparés sur les mêmes courses (celles où le modèle a joué), 1 € par ticket."
        )
      }
    />
  );
}
