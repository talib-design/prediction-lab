import { useEffect, useMemo, useRef, useState } from "react";
import type { CarnetSeries } from "../lib/api";
import { euros, shortDay } from "../lib/format";
import { Segmented } from "./ui";

/** Running total of the carnet's fictitious bets, one point per day: favourite vs Marché+.
 *  One chart, two lines. The model line is dashed and drawn on top, so when the model picks
 *  the favourite (identical results) both lines stay visible instead of one hiding the other. */

type Mode = "ALL" | "SG" | "SP";

const PICKS = [
  { pick: "favori", label: "Favori", color: "var(--series-favori)", dash: undefined },
  { pick: "modèle", label: "Modèle", color: "var(--series-model)", dash: "7 5" },
] as const;

type Point = { day: string; races: number; stake: number; net: number; cum: number };

const signed = (x: number) => `${x >= 0 ? "+" : "−"}${euros(Math.abs(x))}`;

/** One line per pick for the chosen bet type; "ALL" adds win and place day by day. */
function lines(series: CarnetSeries[], mode: Mode): Record<"favori" | "modèle", Point[]> {
  const out = { favori: [] as Point[], modèle: [] as Point[] };
  for (const pick of ["favori", "modèle"] as const) {
    const byDay = new Map<string, Point>();
    for (const s of series) {
      if (s.pick !== pick || (mode !== "ALL" && s.bet !== mode)) continue;
      for (const p of s.points) {
        const d = byDay.get(p.day) ?? { day: p.day, races: 0, stake: 0, net: 0, cum: 0 };
        d.races = Math.max(d.races, p.races);
        d.stake += p.stake;
        d.net += p.net;
        byDay.set(p.day, d);
      }
    }
    let cum = 0;
    out[pick] = [...byDay.values()]
      .sort((a, b) => a.day.localeCompare(b.day))
      .map((p) => {
        cum += p.net;
        return { ...p, cum };
      });
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

export function BetsChart({ series, height = 280 }: { series: CarnetSeries[]; height?: number }) {
  const [mode, setMode] = useState<Mode>("ALL");
  const [hover, setHover] = useState<number | null>(null);
  // Drawn at the container's real width so text stays at its true size on phone and desktop.
  const wrap = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(760);
  const data = useMemo(() => lines(series, mode), [series, mode]);
  const days = useMemo(
    () => [...new Set([...data.favori, ...data.modèle].map((p) => p.day))].sort(),
    [data],
  );

  const ready = days.length >= 2;
  useEffect(() => {
    const el = wrap.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => e && setWidth(Math.max(300, Math.round(e.contentRect.width))));
    ro.observe(el);
    return () => ro.disconnect();
  }, [ready]);
  if (days.length < 2)
    return (
      <p className="small muted" style={{ margin: 0 }}>
        La courbe apparaît après deux jours de paris réglés.
      </p>
    );

  const W = width;
  const narrow = W < 520;
  const H = narrow ? Math.round(height * 0.8) : height;
  const m = { top: 16, right: narrow ? 98 : 120, bottom: 28, left: narrow ? 44 : 56 };
  const iw = W - m.left - m.right;
  const ih = H - m.top - m.bottom;
  const all = [...data.favori, ...data.modèle].map((p) => p.cum);
  const lo0 = Math.min(0, ...all);
  const hi0 = Math.max(0, ...all);
  const pad = Math.max(1, (hi0 - lo0) * 0.1);
  const lo = lo0 - pad;
  const hi = hi0 + pad;
  const x = (i: number) => m.left + (days.length === 1 ? iw / 2 : (i / (days.length - 1)) * iw);
  const y = (v: number) => m.top + ih - ((v - lo) / (hi - lo)) * ih;
  const idx = new Map(days.map((d, i) => [d, i]));
  const ticks = niceTicks(lo, hi, 5);
  const every = Math.max(1, Math.ceil(days.length / (narrow ? 4 : 10)));
  const same =
    data.favori.length === data.modèle.length &&
    data.favori.every((p, i) => Math.abs(p.cum - (data.modèle[i]?.cum ?? NaN)) < 1e-9);

  // End labels, nudged apart when the two lines finish close together.
  const ends = PICKS.map((k) => {
    const pts = data[k.pick];
    const last = pts[pts.length - 1];
    return last ? { k, last, ly: y(last.cum) } : null;
  }).filter((e): e is NonNullable<typeof e> => e !== null);
  if (ends.length === 2 && Math.abs(ends[0]!.ly - ends[1]!.ly) < 16) {
    const [a, b] = ends[0]!.ly <= ends[1]!.ly ? [ends[0]!, ends[1]!] : [ends[1]!, ends[0]!];
    const mid = (a.ly + b.ly) / 2;
    a.ly = mid - 8;
    b.ly = mid + 8;
  }

  const onMove = (e: React.MouseEvent<SVGRectElement>) => {
    const r = (e.currentTarget.ownerSVGElement as SVGSVGElement).getBoundingClientRect();
    const px = ((e.clientX - r.left) / r.width) * W;
    const i = Math.round(((px - m.left) / iw) * (days.length - 1));
    setHover(Math.max(0, Math.min(days.length - 1, i)));
  };
  const hd = hover == null ? null : days[hover]!;
  const hx = hover == null ? 0 : x(hover);

  return (
    <div className="stack" style={{ gap: 10 }}>
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
        </div>
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

      <div className="bets-svg-wrap" ref={wrap}>
        <svg className="chart" viewBox={`0 0 ${W} ${H}`} width={W} height={H} role="img" aria-label="Gains cumulés par jour, favori et modèle">
          {ticks.map((v) => (
            <g key={v}>
              <line x1={m.left} x2={m.left + iw} y1={y(v)} y2={y(v)} className={v === 0 ? "zero" : "grid"} />
              <text x={m.left - 8} y={y(v) + 4} textAnchor="end">
                {v === 0 ? "0 €" : `${v > 0 ? "+" : "−"}${Math.abs(v)} €`}
              </text>
            </g>
          ))}
          {days.map((d, i) =>
            i % every === 0 || i === days.length - 1 ? (
              <text key={d} x={x(i)} y={H - 8} textAnchor="middle">
                {shortDay(d).slice(0, 5)}
              </text>
            ) : null,
          )}
          {PICKS.map((k) => {
            const pts = data[k.pick];
            return (
              <g key={k.pick}>
                <polyline
                  points={pts.map((p) => `${x(idx.get(p.day)!)},${y(p.cum)}`).join(" ")}
                  fill="none"
                  stroke={k.color}
                  strokeWidth={3}
                  strokeDasharray={k.dash}
                  strokeLinejoin="round"
                  strokeLinecap="round"
                />
                {pts.map((p) => (
                  <circle key={p.day} cx={x(idx.get(p.day)!)} cy={y(p.cum)} r={k.dash ? 3 : 4.5} fill={k.color} className="ring" />
                ))}
              </g>
            );
          })}
          {ends.map(({ k, last, ly }) => (
            <text key={k.pick} x={x(idx.get(last.day)!) + 10} y={ly + 4} className="end-label">
              {narrow ? signed(last.cum) : `${k.label} ${signed(last.cum)}`}
            </text>
          ))}
          {hd && (
            <line x1={hx} x2={hx} y1={m.top} y2={m.top + ih} className="crosshair" pointerEvents="none" />
          )}
          <rect x={m.left} y={m.top} width={iw} height={ih} fill="transparent" onMouseMove={onMove} onMouseLeave={() => setHover(null)} />
        </svg>
        {hd && (
          <div
            className="chart-tip"
            style={{ left: `${(hx / W) * 100}%`, transform: hx > W * 0.6 ? "translateX(calc(-100% - 12px))" : "translateX(12px)" }}
          >
            <strong>{shortDay(hd)}</strong>
            {PICKS.map((k) => {
              const p = data[k.pick].find((q) => q.day === hd);
              return (
                <div key={k.pick} className="tip-row">
                  <i style={{ background: k.color }} />
                  <span>{k.label}</span>
                  {p ? (
                    <span className="num">
                      {signed(p.cum)} <span className="muted">(jour {signed(p.net)}, {p.races} c.)</span>
                    </span>
                  ) : (
                    <span className="muted">pas joué</span>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      <p className="small muted" style={{ margin: 0 }}>
        {same
          ? "Les deux courbes sont confondues : jusqu'ici le modèle a choisi le favori sur toutes les courses. "
          : ""}
        Comparés sur les mêmes courses (celles où le modèle a joué), 1 € par ticket.
      </p>

      <details className="small">
        <summary className="muted">Voir les chiffres jour par jour</summary>
        <div className="table-wrap">
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
              {days.map((d) => {
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
