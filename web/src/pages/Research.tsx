import { useMemo, useState } from "react";
import { Card, Empty, Failure, Loading, PageHead, Segmented, disciplineLabel } from "../components/ui";
import {
  api,
  type Discipline,
  type FavouriteBand,
  type Hypothesis,
  type LabExperiment,
  type ReplayTotals,
  type Scoreboard,
} from "../lib/api";
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
  if (!r || r.difference == null || r.ci_low == null || r.ci_high == null)
    return <span className="muted small">—</span>;
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

/** Filter 2: does the challenger's pick earn more than the champion's? (rules: than the
 *  favourite's) */
function Money({ e }: { e: LabExperiment }) {
  const r = e.result;
  if (!r) return <span className="muted small">—</span>;
  if (e.kind === "rule" && r.roi_rule != null && r.roi_favourite != null)
    return (
      <span className="small num" title={`${r.bets ?? 0} paris`}>
        {signedPct(r.roi_rule, 1)} <span className="muted">contre {signedPct(r.roi_favourite, 1)} (favori)</span>
      </span>
    );
  if (e.kind === "calibration") return <span className="small muted">même choix (τ = {fmtTau(r.tau)})</span>;
  const m = r.money;
  if (!m) return <span className="muted small">—</span>;
  return (
    <span
      className="small num"
      title={`Retour par euro : challenger ${signedPct(m.roi_challenger, 1)}, champion ${signedPct(m.roi_champion, 1)}, favori ${signedPct(m.roi_favourite, 1)}. ${m.races_where_picks_differ} courses où les choix diffèrent sur ${m.races}.`}
    >
      <strong className={m.net_difference > 0 ? "pos" : undefined}>{signedEuros(m.net_difference)}</strong>{" "}
      <span className="muted">face au champion</span>
    </span>
  );
}

const fmtTau = (t: number | undefined) => (t == null ? "—" : t.toFixed(2).replace(".", ","));
const signedEuros = (x: number) => `${x >= 0 ? "+" : "−"}${Math.abs(x).toFixed(0)} €`;

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

const KIND: Record<string, string> = {
  criterion: "critère",
  calibration: "calibration",
  rule: "règle de jeu",
};

function Experiments({ items }: { items: LabExperiment[] }) {
  const discs = (["PLAT", "ATTELE", "MONTE"] as const).filter((d) => items.some((e) => e.discipline === d));
  const [d, setD] = useState<Discipline>(discs[0] ?? "PLAT");
  const sorted = [...items]
    .filter((e) => e.source !== "study" && e.discipline === d)
    .sort((a, b) => ORDER[a.status] - ORDER[b.status] || a.label.localeCompare(b.label));
  const current = sorted.filter((e) => e.protocol?.startsWith("obj"));
  const first = sorted.filter((e) => !e.protocol?.startsWith("obj"));
  const done = current.filter((e) => e.result).length;
  return (
    <Card
      title="Tests contre le champion"
      aside={
        <div className="row" style={{ gap: 10 }}>
          <span className="muted small">
            {current.length} pré-enregistrés · {done} testés
          </span>
          {discs.length > 1 && (
            <Segmented<Discipline>
              label="Discipline"
              value={d}
              onChange={setD}
              options={discs.map((x) => ({ value: x, label: disciplineLabel(x) }))}
            />
          )}
        </div>
      }
    >
      <div className="stack" style={{ gap: 12 }}>
        <p className="small muted" style={{ margin: 0 }}>
          Chaque nuit, l'agent du labo enregistre les candidats du catalogue <em>avant</em> tout test, puis les teste une
          seule fois contre le modèle en service : la prévision d'abord (intervalle à 99 %, chaque année), puis l'argent
          (son cheval rapporte-t-il plus que celui du champion ?). Les deux tenus : un essai unique au coffre.
        </p>
        {current.length === 0 ? (
          <Empty title="Aucun candidat enregistré">
            <p className="small">
              Ils s'enregistrent à la prochaine nuit, ou à la main : <code className="mono">uv run predlab racing lab</code>.
            </p>
          </Empty>
        ) : (
          <ExperimentTable rows={current} money />
        )}
        {first.length > 0 && (
          <details className="small">
            <summary className="muted">Premier protocole (3/10, contre Marché+ v1 sur 2024) · {first.length} tests</summary>
            <div style={{ marginTop: 8 }}>
              <ExperimentTable rows={first} />
            </div>
          </details>
        )}
      </div>
    </Card>
  );
}

function ExperimentTable({ rows, money = false }: { rows: LabExperiment[]; money?: boolean }) {
  return (
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
                  {money && <th title="Le cheval choisi rapporte-t-il plus que celui du champion ? (règle : que le favori)">Argent</th>}
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
                        {e.source === "live"
                          ? "cotes en direct"
                          : e.fresh_from
                            ? `critère a posteriori · courses dès le ${shortDay(e.fresh_from)}`
                            : e.protocol?.startsWith("obj")
                              ? KIND[e.kind ?? "criterion"] ?? "critère"
                              : "historique depuis 2024"}{" "}
                        · {ORIGIN[e.origin]}
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
                    {money && (
                      <td>
                        <Money e={e} />
                      </td>
                    )}
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

function pooled(t: Record<string, ReplayTotals>, pick: "favori" | "modèle") {
  const sg = t[`SG ${pick}`];
  const sp = t[`SP ${pick}`];
  const bets = (sg?.bets ?? 0) + (sp?.bets ?? 0);
  const ret = (sg?.returned ?? 0) + (sp?.returned ?? 0);
  return { net: ret - bets, roi: bets ? ret / bets - 1 : null };
}

function Meter({ value, of, ok, label }: { value: number; of: number; ok: boolean; label: string }) {
  return (
    <div className="bet-progress" title={label}>
      <div className="bar">
        <span style={{ width: `${of ? Math.min(100, (value / of) * 100) : 0}%`, background: ok ? "var(--accent)" : "var(--ink-3)" }} />
      </div>
      <span className="small muted num">{label}</span>
    </div>
  );
}

const signedMoney = (x: number) => `${x >= 0 ? "+" : "−"}${Math.abs(x).toFixed(2).replace(".", ",")} €`;

/** The objective's scoreboard: who is in service, model − favourite live and on the
 *  history, and what the lab is waiting for. */
function ObjectiveCard({ board, objective }: { board: Partial<Record<Discipline, Scoreboard>>; objective: string }) {
  const discs = (["PLAT", "ATTELE", "MONTE"] as const).filter((d) => board[d]);
  const [d, setD] = useState<Discipline>(discs[0]!);
  const b = board[d] ?? board[discs[0]!]!;
  const live = b.live;
  const liveDiff = live.modèle.net - live.favori.net;
  const h = b.history;
  const hf = h ? pooled(h.totals, "favori") : null;
  const hm = h ? pooled(h.totals, "modèle") : null;
  const st = b.tests.by_status;
  const tested = (st.SUPPORTED ?? 0) + (st.REJECTED ?? 0) + (st.INCONCLUSIVE ?? 0);
  const waiting = (st.PROPOSED ?? 0) + (st.TESTING ?? 0);
  return (
    <Card
      title="Objectif : battre le favori"
      aside={
        discs.length > 1 ? (
          <Segmented<Discipline>
            label="Discipline"
            value={d}
            onChange={setD}
            options={discs.map((x) => ({ value: x, label: disciplineLabel(x) }))}
          />
        ) : undefined
      }
    >
      <div className="stack" style={{ gap: 14 }}>
        <p className="small muted" style={{ margin: 0 }}>
          {objective}
        </p>
        <div className="overview-grid">
          <div className="card overview-card">
            <div className="kpi-label">En service</div>
            <div className="overview-net num">Marché+ v{b.champion.version}</div>
            <dl className="overview-facts">
              <dt>Facteurs</dt>
              <dd className="num">{b.champion.features}</dd>
              <dt>Calibration</dt>
              <dd className="num">{b.champion.tau === 1 ? "aucune" : `τ = ${fmtTau(b.champion.tau)}`}</dd>
              <dt>Règle de jeu</dt>
              <dd>{b.champion.rules.length ? "valeur ≥ 1,05" : "aucune"}</dd>
            </dl>
            <div className="small muted">
              {b.champion.promoted_at ? `promu le ${shortDay(b.champion.promoted_at.slice(0, 10))}` : "version de départ"}
            </div>
          </div>
          <div className="card overview-card">
            <div className="kpi-label">En direct (carnet) : modèle − favori</div>
            <div className={`overview-net num ${live.races ? (liveDiff >= 0 ? "pos" : "neg") : ""}`}>
              {live.races ? signedMoney(liveDiff) : "—"}
            </div>
            <dl className="overview-facts">
              <dt>Modèle</dt>
              <dd className="num">{signedPct(live.modèle.roi, 1)}</dd>
              <dt>Favori</dt>
              <dd className="num">{signedPct(live.favori.roi, 1)}</dd>
              <dt>Choix différents</dt>
              <dd className="num">
                {live.races_where_picks_differ} / {live.races}
              </dd>
            </dl>
            <div className="small muted">
              {live.since ? `gagnant + placé, depuis le ${shortDay(live.since)}` : "pas encore de course comparée"}
            </div>
          </div>
          <div className="card overview-card">
            <div className="kpi-label">Sur l'historique : modèle − favori</div>
            <div className={`overview-net num ${hm && hf ? (hm.net - hf.net >= 0 ? "pos" : "neg") : ""}`}>
              {hm && hf ? signedMoney(hm.net - hf.net) : "—"}
            </div>
            <dl className="overview-facts">
              <dt>Modèle</dt>
              <dd className="num">{signedPct(hm?.roi, 1)}</dd>
              <dt>Favori</dt>
              <dd className="num">{signedPct(hf?.roi, 1)}</dd>
              <dt>Quitte le favori</dt>
              <dd className="num">{h ? pct(h.differ_share, 1) : "—"}</dd>
            </dl>
            <div className="small muted">
              {h ? `${int(h.races)} courses, du ${shortDay(h.first_day)} au ${shortDay(h.last_day)} (recalculé)` : "pas encore de courbe historique"}
            </div>
          </div>
          <div className="card overview-card">
            <div className="kpi-label">Labo</div>
            <div className="overview-net num">
              {tested}/{b.tests.total}
            </div>
            <dl className="overview-facts">
              <dt>Retenus</dt>
              <dd className="num">{st.SUPPORTED ?? 0}</dd>
              <dt>En attente</dt>
              <dd className="num">{waiting}</dd>
              <dt>Essais au coffre</dt>
              <dd className="num">{b.attempts.length}</dd>
            </dl>
            <div className="small muted">tests contre la version en service</div>
          </div>
        </div>

        <div className="grid-2" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16 }}>
          <div className="stack" style={{ gap: 6 }}>
            <div className="kpi-label">
              Historique 2020-2023 {b.coverage.ready ? "· en place" : "· en cours de rattrapage"}
            </div>
            {Object.entries(b.coverage.years).map(([y, n]) => {
              const share = b.coverage.reference_2024 ? n / b.coverage.reference_2024 : 0;
              return (
                <div key={y} className="row" style={{ gap: 8 }}>
                  <span className="small num" style={{ width: 38 }}>
                    {y}
                  </span>
                  <Meter
                    value={n}
                    of={b.coverage.reference_2024}
                    ok={share >= b.coverage.share}
                    label={`${int(n)} courses (${pct(share, 0)} de 2024)`}
                  />
                </div>
              );
            })}
            <span className="small muted">Les tests démarrent quand chaque année atteint {pct(b.coverage.share, 0)} des courses de 2024.</span>
          </div>
          <div className="stack" style={{ gap: 6 }}>
            <div className="kpi-label">Coffre (courses jamais utilisées par un test)</div>
            <Meter
              value={b.vault.races}
              of={b.vault.min_races}
              ok={b.vault.races >= b.vault.min_races}
              label={`${int(b.vault.races)} / ${int(b.vault.min_races)} courses depuis le ${shortDay(b.vault.start)}`}
            />
            <span className="small muted">
              Un candidat retenu y fait un seul essai ; chaque essai consomme le coffre.
              {b.vault.used_until ? ` Utilisé jusqu'au ${shortDay(b.vault.used_until)}.` : " Jamais utilisé."}
            </span>
          </div>
        </div>

        {(b.versions.length > 1 || b.attempts.length > 0) && (
          <div className="table-wrap">
            <table className="compact">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Événement</th>
                  <th className="r">Prévision (coffre)</th>
                  <th className="r">Argent face au champion</th>
                </tr>
              </thead>
              <tbody>
                {b.attempts.map((a) => (
                  <tr key={a.at + a.experiment}>
                    <td className="small">{shortDay(a.at.slice(0, 10))}</td>
                    <td className="small">
                      {a.passed ? "Promu" : "Refusé au coffre"} : {a.experiment.split(":")[0]}{" "}
                      <span className="muted">
                        ({int(a.result.races)} courses, {shortDay(a.vault[0])} → {shortDay(a.vault[1])})
                      </span>
                    </td>
                    <td className="r num small">{a.result.prediction.difference.toFixed(4)}</td>
                    <td className="r num small">{signedEuros(a.result.money.net_difference)}</td>
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
          {lab.data.scoreboard && Object.keys(lab.data.scoreboard).length > 0 && (
            <ObjectiveCard board={lab.data.scoreboard} objective={lab.data.objective ?? ""} />
          )}
          <Experiments items={lab.data.experiments} />
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
