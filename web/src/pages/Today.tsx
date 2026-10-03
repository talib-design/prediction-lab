import { useMemo, useState } from "react";
import { DisciplineBadge, Empty, Failure, Loading, PageHead, Segmented } from "../components/ui";
import { BetsChart } from "../components/BetsChart";
import { ProfileButton, WinnersProfile } from "../components/WinnersProfile";
import { api, type CarnetState, type Discipline, type RaceSummary } from "../lib/api";
import { euros, longDay, minutesUntil, relative, shiftDay, shortDay, time, todayParis } from "../lib/format";
import { BET_LABEL, rule } from "../lib/tickets";
import { href, useApi } from "../lib/hooks";

type Filter = "ALL" | Discipline;

function statusOf(r: RaceSummary): { label: string; cls: string } {
  if (r.is_final) return { label: "Arrivée", cls: "outline" };
  if ((r.status ?? "").includes("ANNULEE")) return { label: "Annulée", cls: "warn" };
  const m = minutesUntil(r.off_time);
  if (m < 0) return { label: "Courue", cls: "outline" };
  if (m < 60) return { label: relative(m), cls: "k-market" };
  return { label: "À venir", cls: "outline" };
}

const signed = (x: number) => `${x >= 0 ? "+" : "−"}${euros(Math.abs(x))}`;

/** Where the fictitious bets stand: today, this week, this month, since the start. */
function BetsOverview() {
  const load = useApi(() => api.periods(), "periods", 120_000);
  if (load.state !== "ready") return null;
  const { periods, streak, days, series } = load.data;
  if (periods.every((p) => p.races === 0)) return null;
  const plural = (n: number) => (n > 1 ? "s" : "");
  return (
    <section className="overview" aria-label="Bilan des paris fictifs">
      <div className="overview-head">
        <h2>Bilan des paris fictifs</h2>
        <div
          className="streak"
          title="Jours consécutifs terminés en positif, parmi les jours joués (un jour sans pari est ignoré). Aujourd'hui compte tel qu'il est à cette heure."
        >
          <span className="streak-label">
            Série positive <strong className="num">{streak.current} jour{plural(streak.current)}</strong>
            <span className="muted"> · record {streak.best}</span>
          </span>
          <span className="streak-days" aria-hidden>
            {days.map((d) => (
              <i
                key={d.day}
                className={d.net > 0 ? "pos" : "neg"}
                title={`${shortDay(d.day)} : ${signed(d.net)} (${d.races} courses)`}
              />
            ))}
          </span>
        </div>
        <a href="#/carnet" className="small">
          voir le carnet →
        </a>
      </div>
      <div className="overview-grid">
        {periods.map((p) => (
          <a key={p.key} href="#/carnet" className="card overview-card">
            <div className="kpi-label">
              {p.label}
              {p.key === "all" && <span className="muted"> ({shortDay(p.start)})</span>}
            </div>
            <div className={`overview-net num ${p.net >= 0 ? "pos" : "neg"}`}>{p.settled ? signed(p.net) : "—"}</div>
            <dl className="overview-facts">
              <dt>Misé</dt>
              <dd className="num">{euros(p.stake)}</dd>
              <dt>Rapporté</dt>
              <dd className="num">{euros(p.returned)}</dd>
              <dt>Retour</dt>
              <dd className="num">{p.roi == null ? "—" : `${p.roi >= 0 ? "+" : "−"}${Math.abs(p.roi * 100).toFixed(0)} %`}</dd>
            </dl>
            <div className="small muted">
              {p.settled} course{p.settled > 1 ? "s" : ""} réglée{p.settled > 1 ? "s" : ""}
              {p.pending_stake > 0 && ` · ${euros(p.pending_stake)} en attente`}
            </div>
          </a>
        ))}
      </div>
      <div className="card card-body bets-evolution">
        <div className="row" style={{ justifyContent: "space-between", marginBottom: 4 }}>
          <h3 className="bets-h3">Évolution, jour par jour</h3>
          <span className="small muted">gains cumulés : la courbe monte quand on gagne, descend quand on perd</span>
        </div>
        <BetsChart series={series} />
      </div>
      <p className="small muted" style={{ margin: "6px 0 0" }}>
        Paris imaginaires, jamais placés : le favori et le choix du modèle Marché+, en gagnant et en placé, 1 € par
        ticket.
      </p>
    </section>
  );
}

/** The strategy bench in one line, under the carnet's balance: kept apart on purpose. */
function BancTeaser() {
  const load = useApi(() => api.banc(), "banc-teaser", 120_000);
  if (load.state !== "ready" || load.data.strategies.length === 0) return null;
  const d = load.data;
  const playing = d.strategies.filter((s) => s.status === "en test" || s.status === "gagnante");
  const best = [...playing].filter((s) => s.live.bets >= 20).sort((a, b) => (b.live.roi ?? -9) - (a.live.roi ?? -9))[0];
  const t = d.totals.today;
  return (
    <a href="#/banc" className="card banc-teaser">
      <strong>Banc d'essai</strong>
      <span className="small">
        {playing.length} stratégies en test · {d.counts.gagnante ?? 0} gagnante{(d.counts.gagnante ?? 0) > 1 ? "s" : ""}
      </span>
      <span className="small muted">
        aujourd'hui : {t.tickets} ticket{t.tickets > 1 ? "s" : ""} réglé{t.tickets > 1 ? "s" : ""}
        {t.tickets > 0 && `, net ${signed(t.net)}`}
      </span>
      {best && (
        <span className="small muted">
          meilleure en direct : {best.bet === "SG" ? "gagnant" : "placé"} · {best.criteria_list.map((k) => k.level).join(" + ")} (
          {best.live.roi != null && `${best.live.roi >= 0 ? "+" : "−"}${Math.abs(best.live.roi * 100).toFixed(0)} %`} sur{" "}
          {best.live.bets} paris)
        </span>
      )}
      <span className="small" style={{ marginLeft: "auto" }}>
        voir le banc →
      </span>
    </a>
  );
}

/** One line: what the lab played on this race, or when it will. */
function CarnetChip({ c }: { c?: CarnetState }) {
  if (!c) return null;
  if (c.state === "upcoming") return <span className="chip muted">tickets figés à {time(c.freeze_at)}</span>;
  if (c.state === "open") return <span className="chip muted">tickets en cours…</span>;
  if (c.state === "missed") return <span className="chip muted" title="Aucun ticket figé avant le départ (Mac en veille ou marché incomplet)">non jouée</span>;
  if (c.state === "cancelled") return null;
  const simple = (c.tickets ?? []).filter((t) => t.bet_type === "SIMPLE_GAGNANT" && rule(t.strategy) === "favori")[0];
  const pick = (c.tickets ?? []).filter((t) => t.bet_type === "SIMPLE_GAGNANT" && rule(t.strategy) === "modèle")[0];
  const modelPart = pick && simple && pick.numbers[0] !== simple.numbers[0] ? ` · n°${pick.numbers[0]} modèle` : pick ? " = modèle" : "";
  const played = (simple ? `n°${simple.numbers.join("-")}` : `${(c.tickets ?? []).length} tickets`) + (simple ? " favori" : "") + modelPart;
  if (c.state === "frozen")
    return (
      <span className="chip played" title={(c.tickets ?? []).map((t) => `${BET_LABEL[t.bet_type] ?? t.bet_type} ${rule(t.strategy)} : ${t.numbers.join("-")}`).join("\n")}>
        joué · {played}
      </span>
    );
  const net = (c.returned ?? 0) - (c.stake ?? 0);
  return (
    <span className={`chip ${net >= 0 ? "won" : "lost"}`} title={`Misé ${euros(c.stake)}, rapporté ${euros(c.returned)}`}>
      {played} · net {net >= 0 ? "+" : "−"}
      {euros(Math.abs(net))}
    </span>
  );
}

export function Today({ day }: { day?: string }) {
  const today = todayParis();
  const current = day ?? today;
  const load = useApi(() => api.day(current), current, current === today ? 120_000 : undefined);
  const [filter, setFilter] = useState<Filter>("ALL");
  const [quinteOnly, setQuinteOnly] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const meetings = useMemo(() => {
    if (load.state !== "ready") return [];
    const races = load.data.races.filter(
      (r) => (filter === "ALL" || r.discipline === filter) && (!quinteOnly || r.has_quinte),
    );
    const byMeeting = new Map<number, RaceSummary[]>();
    for (const r of races) byMeeting.set(r.meeting, [...(byMeeting.get(r.meeting) ?? []), r]);
    return [...byMeeting.entries()]
      .map(([meeting, rs]) => ({ meeting, races: rs, first: rs[0]! }))
      .sort((a, b) => a.first.off_time.localeCompare(b.first.off_time));
  }, [load, filter, quinteOnly]);

  const counts = useMemo(() => {
    const c: Record<string, number> = { ALL: 0, PLAT: 0, ATTELE: 0, MONTE: 0 };
    if (load.state === "ready")
      for (const r of load.data.races) {
        c.ALL = (c.ALL ?? 0) + 1;
        c[r.discipline] = (c[r.discipline] ?? 0) + 1;
      }
    return c;
  }, [load]);

  const next =
    load.state === "ready"
      ? load.data.races.find((r) => !r.is_final && minutesUntil(r.off_time) > 0)
      : undefined;

  return (
    <>
      <PageHead
        crumbs="Programme PMU · hippodromes français"
        title={<span style={{ textTransform: "capitalize" }}>{longDay(current)}</span>}
        lead={
          next ? (
            <>
              Prochain départ : <a href={href("course", next.day, next.rc)}>{next.off_local} · {next.venue} {next.rc}</a>{" "}
              ({relative(minutesUntil(next.off_time))}).
            </>
          ) : undefined
        }
        aside={
          <div className="row">
            <button className="btn icon" aria-label="Jour précédent" onClick={() => (location.hash = href("jour", shiftDay(current, -1)))}>
              ‹
            </button>
            <input
              type="date"
              value={current}
              aria-label="Choisir un jour"
              onChange={(e) => e.target.value && (location.hash = href("jour", e.target.value))}
            />
            <button className="btn icon" aria-label="Jour suivant" onClick={() => (location.hash = href("jour", shiftDay(current, 1)))}>
              ›
            </button>
            {current !== today && (
              <a className="btn" href="#/">
                Aujourd'hui
              </a>
            )}
          </div>
        }
      />

      <BetsOverview />
      <BancTeaser />

      <div className="row" style={{ justifyContent: "space-between", marginBottom: 16 }}>
        <Segmented<Filter>
          label="Discipline"
          value={filter}
          onChange={setFilter}
          options={[
            { value: "ALL", label: `Toutes · ${counts.ALL}` },
            { value: "PLAT", label: `Plat · ${counts.PLAT}` },
            { value: "ATTELE", label: `Attelé · ${counts.ATTELE}` },
            { value: "MONTE", label: `Monté · ${counts.MONTE}` },
          ]}
        />
        <div className="row">
          <ProfileButton onClick={() => setProfileOpen(true)} />
          <button className="btn" aria-pressed={quinteOnly} onClick={() => setQuinteOnly((q) => !q)}>
            Quinté+ seulement
          </button>
        </div>
      </div>
      <WinnersProfile
        open={profileOpen}
        onClose={() => setProfileOpen(false)}
        discipline={filter === "ALL" ? "PLAT" : filter}
      />

      {load.state === "loading" && <Loading rows={6} />}
      {load.state === "error" && <Failure error={load.error} />}
      {load.state === "ready" && load.data.programme_retrieved_at === null && (
        <div className="card">
          <Empty title="Aucun programme collecté pour ce jour">
            <p className="small">
              Le collecteur prend le programme du jour et du lendemain ; le rattrapage remonte le passé nuit après nuit.
            </p>
          </Empty>
        </div>
      )}
      {load.state === "ready" && load.data.programme_retrieved_at !== null && meetings.length === 0 && (
        <div className="card">
          <Empty title="Aucune course pour ce filtre" />
        </div>
      )}
      {meetings.map(({ meeting, races, first }) => (
        <section key={meeting} className="card meeting">
          <header className="card-head">
            <div className="row">
              <h2>
                R{meeting} · {first.venue}
              </h2>
              {first.going && <span className="badge k-fact">Terrain : {first.going.toLowerCase()}</span>}
            </div>
            <span className="muted small">{races.length} courses</span>
          </header>
          {races.map((r) => {
            const st = statusOf(r);
            return (
              <a key={r.rc} className={`race-row ${r.is_final ? "done" : ""}`} href={href("course", r.day, r.rc)}>
                <span className="race-time">{r.off_local}</span>
                <span className="race-rc">{r.rc}</span>
                <span className="race-name">
                  {r.name ?? "—"}
                  <span className="muted small">
                    {" "}
                    · {r.distance_m ? `${r.distance_m} m` : "—"} · {r.declared_runners ?? "?"} partants
                  </span>
                </span>
                <span className="race-meta">
                  <CarnetChip c={r.carnet} />
                  {r.has_quinte && <span className="badge k-assoc">Quinté+</span>}
                  <DisciplineBadge d={r.discipline} />
                  <span className={`badge ${st.cls}`}>{st.label}</span>
                  <span className="muted small num" title="Instantanés de cotes pris avant le départ">
                    {r.snapshots} inst.
                  </span>
                </span>
              </a>
            );
          })}
        </section>
      ))}
      {load.state === "ready" && load.data.other_races > 0 && (
        <p className="muted small" style={{ marginTop: 16 }}>
          {load.data.other_races} autres courses (étranger, obstacle) ne sont pas suivies par le laboratoire.
        </p>
      )}
    </>
  );
}
