import { Card, DisciplineBadge, Empty, Failure, Kpi, Loading, PageHead } from "../components/ui";
import { api } from "../lib/api";
import { dateTime, int, pct, shortDay } from "../lib/format";
import { useApi } from "../lib/hooks";

export function Data() {
  const load = useApi(() => api.status(), "status", 60_000);
  if (load.state === "loading") return <Loading rows={6} />;
  if (load.state === "error") return <Failure error={load.error} />;
  const s = load.data;
  const fresh = s.minutes_since_last_capture;
  const db = s.database;
  return (
    <>
      <PageHead
        crumbs="Collecte et stockage"
        title="Données"
        lead="Le brut est la source de vérité : chaque réponse du PMU est gardée telle quelle, horodatée et chaînée. La base est reconstruite depuis le brut chaque nuit."
      />
      <div className="stack">
        <div className="kpis">
          <Kpi
            label="Dernière capture"
            value={fresh == null ? "—" : fresh < 90 ? `il y a ${Math.round(fresh)} min` : dateTime(s.last_capture)}
            sub={fresh != null && fresh > 30 ? "Normal la nuit ; sinon vérifier le collecteur" : "Collecteur toutes les 5 min"}
          />
          <Kpi label="Captures brutes" value={int(s.captures)} sub={`${int(s.failed_captures)} échecs (${pct(s.captures ? s.failed_captures / s.captures : 0)})`} />
          <Kpi label="Courses en base" value={int(db.races)} sub={db.built_at ? `reconstruite le ${dateTime(db.built_at)}` : "base absente"} />
          <Kpi label="Chevaux" value={int(db.horses)} sub={`${int(db.odds)} cotes · ${int(db.dividends)} rapports`} />
        </div>

        <Card title="Rattrapage historique" aside={<span className="muted small">du plus récent au plus ancien, une tranche par nuit</span>}>
          <div className="stack">
            {s.backfill.map((b) => {
              const share = b.days_total ? b.days_done / b.days_total : 0;
              return (
                <div key={b.discipline}>
                  <div className="row" style={{ justifyContent: "space-between", marginBottom: 6 }}>
                    <span className="row">
                      <DisciplineBadge d={b.discipline} />
                      <span className="small muted">depuis le {shortDay(b.start)}</span>
                    </span>
                    <span className="small num">
                      {int(b.days_done)} / {int(b.days_total)} jours · {pct(share, 0)}
                      {b.oldest_done && <span className="muted"> · remonté jusqu'au {shortDay(b.oldest_done)}</span>}
                    </span>
                  </div>
                  <div className="progress" role="progressbar" aria-valuenow={Math.round(share * 100)} aria-valuemin={0} aria-valuemax={100}>
                    <span style={{ width: `${share * 100}%` }} />
                  </div>
                </div>
              );
            })}
            <p className="small muted" style={{ margin: 0 }}>
              Ordre : plat d'abord, puis trot attelé, puis trot monté. Un jour est compté une fois son programme, ses
              partants et ses rapports stockés ; le compteur est enregistré à la fin de chaque tranche nocturne.
            </p>
          </div>
        </Card>

        <div className="grid-2">
          <Card title="Base par discipline" flush>
            {db.by_discipline?.length ? (
              <table>
                <thead>
                  <tr>
                    <th>Discipline</th>
                    <th className="r">Courses au programme</th>
                    <th className="r">Avec partants</th>
                  </tr>
                </thead>
                <tbody>
                  {db.by_discipline.map((d) => (
                    <tr key={d.discipline}>
                      <td>
                        <DisciplineBadge d={d.discipline} />
                      </td>
                      <td className="r num">{int(d.races)}</td>
                      <td className="r num">{int(d.with_runners)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <Empty title="Base absente">
                <p className="small">
                  <code className="mono">uv run predlab racing build</code>
                </p>
              </Empty>
            )}
          </Card>
          <Card title="Journaux">
            <div className="stack">
              <div>
                <h3>Collecteur</h3>
                <pre className="log">{s.collect_log.join("\n") || "—"}</pre>
              </div>
              <div>
                <h3>Rattrapage</h3>
                <pre className="log">{s.backfill_log.join("\n") || "—"}</pre>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </>
  );
}
