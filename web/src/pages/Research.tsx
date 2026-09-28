import { Card, Empty, Failure, Loading, PageHead } from "../components/ui";
import { api, type Hypothesis } from "../lib/api";
import { dateTime } from "../lib/format";
import { useApi } from "../lib/hooks";

const STATUS: Record<Hypothesis["status"], { label: string; cls: string }> = {
  PROPOSED: { label: "Proposée", cls: "outline" },
  TESTING: { label: "En test", cls: "k-feature" },
  REJECTED: { label: "Rejetée", cls: "k-fact" },
  INCONCLUSIVE: { label: "Non concluante", cls: "k-assoc" },
  SUPPORTED: { label: "Soutenue", cls: "k-forecast" },
};

const ORIGIN: Record<Hypothesis["origin"], string> = {
  human: "Chris",
  literature: "Littérature",
  folk_heuristic: "Savoir turfiste",
  automated: "Agent",
};

export function Research() {
  const load = useApi(() => api.hypotheses(), "hypotheses");
  return (
    <>
      <PageHead
        crumbs="Registre d'hypothèses"
        title="Recherche"
        lead="Toute idée testée est enregistrée avant le test, y compris celles qui échouent : c'est ce qui fixe la correction pour tests multiples. Non concluante ≠ rejetée."
      />
      {load.state === "loading" && <Loading />}
      {load.state === "error" && <Failure error={load.error} />}
      {load.state === "ready" && load.data.hypotheses.length === 0 && (
        <div className="card">
          <Empty title="Aucune hypothèse enregistrée">
            <p className="small">
              <code className="mono">uv run predlab hypothesis add "…"</code>
            </p>
          </Empty>
        </div>
      )}
      {load.state === "ready" && load.data.hypotheses.length > 0 && (
        <div className="stack">
          {load.data.hypotheses.map((h) => (
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
                {h.experiment && (
                  <>
                    <dt>Expérience</dt>
                    <dd className="mono">{h.experiment}</dd>
                  </>
                )}
                {h.in_sample_result && (
                  <>
                    <dt>En échantillon</dt>
                    <dd>{h.in_sample_result}</dd>
                  </>
                )}
                {h.out_of_sample_result && (
                  <>
                    <dt>Hors échantillon</dt>
                    <dd>{h.out_of_sample_result}</dd>
                  </>
                )}
                {h.forward_result && (
                  <>
                    <dt>En conditions réelles</dt>
                    <dd>{h.forward_result}</dd>
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
      )}
    </>
  );
}
