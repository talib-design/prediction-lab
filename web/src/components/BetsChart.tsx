import { useMemo, useRef, useState } from "react";
import type { CarnetSeries } from "../lib/api";
import { euros, shortDay } from "../lib/format";

/** Running total of the carnet's fictitious bets, day by day: favourite vs Marché+, one
 *  panel per bet type. Both panels share the same time and euro scales so they compare. */

const PICKS = [
  { pick: "favori", label: "Favori", color: "var(--series-favori)" },
  { pick: "modèle", label: "Modèle Marché+", color: "var(--series-model)" },
] as const;

const signed = (x: number) => `${x >= 0 ? "+" : "−"}${euros(Math.abs(x))}`;
const DAY = 86_400_000;
const t = (d: string) => new Date(`${d}T00:00:00Z`).getTime();

function Panel({
  title,
  series,
  domain,
  height,
}: {
  title: string;
  series: CarnetSeries[];
  domain: { x0: number; x1: number; y0: number; y1: number };
  height: number;
}) {
  const W = 560;
  const H = height;
  const m = { top: 12, right: 104, bottom: 22, left: 52 };
  const iw = W - m.left - m.right;
  const ih = H - m.top - m.bottom;
  const x = (ms: number) => m.left + (domain.x1 === domain.x0 ? iw / 2 : ((ms - domain.x0) / (domain.x1 - domain.x0)) * iw);
  const y = (v: number) => m.top + ih - ((v - domain.y0) / (domain.y1 - domain.y0)) * ih;
  const days = useMemo(
    () => [...new Set(series.flatMap((s) => s.points.map((p) => p.day)))].sort(),
    [series],
  );
  const [hover, setHover] = useState<string | null>(null);
  const box = useRef<HTMLDivElement>(null);

  const ticks = niceTicks(domain.y0, domain.y1, 4);
  const xTicks = days.length <= 6 ? days : days.filter((_, i) => i % Math.ceil(days.length / 5) === 0);

  const onMove = (e: React.MouseEvent<SVGRectElement>) => {
    const r = (e.currentTarget.ownerSVGElement as SVGSVGElement).getBoundingClientRect();
    const px = ((e.clientX - r.left) / r.width) * W;
    let best: string | null = null;
    let dist = Infinity;
    for (const d of days) {
      const dd = Math.abs(x(t(d)) - px);
      if (dd < dist) {
        dist = dd;
        best = d;
      }
    }
    setHover(best);
  };

  // End labels, nudged apart when the two lines finish close together.
  const ends = series
    .map((s) => ({ s, last: s.points[s.points.length - 1] }))
    .filter((e) => e.last)
    .map((e) => ({ ...e, ly: y(e.last!.cum) }));
  if (ends.length === 2 && Math.abs(ends[0]!.ly - ends[1]!.ly) < 14) {
    const [a, b] = ends[0]!.ly <= ends[1]!.ly ? [ends[0]!, ends[1]!] : [ends[1]!, ends[0]!];
    const mid = (a.ly + b.ly) / 2;
    a.ly = mid - 7;
    b.ly = mid + 7;
  }

  const hoverX = hover ? x(t(hover)) : 0;
  return (
    <div className="bets-panel" ref={box}>
      <div className="bets-panel-title">{title}</div>
      <div className="bets-svg-wrap">
        <svg className="chart" viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label={`${title} : gains cumulés par jour`}>
          {ticks.map((v) => (
            <g key={v}>
              <line x1={m.left} x2={m.left + iw} y1={y(v)} y2={y(v)} className={v === 0 ? "zero" : "grid"} />
              <text x={m.left - 6} y={y(v) + 3} textAnchor="end">
                {v === 0 ? "0 €" : `${v > 0 ? "+" : "−"}${Math.abs(v)} €`}
              </text>
            </g>
          ))}
          {xTicks.map((d) => (
            <text key={d} x={x(t(d))} y={H - 6} textAnchor="middle">
              {shortDay(d).slice(0, 5)}
            </text>
          ))}
          {series.map((s) => {
            const color = PICKS.find((p) => p.pick === s.pick)!.color;
            const pts = s.points.map((p) => `${x(t(p.day))},${y(p.cum)}`).join(" ");
            const last = s.points[s.points.length - 1];
            return (
              <g key={s.strategy}>
                {s.points.length > 1 && <polyline points={pts} fill="none" stroke={color} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />}
                {last && <circle cx={x(t(last.day))} cy={y(last.cum)} r={4} fill={color} className="ring" />}
              </g>
            );
          })}
          {ends.map(({ s, last, ly }) => (
            <text key={s.strategy} x={x(t(last!.day)) + 9} y={ly + 4} className="end-label">
              {PICKS.find((p) => p.pick === s.pick)!.label.split(" ")[0]} {signed(last!.cum)}
            </text>
          ))}
          {hover && (
            <g pointerEvents="none">
              <line x1={hoverX} x2={hoverX} y1={m.top} y2={m.top + ih} className="crosshair" />
              {series.map((s) => {
                const p = s.points.find((q) => q.day === hover);
                const color = PICKS.find((k) => k.pick === s.pick)!.color;
                return p ? <circle key={s.strategy} cx={hoverX} cy={y(p.cum)} r={4.5} fill={color} className="ring" /> : null;
              })}
            </g>
          )}
          <rect
            x={m.left}
            y={m.top}
            width={iw}
            height={ih}
            fill="transparent"
            onMouseMove={onMove}
            onMouseLeave={() => setHover(null)}
          />
        </svg>
        {hover && (
          <div
            className="chart-tip"
            style={{ left: `${(hoverX / W) * 100}%`, transform: hoverX > W * 0.6 ? "translateX(calc(-100% - 12px))" : "translateX(12px)" }}
          >
            <strong>{shortDay(hover)}</strong>
            {series.map((s) => {
              const p = s.points.find((q) => q.day === hover);
              const k = PICKS.find((q) => q.pick === s.pick)!;
              return (
                <div key={s.strategy} className="tip-row">
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
    </div>
  );
}

function niceTicks(lo: number, hi: number, n: number): number[] {
  const span = hi - lo || 1;
  const raw = span / n;
  const pow = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 5, 10].map((k) => k * pow).find((s) => s >= raw) ?? raw;
  const out: number[] = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(Math.round(v));
  if (!out.includes(0) && lo <= 0 && hi >= 0) out.push(0);
  return out.sort((a, b) => a - b);
}

export function BetsChart({ series, height = 190 }: { series: CarnetSeries[]; height?: number }) {
  const all = series.flatMap((s) => s.points);
  const days = [...new Set(all.map((p) => p.day))].sort();
  if (days.length < 2)
    return (
      <p className="small muted" style={{ margin: 0 }}>
        La courbe apparaît après deux jours de paris réglés.
      </p>
    );
  const lo = Math.min(0, ...all.map((p) => p.cum));
  const hi = Math.max(0, ...all.map((p) => p.cum));
  const pad = Math.max(2, (hi - lo) * 0.12);
  const domain = { x0: t(days[0]!), x1: t(days[days.length - 1]!) || t(days[0]!) + DAY, y0: lo - pad, y1: hi + pad };
  const by = (bet: "SG" | "SP") => series.filter((s) => s.bet === bet && s.points.length > 0);
  const modelStart = series.filter((s) => s.pick === "modèle").flatMap((s) => s.points.map((p) => p.day)).sort()[0];
  return (
    <div className="stack" style={{ gap: 8 }}>
      <div className="row" style={{ justifyContent: "space-between" }}>
        <div className="legend" aria-label="Légende">
          {PICKS.map((p) => (
            <span key={p.pick}>
              <i style={{ background: p.color }} />
              {p.label}
            </span>
          ))}
        </div>
        {modelStart && (
          <span className="small muted">
            comparés sur les mêmes courses : celles où le modèle a joué (depuis le {shortDay(modelStart)})
          </span>
        )}
      </div>
      <div className="bets-grid">
        <Panel title="Gagnant (simple gagnant)" series={by("SG")} domain={domain} height={height} />
        <Panel title="Placé (simple placé)" series={by("SP")} domain={domain} height={height} />
      </div>
      <details className="small">
        <summary className="muted">Voir les chiffres jour par jour</summary>
        <div className="table-wrap">
          <table className="compact">
            <thead>
              <tr>
                <th>Jour</th>
                {series.map((s) => (
                  <th key={s.strategy} className="r">
                    {s.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {days.map((d) => (
                <tr key={d}>
                  <td>{shortDay(d)}</td>
                  {series.map((s) => {
                    const p = s.points.find((q) => q.day === d);
                    return (
                      <td key={s.strategy} className="r num">
                        {p ? `${signed(p.net)} → ${signed(p.cum)}` : "—"}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
