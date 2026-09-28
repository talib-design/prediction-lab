import { useMemo, useState } from "react";
import { DisciplineBadge, Empty, Failure, Loading, PageHead, Segmented } from "../components/ui";
import { api, type Discipline, type RaceSummary } from "../lib/api";
import { longDay, minutesUntil, relative, shiftDay, todayParis } from "../lib/format";
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

export function Today({ day }: { day?: string }) {
  const today = todayParis();
  const current = day ?? today;
  const load = useApi(() => api.day(current), current, current === today ? 120_000 : undefined);
  const [filter, setFilter] = useState<Filter>("ALL");
  const [quinteOnly, setQuinteOnly] = useState(false);

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
        <button className="btn" aria-pressed={quinteOnly} onClick={() => setQuinteOnly((q) => !q)}>
          Quinté+ seulement
        </button>
      </div>

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
