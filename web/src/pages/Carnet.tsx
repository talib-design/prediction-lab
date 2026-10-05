import { CarnetBetsChart } from "../components/BetsChart";
import { useMemo, useState } from "react";
import { IntervalChart } from "../components/charts";
import { DeltaChip, duelState, pct1, plural, signed } from "../components/duel";
import { Card, DisciplineBadge, Empty, Failure, Kpi, Loading, PageHead, Segmented } from "../components/ui";
import { api, type CarnetEntry, type CarnetTicket } from "../lib/api";
import { euros, int, longDay, pct, shiftDay, shortDay, signedPct, time, todayParis } from "../lib/format";
import { href, useApi } from "../lib/hooks";
import { ticketTitle } from "../lib/tickets";

export function TicketList({ tickets, settled }: { tickets: CarnetTicket[]; settled: boolean }) {
  if (tickets.length === 0) return <span className="muted small">aucun ticket (paris non proposés)</span>;
  return (
    <div className="row" style={{ gap: 6 }}>
      {tickets.map((t, i) => {
        const won = settled && (t.returned ?? 0) > 0;
        return (
          <span
            key={`${t.strategy}-${i}`}
            className={`chip ${!settled ? "played" : won ? "won" : "lost"}`}
            title={`Mise ${euros(t.stake)}`}
          >
            {ticketTitle(t)} · n°{t.numbers.join("-")}
            {settled && (won ? ` · ${euros(t.returned)}` : " · perdu")}
          </span>
        );
      })}
    </div>
  );
}

// ------------------------------------------------------------------ periods

type Period = "jour" | "semaine" | "mois" | "tout";
const PERIODS: { value: Period; label: string }[] = [
  { value: "jour", label: "Jour" },
  { value: "semaine", label: "Semaine" },
  { value: "mois", label: "Mois" },
  { value: "tout", label: "Tout" },
];
const isPeriod = (x: string | undefined): x is Period => PERIODS.some((p) => p.value === x);
const isDay = (x: string | undefined): x is string => !!x && /^\d{4}-\d{2}-\d{2}$/.test(x);

const weekStart = (d: string) => shiftDay(d, -((new Date(`${d}T12:00:00Z`).getUTCDay() + 6) % 7));
const monthStart = (d: string) => `${d.slice(0, 8)}01`;
function monthEnd(d: string): string {
  const [y, m] = d.split("-").map(Number) as [number, number];
  return `${d.slice(0, 8)}${String(new Date(Date.UTC(y, m, 0)).getUTCDate()).padStart(2, "0")}`;
}
function shiftMonth(d: string, k: number): string {
  const [y, m] = d.split("-").map(Number) as [number, number];
  return new Date(Date.UTC(y, m - 1 + k, 1)).toISOString().slice(0, 10);
}

/** First and last day (inclusive) of the period holding `anchor`. */
function spanOf(period: Period, anchor: string, first: string, last: string): [string, string] {
  if (period === "jour") return [anchor, anchor];
  if (period === "semaine") return [weekStart(anchor), shiftDay(weekStart(anchor), 6)];
  if (period === "mois") return [monthStart(anchor), monthEnd(anchor)];
  return [first, last];
}

const dayMonth = (d: string, withYear = false) =>
  new Intl.DateTimeFormat("fr-FR", {
    day: "numeric",
    month: "long",
    ...(withYear ? { year: "numeric" } : {}),
    timeZone: "UTC",
  }).format(new Date(`${d}T00:00:00Z`));
const capital = (x: string) => x.charAt(0).toUpperCase() + x.slice(1);

function periodTitle(period: Period, [start, end]: [string, string]): string {
  if (period === "jour") return capital(longDay(start));
  if (period === "semaine")
    return start.slice(0, 7) === end.slice(0, 7)
      ? `Semaine du ${Number(start.slice(8))} au ${dayMonth(end, true)}`
      : `Semaine du ${dayMonth(start)} au ${dayMonth(end, true)}`;
  if (period === "mois")
    return capital(
      new Intl.DateTimeFormat("fr-FR", { month: "long", year: "numeric", timeZone: "UTC" }).format(
        new Date(`${start}T00:00:00Z`),
      ),
    );
  return `Depuis le ${shortDay(start)}`;
}

const go = (period: Period, day: string) => (location.hash = href("carnet", period, day));

const weekdayTime = (iso: string) =>
  new Intl.DateTimeFormat("fr-FR", {
    weekday: "short",
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Europe/Paris",
  }).format(new Date(iso));

// ------------------------------------------------------------------ the duel, race by race

const diffOf = (e: CarnetEntry) =>
  e.duel && e.duel.model.net != null && e.duel.favori.net != null ? e.duel.model.net - e.duel.favori.net : null;

const favouriteNumbers = (e: CarnetEntry) =>
  e.duel?.favori.numbers ?? e.tickets.find((t) => t.strategy === "SG favori")?.numbers ?? [];

/** Model against favourite over the period's races: the same figures as the cards on
 *  the Courses page. */
function PeriodSummary({ entries }: { entries: CarnetEntry[] }) {
  const settled = entries.filter((e) => e.settled);
  const duels = settled.flatMap((e) => (e.duel ? [e.duel] : []));
  const side = (k: "model" | "favori") => {
    const stake = duels.reduce((a, d) => a + d[k].stake, 0);
    const returned = duels.reduce((a, d) => a + d[k].returned, 0);
    return { net: returned - stake, roi: stake ? returned / stake - 1 : null };
  };
  const model = side("model");
  const fav = side("favori");
  const sg = duels.filter((d) => d.model.win != null && d.favori.win != null);
  const pending = entries.length - settled.length;
  return (
    <div className="period-summary">
      <div className="period-counts small">
        <span>
          <strong className="num">{entries.length}</strong> <span className="muted">course{plural(entries.length)} jouée{plural(entries.length)}</span>
        </span>
        <span>
          <strong className="num">{duels.length}</strong> <span className="muted">comparée{plural(duels.length)} (réglées, modèle et favori)</span>
        </span>
        {pending > 0 && <span className="muted">{pending} en attente du rapport</span>}
      </div>
      {duels.length > 0 ? (
        <div className="period-duel">
          <span className="overview-side">
            <i className="side-mark model" aria-hidden />
            Modèle <strong className="num period-net">{signed(model.net)}</strong>
            <span className="muted num">{pct1(model.roi)}</span>
          </span>
          <span className="overview-side">
            <i className="side-mark favori" aria-hidden />
            Favori <strong className="num period-net">{signed(fav.net)}</strong>
            <span className="muted num">{pct1(fav.roi)}</span>
          </span>
          <DeltaChip diff={model.net - fav.net} />
          <span className="small muted">
            Choix différents : {duels.filter((d) => d.differ).length} sur {duels.length}
          </span>
          {sg.length > 0 && (
            <span className="small muted">
              En gagnant : favori {sg.filter((d) => d.favori.win).length}/{sg.length}, modèle{" "}
              {sg.filter((d) => d.model.win).length}/{sg.length}
            </span>
          )}
        </div>
      ) : (
        <div className="small muted">Aucune course comparée sur cette période : le modèle n'y a pas joué, ou rien n'est encore réglé.</div>
      )}
    </div>
  );
}

type SortKey = "off" | "favori" | "model" | "diff";
type Show = "all" | "paired" | "differ";

function SortHead({
  k,
  label,
  sort,
  setSort,
  right,
  title,
}: {
  k: SortKey;
  label: string;
  sort: { key: SortKey; desc: boolean };
  setSort: (s: { key: SortKey; desc: boolean }) => void;
  right?: boolean;
  title?: string;
}) {
  const on = sort.key === k;
  return (
    <th className={right ? "r" : undefined} aria-sort={on ? (sort.desc ? "descending" : "ascending") : "none"} title={title}>
      <button className={`th-sort${on ? " on" : ""}`} onClick={() => setSort({ key: k, desc: on ? !sort.desc : true })}>
        {label}
        <span aria-hidden className="th-arrow">
          {on ? (sort.desc ? "↓" : "↑") : "↕"}
        </span>
      </button>
    </th>
  );
}

function Net({ v, pending }: { v: number | null | undefined; pending: boolean }) {
  if (pending) return <span className="muted small">en attente</span>;
  if (v == null) return <span className="muted">—</span>;
  return <span className="num">{signed(v)}</span>;
}

function DuelRow({ e, open, toggle, withDay }: { e: CarnetEntry; open: boolean; toggle: () => void; withDay: boolean }) {
  const d = e.duel;
  const diff = diffOf(e);
  const state = diff == null ? null : duelState(diff);
  const top = e.finish_order?.slice(0, 3).map((g) => g.join("=")).join("-");
  return (
    <>
      <tr className={`clickable${d?.differ ? " differ" : ""}`} onClick={toggle}>
        <td className="num nowrap">{withDay ? weekdayTime(e.off_time) : time(e.off_time)}</td>
        <td>
          <span className="row" style={{ gap: 6, flexWrap: "nowrap" }}>
            <a href={href("course", e.day, e.rc)} onClick={(ev) => ev.stopPropagation()} className="nowrap">
              {e.rc}
            </a>
            <span className="muted small nowrap">{e.venue}</span>
            <DisciplineBadge d={e.discipline} />
            {e.has_quinte && <span className="badge k-assoc">Quinté+</span>}
          </span>
        </td>
        <td className="r num">{favouriteNumbers(e).map((n) => `n°${n}`).join("-") || "—"}</td>
        <td className="r num">
          {d ? (
            d.differ ? (
              <strong className="pick-differ" title="Le modèle a choisi un autre cheval que le favori">
                ≠ n°{d.model.numbers.join("-")}
              </strong>
            ) : (
              `n°${d.model.numbers.join("-")}`
            )
          ) : (
            <span className="muted" title="Le modèle n'a pas joué cette course : hors comparaison">
              —
            </span>
          )}
        </td>
        <td className="num small">{e.settled ? top || "—" : <span className="muted">—</span>}</td>
        <td className="r">
          <Net v={d?.favori.net} pending={!e.settled && !!d} />
        </td>
        <td className="r">
          <Net v={d?.model.net} pending={!e.settled && !!d} />
        </td>
        <td className="r">
          {state == null || diff == null ? (
            <span className="muted">—</span>
          ) : state === "same" ? (
            <span className="muted" title="Même résultat">
              =
            </span>
          ) : (
            <span className={`diff ${state}`}>
              <span aria-hidden>{state === "ahead" ? "▲" : "▼"}</span> {signed(diff)}
            </span>
          )}
        </td>
        <td className="r">
          <button
            className="btn icon row-toggle"
            aria-expanded={open}
            aria-label={open ? "Masquer les tickets" : "Voir les tickets"}
            onClick={(ev) => {
              ev.stopPropagation();
              toggle();
            }}
          >
            {open ? "▾" : "▸"}
          </button>
        </td>
      </tr>
      {open && (
        <tr className="duel-detail">
          <td colSpan={9}>
            <div className="stack" style={{ gap: 8 }}>
              <TicketList tickets={e.tickets} settled={e.settled} />
              <span className="small muted">
                figé à {time(e.frozen_at)} · cotes de {time(e.odds_as_of)}
                {e.settled && ` · arrivée ${e.finish_order?.map((g) => g.join("=")).join("-") ?? "—"}`}
                {e.note && ` · ${e.note}`} · <a href={href("course", e.day, e.rc)}>voir la course →</a>
              </span>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

function DuelTable({ entries, withDay }: { entries: CarnetEntry[]; withDay: boolean }) {
  const [sort, setSort] = useState<{ key: SortKey; desc: boolean }>({ key: "off", desc: true });
  const [show, setShow] = useState<Show>("all");
  const [open, setOpen] = useState<Set<string>>(new Set());
  const paired = entries.filter((e) => e.duel);
  const differ = paired.filter((e) => e.duel!.differ);
  const rows = useMemo(() => {
    const base = show === "all" ? entries : show === "paired" ? paired : differ;
    const value = (e: CarnetEntry): number | string | null =>
      sort.key === "off"
        ? e.off_time
        : sort.key === "favori"
          ? (e.duel?.favori.net ?? null)
          : sort.key === "model"
            ? (e.duel?.model.net ?? null)
            : diffOf(e);
    return [...base].sort((a, b) => {
      const x = value(a);
      const y = value(b);
      if (x == null || y == null) return x == null ? (y == null ? 0 : 1) : -1; // no value: last
      const c = x < y ? -1 : x > y ? 1 : 0;
      return (sort.desc ? -c : c) || b.off_time.localeCompare(a.off_time);
    });
  }, [entries, paired, differ, show, sort]);
  const toggle = (id: string) =>
    setOpen((s) => {
      const n = new Set(s);
      if (n.has(id)) n.delete(id);
      else n.add(id);
      return n;
    });
  return (
    <>
      <div className="duel-filters">
        <Segmented<Show>
          label="Courses affichées"
          value={show}
          onChange={setShow}
          options={[
            { value: "all", label: `Toutes (${entries.length})` },
            { value: "paired", label: `Comparées (${paired.length})` },
            { value: "differ", label: `Choix différents (${differ.length})` },
          ]}
        />
        <span className="small muted">Gains nets en gagnant + placé, 1 € par ticket. Clic sur une ligne : ses tickets.</span>
      </div>
      {rows.length === 0 ? (
        <Empty title="Aucune course ici">
          <p className="small">
            {show === "differ"
              ? "Le modèle n'a choisi aucun autre cheval que le favori sur cette période."
              : "Le modèle n'a joué aucune de ces courses (ou elles ne sont pas encore réglées)."}
          </p>
        </Empty>
      ) : (
        <div className="table-wrap">
          <table className="duel-table">
            <thead>
              <tr>
                <SortHead k="off" label="Départ" sort={sort} setSort={setSort} />
                <th>Course</th>
                <th className="r">Favori</th>
                <th className="r">Modèle</th>
                <th>Arrivée</th>
                <SortHead k="favori" label="Net favori" sort={sort} setSort={setSort} right />
                <SortHead k="model" label="Net modèle" sort={sort} setSort={setSort} right />
                <SortHead k="diff" label="Écart" sort={sort} setSort={setSort} right title="Net du modèle moins net du favori" />
                <th aria-label="Tickets" />
              </tr>
            </thead>
            <tbody>
              {rows.map((e) => (
                <DuelRow key={e.race_id} e={e} open={open.has(e.race_id)} toggle={() => toggle(e.race_id)} withDay={withDay} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function Evolution() {
  const load = useApi(() => api.periods(), "carnet-series", 120_000);
  if (load.state !== "ready") return null;
  return (
    <Card title="Suivi des paris, jour par jour" aside={<span className="muted small">gains cumulés : favori contre modèle</span>}>
      <CarnetBetsChart series={load.data.series} />
    </Card>
  );
}

export function Carnet({ period: rawPeriod, day: rawDay }: { period?: string; day?: string }) {
  const load = useApi(() => api.carnet(), "carnet", 60_000);
  if (load.state === "loading") return <Loading rows={6} />;
  if (load.state === "error") return <Failure error={load.error} />;
  const c = load.data;
  const period: Period = isPeriod(rawPeriod) ? rawPeriod : "jour";
  const last = c.days[0] ?? todayParis();
  const first = c.first_day ?? last;
  const anchor = isDay(rawDay) ? rawDay : last;
  const span = spanOf(period, anchor, first, last);
  const shown = c.entries.filter((e) => e.day >= span[0] && e.day <= span[1]);
  // Jour: the previous / next day that has tickets; week and month: the calendar.
  const prev =
    period === "jour"
      ? c.days.find((d) => d < anchor)
      : period === "semaine"
        ? shiftDay(span[0], -7)
        : shiftMonth(span[0], -1);
  const next =
    period === "jour"
      ? [...c.days].reverse().find((d) => d > anchor)
      : period === "semaine"
        ? shiftDay(span[0], 7)
        : shiftMonth(span[0], 1);
  const canPrev = !!prev && span[0] > first;
  const canNext = !!next && span[1] < last;
  const settledRows = c.summary.filter((r) => r.races > 0);
  const withCi = settledRows.filter((r) => r.roi_low != null && !Number.isNaN(r.roi_low));
  return (
    <>
      <PageHead
        crumbs="Paris fictifs en conditions réelles"
        title="Carnet"
        lead="Chaque ticket est figé 25 minutes avant le départ, avec les seules cotes connues à ce moment, puis réglé au rapport officiel. Aucune mise réelle. Rien n'est jamais réécrit : c'est la seule preuve qui ne dépend pas du passé."
      />
      <div className="stack">
        <Card
          title={periodTitle(period, span)}
          aside={
            <div className="row carnet-nav">
              <Segmented<Period> label="Période" value={period} options={PERIODS} onChange={(p) => go(p, anchor)} />
              {period !== "tout" && (
                <>
                  <button className="btn icon" aria-label="Période précédente" disabled={!canPrev} onClick={() => prev && go(period, prev)}>
                    ‹
                  </button>
                  <input
                    type="date"
                    value={anchor}
                    min={first}
                    max={last}
                    aria-label="Choisir une date"
                    onChange={(ev) => ev.target.value && go(period, ev.target.value)}
                  />
                  <button className="btn icon" aria-label="Période suivante" disabled={!canNext} onClick={() => next && go(period, next)}>
                    ›
                  </button>
                </>
              )}
            </div>
          }
          flush
        >
          {shown.length === 0 ? (
            <Empty title="Aucun ticket figé sur cette période">
              <p className="small">
                Les tickets sont écrits par le collecteur dans la fenêtre des 25 minutes avant chaque départ ; une course
                manquée (Mac en veille) n'est jamais rattrapée.
              </p>
            </Empty>
          ) : (
            <>
              <PeriodSummary entries={shown} />
              <DuelTable entries={shown} withDay={period !== "jour"} />
            </>
          )}
        </Card>
        {c.integrity_error ? (
          <div className="note warn">
            <span>
              <strong>Carnet altéré.</strong> {c.integrity_error}
            </span>
          </div>
        ) : (
          <div className="note small">
            <span>
              Chaîne de hash intacte · {int(c.records)} enregistrements · empreinte{" "}
              <code className="mono">
                {c.head_hash.slice(0, 8)}…{c.head_hash.slice(-6)}
              </code>
              . Un commit git du fichier <code className="mono">data/carnet.jsonl</code> date publiquement ce qui a été
              écrit.
            </span>
          </div>
        )}
        <div className="kpis">
          <Kpi label="Suivi depuis" value={c.first_day ? shortDay(c.first_day) : "—"} sub="figé par le collecteur, toutes les 5 min" />
          <Kpi label="Courses figées" value={int(c.races)} kind="fact" sub="départs manqués (Mac en veille) : jamais rattrapés" />
          <Kpi label="Réglées" value={int(c.settled)} kind="fact" sub={`${int(c.races - c.settled)} en attente du rapport`} />
        </div>

        <Evolution />

        <Card
          title="Bilan par stratégie"
          aside={
            <span className="muted small">
              toutes les courses depuis le {c.first_day ? shortDay(c.first_day) : "—"}, quelle que soit la période choisie · 1 € par
              ticket
            </span>
          }
        >
          {settledRows.length === 0 ? (
            <Empty title="Pas encore de course réglée">
              <p className="small">
                Le bilan apparaît après la première arrivée officielle. Les intervalles de confiance, à partir de 10 courses
                réglées par stratégie ; un verdict sérieux demande des centaines de courses.
              </p>
            </Empty>
          ) : (
            <div className="stack">
              {withCi.length > 0 && (
                <IntervalChart
                  rows={withCi.map((r) => ({
                    label: r.label,
                    est: r.roi ?? 0,
                    lo: r.roi_low,
                    hi: r.roi_high,
                    tone: r.strategy.includes("hasard") ? "muted" : "neutral",
                  }))}
                  format={(v) => signedPct(v)}
                  zeroLabel="à l'équilibre"
                />
              )}
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Stratégie</th>
                      <th className="r">Courses</th>
                      <th className="r">Misé</th>
                      <th className="r">Rapporté</th>
                      <th className="r">ROI</th>
                      <th className="r">IC 95 %</th>
                      <th className="r">Réussite</th>
                      <th className="r">En attente</th>
                      <th>Verdict</th>
                    </tr>
                  </thead>
                  <tbody>
                    {c.summary.map((r) => (
                      <tr key={r.strategy} className={r.races ? undefined : "dim"}>
                        <td>{r.label}</td>
                        <td className="r num">{int(r.races)}</td>
                        <td className="r num">{euros(r.stake)}</td>
                        <td className="r num">{euros(r.returned)}</td>
                        <td className="r num" style={{ fontWeight: 600 }}>
                          {signedPct(r.roi)}
                        </td>
                        <td className="r num muted">
                          {r.roi_low != null && !Number.isNaN(r.roi_low)
                            ? `${signedPct(r.roi_low, 0)} ; ${signedPct(r.roi_high, 0)}`
                            : "—"}
                        </td>
                        <td className="r num">{pct(r.hit_rate)}</td>
                        <td className="r num">{int(r.pending)}</td>
                        <td>{r.verdict ? <span className="badge outline">{r.verdict}</span> : <span className="muted">—</span>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </Card>

      </div>
    </>
  );
}
