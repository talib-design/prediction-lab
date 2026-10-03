import { useMemo, useState } from "react";
import { Card, Empty, Failure, Loading, PageHead, Segmented, disciplineLabel } from "../components/ui";
import { api, type Discipline, type FavouriteBand, type Hypothesis, type LabExperiment } from "../lib/api";
import { dateTime, int, pct, shortDay, signedPct } from "../lib/format";
import { useApi } from "../lib/hooks";

const STATUS: Record<Hypothesis["status"], { label: string; cls: string }> = {
  PROPOSED: { label: "Pré-enregistré", cls: "outline" },
  TESTING: { label: "En test", cls: "k-feature" },
  REJECTED: { label: "Rejeté", cls: "k-fact" },
  INCONCLUSIVE: { label: "Non concluant", cls: "k-assoc" },
  SUPPORTED: { label: "Retenu", cls: "k-forecast" },
};

const ORIGIN: Record<Hypothesis["origin"], string> = {
  human: "Chris",
  literature: "Littérature",
  folk_heuristic: "Savoir turfiste",
  automated: "Agent",
};

const ORDER: Record<Hypothesis["status"], number> = { SUPPORTED: 0, TESTING: 1, PROPOSED: 2, INCONCLUSIVE: 3, REJECTED: 4 };

/** Log loss difference challenger − base with its 99 % interval; left of 0 = better. */
function GainBar({ e }: { e: LabExperiment }) {
  const r = e.result;
  if (!r) return <span className="muted small">—</span>;
  const W = 120;
  const R = 0.0015;
  const x = (v: number) => ((Math.max(-R, Math.min(R, v)) + R) / (2 * R)) * W;
  const strong = r.ci_high < 0;
  return (
    <span
      className="ratio"
      title={`Écart de log loss ${r.difference.toFixed(4)} (IC 99 % ${r.ci_low.toFixed(4)} à ${r.ci_high.toFixed(4)}). À gauche de 0 : le critère améliore la prévision.`}
    >
      <svg width={W} height={14} aria-hidden>
        <line x1={x(0)} x2={x(0)} y1={1} y2={13} className="ratio-axis" />
        <line x1={x(r.ci_low)} x2={x(r.ci_high)} y1={7} y2={7} className="ratio-ci" />
        <circle cx={x(r.difference)} cy={7} r={3.5} className={strong ? "ratio-dot strong" : "ratio-dot"} />
      </svg>
    </span>
  );
}

function Effect({ e }: { e: LabExperiment }) {
  const r = e.result;
  if (!r || r.per_sd == null) return <span className="muted">—</span>;
  const up = r.per_sd >= 1;
  const neutral = Math.abs(r.per_sd - 1) < 0.01;
  return (
    <span className="small" title="Chances de victoire multipliées par ce facteur pour un écart-type de plus du critère, cote égale">
      ×{r.per_sd.toFixed(2).replace(".", ",")}{" "}
      <span className="muted">{neutral ? "(neutre)" : up ? "(sous-estimé par la cote)" : "(surestimé par la cote)"}</span>
    </span>
  );
}

function Waiting({ text }: { text: string }) {
  const m = text.match(/(\d+)\/(\d+)/);
  if (!m) return <span className="small muted">{text}</span>;
  const n = Number(m[1]);
  const of = Number(m[2]);
  return (
    <div className="bet-progress" title={text}>
      <div className="bar">
        <span style={{ width: `${Math.min(100, (n / of) * 100)}%`, background: "var(--accent)" }} />
      </div>
      <span className="small muted num">
        {int(n)}/{int(of)} courses suivies en direct
      </span>
    </div>
  );
}

function Experiments({ items, rule }: { items: LabExperiment[]; rule: string }) {
  const rows = [...items]
    .filter((e) => e.source !== "study")
    .sort((a, b) => ORDER[a.status] - ORDER[b.status] || a.discipline.localeCompare(b.discipline) || a.label.localeCompare(b.label));
  const done = rows.filter((e) => e.result).length;
  return (
    <Card
      title="Nouveaux critères pour le modèle"
      aside={
        <span className="muted small">
          {rows.length} critères pré-enregistrés · {done} testés
        </span>
      }
    >
      <div className="stack" style={{ gap: 12 }}>
        <p className="small muted" style={{ margin: 0 }}>
          Chaque nuit, l'agent du labo enregistre les nouveaux critères du catalogue <em>avant</em> tout test, puis lance
          une seule fois ceux dont les données sont prêtes. {rule}
        </p>
        {rows.length === 0 ? (
          <Empty title="Aucun critère enregistré">
            <p className="small">
              Ils s'enregistrent à la prochaine nuit, ou à la main : <code className="mono">uv run predlab racing lab</code>.
            </p>
          </Empty>
        ) : (
          <div className="table-wrap">
            <table className="compact">
              <thead>
                <tr>
                  <th>Critère</th>
                  <th>Discipline</th>
                  <th title="Date d'inscription au registre, avant le test">Pré-enregistré</th>
                  <th>Statut</th>
                  <th title="Écart de log loss avec et sans le critère, intervalle à 99 %. À gauche de 0 : meilleure prévision">
                    Gain de prévision
                  </th>
                  <th>Effet</th>
                  <th>Conclusion</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((e) => (
                  <tr key={e.experiment} className={e.status === "REJECTED" ? "dim" : undefined}>
                    <td>
                      <div title={e.hypothesis}>{e.label}</div>
                      <div className="small muted">
                        {e.source === "live" ? "cotes en direct" : "historique depuis 2024"} · {ORIGIN[e.origin]}
                      </div>
                    </td>
                    <td>
                      <span className={`badge d-${e.discipline}`}>{disciplineLabel(e.discipline)}</span>
                    </td>
                    <td className="small">{e.registered_at ? shortDay(e.registered_at.slice(0, 10)) : "—"}</td>
                    <td>
                      <span className={`badge ${STATUS[e.status].cls}`}>{STATUS[e.status].label}</span>
                    </td>
                    <td>
                      <GainBar e={e} />
                    </td>
                    <td>
                      <Effect e={e} />
                    </td>
                    <td className="small" style={{ maxWidth: 380 }}>
                      {e.waiting ? (
                        <Waiting text={e.waiting} />
                      ) : e.conclusion ? (
                        e.conclusion
                      ) : (
                        <span className="muted">
                          {e.discipline === "PLAT" ? "Test à la prochaine nuit." : "Attend l'historique de cette discipline (2024)."}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Card>
  );
}

/** Win rate (bar) against what the odds promised (tick). */
function WinVsOdds({ b }: { b: FavouriteBand }) {
  if (b.win_rate == null || b.implied == null) return <span className="muted">—</span>;
  const W = 120;
  return (
    <span className="ratio" title={`Gagne ${pct(b.win_rate, 1)} ; la cote promettait ${pct(b.implied, 1)}`}>
      <svg width={W} height={14} aria-hidden>
        <rect x={0} y={4} width={W} height={6} rx={3} className="track" />
        <rect x={0} y={4} width={b.win_rate * W} height={6} rx={3} style={{ fill: "var(--series-favori)" }} />
        <line x1={b.implied * W} x2={b.implied * W} y1={0} y2={14} style={{ stroke: "var(--ink)", strokeWidth: 2 }} />
      </svg>
      <span className="num small">
        {pct(b.win_rate, 0)} <span className="muted">/ {pct(b.implied, 0)}</span>
      </span>
    </span>
  );
}

function Favourites({ data }: { data: NonNullable<ReturnType<typeof useFav>> }) {
  const available = Object.keys(data) as Discipline[];
  const [d, setD] = useState<Discipline>(available.includes("PLAT") ? "PLAT" : available[0]!);
  const rep = data[d];
  if (!rep) return null;
  const top = rep.bands[0]!;
  return (
    <Card
      title="Étude : les gros favoris"
      aside={
        available.length > 1 ? (
          <Segmented<Discipline>
            label="Discipline"
            value={d}
            onChange={setD}
            options={available.map((x) => ({ value: x, label: disciplineLabel(x) }))}
          />
        ) : (
          <span className="muted small">{disciplineLabel(d)}</span>
        )
      }
    >
      <div className="stack" style={{ gap: 12 }}>
        {top.races > 0 && top.win_rate != null && top.implied != null && (
          <p className="small" style={{ margin: 0 }}>
            Sur {int(top.races)} courses où le favori était à moins de 1,5 contre 1, il a gagné{" "}
            <strong className="num">{pct(top.win_rate, 0)}</strong> du temps alors que sa cote promettait{" "}
            <strong className="num">{pct(top.implied, 0)}</strong> : il a perdu <strong className="num">{int(top.lost)}</strong>{" "}
            fois. 1 € joué sur chacun a rendu <strong className="num">{signedPct(top.roi_sg, 1)}</strong> en gagnant et{" "}
            <strong className="num">{signedPct(top.roi_sp, 1)}</strong> en placé. Les « courses sûres » n'existent pas, et
            les très gros favoris sont même légèrement surjoués.
          </p>
        )}
        <div className="table-wrap">
          <table className="compact">
            <thead>
              <tr>
                <th>Cote du favori à 25 min</th>
                <th className="r">Courses</th>
                <th title="Barre : part de victoires. Trait : probabilité promise par la cote">Gagne / promis</th>
                <th className="r">Perd</th>
                <th className="r">Placé</th>
                <th className="r" title="Intervalle à 95 %">
                  Retour gagnant
                </th>
                <th className="r" title="Intervalle à 95 %">
                  Retour placé
                </th>
              </tr>
            </thead>
            <tbody>
              {rep.bands.map((b) => (
                <tr key={b.band} style={b.band.startsWith("Tous") ? { fontWeight: 600 } : undefined}>
                  <td>{b.band}</td>
                  <td className="r num">{int(b.races)}</td>
                  <td>
                    <WinVsOdds b={b} />
                  </td>
                  <td className="r num">{b.races ? pct(b.lost / b.races, 0) : "—"}</td>
                  <td className="r num">{pct(b.place_rate, 0)}</td>
                  <td className="r num">
                    {signedPct(b.roi_sg, 1)}
                    <div className="small muted">
                      {signedPct(b.roi_sg_low, 0)} ; {signedPct(b.roi_sg_high, 0)}
                    </div>
                  </td>
                  <td className="r num">
                    {signedPct(b.roi_sp, 1)}
                    <div className="small muted">
                      {signedPct(b.roi_sp_low, 0)} ; {signedPct(b.roi_sp_high, 0)}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="small muted" style={{ margin: 0 }}>
          Toutes les courses du {rep.first_day ? shortDay(rep.first_day) : "—"} au {rep.last_day ? shortDay(rep.last_day) : "—"}, 1 €
          par course au rapport officiel. Mis à jour : {dateTime(rep.generated_at)}.
        </p>
      </div>
    </Card>
  );
}

function useFav(data: Awaited<ReturnType<typeof api.lab>> | null) {
  return data && Object.keys(data.favourites).length ? data.favourites : null;
}

export function Research() {
  const lab = useApi(() => api.lab(), "lab", 300_000);
  const load = useApi(() => api.hypotheses(), "hypotheses");
  const fav = useFav(lab.state === "ready" ? lab.data : null);
  const others = useMemo(
    () => (load.state === "ready" ? load.data.hypotheses.filter((h) => !h.experiment?.includes(":")) : []),
    [load],
  );
  return (
    <>
      <PageHead
        crumbs="Laboratoire"
        title="Recherche"
        lead="Toute idée est enregistrée avant d'être testée, y compris celles qui échouent, et testée une seule fois. Non concluant ne veut pas dire faux : on n'a pas pu le voir."
      />
      {lab.state === "loading" && <Loading />}
      {lab.state === "error" && (
        <div className="card">
          <Empty title="Labo indisponible">
            <p className="small">
              Le tableau de bord tourne encore sur l'ancien code : relancez-le avec{" "}
              <code className="mono">bash ops/install_dashboard.sh</code>.
            </p>
          </Empty>
        </div>
      )}
      {lab.state === "ready" && (
        <div className="stack">
          <Experiments items={lab.data.experiments} rule={lab.data.rule} />
          {fav && <Favourites data={fav} />}
        </div>
      )}

      {others.length > 0 && (
        <details className="card card-body" style={{ marginTop: 16 }}>
          <summary className="muted">Autres hypothèses du registre ({others.length})</summary>
          <div className="stack" style={{ marginTop: 12 }}>
            {others.map((h) => (
              <Card
                key={h.hypothesis_id}
                title={h.description}
                aside={<span className={`badge ${STATUS[h.status].cls}`}>{STATUS[h.status].label}</span>}
              >
                <dl className="facts small">
                  <dt>Origine</dt>
                  <dd>{ORIGIN[h.origin]}</dd>
                  <dt>Créée</dt>
                  <dd>
                    {dateTime(h.created_at)} · révision {h.revision}
                  </dd>
                  {h.out_of_sample_result && (
                    <>
                      <dt>Hors échantillon</dt>
                      <dd>{h.out_of_sample_result}</dd>
                    </>
                  )}
                  {h.conclusion && (
                    <>
                      <dt>Conclusion</dt>
                      <dd>{h.conclusion}</dd>
                    </>
                  )}
                </dl>
              </Card>
            ))}
          </div>
        </details>
      )}
      {load.state === "error" && <Failure error={load.error} />}
    </>
  );
}
