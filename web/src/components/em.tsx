// EuroMillions building blocks: balls and stars, the frequency chart, the chance band.
import { useEffect, useRef, useState } from "react";
import { fmt, int } from "../lib/format";

export const EM_LOGIC_LABELS: Record<string, string> = {
  frequency: "Fréquence totale",
  rolling_frequency_100: "Fréquence 100 derniers",
  rolling_frequency_300: "Fréquence 300 derniers",
  shrunk_frequency: "Fréquence rétrécie",
  gap: "Retard",
  hot50: "Chauds (50 derniers)",
  cold50: "Froids (50 derniers)",
  repeat: "Répétition du dernier tirage",
  temoin_r1: "Témoin hasard",
};
export const emLogic = (k: string) => EM_LOGIC_LABELS[k] ?? k;

export const EM_RANKS: Record<number, string> = {
  1: "5 + 2", 2: "5 + 1", 3: "5 + 0", 4: "4 + 2", 5: "4 + 1", 6: "3 + 2", 7: "4 + 0",
  8: "2 + 2", 9: "3 + 1", 10: "3 + 0", 11: "1 + 2", 12: "2 + 1", 13: "2 + 0",
};

/** Five balls then two stars; numbers present in `hitBalls`/`hitStars` are marked. */
export function Grid({
  balls,
  stars,
  hitBalls,
  hitStars,
}: {
  balls: number[];
  stars: number[];
  hitBalls?: number[] | null;
  hitStars?: number[] | null;
}) {
  const hb = new Set(hitBalls ?? []);
  const hs = new Set(hitStars ?? []);
  return (
    <span className="em-grid" aria-label={`boules ${balls.join(", ")} ; étoiles ${stars.join(", ")}`}>
      {balls.map((b) => (
        <span key={`b${b}`} className={`em-ball${hb.has(b) ? " hit" : ""}`}>
          {b}
        </span>
      ))}
      <span className="em-sep" aria-hidden />
      {stars.map((s) => (
        <span key={`s${s}`} className={`em-star${hs.has(s) ? " hit" : ""}`}>
          {s}
        </span>
      ))}
    </span>
  );
}

/** Width of an element, kept in sync with its layout (so chart text stays at its real size). */
function useWidth<T extends HTMLElement>(fallback: number): [React.RefObject<T | null>, number] {
  const ref = useRef<T>(null);
  const [width, setWidth] = useState(fallback);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => {
      if (entry) setWidth(Math.max(280, Math.floor(entry.contentRect.width)));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return [ref, width];
}

/** Each number's count as a dot on a stem from the fair expectation, with the band where
 *  95 % of numbers fall if the draw is fair (binomial, per number, uncorrected). Dots and
 *  stems rather than bars: the axis does not start at zero, and bars would exaggerate. */
export function FreqChart({
  counts,
  draws,
  k,
  label,
}: {
  counts: Record<string, number>;
  draws: number;
  k: number;
  label: string;
}) {
  const [ref, W] = useWidth<HTMLDivElement>(760);
  const [hover, setHover] = useState<number | null>(null);
  const numbers = Object.keys(counts)
    .map(Number)
    .sort((a, b) => a - b);
  const size = numbers.length;
  const p = k / size;
  const expected = draws * p;
  const sd = Math.sqrt(draws * p * (1 - p));
  const lo = expected - 1.96 * sd;
  const hi = expected + 1.96 * sd;
  const values = numbers.map((n) => counts[String(n)] ?? 0);
  const reach = Math.max(hi - expected, ...values.map((v) => Math.abs(v - expected))) * 1.12;
  const min = expected - reach;
  const max = expected + reach;
  const H = 200;
  const padL = 36;
  const padR = 8;
  const padB = 22;
  const padT = 8;
  const plotW = W - padL - padR;
  const plotH = H - padB - padT;
  const step = plotW / size;
  const y = (v: number) => padT + plotH - ((v - min) / (max - min)) * plotH;
  const cx = (i: number) => padL + i * step + step / 2;
  const ticks = [Math.round(lo), Math.round(expected), Math.round(hi)];
  const every = size <= 12 ? 1 : W < 520 ? 10 : 5;
  const h = hover == null ? null : { n: numbers[hover]!, v: values[hover]! };
  return (
    <div className="em-chart" ref={ref}>
      <svg width={W} height={H} role="img" aria-label={label} onMouseLeave={() => setHover(null)}>
        <rect x={padL} y={y(hi)} width={plotW} height={y(lo) - y(hi)} className="em-band" />
        {ticks.map((t) => (
          <text key={t} x={padL - 6} y={y(t) + 4} className="em-axis" textAnchor="end">
            {t}
          </text>
        ))}
        <line x1={padL} x2={W - padR} y1={y(expected)} y2={y(expected)} className="em-expected" />
        {values.map((v, i) => {
          const out = v < lo || v > hi;
          const cls = `em-lolli${out ? " out" : ""}${hover === i ? " on" : ""}`;
          return (
            <g key={numbers[i]} onMouseEnter={() => setHover(i)}>
              <rect x={padL + i * step} y={padT} width={step} height={plotH} fill="transparent" />
              <line x1={cx(i)} x2={cx(i)} y1={y(expected)} y2={y(v)} className={`${cls} stem`} />
              <circle cx={cx(i)} cy={y(v)} r={hover === i ? 5 : 4} className={`${cls} dot`} />
              {(i === 0 || (i + 1) % every === 0) && (
                <text x={cx(i)} y={H - 6} className="em-axis" textAnchor="middle">
                  {numbers[i]}
                </text>
              )}
            </g>
          );
        })}
      </svg>
      <div className="em-chart-foot small">
        {h ? (
          <span>
            <strong>
              {size > 12 ? "Boule" : "Étoile"} {h.n}
            </strong>{" "}
            : {int(h.v)} sorties pour {fmt(expected, 1)} attendues ({h.v >= expected ? "+" : "−"}
            {fmt((Math.abs(h.v - expected) / expected) * 100, 1)} %)
          </span>
        ) : (
          <span className="muted">
            Pointillé : attendu au hasard ({fmt(expected, 1)} sorties). Bande : où tombent 95 % des numéros si le
            tirage est équitable ; sur {size} numéros, {size > 12 ? "2 ou 3" : "0 ou 1"} en dehors est normal. Survolez
            un numéro pour le détail.
          </span>
        )}
      </div>
    </div>
  );
}

/** Where a value sits relative to the spread chance produces (2.5 %-97.5 % of random
 *  players), on a shared axis. */
export function ChanceBand({
  value,
  low,
  high,
  min,
  max,
  expected,
  title,
}: {
  value: number;
  low: number;
  high: number;
  min: number;
  max: number;
  expected: number;
  title: string;
}) {
  const W = 160;
  const x = (v: number) => ((Math.max(min, Math.min(max, v)) - min) / (max - min)) * W;
  const inside = value >= low && value <= high;
  return (
    <span className="ratio" title={title}>
      <svg width={W} height={14} aria-hidden>
        <rect x={x(low)} y={3} width={x(high) - x(low)} height={8} rx={2} className="em-band" />
        <line x1={x(expected)} x2={x(expected)} y1={1} y2={13} className="ratio-axis" />
        <circle cx={x(value)} cy={7} r={3.5} className={inside ? "ratio-dot" : "ratio-dot strong"} />
      </svg>
    </span>
  );
}
