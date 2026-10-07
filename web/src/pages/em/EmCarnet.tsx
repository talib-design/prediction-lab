import { Card, Empty, Failure, Kpi, Loading, PageHead } from "../../components/ui";
import { EM_RANKS, Grid, emLogic } from "../../components/em";
import { api } from "../../lib/api";
import { dateTime, euros, fmt, int, longDay, shortDay, signedPct } from "../../lib/format";
import { useApi } from "../../lib/hooks";

const zText = (z: number) => `${z >= 0 ? "+" : "−"}${fmt(Math.abs(z), 2)}`;

export function EmCarnet() {
  const load = useApi(() => api.em.carnet(), "em-carnet", 300_000);
  if (load.state === "loading") return <Loading rows={6} />;
  if (load.state === "error") return <Failure error={load.error} />;
  const c = load.data;
  const pendingDays = [...new Set(c.pending.map((g) => g.draw_date))].sort();
  const summary = Object.entries(c.summary).sort(([a], [b]) =>
    a === "temoin_r1" ? 1 : b === "temoin_r1" ? -1 : 0,
  );
  const settledDraws = c.draws.length;
  return (
    <>
      <PageHead
        crumbs="EuroMillions · carnet à terme"
        title={c.next_draw ? `Prochain tirage : ${longDay(c.next_draw)}` : "Carnet à terme"}
        lead="Chaque logique joue une grille, figée avant 20 h le jour du tirage puis notée avec le résultat et les rapports officiels. Le témoin joue au hasard. Grilles fictives : rien n'est misé."
      />
      <div className="stack">
        {!c.chain_ok && (
          <div className="note warn">
            <span>
              <strong>Registre altéré</strong> : la chaîne de hachage du carnet ne se vérifie plus. Les résultats
              affichés ne sont pas fiables.
            </span>
          </div>
        )}
        <div className="kpis">
          <Kpi
            label="Dernier tirage"
            value={c.last_draw ? shortDay(c.last_draw.draw_date) : "—"}
            sub={c.last_draw ? <Grid balls={c.last_draw.balls} stars={c.last_draw.stars} /> : "store vide"}
          />
          <Kpi label="Tirages notés" value={int(settledDraws)} sub="depuis le 6 octobre 2026" />
          <Kpi label="Grilles en attente" value={int(c.pending.length)} sub={pendingDays.map(shortDay).join(", ") || "aucune"} />
          <Kpi
            label="Pour conclure"
            value="≈ 325 tirages"
            sub="pour voir +0,1 boule trouvée par tirage (3 ans)"
          />
        </div>

        {pendingDays.map((day) => {
          const grids = c.pending.filter((g) => g.draw_date === day);
          const first = grids[0];
          return (
            <Card
              key={day}
              title={`Grilles figées pour ${longDay(day)}`}
              aside={first && <span className="small muted">figées le {dateTime(first.frozen_at)}</span>}
              flush
            >
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Logique</th>
                      <th>Grille</th>
                      <th>Calculée avec</th>
                    </tr>
                  </thead>
                  <tbody>
                    {grids.map((g) => (
                      <tr key={g.logic} className={g.logic === "temoin_r1" ? "dim" : undefined}>
                        <td>{emLogic(g.logic)}</td>
                        <td>
                          <Grid balls={g.balls} stars={g.stars} />
                        </td>
                        <td className="small muted">
                          {g.logic === "temoin_r1"
                            ? "graine tirée de la date"
                            : `${int(g.history_draws)} tirages, jusqu'au ${shortDay(g.history_last_draw)}`}
                          {g.history_stale && <span className="badge k-assoc"> historique en retard</span>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          );
        })}

        <Card title="Bilan par logique" flush>
          {summary.length === 0 ? (
            <Empty title="Aucun tirage noté pour l'instant">
              <p className="small">Le premier bilan arrive après le tirage {c.next_draw ? `du ${shortDay(c.next_draw)}` : "suivant"}.</p>
            </Empty>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Logique</th>
                    <th className="r">Tirages</th>
                    <th className="r">Boules trouvées</th>
                    <th className="r">z</th>
                    <th className="r">Étoiles trouvées</th>
                    <th className="r">Grilles gagnantes</th>
                    <th className="r">Gains</th>
                    <th className="r">Rendement</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.map(([logic, s]) => (
                    <tr key={logic} className={logic === "temoin_r1" ? "dim" : undefined}>
                      <td>{emLogic(logic)}</td>
                      <td className="r num">{int(s.draws)}</td>
                      <td className="r num">{fmt(s.mean_balls, 3)}</td>
                      <td className="r num">{zText(s.z_balls)}</td>
                      <td className="r num">{fmt(s.mean_stars, 3)}</td>
                      <td className="r num">{int(s.wins)}</td>
                      <td className="r num">{euros(s.paid_eur)}</td>
                      <td className="r num">{signedPct(s.roi, 0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="small muted card-body" style={{ margin: 0 }}>
                Au hasard : 0,500 boule et 0,333 étoile trouvées par tirage. z mesure l'écart à ce hasard ; |z| sous 2
                n'est pas un signal. Mise fictive de 2,50 € par grille.
              </p>
            </div>
          )}
        </Card>

        {c.draws.map((d) => (
          <Card
            key={d.draw_date}
            title={`Tirage ${longDay(d.draw_date)}`}
            aside={d.balls && d.stars ? <Grid balls={d.balls} stars={d.stars} /> : undefined}
            flush
          >
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Logique</th>
                    <th>Grille</th>
                    <th className="r">Trouvés</th>
                    <th>Rang</th>
                    <th className="r">Gain</th>
                  </tr>
                </thead>
                <tbody>
                  {d.grids.map((g) => (
                    <tr key={g.logic} className={g.logic === "temoin_r1" ? "dim" : undefined}>
                      <td>{emLogic(g.logic)}</td>
                      <td>
                        <Grid balls={g.balls} stars={g.stars} hitBalls={d.balls} hitStars={d.stars} />
                      </td>
                      <td className="r num">
                        {g.ball_hits} + {g.star_hits}
                      </td>
                      <td>{g.rank ? `rang ${g.rank} (${EM_RANKS[g.rank]})` : <span className="muted">—</span>}</td>
                      <td className="r num">{g.rank ? (g.payout_eur == null ? "inconnu" : euros(g.payout_eur)) : "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        ))}

        <Card title="Agent automatique" aside={<span className="small muted">toutes les heures sur le Mac</span>}>
          {c.agent_log.length === 0 ? (
            <p className="small" style={{ margin: 0 }}>
              Aucune trace : l'agent n'a pas encore tourné. Installation : <code className="mono">bash ops/install_lottery.sh</code>
            </p>
          ) : (
            <pre className="mono em-log">{c.agent_log.join("\n")}</pre>
          )}
        </Card>
      </div>
    </>
  );
}
