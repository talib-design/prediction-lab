import { Card, Empty, Failure, Kpi, Loading, PageHead } from "../../components/ui";
import { Grid } from "../../components/em";
import { api } from "../../lib/api";
import { dateTime, euros0, int, shortDay } from "../../lib/format";
import { useApi } from "../../lib/hooks";

const DAY = ["", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"];
const ERA_LABEL: Record<string, string> = {
  "2004-02": "2004 → mai 2011 · étoiles 1-9, vendredi",
  "2011-05": "mai 2011 → sept. 2016 · étoiles 1-11",
  "2016-09": "sept. 2016 → · étoiles 1-12",
};

export function EmData() {
  const load = useApi(() => api.em.data(), "em-data", 300_000);
  if (load.state === "loading") return <Loading rows={6} />;
  if (load.state === "error") return <Failure error={load.error} />;
  const d = load.data;
  return (
    <>
      <PageHead
        crumbs="EuroMillions · données"
        title="Données"
        lead="Les archives officielles de la FDJ, lues strictement : une ligne non conforme bloque l'import au lieu d'être réparée en silence. Un tirage enregistré n'est jamais réécrit."
      />
      <div className="stack">
        {!d.store ? (
          <div className="card">
            <Empty title="Aucun tirage en base">
              <p className="small">
                <code className="mono">uv run predlab lottery ingest</code>
              </p>
            </Empty>
          </div>
        ) : (
          <>
            <div className="kpis">
              <Kpi label="Tirages en base" value={int(d.store.draws)} sub={`du ${shortDay(d.store.first)} au ${shortDay(d.store.last)}`} />
              {Object.entries(d.store.eras).map(([era, n]) => (
                <Kpi key={era} label={`Époque ${era}`} value={int(n)} sub={ERA_LABEL[era] ?? ""} />
              ))}
            </div>

            <Card title="Derniers tirages" aside={<span className="small muted">import du {dateTime(d.store.retrieved_at)}</span>} flush>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Numéros</th>
                      <th>Ordre de sortie</th>
                      <th className="r">Jackpot</th>
                    </tr>
                  </thead>
                  <tbody>
                    {d.recent.map((r) => (
                      <tr key={r.draw_date}>
                        <td className="nowrap">
                          {DAY[r.weekday]} {shortDay(r.draw_date)}
                        </td>
                        <td>
                          <Grid balls={r.balls} stars={r.stars} />
                        </td>
                        <td className="mono muted">{r.balls_order?.join(" · ")}</td>
                        <td className="r num">
                          {r.jackpot_winners ? `${int(r.jackpot_winners)} gagnant${r.jackpot_winners > 1 ? "s" : ""} · ${euros0(r.jackpot_eur)}` : <span className="muted">non gagné</span>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </>
        )}

        <Card title="Archives FDJ" aside={<span className="small muted">empreintes SHA-256, jamais commitées</span>} flush>
          {d.archives.length === 0 ? (
            <Empty title="Aucune archive enregistrée" />
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Archive</th>
                    <th>Période</th>
                    <th className="r">Tirages</th>
                    <th>Encodage</th>
                    <th>Empreinte</th>
                    <th>Enregistrée</th>
                  </tr>
                </thead>
                <tbody>
                  {d.archives.map((a) => (
                    <tr key={a.archive_sha256}>
                      <td>
                        {a.url ? (
                          <a href={a.url} target="_blank" rel="noreferrer">
                            {a.archive}
                          </a>
                        ) : (
                          a.archive
                        )}
                      </td>
                      <td className="nowrap">
                        {shortDay(a.first_draw)} → {shortDay(a.last_draw)}
                      </td>
                      <td className="r num">{int(a.rows)}</td>
                      <td>{a.encoding}</td>
                      <td className="mono muted" title={a.archive_sha256}>
                        {a.archive_sha256.slice(0, 12)}…
                      </td>
                      <td className="small muted">{dateTime(a.recorded_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card title="Agent automatique" aside={<span className="small muted">toutes les heures sur le Mac</span>}>
          <div className="stack">
            <p className="small" style={{ margin: 0 }}>
              À chaque passage : télécharge l'archive FDJ du moment si un tirage publié manque, note les grilles du
              carnet, puis fige celles du tirage suivant (avant 20 h le jour du tirage).
            </p>
            {d.agent_log.length ? (
              <pre className="mono em-log">{d.agent_log.join("\n")}</pre>
            ) : (
              <p className="small muted" style={{ margin: 0 }}>
                Pas encore de trace. Installation : <code className="mono">bash ops/install_lottery.sh</code>
              </p>
            )}
            {d.agent_errors && d.agent_errors.length > 0 && (
              <div className="note warn">
                <pre className="mono em-log" style={{ margin: 0 }}>
                  {d.agent_errors.join("\n")}
                </pre>
              </div>
            )}
          </div>
        </Card>
      </div>
    </>
  );
}
