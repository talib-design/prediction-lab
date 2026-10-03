import { BetsChart } from "../components/BetsChart";
import { useState } from "react";
import { IntervalChart } from "../components/charts";
import { Card, DisciplineBadge, Empty, Failure, Kpi, Loading, PageHead } from "../components/ui";
import { api, type CarnetEntry, type CarnetTicket } from "../lib/api";
import { euros, int, longDay, pct, shortDay, signedPct, time } from "../lib/format";
import { href, useApi } from "../lib/hooks";
import { ticketTitle } from "../lib/tickets";

export function TicketList({ tickets, settled }: { tickets: CarnetTicket[]; settled: boolean }) {
  if (tickets.length === 0) return <span className="muted small">aucun ticket (paris non proposés)</span>;
  return (
    <div className="row" style={{ gap: 6 }}>
      {tickets.map((t, i) => {
        const won = settled && (t.returned ?? 0) > 0;
        return (
          <span
            key={`${t.strategy}-${i}`}
            className={`chip ${!settled ? "played" : won ? "won" : "lost"}`}
            title={`Mise ${euros(t.stake)}`}
          >
            {ticketTitle(t)} · n°{t.numbers.join("-")}
            {settled && (won ? ` · ${euros(t.returned)}` : " · perdu")}
          </span>
        );
      })}
    </div>
  );
}

function EntryCard({ e }: { e: CarnetEntry }) {
  const stake = e.tickets.reduce((a, t) => a + t.stake, 0);
  const back = e.tickets.reduce((a, t) => a + (t.returned ?? 0), 0);
  return (
    <div className="carnet-entry">
      <div className="row" style={{ justifyContent: "space-between" }}>
        <a href={href("course", e.day, e.rc)} className="row" style={{ gap: 8, color: "var(--ink)" }}>
          <strong className="num">{time(e.off_time)}</strong>
          <span>{[e.rc, e.venue].filter(Boolean).join(" · ")}</span>
          <DisciplineBadge d={e.discipline} />
          {e.has_quinte && <span className="badge k-assoc">Quinté+</span>}
        </a>
        <span className="small muted">
          figé à {time(e.frozen_at)} · cotes de {time(e.odds_as_of)}
        </span>
      </div>
      <TicketList tickets={e.tickets} settled={e.settled} />
      <div className="row small" style={{ justifyContent: "space-between" }}>
        <span className="muted">
          {e.settled
            ? `Arrivée ${e.finish_order?.map((g) => g.join("=")).join("-") ?? "—"}`
            : "En attente du rapport officiel"}
          {e.note && ` · ${e.note}`}
        </span>
        {e.settled && (
          <span className="num">
            misé {euros(stake)} · rapporté <strong>{euros(back)}</strong>
          </span>
        )}
      </div>
    </div>
  );
}

function DaySummary({ entries }: { entries: CarnetEntry[] }) {
  const settled = entries.filter((e) => e.settled);
  const stake = settled.reduce((a, e) => a + e.tickets.reduce((b, t) => b + t.stake, 0), 0);
  const back = settled.reduce((a, e) => a + e.tickets.reduce((b, t) => b + (t.returned ?? 0), 0), 0);
  const fav = settled.flatMap((e) => e.tickets.filter((t) => t.strategy === "SG favori"));
  const favWins = fav.filter((t) => (t.returned ?? 0) > 0).length;
  return (
    <div className="carnet-entry" style={{ background: "var(--surface-2)" }}>
      <div className="row" style={{ gap: 24 }}>
        <span>
          <strong className="num">{entries.length}</strong> <span className="muted">courses jouées</span>
        </span>
        <span>
          <strong className="num">{settled.length}</strong> <span className="muted">réglées</span>
        </span>
        <span>
          <span className="muted">misé</span> <strong className="num">{euros(stake)}</strong>
        </span>
        <span>
          <span className="muted">rapporté</span> <strong className="num">{euros(back)}</strong>
        </span>
        <span>
          <span className="muted">net</span>{" "}
          <strong className="num">
            {back - stake >= 0 ? "+" : "−"}
            {euros(Math.abs(back - stake))}
          </strong>
        </span>
        {fav.length > 0 && (
          <span className="muted small">
            le favori a gagné {favWins} fois sur {fav.length}
          </span>
        )}
      </div>
    </div>
  );
}

function Evolution() {
  const load = useApi(() => api.periods(), "carnet-series", 120_000);
  if (load.state !== "ready") return null;
  return (
    <Card title="Évolution, jour par jour" aside={<span className="muted small">gains cumulés, favori contre modèle, sur les mêmes courses</span>}>
      <BetsChart series={load.data.series} height={220} />
    </Card>
  );
}

export function Carnet() {
  const load = useApi(() => api.carnet(), "carnet", 60_000);
  const [day, setDay] = useState<string | undefined>();
  if (load.state === "loading") return <Loading rows={6} />;
  if (load.state === "error") return <Failure error={load.error} />;
  const c = load.data;
  const current = day ?? c.days[0];
  const shown = c.entries.filter((e) => e.day === current);
  const settledRows = c.summary.filter((r) => r.races > 0);
  const withCi = settledRows.filter((r) => r.roi_low != null && !Number.isNaN(r.roi_low));
  return (
    <>
      <PageHead
        crumbs="Paris fictifs en conditions réelles"
        title="Carnet"
        lead="Chaque ticket est figé 25 minutes avant le départ, avec les seules cotes connues à ce moment, puis réglé au rapport officiel. Aucune mise réelle. Rien n'est jamais réécrit : c'est la seule preuve qui ne dépend pas du passé."
      />
      <div className="stack">
        <Card
          title={current ? <span style={{ textTransform: "capitalize" }}>{longDay(current)}</span> : "Aujourd'hui"}
          aside={
            c.days.length > 1 ? (
              <select className="btn" value={current} onChange={(e) => setDay(e.target.value)} aria-label="Choisir un jour">
                {c.days.map((d) => (
                  <option key={d} value={d}>
                    {shortDay(d)}
                  </option>
                ))}
              </select>
            ) : undefined
          }
          flush
        >
          {shown.length > 0 && <DaySummary entries={shown} />}
          {shown.length === 0 ? (
            <Empty title="Aucun ticket figé pour l'instant">
              <p className="small">
                Le premier sera écrit par le collecteur dans la fenêtre des 25 minutes avant le prochain départ.
              </p>
            </Empty>
          ) : (
            shown.map((e) => <EntryCard key={e.race_id} e={e} />)
          )}
        </Card>
        {c.integrity_error ? (
          <div className="note warn">
            <span>
              <strong>Carnet altéré.</strong> {c.integrity_error}
            </span>
          </div>
        ) : (
          <div className="note small">
            <span>
              Chaîne de hash intacte · {int(c.records)} enregistrements · empreinte{" "}
              <code className="mono">
                {c.head_hash.slice(0, 8)}…{c.head_hash.slice(-6)}
              </code>
              . Un commit git du fichier <code className="mono">data/carnet.jsonl</code> date publiquement ce qui a été
              écrit.
            </span>
          </div>
        )}
        <div className="kpis">
          <Kpi label="Suivi depuis" value={c.first_day ? shortDay(c.first_day) : "—"} sub="figé par le collecteur, toutes les 5 min" />
          <Kpi label="Courses figées" value={int(c.races)} kind="fact" sub="départs manqués (Mac en veille) : jamais rattrapés" />
          <Kpi label="Réglées" value={int(c.settled)} kind="fact" sub={`${int(c.races - c.settled)} en attente du rapport`} />
        </div>

        <Evolution />

        <Card title="Bilan par stratégie" aside={<span className="muted small">1 € par ticket · favori et modèle, en gagnant et en placé</span>}>
          {settledRows.length === 0 ? (
            <Empty title="Pas encore de course réglée">
              <p className="small">
                Le bilan apparaît après la première arrivée officielle. Les intervalles de confiance, à partir de 10 courses
                réglées par stratégie ; un verdict sérieux demande des centaines de courses.
              </p>
            </Empty>
          ) : (
            <div className="stack">
              {withCi.length > 0 && (
                <IntervalChart
                  rows={withCi.map((r) => ({
                    label: r.label,
                    est: r.roi ?? 0,
                    lo: r.roi_low,
                    hi: r.roi_high,
                    tone: r.strategy.includes("hasard") ? "muted" : "neutral",
                  }))}
                  format={(v) => signedPct(v)}
                  zeroLabel="à l'équilibre"
                />
              )}
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Stratégie</th>
                      <th className="r">Courses</th>
                      <th className="r">Misé</th>
                      <th className="r">Rapporté</th>
                      <th className="r">ROI</th>
                      <th className="r">IC 95 %</th>
                      <th className="r">Réussite</th>
                      <th className="r">En attente</th>
                      <th>Verdict</th>
                    </tr>
                  </thead>
                  <tbody>
                    {c.summary.map((r) => (
                      <tr key={r.strategy} className={r.races ? undefined : "dim"}>
                        <td>{r.label}</td>
                        <td className="r num">{int(r.races)}</td>
                        <td className="r num">{euros(r.stake)}</td>
                        <td className="r num">{euros(r.returned)}</td>
                        <td className="r num" style={{ fontWeight: 600 }}>
                          {signedPct(r.roi)}
                        </td>
                        <td className="r num muted">
                          {r.roi_low != null && !Number.isNaN(r.roi_low)
                            ? `${signedPct(r.roi_low, 0)} ; ${signedPct(r.roi_high, 0)}`
                            : "—"}
                        </td>
                        <td className="r num">{pct(r.hit_rate)}</td>
                        <td className="r num">{int(r.pending)}</td>
                        <td>{r.verdict ? <span className="badge outline">{r.verdict}</span> : <span className="muted">—</span>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </Card>

      </div>
    </>
  );
}
