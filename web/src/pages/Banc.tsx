import { useMemo, useState } from "react";
import { Empty, Failure, Loading, PageHead, Segmented } from "../components/ui";
import { api, type BancStrategy, type BancTotals, type Summary } from "../lib/api";
import { euros, fmt, int, shortDay } from "../lib/format";
import { useApi } from "../lib/hooks";

type Filter = "play" | "winners" | "gone" | "all";
type Bet = "ALL" | "SG" | "SP";

const signedEuros = (x: number) => `${x >= 0 ? "+" : "−"}${euros(Math.abs(x))}`;
const signedPct = (x: number | null | undefined, d = 0) =>
  x == null ? "—" : `${x >= 0 ? "+" : "−"}${fmt(Math.abs(x) * 100, d)} %`;

/** Return on stakes, centred on 0 %, with its 95 % interval and the +10 % target. */
function RoiBar({ s, target }: { s: Summary; target: number }) {
  if (s.roi == null) return <span className="muted small">pas encore réglé</span>;
  const W = 110;
  const R = 0.6;
  const x = (v: number) => ((Math.max(-R, Math.min(R, v)) + R) / (2 * R)) * W;
  return (
    <span className="ratio" title={`Retour ${signedPct(s.roi, 1)} sur ${s.bets} paris, IC 95 % ${signedPct(s.low, 0)} à ${signedPct(s.high, 0)}`}>
      <svg width={W} height={14} aria-hidden>
        <line x1={x(0)} x2={x(0)} y1={1} y2={13} className="ratio-axis" />
        <line x1={x(target)} x2={x(target)} y1={3} y2={11} className="roi-target" />
        {s.low != null && s.high != null && <line x1={x(s.low)} x2={x(s.high)} y1={7} y2={7} className="ratio-ci" />}
        <circle cx={x(s.roi)} cy={7} r={3.5} className={s.low != null && s.low > 0 ? "ratio-dot strong" : "ratio-dot"} />
      </svg>
      <span className={`num ${s.roi >= 0 ? "ratio-strong" : ""}`}>{signedPct(s.roi)}</span>
    </span>
  );
}

function TotalCard({ title, t, sub }: { title: string; t: BancTotals; sub?: string }) {
  return (
    <div className="card overview-card">
      <div className="kpi-label">{title}</div>
      <div className={`overview-net num ${t.net >= 0 ? "pos" : "neg"}`}>{t.tickets ? signedEuros(t.net) : "—"}</div>
      <dl className="overview-facts">
        <dt>Misé</dt>
        <dd className="num">{euros(t.stake)}</dd>
        <dt>Rapporté</dt>
        <dd className="num">{euros(t.returned)}</dd>
        <dt>Retour</dt>
        <dd className="num">{signedPct(t.roi)}</dd>
      </dl>
      <div className="small muted">
        {int(t.tickets)} ticket{t.tickets > 1 ? "s" : ""} réglé{t.tickets > 1 ? "s" : ""}
        {sub && ` · ${sub}`}
      </div>
    </div>
  );
}

const STATUS_CLASS: Record<BancStrategy["status"], string> = {
  gagnante: "won",
  "en test": "played",
  éliminée: "muted",
  référence: "lost",
};

const ORDER: Record<BancStrategy["status"], number> = { gagnante: 0, "en test": 1, référence: 2, éliminée: 3 };

function History({ s }: { s: BancStrategy }) {
  const e = s.exploration;
  if (e.roi == null) return <span className="muted">—</span>;
  return (
    <div className="small">
      <span className="num" style={{ fontWeight: 600 }}>{signedPct(e.roi)}</span>
      <span className="muted num"> · {int(e.bets ?? 0)} paris</span>
      {e.periods && (
        <div className="muted num" title="Retour par année : la stratégie n'est retenue que si chaque année est positive">
          {e.periods.map((p) => `${p.from.slice(0, 4)} ${signedPct(p.roi)}`).join(" · ")}
        </div>
      )}
      {s.confirmation && (
        <div className="muted" title="Découverte sur 2024, vérifiée une fois sur 2025-2026">
          2025-26 : {signedPct(s.confirmation.roi)} · {s.confirmation.verdict}
        </div>
      )}
    </div>
  );
}

function Progress({ n, of }: { n: number; of: number }) {
  return (
    <div className="bet-progress" title={`${n} paris réglés sur les ${of} nécessaires pour conclure`}>
      <div className="bar">
        <span style={{ width: `${Math.min(100, (n / of) * 100)}%`, background: "var(--accent)" }} />
      </div>
      <span className="small muted num">
        {int(n)}/{of}
      </span>
    </div>
  );
}

export function Banc() {
  const load = useApi(() => api.banc(), "banc", 120_000);
  const [filter, setFilter] = useState<Filter>("play");
  const [bet, setBet] = useState<Bet>("ALL");

  const rows = useMemo(() => {
    if (load.state !== "ready") return [];
    return load.data.strategies
      .filter((s) =>
        filter === "all"
          ? true
          : filter === "winners"
            ? s.status === "gagnante"
            : filter === "gone"
              ? s.status === "éliminée"
              : s.status !== "éliminée",
      )
      .filter((s) => bet === "ALL" || s.bet === bet)
      .sort(
        (a, b) =>
          ORDER[a.status] - ORDER[b.status] ||
          (b.live.roi ?? -9) - (a.live.roi ?? -9) ||
          (b.exploration.low ?? -9) - (a.exploration.low ?? -9),
      );
  }, [load, filter, bet]);

  if (load.state === "loading") return <Loading rows={8} />;
  if (load.state === "error") return <Failure error={load.error} />;
  const d = load.data;
  const gauge = d.gauge.PLAT;
  const c = d.counts;

  return (
    <>
      <PageHead
        crumbs="Paris fictifs · 1 € par ticket · jamais placés"
        title="Banc d'essai des stratégies"
        lead={
          <>
            Chaque course est jouée par toutes les stratégies en test, 25 min avant le départ. Le but : trouver une
            combinaison de critères qui rapporte au moins {signedPct(d.rules.target_roi)} des mises. Bilan séparé du
            carnet.
          </>
        }
      />

      {d.strategies.length === 0 ? (
        <div className="card">
          <Empty title="Banc pas encore constitué">
            <p className="small">
              Il se construit chaque nuit, ou à la main avec <code className="mono">uv run predlab racing banc</code>.
            </p>
          </Empty>
        </div>
      ) : (
        <div className="stack">
          <div className="overview-grid">
            <TotalCard title="Aujourd'hui" t={d.totals.today} />
            <TotalCard
              title="Depuis le début"
              t={d.totals.all}
              sub={d.totals.first_day ? `depuis le ${shortDay(d.totals.first_day)}` : undefined}
            />
            <div className="card overview-card">
              <div className="kpi-label">Stratégies</div>
              <div className="overview-net num">{int((c["en test"] ?? 0) + (c.gagnante ?? 0))}</div>
              <dl className="overview-facts">
                <dt>En test</dt>
                <dd className="num">{int(c["en test"] ?? 0)}</dd>
                <dt>Gagnantes</dt>
                <dd className="num">{int(c.gagnante ?? 0)}</dd>
                <dt>Éliminées</dt>
                <dd className="num">{int(c.éliminée ?? 0)}</dd>
              </dl>
              <div className="small muted">+ {int(c.référence ?? 0)} référence(s) : le favori</div>
            </div>
            <div className="card overview-card">
              <div className="kpi-label">Règles du verdict</div>
              <dl className="overview-facts" style={{ marginTop: 6 }}>
                <dt>Gagnante</dt>
                <dd>{d.rules.win_bets} paris, fourchette &gt; 0</dd>
                <dt>Éliminée</dt>
                <dd>
                  {d.rules.kill_bets} paris, &lt; {signedPct(d.rules.kill_roi)}
                </dd>
                <dt>Objectif</dt>
                <dd>{signedPct(d.rules.target_roi)}</dd>
              </dl>
              <div className="small muted">{int(d.totals.pending)} ticket(s) en attente d'arrivée</div>
            </div>
          </div>

          {gauge && gauge.tested > 0 && (
            <div className="callout">
              <strong>Ce que l'historique a appris.</strong>{" "}
              <span className="small">
                Les {gauge.tested} meilleures combinaisons trouvées sur 2024 y rapportaient en moyenne{" "}
                {signedPct(gauge.exploration_roi)}. Rejouées sur 2025-2026, elles font {signedPct(gauge.confirmation_roi)} :{" "}
                {gauge.confirmed === 0
                  ? "aucune ne tient. Ce qui « marche » une année est surtout de la chance."
                  : `${gauge.confirmed} tiennent.`}{" "}
                Le banc ne garde donc que des combinaisons positives <em>chaque année</em> de 2024 à 2026, et seules les
                courses à venir peuvent les déclarer gagnantes.
              </span>
            </div>
          )}

          <section className="card">
            <header className="card-head">
              <h2>Stratégies</h2>
              <div className="row">
                <Segmented<Bet>
                  label="Type de pari"
                  value={bet}
                  onChange={setBet}
                  options={[
                    { value: "ALL", label: "Tous" },
                    { value: "SG", label: "Gagnant" },
                    { value: "SP", label: "Placé" },
                  ]}
                />
                <Segmented<Filter>
                  label="Statut"
                  value={filter}
                  onChange={setFilter}
                  options={[
                    { value: "play", label: "En jeu" },
                    { value: "winners", label: `Gagnantes · ${int(c.gagnante ?? 0)}` },
                    { value: "gone", label: `Éliminées · ${int(c.éliminée ?? 0)}` },
                    { value: "all", label: "Toutes" },
                  ]}
                />
              </div>
            </header>
            {rows.length === 0 ? (
              <Empty title={filter === "winners" ? "Aucune stratégie gagnante pour l'instant" : "Rien à afficher"}>
                {filter === "winners" && (
                  <p className="small">Il faut {d.rules.win_bets} paris réglés en direct avant de pouvoir conclure.</p>
                )}
              </Empty>
            ) : (
              <div className="table-wrap">
                <table className="compact banc">
                  <thead>
                    <tr>
                      <th>Critères</th>
                      <th>Pari</th>
                      <th title="Retour sur les courses passées, et par année">Historique</th>
                      <th title="Paris réglés en direct depuis son entrée au banc">En direct</th>
                      <th className="r">Net</th>
                      <th title="Retour en direct, avec sa fourchette à 95 %. Trait vertical : l'objectif">Retour en direct</th>
                      <th>Statut</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((s) => (
                      <tr key={s.id} className={s.status === "éliminée" ? "dim" : undefined}>
                        <td>
                          <div className="criteria">
                            {s.criteria_list.map((k) => (
                              <span key={k.key} className="crit" title={k.label}>
                                <span className="crit-key">{k.label}</span> {k.level}
                              </span>
                            ))}
                          </div>
                          <div className="small muted">{s.origin}</div>
                        </td>
                        <td>
                          <span className="badge outline">{s.bet === "SG" ? "Gagnant" : "Placé"}</span>
                        </td>
                        <td>
                          <History s={s} />
                        </td>
                        <td>
                          <Progress n={s.live.bets} of={d.rules.win_bets} />
                          {s.pending > 0 && <div className="small muted">{s.pending} en attente</div>}
                        </td>
                        <td className="r num">{s.live.bets ? signedEuros(s.live.net) : "—"}</td>
                        <td>
                          <RoiBar s={s.live} target={d.rules.target_roi} />
                        </td>
                        <td>
                          <span className={`chip ${STATUS_CLASS[s.status]}`}>{s.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      )}
    </>
  );
}
