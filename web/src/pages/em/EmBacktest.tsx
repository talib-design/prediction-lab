import { useState } from "react";
import { Card, Empty, Failure, Kpi, Loading, PageHead, Segmented } from "../../components/ui";
import { ChanceBand, emLogic } from "../../components/em";
import { api, type EmPoolBlock, type EmRunBlock } from "../../lib/api";
import { euros, fmt, int, shortDay, signedPct } from "../../lib/format";
import { useApi } from "../../lib/hooks";

type View = "balls" | "era-balls" | "era-stars";

const zText = (z: number) => `${z >= 0 ? "+" : "−"}${fmt(Math.abs(z), 2)}`;
const pText = (p: number | null | undefined) => (p == null ? "—" : p < 0.001 ? "< 0,001" : fmt(p, 3));
const ll = (x: number) => `${x >= 0 ? "+" : "−"}${fmt(Math.abs(x) * 1000, 2)}`;

function PoolTable({ run, pool }: { run: EmRunBlock; pool: EmPoolBlock }) {
  const q = pool.random_players.mean_matches_quantiles;
  const low = q["0.025"] ?? pool.expected_matches;
  const high = q["0.975"] ?? pool.expected_matches;
  const values = [...pool.logics.map((l) => l.mean_matches), pool.witness_r1.mean_matches, low, high];
  const span = Math.max(...values.map((v) => Math.abs(v - pool.expected_matches))) * 1.15;
  const min = pool.expected_matches - span;
  const max = pool.expected_matches + span;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Logique</th>
            <th className="r">Trouvés / tirage</th>
            <th>Face à 1 000 joueurs au hasard</th>
            <th className="r">z</th>
            <th className="r">Dépasse</th>
            <th className="r" title="Coût de ses probabilités face au tirage uniforme, en millièmes ; négatif = mieux que le hasard">
              Log loss vs uniforme (‰)
            </th>
            <th className="r">q</th>
          </tr>
        </thead>
        <tbody>
          {pool.logics.map((l) => (
            <tr key={l.logic}>
              <td>{emLogic(l.logic)}</td>
              <td className="r num">{fmt(l.mean_matches, 3)}</td>
              <td>
                <ChanceBand
                  value={l.mean_matches}
                  low={low}
                  high={high}
                  min={min}
                  max={max}
                  expected={pool.expected_matches}
                  title={`${fmt(l.mean_matches, 3)} trouvés ; 95 % des joueurs au hasard entre ${fmt(low, 3)} et ${fmt(high, 3)}`}
                />
              </td>
              <td className="r num">{zText(l.matches_z)}</td>
              <td className="r num">{fmt(l.percentile_vs_players * 100, 0)} %</td>
              <td className="r num">{ll(l.logloss_diff)}</td>
              <td className="r num">{pText(l.logloss_q)}</td>
            </tr>
          ))}
          <tr className="dim">
            <td>{emLogic("temoin_r1")}</td>
            <td className="r num">{fmt(pool.witness_r1.mean_matches, 3)}</td>
            <td>
              <ChanceBand
                value={pool.witness_r1.mean_matches}
                low={low}
                high={high}
                min={min}
                max={max}
                expected={pool.expected_matches}
                title="Le témoin joue au hasard"
              />
            </td>
            <td className="r num">{zText(pool.witness_r1.z)}</td>
            <td className="r num">—</td>
            <td className="r num">—</td>
            <td className="r num">—</td>
          </tr>
        </tbody>
      </table>
      <p className="small muted card-body" style={{ margin: 0 }}>
        {int(run.n_targets)} tirages du {shortDay(run.first_target)} au {shortDay(run.last_target)}, chacun prédit avec
        les seuls tirages précédents. Au hasard : {fmt(pool.expected_matches, 3)} trouvés par tirage ; la bande couvre 95 %
        des 1 000 joueurs au hasard. Log loss en millièmes : positif = la logique se trompe plus que
        « tous les numéros se valent ».
      </p>
    </div>
  );
}

export function EmBacktest() {
  const [view, setView] = useState<View>("balls");
  const load = useApi(() => api.em.backtest(), "em-backtest");
  if (load.state === "loading") return <Loading rows={8} />;
  if (load.state === "error") return <Failure error={load.error} />;
  const bt = load.data.backtest;
  if (!bt)
    return (
      <div className="card">
        <Empty title="Backtest pas encore lancé">
          <p className="small">
            <code className="mono">uv run predlab lottery backtest</code>
          </p>
        </Empty>
      </div>
    );
  const run = view === "balls" ? bt.balls_2004 : bt.grid_2016_09;
  const pool = run.pools[view === "era-stars" ? "stars" : "main"];
  const pay = bt.payouts_2016_09;
  const rp = pay.random_players.mean_payout_quantiles;
  const decisive = bt.balls_2004.pools.main?.logics ?? [];
  const better = decisive.filter((l) => l.logloss_diff < 0 && l.logloss_q < 0.05).length;
  const payRows = [
    ...Object.entries(pay.logics),
    ["temoin_r1", { ...pay.witness_r1, percentile_vs_players: undefined }] as const,
  ];
  return (
    <>
      <PageHead
        crumbs="EuroMillions · logiques contre hasard"
        title="Une logique bat-elle le hasard ?"
        lead="Huit logiques figées d'avance, sans aucun réglage, jouent une grille par tirage en marche avant. On les compare au hasard de trois façons : la loi exacte, un témoin au hasard et 1 000 joueurs au hasard."
      />
      <div className="stack">
        <div className="kpis">
          <Kpi label="Logiques testées" value={int(decisive.length)} sub="fréquences, retard, chauds, froids, répétition" />
          <Kpi
            label="Meilleures que le hasard"
            value={int(better)}
            sub={better === 0 ? "aucune ne bat le tirage uniforme (boules 2004-2026)" : "log loss, après correction"}
          />
          <Kpi label="Gain moyen d'une grille" value={euros(rp["0.5"] ?? null)} sub={`joueur au hasard, pour ${euros(pay.price_eur)} misés`} />
          <Kpi label="Rendement au hasard" value={signedPct(pay.random_players.roi_median, 0)} sub="médiane de 1 000 joueurs, hors jackpot" />
        </div>

        <Card
          title="Numéros trouvés par tirage"
          aside={
            <Segmented<View>
              value={view}
              onChange={setView}
              label="Jeu de données"
              options={[
                { value: "balls", label: "Boules 2004-2026" },
                { value: "era-balls", label: "Boules depuis 2016" },
                { value: "era-stars", label: "Étoiles depuis 2016" },
              ]}
            />
          }
          flush
        >
          {pool ? <PoolTable run={run} pool={pool} /> : <Empty title="Pas de données" />}
        </Card>

        <Card title="Gains fictifs, une grille par tirage" aside={<span className="small muted">depuis 2016 · {int(pay.n_draws)} tirages</span>} flush>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Logique</th>
                  <th className="r">Gain moyen / grille</th>
                  <th className="r">IC 95 %</th>
                  <th className="r">Rendement</th>
                  <th className="r">Grilles gagnantes</th>
                  <th className="r">Dépasse</th>
                </tr>
              </thead>
              <tbody>
                {payRows.map(([name, info]) => (
                  <tr key={name} className={name === "temoin_r1" ? "dim" : undefined}>
                    <td>{emLogic(name)}</td>
                    <td className="r num">{euros(info.mean_payout_eur)}</td>
                    <td className="r num">
                      {fmt(info.ci95[0], 2)} – {fmt(info.ci95[1], 2)}
                    </td>
                    <td className="r num">{signedPct(info.roi, 0)}</td>
                    <td className="r num">{int(info.wins)}</td>
                    <td className="r num">
                      {info.percentile_vs_players == null ? "—" : `${fmt(info.percentile_vs_players * 100, 0)} %`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="small muted card-body" style={{ margin: 0 }}>
              Grille à {euros(pay.price_eur)} payée au rapport officiel du rang atteint. 95 % des joueurs au hasard
              gagnent en moyenne entre {euros(rp["0.025"] ?? null)} et {euros(rp["0.975"] ?? null)} par grille. Aucune
              grille n'a touché le jackpot : il n'est pas dans ces chiffres. Mesure de performance, pas une stratégie de
              mise.
            </p>
          </div>
        </Card>
      </div>
    </>
  );
}
