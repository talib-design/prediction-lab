import { Card, Empty, Failure, Kpi, Loading, PageHead } from "../../components/ui";
import { FreqChart } from "../../components/em";
import { api, type EmTest, type Hypothesis } from "../../lib/api";
import { fmt, int, shortDay, signedPct } from "../../lib/format";
import { useApi } from "../../lib/hooks";

const STATUS: Record<Hypothesis["status"], { label: string; cls: string }> = {
  PROPOSED: { label: "Pré-enregistré", cls: "outline" },
  TESTING: { label: "En test", cls: "k-feature" },
  REJECTED: { label: "Rejeté", cls: "k-fact" },
  INCONCLUSIVE: { label: "Rien de détecté", cls: "k-assoc" },
  SUPPORTED: { label: "Retenu", cls: "k-forecast" },
};

const pText = (p: number | null | undefined) =>
  p == null ? "—" : p < 0.001 ? "< 0,001" : fmt(p, 3);
const zText = (z: number) => `${z >= 0 ? "+" : "−"}${fmt(Math.abs(z), 2)}`;

/** Ratio of hits to chance, with the smallest effect the test could have seen. */
function RatioBar({ ratio, detectable }: { ratio: number; detectable: number }) {
  const W = 140;
  const R = 0.16;
  const x = (v: number) => ((Math.max(1 - R, Math.min(1 + R, v)) - (1 - R)) / (2 * R)) * W;
  const reach = detectable - 1;
  return (
    <span
      className="ratio"
      title={`Ratio ${fmt(ratio, 3)} ; un effet de ±${fmt(reach * 100, 0)} % aurait été vu 8 fois sur 10.`}
    >
      <svg width={W} height={14} aria-hidden>
        <rect x={x(1 - reach)} y={3} width={x(1 + reach) - x(1 - reach)} height={8} rx={2} className="em-band" />
        <line x1={x(1)} x2={x(1)} y1={1} y2={13} className="ratio-axis" />
        <circle cx={x(ratio)} cy={7} r={3.5} className="ratio-dot" />
      </svg>
    </span>
  );
}

function TestsTable({ rows, observed }: { rows: EmTest[]; observed?: string }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Test</th>
            <th className="r">Tirages</th>
            {observed && <th className="r">{observed}</th>}
            <th className="r">p</th>
            <th className="r">q (corrigé)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.test_id}>
              <td>{r.label}</td>
              <td className="r num">{int(r.n_draws)}</td>
              {observed && (
                <td className="r num">
                  {r.observed == null ? "—" : fmt(r.observed, 2)}
                  {r.expected != null && <span className="muted"> / {fmt(r.expected, 2)}</span>}
                </td>
              )}
              <td className="r num">{pText(r.p_value)}</td>
              <td className="r num">{pText(r.q_value)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function EmHistory() {
  const load = useApi(() => api.em.analysis(), "em-analysis");
  if (load.state === "loading") return <Loading rows={8} />;
  if (load.state === "error") return <Failure error={load.error} />;
  const { analysis, control, hypotheses } = load.data;
  if (!analysis)
    return (
      <div className="card">
        <Empty title="Analyse pas encore lancée">
          <p className="small">
            <code className="mono">uv run predlab lottery analyze</code>
          </p>
        </Empty>
      </div>
    );
  const s = analysis.summary;
  const total = Object.values(s).reduce((a, f) => a + f.tests, 0);
  const nominal = Object.values(s).reduce((a, f) => a + f.nominal_p_lt_0_05, 0);
  const survivors = Object.values(s).reduce((a, f) => a + f.bh_survivors, 0);
  const res = analysis.results;
  const ballsAll = res.find((r) => r.test_id === "A1/balls/all");
  const stars = res.find((r) => r.test_id === "A1/stars/2016-09");
  const theories = res.filter((r) => r.family === "B");
  const extremes = res
    .filter((r) => r.family === "A2")
    .sort((a, b) => a.p_value - b.p_value)
    .slice(0, 3);
  return (
    <>
      <PageHead
        crumbs="EuroMillions · historique"
        title={`Que disent ${int(analysis.n_draws)} tirages ?`}
        lead={`Tous les tirages officiels du ${shortDay(analysis.first_draw)} au ${shortDay(analysis.last_draw)}. Chaque test a été inscrit au registre avant d'être calculé, avec sa règle de décision.`}
      />
      <div className="stack">
        <div className="kpis">
          <Kpi label="Tests" value={int(total)} sub="mécanisme, théories, forme" />
          <Kpi label="À p < 0,05" value={int(nominal)} sub={`${fmt(0.05 * total, 1)} attendus au hasard seul`} />
          <Kpi label="Après correction" value={int(survivors)} sub="tests multiples (Benjamini-Hochberg)" />
          <Kpi
            label="Contrôle 100 % hasard"
            value={control ? (control.passed ? "Réussi" : "Échec") : "—"}
            sub={control ? `${int(control.histories)} historiques fabriqués` : "pas encore lancé"}
          />
        </div>

        <div className="callout small">
          <strong>En bref.</strong> Les numéros chauds, froids, en retard ou répétés ne sortent ni plus ni moins que les
          autres. Le tirage se comporte comme un hasard équitable et sans mémoire, à la précision que{" "}
          {int(analysis.n_draws)} tirages permettent. Le seul effet net porte sur les joueurs : les petits numéros,
          surjoués, rapportent moins quand ils sortent.
        </div>

        {ballsAll && (
          <Card title="Les 50 boules depuis 2004" aside={<span className="small muted">p = {pText(ballsAll.p_value)}</span>}>
            <FreqChart counts={ballsAll.detail.counts} draws={ballsAll.n_draws} k={5} label="Sorties de chaque boule depuis 2004" />
          </Card>
        )}
        {stars && (
          <Card title="Les 12 étoiles depuis septembre 2016" aside={<span className="small muted">p = {pText(stars.p_value)}</span>}>
            <FreqChart counts={stars.detail.counts} draws={stars.n_draws} k={2} label="Sorties de chaque étoile depuis 2016" />
          </Card>
        )}

        <Card title="Les numéros qui s'écartent le plus" flush>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Numéro</th>
                  <th className="r">Sorties</th>
                  <th className="r">Attendues</th>
                  <th className="r">p</th>
                  <th className="r">q (corrigé)</th>
                </tr>
              </thead>
              <tbody>
                {extremes.map((r) => (
                  <tr key={r.test_id}>
                    <td>{r.label.replace("(all)", "(2004-2026)").replace(/\((\d{4}-\d{2})\)/, "(époque $1)")}</td>
                    <td className="r num">{int(r.observed)}</td>
                    <td className="r num">{fmt(r.expected, 1)}</td>
                    <td className="r num">{pText(r.p_value)}</td>
                    <td className="r num">{pText(r.q_value)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="small muted card-body" style={{ margin: 0 }}>
              Sur 82 numéros testés, {s.A2?.nominal_p_lt_0_05 ?? "—"} sortent à p &lt; 0,05 pour{" "}
              {fmt(s.A2?.expected_by_chance ?? null, 1)} attendus au hasard. Le plus extrême a gagné un concours entre
              82 candidats : seul le q corrigé compte.
            </p>
          </div>
        </Card>

        <Card title="Chaud, froid, séries, retard" flush>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Théorie</th>
                  <th className="r">Tirages</th>
                  <th>Sorties / hasard</th>
                  <th className="r">Ratio</th>
                  <th className="r">z</th>
                  <th className="r">q</th>
                  <th className="r">Avant 2020 / depuis</th>
                </tr>
              </thead>
              <tbody>
                {theories.map((r) => (
                  <tr key={r.test_id}>
                    <td>{r.label}</td>
                    <td className="r num">{int(r.n_draws)}</td>
                    <td>
                      <RatioBar ratio={r.detail.ratio} detectable={r.detail.detectable_ratio} />
                    </td>
                    <td className="r num">{fmt(r.detail.ratio, 3)}</td>
                    <td className="r num">{zText(r.statistic)}</td>
                    <td className="r num">{pText(r.q_value)}</td>
                    <td className="r num">
                      {zText(r.detail.early.z)} / {zText(r.detail.late.z)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="small muted card-body" style={{ margin: 0 }}>
              Ratio = sorties des numéros choisis par la théorie / sorties attendues au hasard. Le point est le
              résultat ; la bande, la plus petite différence que le test aurait vue 8 fois sur 10. Un point dans la
              bande : rien de mesurable.
            </p>
          </div>
        </Card>

        <div className="grid-2">
          <Card title="Le mécanisme est-il équitable ?" flush>
            <TestsTable rows={res.filter((r) => r.family === "A1" || r.family === "A4")} />
          </Card>
          <Card title="La forme des tirages" flush>
            <TestsTable rows={res.filter((r) => ["C1", "C2", "C3"].includes(r.family))} observed="Observé / hasard" />
          </Card>
        </div>

        {analysis.d3_popularity.length > 0 && (
          <Card title="Popularité des numéros et gains" aside={<span className="badge k-forecast">effet net</span>} flush>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Rang</th>
                    <th className="r">Tirages</th>
                    <th className="r">Rapport par boule ≤ 31 en plus</th>
                    <th className="r">p</th>
                  </tr>
                </thead>
                <tbody>
                  {analysis.d3_popularity.map((r) => (
                    <tr key={r.test_id}>
                      <td>{r.test_id.replace("D3/rank", "rang ")}</td>
                      <td className="r num">{int(r.n_draws)}</td>
                      <td className="r num">{signedPct(r.observed, 1)}</td>
                      <td className="r num">{pText(r.p_value)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="small muted card-body" style={{ margin: 0 }}>
                Les joueurs surjouent les petits numéros (dates de naissance). Quand ils sortent, les gagnants sont plus
                nombreux et chacun touche moins. La probabilité de gagner ne change pas, seulement le montant.
              </p>
            </div>
          </Card>
        )}

        {control && (
          <Card title="Contrôle 100 % hasard" aside={<span className={`badge ${control.passed ? "k-forecast" : "k-assoc"}`}>{control.passed ? "réussi" : "échec"}</span>} flush>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Critère inscrit d'avance</th>
                    <th className="r">Seuil</th>
                    <th className="r">Mesuré</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Part des tests à p &lt; 0,05</td>
                    <td className="r">3 % à 7 %</td>
                    <td className="r num">{fmt(control.nominal_rate * 100, 2)} %</td>
                  </tr>
                  {Object.entries(control.histories_with_survivor).map(([fam, frac]) => (
                    <tr key={fam}>
                      <td>Faux signal après correction, famille {fam}</td>
                      <td className="r">≤ 8 %</td>
                      <td className="r num">{fmt(frac * 100, 1)} %</td>
                    </tr>
                  ))}
                  <tr>
                    <td>p des théories uniformes (Kolmogorov-Smirnov)</td>
                    <td className="r">p &gt; 0,01</td>
                    <td className="r num">{pText(control.ks_p_family_b)}</td>
                  </tr>
                </tbody>
              </table>
              <p className="small muted card-body" style={{ margin: 0 }}>
                La même batterie, lancée sur {int(control.histories)} historiques fabriqués 100 % au hasard. Si le labo y
                trouvait des signaux, ses conclusions sur les vrais tirages ne vaudraient rien.
              </p>
            </div>
          </Card>
        )}

        <Card title="Registre des hypothèses" aside={<span className="small muted">chaîné, en ajout seul</span>} flush>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Hypothèse</th>
                  <th>Statut</th>
                  <th>Conclusion</th>
                </tr>
              </thead>
              <tbody>
                {hypotheses.map((h) => (
                  <tr key={h.hypothesis_id}>
                    <td style={{ maxWidth: 420 }}>
                      <span className="mono">{h.hypothesis_id}</span>{" "}
                      <span className="small">{h.description.split(" -- ")[1]?.split(".")[0] ?? h.description}</span>
                    </td>
                    <td>
                      <span className={`badge ${STATUS[h.status].cls}`}>{STATUS[h.status].label}</span>
                    </td>
                    <td className="small">{h.conclusion ?? <span className="muted">en cours</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </>
  );
}
