import { useMemo, useState } from "react";
import { IntervalChart, ReliabilityChart } from "../components/charts";
import { Card, Empty, Failure, KindBadge, Kpi, Loading, PageHead, Segmented, disciplineLabel } from "../components/ui";
import { api, type BacktestReport, type Discipline, type ReportListItem, type SimulationReport } from "../lib/api";
import { PHASE_LABELS, dateTime, euros, fmt, int, modelLabel, pct, signedPct } from "../lib/format";
import { useApi } from "../lib/hooks";

const PLANNED_TEST_RACES = 8000;

function ReportPicker({
  items,
  value,
  onChange,
}: {
  items: ReportListItem[];
  value: string | undefined;
  onChange: (id: string) => void;
}) {
  if (items.length < 2) return null;
  return (
    <select className="btn" value={value} onChange={(e) => onChange(e.target.value)} aria-label="Choisir un rapport">
      {items.map((r) => (
        <option key={r.id} value={r.id}>
          {dateTime(r.generated_at)} · {int(r.n_eligible)} courses
        </option>
      ))}
    </select>
  );
}

function Backtest({ id }: { id: string }) {
  const load = useApi(() => api.report<BacktestReport>(id), id);
  if (load.state === "loading") return <Loading />;
  if (load.state === "error") return <Failure error={load.error} />;
  const rep = load.data;
  const phase = rep.decision_phase;
  const rows = rep.summary[phase] ?? [];
  const ref = rows.find((r) => r.model === rep.reference);
  const n = ref?.n_races ?? 0;
  // Pre-registered planning figure (docs/STATUS.md, audit): ~2 years of test races to
  // detect a 0.01 log-loss gain. Per-model figures are listed under the forest plot.
  const needed = PLANNED_TEST_RACES;
  const tooSmall = n < needed;
  const intervals = rep.comparisons
    .filter((c) => c.mean_difference != null)
    .map((c) => ({
      label: modelLabel(c.model),
      est: c.mean_difference!,
      lo: c.ci_low,
      hi: c.ci_high,
      tone: c.verdict === "meilleur que la référence" ? ("strong" as const) : ("neutral" as const),
    }));
  return (
    <div className="stack">
      <div className="kpis">
        <Kpi label="Courses évaluées" value={int(rep.n_eligible)} kind="fact" sub={`sur ${int(rep.n_events)} chargées`} />
        <Kpi label="Phase de décision" value={PHASE_LABELS[phase] ?? phase} sub={`horizon T-${rep.horizon_minutes} min`} />
        <Kpi
          label="Log loss du marché calibré"
          value={fmt(ref?.log_loss, 4)}
          kind="market"
          sub={rep.alpha != null ? `α = ${fmt(rep.alpha, 3)} (${rep.alpha_refits ?? 0} ajustements)` : undefined}
        />
        <Kpi
          label="Courses de test"
          value={`${int(n)} / ~${int(needed)}`}
          sub="requises pour détecter Δ = 0,01 (estimation)"
        />
      </div>
      {tooSmall && (
        <div className="note warn">
          <span>
            <strong>Échantillon trop petit pour conclure.</strong> Il faut de l'ordre de {int(needed)} courses en
            phase {PHASE_LABELS[phase]?.toLowerCase()} pour détecter un écart de 0,01 face au marché. Les écarts
            énormes (modèles naïfs) restent visibles ; un gain fin, non.
          </span>
        </div>
      )}
      <Card title={`Scores par modèle — ${PHASE_LABELS[phase] ?? phase}`} aside={<span className="muted small">plus bas = mieux (log loss, Brier)</span>} flush>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Modèle</th>
                <th className="r">Courses</th>
                <th className="r">Log loss</th>
                <th className="r">Brier</th>
                <th className="r">Gagnant en tête</th>
                <th className="r">Rang réciproque</th>
                <th className="r">Erreur de calibration</th>
              </tr>
            </thead>
            <tbody>
              {[...rows]
                .sort((a, b) => a.log_loss - b.log_loss)
                .map((r) => (
                  <tr key={r.model} style={r.model === rep.reference ? { background: "var(--k-market-bg)" } : undefined}>
                    <td>
                      {modelLabel(r.model)}
                      {r.model === rep.reference && <span className="badge k-market" style={{ marginLeft: 8 }}>référence</span>}
                    </td>
                    <td className="r num">{int(r.n_races)}</td>
                    <td className="r num" style={{ fontWeight: 600 }}>
                      {fmt(r.log_loss, 4)}
                    </td>
                    <td className="r num">{fmt(r.brier, 4)}</td>
                    <td className="r num">{pct(r.top1)}</td>
                    <td className="r num">{fmt(r.mrr, 3)}</td>
                    <td className="r num">{fmt(r.calibration_error, 4)}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </Card>
      <div className="grid-2">
        <Card title="Écart au marché calibré" aside={<KindBadge kind="forecast" />}>
          <p className="small muted" style={{ marginTop: 0 }}>
            Différence de log loss appariée course par course, IC 95 % bootstrap par blocs. À gauche de 0 : mieux que le
            marché calibré.
          </p>
          {intervals.length ? (
            <IntervalChart rows={intervals} format={(v) => fmt(v, 4)} zeroLabel="marché calibré" />
          ) : (
            <Empty title="Pas assez de courses pour comparer" />
          )}
          <ul className="small" style={{ paddingLeft: 18, color: "var(--ink-2)" }}>
            {rep.comparisons.map((c) => (
              <li key={c.model}>
                {modelLabel(c.model)} : <strong>{c.verdict}</strong>
                {c.p_value != null && ` (p = ${fmt(c.p_value, 3)}${c.survives_fdr ? ", survit à la correction BY" : ""})`}
                {c.minimum_detectable_effect != null && (
                  <span className="muted"> · écart détectable ≈ {fmt(c.minimum_detectable_effect, 3)}</span>
                )}
              </li>
            ))}
          </ul>
        </Card>
        <Card title="Calibration du marché" aside={<KindBadge kind="market" />}>
          <p className="small muted" style={{ marginTop: 0 }}>
            Chaque point : une tranche de probabilité. Sur la diagonale = calibré. Taille = nombre de partants.
          </p>
          <div className="row" style={{ alignItems: "flex-start", gap: 16 }}>
            {(["market", "market_calibrated"] as const).map((m) =>
              rep.calibration[m]?.length ? (
                <div key={m} style={{ flex: "1 1 200px" }}>
                  <h3>{modelLabel(m)}</h3>
                  <ReliabilityChart rows={rep.calibration[m]!} size={240} maxP={0.7} />
                </div>
              ) : null,
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}

function Simulation({ id }: { id: string }) {
  const load = useApi(() => api.report<SimulationReport>(id), id);
  const [phase, setPhase] = useState<string | undefined>();
  if (load.state === "loading") return <Loading />;
  if (load.state === "error") return <Failure error={load.error} />;
  const rep = load.data;
  const current = phase ?? rep.decision_phase;
  const rows = (rep.by_phase[current] ?? []).filter((r) => r.races > 0);
  const phases = Object.keys(rep.by_phase);
  return (
    <div className="stack">
      <div className="note">
        <span>
          <strong>Paris fictifs.</strong> Aucune mise réelle : une unité par ticket (1 €, 2 € au Quinté+), décision à
          T-{rep.horizon_minutes} min, réglée au rapport officiel. Résultat attendu, annoncé d'avance : une perte pour
          toutes les stratégies (prélèvement du PMU). La question est de perdre <em>significativement moins</em> que les
          témoins.
        </span>
      </div>
      <div className="row" style={{ justifyContent: "space-between" }}>
        <span className="muted small">
          {int(rep.n_races_with_dividends)} courses réglées sur {int(rep.n_eligible)} évaluées · seuil de valeur p × cote ≥{" "}
          {fmt(rep.value_threshold, 2)}
        </span>
        {phases.length > 1 && (
          <Segmented
            label="Phase"
            value={current}
            onChange={setPhase}
            options={phases.map((p) => ({ value: p, label: PHASE_LABELS[p] ?? p }))}
          />
        )}
      </div>
      {rows.length === 0 ? (
        <div className="card">
          <Empty title="Aucune course réglée dans cette phase">
            <p className="small">Les rapports officiels arrivent avec le rattrapage.</p>
          </Empty>
        </div>
      ) : (
        <>
          <Card title="Retour sur mise (ROI) avec IC 95 %">
            <IntervalChart
              rows={rows.map((r) => ({
                label: r.strategy,
                est: r.roi ?? 0,
                lo: r.roi_low,
                hi: r.roi_high,
                tone: r.verdict === "gain significatif" ? "strong" : r.strategy.includes("hasard") ? "muted" : "neutral",
              }))}
              format={(v) => signedPct(v)}
              zeroLabel="à l'équilibre"
            />
          </Card>
          <Card title="Détail par stratégie" flush>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Stratégie</th>
                    <th className="r">Courses</th>
                    <th className="r">Misé</th>
                    <th className="r">Net</th>
                    <th className="r">ROI</th>
                    <th className="r">IC 95 %</th>
                    <th className="r">Réussite</th>
                    <th className="r" title="Part du total rapporté par le plus gros gain">Plus gros gain</th>
                    <th>Verdict</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r) => (
                    <tr key={r.strategy}>
                      <td>{r.strategy}</td>
                      <td className="r num">{int(r.races)}</td>
                      <td className="r num">{euros(r.stake)}</td>
                      <td className="r num">{euros(r.net)}</td>
                      <td className="r num" style={{ fontWeight: 600 }}>
                        {signedPct(r.roi)}
                      </td>
                      <td className="r num muted">
                        {signedPct(r.roi_low, 0)} ; {signedPct(r.roi_high, 0)}
                      </td>
                      <td className="r num">{pct(r.hit_rate)}</td>
                      <td className="r num">{pct(r.largest_share, 0)}</td>
                      <td>
                        <span className={`badge ${r.verdict === "gain significatif" ? "k-forecast" : "outline"}`}>{r.verdict}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
      {rep.place_calibration.length > 0 && (
        <Card title="Probabilités de place (Harville sur le marché calibré)" aside={<KindBadge kind="market" />}>
          <div style={{ maxWidth: 300 }}>
            <ReliabilityChart rows={rep.place_calibration} size={260} maxP={1} />
          </div>
        </Card>
      )}
    </div>
  );
}

export function Performance() {
  const load = useApi(() => api.reports(), "reports");
  const [discipline, setDiscipline] = useState<Discipline>("PLAT");
  const [kind, setKind] = useState<"backtest" | "simulation">("backtest");
  const [picked, setPicked] = useState<string | undefined>();

  const items = useMemo(
    () => (load.state === "ready" ? load.data.reports.filter((r) => r.discipline === discipline && r.kind === kind) : []),
    [load, discipline, kind],
  );
  const id = picked && items.some((r) => r.id === picked) ? picked : items[0]?.id;

  return (
    <>
      <PageHead
        crumbs="Évaluation hors échantillon"
        title="Performance"
        lead="Les modèles face au marché calibré, puis des paris fictifs réglés aux rapports officiels. Rien n'est affiché sans son intervalle d'incertitude."
        aside={
          <div className="row">
            <Segmented<Discipline>
              label="Discipline"
              value={discipline}
              onChange={setDiscipline}
              options={(["PLAT", "ATTELE", "MONTE"] as const).map((d) => ({ value: d, label: disciplineLabel(d) }))}
            />
            <Segmented
              label="Rapport"
              value={kind}
              onChange={setKind}
              options={[
                { value: "backtest", label: "Backtest" },
                { value: "simulation", label: "Paris fictifs" },
              ]}
            />
          </div>
        }
      />
      {load.state === "loading" && <Loading />}
      {load.state === "error" && <Failure error={load.error} />}
      {load.state === "ready" && items.length === 0 && (
        <div className="card">
          <Empty title={`Pas encore de ${kind === "backtest" ? "backtest" : "simulation"} en ${disciplineLabel(discipline).toLowerCase()}`}>
            <p className="small">
              Lancez <code className="mono">uv run predlab racing {kind === "backtest" ? "backtest" : "simulate"} --discipline {discipline}</code>{" "}
              après un <code className="mono">racing build</code>.
            </p>
          </Empty>
        </div>
      )}
      {id && (
        <>
          <div className="row" style={{ justifyContent: "flex-end", marginBottom: 12 }}>
            <ReportPicker items={items} value={id} onChange={setPicked} />
          </div>
          {kind === "backtest" ? <Backtest id={id} /> : <Simulation id={id} />}
        </>
      )}
    </>
  );
}
