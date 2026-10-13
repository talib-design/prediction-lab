// EuroMillions P&L, racing-carnet style: one card per grid (8 logics + the chance witness)
// with the leader highlighted, then the series of cumulative curves. The leader (or the
// card you pick) is drawn in colour, the witness in the "reference" colour, the rest in
// grey: nine categorical hues would be noise. The band shows where chance ends up.
import { type ReactNode, useEffect, useMemo, useRef, useState } from "react";
import { Segmented } from "./ui";
import { emLogic } from "./em";
import type { EmCurves } from "../lib/api";
import { euros, fmt, shortDay } from "../lib/format";

type Mode = "grid" | "total";
type Range = "last" | "1w" | "1m" | "3m" | "6m" | "1y" | "all";

const RANGES: { value: Range; label: string; days: number }[] = [
  { value: "last", label: "Dernier", days: 0 },
  { value: "1w", label: "1S", days: 7 },
  { value: "1m", label: "1M", days: 31 },
  { value: "3m", label: "3M", days: 92 },
  { value: "6m", label: "6M", days: 183 },
  { value: "1y", label: "1A", days: 366 },
  { value: "all", label: "Tout", days: Infinity },
];
const MONTHS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."];
const WITNESS = "temoin_r1";
const DAY_MS = 86_400_000;
const dayNum = (d: string) => Date.parse(`${d}T00:00:00Z`) / DAY_MS;
const signed = (x: number) => `${x >= 0 ? "+" : "−"}${euros(Math.abs(x))}`;
const signed0 = (x: number) => `${x >= 0 ? "+" : "−"}${Math.round(Math.abs(x)).toLocaleString("fr-FR")} €`;
const pct = (r: number) => `${r >= 0 ? "+" : "−"}${fmt(Math.abs(r) * 100, 1)} %`;

type Pnl = { key: string; net: number; stake: number; roi: number; wins: number; cum: number[] };

function niceTicks(lo: number, hi: number, n: number): number[] {
  const span = hi - lo || 1;
  const raw = span / n;
  const pow = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((k) => k * pow).find((s) => s >= raw) ?? raw;
  const out: number[] = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(Math.round(v * 100) / 100);
  if (!out.includes(0) && lo <= 0 && hi >= 0) out.push(0);
  return out.sort((a, b) => a - b);
}

function xLabels(days: string[], narrow: boolean): { i: number; text: string }[] {
  const max = narrow ? 4 : 9;
  if (days.length < 2) return days.map((d, i) => ({ i, text: shortDay(d).slice(0, 5) }));
  const span = dayNum(days[days.length - 1]!) - dayNum(days[0]!);
  if (span <= 75) {
    const every = Math.max(1, Math.ceil(days.length / max));
    return days.map((d, i) => ({ i, text: shortDay(d).slice(0, 5) })).filter((_, i) => i % every === 0 || i === days.length - 1);
  }
  const starts: { i: number; text: string }[] = [];
  let prev = "";
  days.forEach((d, i) => {
    const key = span > 900 ? d.slice(0, 4) : d.slice(0, 7);
    if (key !== prev && i > 0)
      starts.push({ i, text: span > 900 ? d.slice(0, 4) : `${MONTHS[Number(d.slice(5, 7)) - 1]} ${d.slice(2, 4)}` });
    prev = key;
  });
  const every = Math.max(1, Math.ceil(starts.length / max));
  return starts.filter((_, k) => k % every === 0);
}

/** "mieux que 54 % du hasard", flagged when outside the 2.5-97.5 % band. */
function Beat({ p }: { p: number }) {
  const out = p < 0.025 || p > 0.975;
  return (
    <span className={`small ${out ? "" : "muted"}`}>
      mieux que {fmt(p * 100, 0)} % du hasard
      {out && <span className="badge k-assoc" style={{ marginLeft: 6 }}>hors bande</span>}
    </span>
  );
}

function useWidth(fallback: number) {
  const ref = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(fallback);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => e && setW(Math.max(300, Math.round(e.contentRect.width))));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return [ref, w] as const;
}

export function EmPnl({
  curves,
  title,
  note,
  defaultGap = false,
}: {
  curves: EmCurves;
  title: string;
  note?: ReactNode;
  /** Start on « écart au hasard » (long histories, where the stake slope hides everything). */
  defaultGap?: boolean;
}) {
  const [range, setRange] = useState<Range>("all");
  const [mode, setMode] = useState<Mode>("grid");
  const [gap, setGap] = useState(defaultGap);
  const [picked, setPicked] = useState<string | null>(null);
  const [hover, setHover] = useState<number | null>(null);
  const [wrap, width] = useWidth(900);

  const n = curves.dates.length;
  const lastDay = curves.dates[n - 1] ?? "";
  const spanDays = n ? dayNum(lastDay) - dayNum(curves.dates[0]!) : 0;
  const choices = RANGES.filter((r) => r.value === "all" || r.value === "last" || r.days < spanDays + 1);
  const active = choices.some((c) => c.value === range) ? range : "all";
  const start = useMemo(() => {
    if (active === "all") return 0;
    if (active === "last") return Math.max(0, n - 1);
    const r = RANGES.find((x) => x.value === active)!;
    const from = dayNum(lastDay) - r.days + 1;
    const i = curves.dates.findIndex((d) => dayNum(d) >= from);
    return i < 0 ? 0 : i;
  }, [active, n, lastDay, curves.dates]);
  const days = curves.dates.slice(start);
  const len = days.length;
  const full = active === "all";

  const names = Object.keys(curves.grids);
  const pnl: Pnl[] = useMemo(
    () =>
      names.map((key) => {
        const pays = (curves.grids[key] ?? []).slice(start);
        let acc = 0;
        const cum = pays.map((p) => (acc += (p ?? 0) - curves.price));
        return {
          key,
          net: acc,
          stake: curves.price * pays.length,
          roi: pays.length ? acc / (curves.price * pays.length) : 0,
          wins: pays.filter((p) => (p ?? 0) > 0).length,
          cum,
        };
      }),
    [curves, start], // eslint-disable-line react-hooks/exhaustive-deps
  );
  const ranked = [...pnl].sort((a, b) => b.net - a.net);
  const leader = ranked[0]!;
  const focus = pnl.find((p) => p.key === (picked ?? leader.key)) ?? leader;
  const witness = pnl.find((p) => p.key === WITNESS);
  const total = days.map((_, i) => pnl.reduce((a, p) => a + (p.cum[i] ?? 0), 0));
  const totalNet = total[len - 1] ?? 0;
  const totalStake = curves.price * curves.n_grids * len;

  const band = full ? (mode === "grid" ? curves.single_band : curves.total_band) : null;
  const shift = (v: number[]) => (gap && band ? v.map((x, i) => x - (band.q500[i] ?? 0)) : v);
  const lo = band ? shift(band.q025) : null;
  const mid = band ? shift(band.q500) : null;
  const hi = band ? shift(band.q975) : null;

  const W = width;
  const narrow = W < 560;
  const H = narrow ? 240 : 300;
  const m = { top: 14, right: narrow ? 92 : 190, bottom: 28, left: narrow ? 52 : 66 };
  const iw = W - m.left - m.right;
  const ih = H - m.top - m.bottom;

  const lineSet =
    mode === "grid"
      ? pnl.map((p) => ({ key: p.key, values: shift(p.cum) }))
      : [{ key: "total", values: shift(total) }];
  const vals = [...lineSet.flatMap((l) => l.values), ...(lo ?? []), ...(hi ?? []), 0];
  const vMin = Math.min(...vals);
  const vMax = Math.max(...vals);
  const pad = Math.max(2, (vMax - vMin) * 0.08);
  const yLo = vMin - pad;
  const yHi = vMax + pad;
  const x = (i: number) => m.left + (len <= 1 ? iw / 2 : (i / (len - 1)) * iw);
  const y = (v: number) => m.top + ih - ((v - yLo) / (yHi - yLo)) * ih;
  const poly = (v: number[]) => v.map((val, i) => `${x(i).toFixed(1)},${y(val).toFixed(1)}`).join(" ");
  const area =
    lo && hi && len > 1
      ? `M${hi.map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join("L")}L${lo
          .map((_, j) => {
            const i = len - 1 - j;
            return `${x(i).toFixed(1)},${y(lo[i]!).toFixed(1)}`;
          })
          .join("L")}Z`
      : null;
  const markers = len <= 45;

  const focusKey = mode === "grid" ? focus.key : "total";
  const colorOf = (k: string) =>
    k === focusKey ? "var(--series-model)" : k === WITNESS ? "var(--series-favori)" : "var(--ink-3)";
  const order = [...lineSet].sort((a, b) => (a.key === focusKey ? 1 : 0) - (b.key === focusKey ? 1 : 0) || (a.key === WITNESS ? 1 : 0) - (b.key === WITNESS ? 1 : 0));
  const labelled = lineSet.filter((l) => l.key === focusKey || l.key === WITNESS);
  const ends = labelled
    .map((l) => ({ l, ly: y(l.values[len - 1] ?? 0) }))
    .sort((a, b) => a.ly - b.ly);
  for (let i = 1; i < ends.length; i++)
    if (ends[i]!.ly - ends[i - 1]!.ly < 15) {
      const c = (ends[i]!.ly + ends[i - 1]!.ly) / 2;
      ends[i - 1]!.ly = c - 7.5;
      ends[i]!.ly = c + 7.5;
    }
  const nameOf = (k: string) => (k === "total" ? `Les ${curves.n_grids} grilles` : emLogic(k));

  const onMove = (e: React.MouseEvent<SVGRectElement>) => {
    const r = (e.currentTarget.ownerSVGElement as SVGSVGElement).getBoundingClientRect();
    const px = ((e.clientX - r.left) / r.width) * W;
    const i = len <= 1 ? 0 : Math.round(((px - m.left) / iw) * (len - 1));
    setHover(Math.max(0, Math.min(len - 1, i)));
  };
  const hx = hover == null ? 0 : x(hover);
  const fmtV = (v: number) => (gap ? signed0(v) : signed(v));

  return (
    <div className="stack">
      <div className="row" style={{ justifyContent: "space-between" }}>
        <h3 className="bets-h3">{title}</h3>
        <span className="small muted">
          {len} tirage{len > 1 ? "s" : ""} · du {shortDay(days[0] ?? lastDay)} au {shortDay(lastDay)} · {euros(curves.price)} la grille
        </span>
      </div>

      <div className="pnl-grid" role="list" aria-label="Gains et pertes par grille">
        <button
          type="button"
          role="listitem"
          className={`card pnl-card total${mode === "total" ? " on" : ""}`}
          onClick={() => setMode(mode === "total" ? "grid" : "total")}
          aria-pressed={mode === "total"}
        >
          <span className="kpi-label">Les {curves.n_grids} grilles ensemble</span>
          <span className="pnl-net num">{signed(totalNet)}</span>
          <span className="small muted num">
            {pct(totalStake ? totalNet / totalStake : 0)} · {euros(totalStake)} misés
          </span>
          {full && <Beat p={curves.total_percentile} />}
        </button>
        {ranked.map((p, i) => {
          const pctl = curves.percentile?.[p.key];
          const isLeader = i === 0;
          return (
            <button
              type="button"
              role="listitem"
              key={p.key}
              className={`card pnl-card${isLeader ? " leader" : ""}${mode === "grid" && p.key === focus.key ? " on" : ""}${p.key === WITNESS ? " witness" : ""}`}
              onClick={() => {
                setMode("grid");
                setPicked(p.key === leader.key ? null : p.key);
              }}
              aria-pressed={mode === "grid" && p.key === focus.key}
            >
              <span className="pnl-head">
                <span className="pnl-rank num">{i + 1}</span>
                <span className="kpi-label">{emLogic(p.key)}</span>
                {isLeader && <span className="delta-chip ahead">▲ en tête</span>}
              </span>
              <span className="pnl-net num">{signed(p.net)}</span>
              <span className="small muted num">
                {pct(p.roi)} · {p.wins} grille{p.wins > 1 ? "s" : ""} gagnante{p.wins > 1 ? "s" : ""}
              </span>
              {full && pctl != null && <Beat p={pctl} />}
            </button>
          );
        })}
      </div>

      <div className="card card-body bets-evolution">
        <div className="row" style={{ justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
          <div className="legend" aria-label="Légende">
            {mode === "grid" ? (
              <>
                <span>
                  <svg width="26" height="10" aria-hidden>
                    <line x1="1" x2="25" y1="5" y2="5" stroke="var(--series-model)" strokeWidth={3} strokeLinecap="round" />
                  </svg>
                  {emLogic(focus.key)}
                  {focus.key === leader.key ? " (en tête)" : ""}
                </span>
                {focus.key !== WITNESS && (
                  <span>
                    <svg width="26" height="10" aria-hidden>
                      <line x1="1" x2="25" y1="5" y2="5" stroke="var(--series-favori)" strokeWidth={2.5} strokeDasharray="6 4" strokeLinecap="round" />
                    </svg>
                    Témoin hasard
                  </span>
                )}
                <span>
                  <svg width="26" height="10" aria-hidden>
                    <line x1="1" x2="25" y1="5" y2="5" stroke="var(--ink-3)" strokeWidth={1.5} strokeLinecap="round" opacity={0.6} />
                  </svg>
                  autres logiques
                </span>
              </>
            ) : (
              <span>
                <svg width="26" height="10" aria-hidden>
                  <line x1="1" x2="25" y1="5" y2="5" stroke="var(--series-model)" strokeWidth={3} strokeLinecap="round" />
                </svg>
                Les {curves.n_grids} grilles
              </span>
            )}
            {band && (
              <span>
                <svg width="26" height="10" aria-hidden>
                  <rect x="1" y="1" width="24" height="8" rx="2" className="pnl-band" />
                </svg>
                95 % du hasard
              </span>
            )}
          </div>
          <div className="row" style={{ gap: 8, flexWrap: "wrap" }}>
            {full && (
              <label className="small check">
                <input type="checkbox" checked={gap} onChange={(e) => setGap(e.target.checked)} /> Écart au hasard
              </label>
            )}
            <Segmented<Mode>
              label="Grilles"
              value={mode}
              onChange={setMode}
              options={[
                { value: "grid", label: "Par grille" },
                { value: "total", label: `Les ${curves.n_grids} grilles` },
              ]}
            />
          </div>
        </div>

        <div className="bets-svg-wrap" ref={wrap}>
          <svg className="chart" viewBox={`0 0 ${W} ${H}`} width={W} height={H} role="img" aria-label={`Gains cumulés, ${title}`}>
            {niceTicks(yLo, yHi, 5).map((v) => (
              <g key={v}>
                <line x1={m.left} x2={m.left + iw} y1={y(v)} y2={y(v)} className={v === 0 ? "zero" : "grid"} />
                <text x={m.left - 8} y={y(v) + 4} textAnchor="end">
                  {v === 0 ? "0 €" : signed0(v)}
                </text>
              </g>
            ))}
            {xLabels(days, narrow).map(({ i, text }) => (
              <text key={i} x={x(i)} y={H - 8} textAnchor="middle">
                {text}
              </text>
            ))}
            {area && <path d={area} className="pnl-band" />}
            {mid && len > 1 && <polyline points={poly(mid)} fill="none" className="pnl-mid" />}
            {order.map((l) => {
              const isFocus = l.key === focusKey;
              const isWitness = l.key === WITNESS;
              const color = colorOf(l.key);
              return (
                <g key={l.key} opacity={isFocus || isWitness ? 1 : 0.5}>
                  {len > 1 && (
                    <polyline
                      points={poly(l.values)}
                      fill="none"
                      stroke={color}
                      strokeWidth={isFocus ? (len > 200 ? 2.25 : 3) : isWitness ? 2 : 1.25}
                      strokeDasharray={isWitness && !isFocus ? "6 4" : undefined}
                      strokeLinejoin="round"
                      strokeLinecap="round"
                    />
                  )}
                  {(markers || len <= 1) &&
                    (isFocus || isWitness || len <= 1) &&
                    l.values.map((v, i) => (
                      <circle key={i} cx={x(i)} cy={y(v)} r={isFocus ? 4 : 3} fill={color} className="ring" />
                    ))}
                </g>
              );
            })}
            {ends.map(({ l, ly }) => (
              <text key={l.key} x={x(len - 1) + 10} y={ly + 4} className="end-label">
                {narrow ? fmtV(l.values[len - 1] ?? 0) : `${nameOf(l.key)} ${fmtV(l.values[len - 1] ?? 0)}`}
              </text>
            ))}
            {hover != null && <line x1={hx} x2={hx} y1={m.top} y2={m.top + ih} className="crosshair" pointerEvents="none" />}
            <rect x={m.left} y={m.top} width={iw} height={ih} fill="transparent" onMouseMove={onMove} onMouseLeave={() => setHover(null)} />
          </svg>
          {hover != null && (
            <div
              className="chart-tip"
              style={{ left: `${(hx / W) * 100}%`, transform: hx > W * 0.55 ? "translateX(calc(-100% - 12px))" : "translateX(12px)" }}
            >
              <strong>
                {shortDay(days[hover]!)} · {hover + 1}
                <sup>e</sup> tirage
              </strong>
              {(mode === "grid" ? [...ranked].sort((a, b) => (b.cum[hover] ?? 0) - (a.cum[hover] ?? 0)) : []).map((p) => (
                <div key={p.key} className="tip-row">
                  <i style={{ background: colorOf(p.key), opacity: p.key === focusKey || p.key === WITNESS ? 1 : 0.45 }} />
                  <span>{emLogic(p.key)}</span>
                  <span className="num">{fmtV(shift(p.cum)[hover] ?? 0)}</span>
                </div>
              ))}
              {mode === "total" && (
                <div className="tip-row">
                  <i style={{ background: "var(--series-model)" }} />
                  <span>Les {curves.n_grids} grilles</span>
                  <span className="num">{fmtV(shift(total)[hover] ?? 0)}</span>
                </div>
              )}
              {lo && hi && (
                <div className="tip-row">
                  <i className="pnl-band-swatch" />
                  <span>95 % du hasard</span>
                  <span className="num">
                    {signed0(lo[hover]!)} à {signed0(hi[hover]!)}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>

        {choices.length > 1 && (
          <div className="range-bar" role="group" aria-label="Période">
            {choices.map((r) => (
              <button key={r.value} aria-pressed={r.value === active} onClick={() => setRange(r.value)}>
                {r.label}
              </button>
            ))}
          </div>
        )}

        <p className="small muted" style={{ margin: "8px 0 0" }}>
          {full
            ? mode === "grid"
              ? `Bande : où finissent 95 % de ${curves.players.toLocaleString("fr-FR")} joueurs qui jouent une grille au hasard sur les mêmes tirages. Une courbe dans la bande, c'est un hasard comme un autre ; « hors bande » : moins bien que 97,5 % ou mieux que 97,5 % des joueurs au hasard, à regarder de près (avec 10 cartes, au moins une sort de la bande environ 4 fois sur 10 par pur hasard). `
              : `Bande : ces mêmes ${curves.n_grids} grilles rejouées contre ${curves.players.toLocaleString("fr-FR")} tirages au hasard, avec les vrais rapports (elle tient compte des grilles en double). `
            : "La bande du hasard n'est calculée que depuis le début (« Tout »). "}
          {gap ? "Écart au hasard : chaque courbe moins le joueur médian au hasard. " : ""}
          {note}
        </p>

        <details className="small">
          <summary className="muted">Voir les chiffres tirage par tirage</summary>
          <div className="table-wrap" style={{ maxHeight: 320, overflowY: "auto" }}>
            <table className="compact">
              <thead>
                <tr>
                  <th>Tirage</th>
                  <th className="r">{emLogic(focus.key)} (tirage → cumul)</th>
                  {witness && focus.key !== WITNESS && <th className="r">Témoin hasard (tirage → cumul)</th>}
                  <th className="r">Les {curves.n_grids} grilles (cumul)</th>
                </tr>
              </thead>
              <tbody>
                {[...days.keys()].reverse().slice(0, 400).map((i) => {
                  const pay = (k: string) => (curves.grids[k]?.[start + i] ?? 0) - curves.price;
                  return (
                    <tr key={days[i]}>
                      <td>{shortDay(days[i]!)}</td>
                      <td className="r num">
                        {signed(pay(focus.key))} → {signed(focus.cum[i] ?? 0)}
                      </td>
                      {witness && focus.key !== WITNESS && (
                        <td className="r num">
                          {signed(pay(WITNESS))} → {signed(witness.cum[i] ?? 0)}
                        </td>
                      )}
                      <td className="r num">{signed(total[i] ?? 0)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </details>
      </div>
    </div>
  );
}
