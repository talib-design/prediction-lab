// Plain SVG charts: no chart library, every mark is explainable.
import type { CalibrationRow, OddsPoint } from "../lib/api";
import { fmt, odds as fmtOdds, pct, time } from "../lib/format";
import type { Kind } from "./ui";

const KIND_VAR: Record<Kind, string> = {
  fact: "var(--k-fact)",
  feature: "var(--k-feature)",
  assoc: "var(--k-assoc)",
  forecast: "var(--k-forecast)",
  market: "var(--k-market)",
};

export function ProbBar({ p, kind = "market", scale = 1 }: { p: number | null; kind?: Kind; scale?: number }) {
  if (p == null) return <span className="muted">—</span>;
  return (
    <div className="prob-cell">
      <span className="num small">{pct(p)}</span>
      <div className="bar" aria-hidden>
        <span style={{ width: `${Math.min(100, (p / scale) * 100)}%`, background: KIND_VAR[kind] }} />
      </div>
    </div>
  );
}

/**
 * Implied win probability (1/odds) over time: a rising line means money coming in.
 * Quotes stamped after the scheduled off are closing odds -- drawn faded, past a dashed
 * line, because no model may ever use them.
 */
export function OddsSparkline({
  series,
  offTime,
  width = 112,
  height = 30,
}: {
  series: OddsPoint[];
  offTime: string;
  width?: number;
  height?: number;
}) {
  if (series.length === 0) return <span className="muted small">pas de cote</span>;
  const pts = series.map((p) => ({ t: new Date(p.t).getTime(), y: 1 / p.odds, p }));
  const off = new Date(offTime).getTime();
  const t0 = Math.min(...pts.map((p) => p.t), off - 60 * 60000);
  const t1 = Math.max(...pts.map((p) => p.t), off + 5 * 60000);
  const ys = pts.map((p) => p.y);
  const lo = Math.min(...ys) * 0.9;
  const hi = Math.max(...ys) * 1.1 || 1;
  const pad = 3;
  const x = (t: number) => pad + ((t - t0) / (t1 - t0 || 1)) * (width - 2 * pad);
  const y = (v: number) => height - pad - ((v - lo) / (hi - lo || 1)) * (height - 2 * pad);
  const before = pts.filter((p) => p.t < off);
  const after = pts.filter((p) => p.t >= off);
  const path = (arr: typeof pts) => arr.map((p, i) => `${i ? "L" : "M"}${x(p.t).toFixed(1)},${y(p.y).toFixed(1)}`).join("");
  const first = series[0]!;
  const lastBefore = before.at(-1);
  const label = `${series.length} cotes, de ${fmtOdds(first.odds)} (${time(first.t)}) à ${
    lastBefore ? fmtOdds(lastBefore.p.odds) : "—"
  } avant le départ`;
  return (
    <svg className="chart" width={width} height={height} role="img" aria-label={label}>
      <title>{label}</title>
      <line x1={x(off)} x2={x(off)} y1={0} y2={height} className="axis" strokeDasharray="2 2" />
      {after.length > 0 && before.length > 0 && (
        <path d={path([before.at(-1)!, ...after])} fill="none" stroke="var(--ink-3)" strokeOpacity={0.45} strokeWidth={1.2} />
      )}
      <path d={path(before)} fill="none" stroke="var(--k-market)" strokeWidth={1.6} />
      {before
        .filter((p) => p.p.kind === "REFERENCE")
        .map((p) => (
          <circle key={p.t} cx={x(p.t)} cy={y(p.y)} r={2.2} fill="var(--surface)" stroke="var(--k-market)" strokeWidth={1.2} />
        ))}
      {lastBefore && <circle cx={x(lastBefore.t)} cy={y(lastBefore.y)} r={2.2} fill="var(--k-market)" />}
    </svg>
  );
}

/** Reliability diagram: forecast vs observed frequency, one dot per probability bucket. */
export function ReliabilityChart({
  rows,
  kind = "market",
  size = 260,
  maxP,
}: {
  rows: CalibrationRow[];
  kind?: Kind;
  size?: number;
  maxP?: number;
}) {
  if (rows.length === 0) return null;
  const m = 46;
  const w = size;
  const top = maxP ?? Math.min(1, Math.max(0.1, ...rows.map((r) => Math.max(r.mean_forecast, r.observed))) * 1.1);
  const sx = (v: number) => m + (v / top) * (w - m - 10);
  const sy = (v: number) => w - m - (v / top) * (w - m - 10);
  const nMax = Math.max(...rows.map((r) => r.n));
  const ticks = [0, top / 2, top];
  return (
    <svg className="chart" width="100%" viewBox={`0 0 ${w} ${w}`} style={{ maxWidth: w }} role="img" aria-label="Diagramme de fiabilité">
      {ticks.map((t) => (
        <g key={t}>
          <line x1={sx(0)} x2={sx(top)} y1={sy(t)} y2={sy(t)} className="grid" />
          <text x={m - 6} y={sy(t) + 3} textAnchor="end">
            {pct(t, 0)}
          </text>
          <text x={sx(t)} y={w - m + 14} textAnchor="middle">
            {pct(t, 0)}
          </text>
        </g>
      ))}
      <line x1={sx(0)} y1={sy(0)} x2={sx(top)} y2={sy(top)} stroke="var(--ink-3)" strokeDasharray="3 3" />
      {rows.map((r) => (
        <circle
          key={r.bucket}
          cx={sx(r.mean_forecast)}
          cy={sy(r.observed)}
          r={3 + 6 * Math.sqrt(r.n / nMax)}
          fill={KIND_VAR[kind]}
          fillOpacity={0.35}
          stroke={KIND_VAR[kind]}
        >
          <title>
            {`Tranche ${r.bucket} : prévu ${pct(r.mean_forecast)}, observé ${pct(r.observed)} (${r.n} partants)`}
          </title>
        </circle>
      ))}
      <text x={(sx(0) + sx(top)) / 2} y={w - 4} textAnchor="middle">
        probabilité prévue
      </text>
      <text x={10} y={(sy(0) + sy(top)) / 2} textAnchor="middle" transform={`rotate(-90 10 ${(sy(0) + sy(top)) / 2})`}>
        fréquence observée
      </text>
    </svg>
  );
}

export interface Interval {
  label: string;
  est: number;
  lo?: number;
  hi?: number;
  tone?: "neutral" | "strong" | "muted";
}

/** Forest plot: an estimate and its 95 % interval per row, against a zero line. */
export function IntervalChart({
  rows,
  format = (v: number) => fmt(v, 3),
  zeroLabel,
  width = 560,
}: {
  rows: Interval[];
  format?: (v: number) => string;
  zeroLabel?: string;
  width?: number;
}) {
  if (rows.length === 0) return null;
  const rowH = 26;
  const left = 190;
  const right = 70;
  const h = rows.length * rowH + 28;
  const vals = rows.flatMap((r) => [r.est, r.lo ?? r.est, r.hi ?? r.est, 0]).filter((v) => Number.isFinite(v));
  const span = Math.max(...vals.map(Math.abs)) * 1.1 || 1;
  const lo = Math.min(...vals) < 0 ? -span : 0;
  const hi = Math.max(...vals) > 0 ? span : 0;
  const sx = (v: number) => left + ((v - lo) / (hi - lo || 1)) * (width - left - right);
  const color = (t?: Interval["tone"]) =>
    t === "strong" ? "var(--accent)" : t === "muted" ? "var(--ink-3)" : "var(--ink-2)";
  return (
    <svg className="chart" width="100%" style={{ maxWidth: width * 1.3 }} viewBox={`0 0 ${width} ${h}`} role="img" aria-label="Intervalles de confiance">
      <line x1={sx(0)} x2={sx(0)} y1={4} y2={h - 20} className="axis" />
      <text x={sx(0)} y={h - 6} textAnchor="middle">
        {zeroLabel ?? "0"}
      </text>
      {rows.map((r, i) => {
        const cy = 14 + i * rowH;
        return (
          <g key={r.label}>
            <text x={left - 10} y={cy + 4} textAnchor="end" style={{ fill: "var(--ink)", fontSize: 12 }}>
              {r.label}
            </text>
            {r.lo != null && r.hi != null && Number.isFinite(r.lo) && (
              <line x1={sx(r.lo)} x2={sx(r.hi)} y1={cy} y2={cy} stroke={color(r.tone)} strokeWidth={2} strokeLinecap="round" />
            )}
            <circle cx={sx(r.est)} cy={cy} r={4} fill={color(r.tone)} />
            <text x={width - right + 8} y={cy + 4} style={{ fill: "var(--ink-2)", fontSize: 11 }} className="num">
              {format(r.est)}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
