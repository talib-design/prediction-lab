import { Card, DisciplineBadge, Empty, Failure, KindBadge, Kpi, Loading, PageHead } from "../components/ui";
import { api } from "../lib/api";
import { fmt, int, pct, shortDay } from "../lib/format";
import { href, useApi } from "../lib/hooks";

export function Horse({ id }: { id: string }) {
  const load = useApi(() => api.horse(id), id);
  if (load.state === "loading") return <Loading rows={6} />;
  if (load.state === "error") return <Failure error={load.error} />;
  const { horse, runs } = load.data;
  const ran = runs.filter((r) => r.status === "PARTANT");
  const wins = ran.filter((r) => r.position === 1).length;
  const places = ran.filter((r) => r.position != null && r.position <= 3).length;
  return (
    <>
      <PageHead
        crumbs="Cheval"
        title={horse.name}
        lead={
          <>
            {[horse.breed?.toLowerCase(), horse.birth_year && `né vers ${horse.birth_year}`].filter(Boolean).join(" · ")}
            <br />
            <span className="muted">
              par {horse.sire ?? "?"} et {horse.dam ?? "?"}
              {horse.dam_sire && ` (par ${horse.dam_sire})`}
            </span>
          </>
        }
      />
      <div className="stack">
        <div className="kpis">
          <Kpi label="Courses en base" value={int(ran.length)} kind="fact" sub={`${runs.length - ran.length} non-partant(s)`} />
          <Kpi label="Victoires" value={int(wins)} kind="fact" sub={ran.length ? pct(wins / ran.length, 0) : undefined} />
          <Kpi label="Top 3" value={int(places)} kind="fact" sub={ran.length ? pct(places / ran.length, 0) : undefined} />
        </div>
        <p className="note small">
          Seules les courses présentes dans la base apparaissent (plat depuis 2015, trot depuis 2017, au fil du
          rattrapage). Identité : <code className="mono">{horse.horse_id}</code>
        </p>
        <Card title="Courses" aside={<KindBadge kind="fact" />} flush>
          {runs.length === 0 ? (
            <Empty title="Aucune course" />
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Hippodrome</th>
                    <th>Discipline</th>
                    <th className="r">Distance</th>
                    <th>Terrain</th>
                    <th className="r">Place</th>
                    <th>Jockey / driver</th>
                    <th>Entraîneur</th>
                    <th className="r">Corde</th>
                    <th className="r">Poids</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.map((r) => {
                    const [day, rc] = r.race_id.split("/");
                    return (
                      <tr key={r.race_id} className="clickable" onClick={() => (location.hash = href("course", day!, rc!))}>
                        <td className="num">
                          <a href={href("course", day!, rc!)}>{shortDay(r.day)}</a>
                        </td>
                        <td>{r.venue}</td>
                        <td>
                          <DisciplineBadge d={r.discipline} />
                        </td>
                        <td className="r num">{r.distance_m ? `${int(r.distance_m)} m` : "—"}</td>
                        <td className="small">{r.going?.toLowerCase() ?? "—"}</td>
                        <td className="r num" style={{ fontWeight: 600 }}>
                          {r.status !== "PARTANT" ? "NP" : r.position ? `${r.position}/${r.field ?? "?"}` : "—"}
                        </td>
                        <td>{r.jockey ?? "—"}</td>
                        <td className="muted">{r.trainer ?? "—"}</td>
                        <td className="r num">{r.draw ?? "—"}</td>
                        <td className="r num">{r.weight_kg ? fmt(r.weight_kg, 1) : "—"}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </>
  );
}
