import { OddsSparkline, ProbBar } from "../components/charts";
import { Card, DisciplineBadge, Empty, Failure, KindBadge, Kpi, Loading, PageHead } from "../components/ui";
import { api, type RaceDetail, type RunnerRow, type Tally } from "../lib/api";
import { euros, euros0, fmt, int, longDay, minutesUntil, odds, pct, relative, time } from "../lib/format";
import { href, useApi } from "../lib/hooks";

const SHOEING: Record<string, string> = {
  DEFERRE_ANTERIEURS: "D. antérieurs",
  DEFERRE_POSTERIEURS: "D. postérieurs",
  DEFERRE_ANTERIEURS_POSTERIEURS: "D. 4 pieds",
  PROTEGE_ANTERIEURS: "Protégé ant.",
  PROTEGE_POSTERIEURS: "Protégé post.",
  PROTEGE_ANTERIEURS_POSTERIEURS: "Protégé 4 pieds",
};

const SEX: Record<string, string> = { MALES: "M", FEMELLES: "F", HONGRES: "H" };

const tally = (t: Tally | null) =>
  t && t.runs > 0 ? (
    <span className="muted small num" title={`${t.wins} victoires sur ${t.runs} courses dans la discipline, avant ce jour`}>
      {pct(t.wins / t.runs, 0)} v. · {int(t.runs)} c.
    </span>
  ) : null;

function History({ r }: { r: RunnerRow }) {
  if (!r.history) return <span className="muted small">aucune course en base</span>;
  const h = r.history;
  return (
    <div className="small">
      <span className="num">
        {h.runs} c. · {h.wins} v. · {h.places} pl.
      </span>
      <div className="mono muted" title="5 dernières places connues de la base, la plus récente à gauche">
        {h.last5.map((p) => (p === "-" ? "·" : p)).join(" ")}
      </div>
    </div>
  );
}

function RunnersTable({ data }: { data: RaceDetail }) {
  const trot = data.race.discipline !== "PLAT";
  const maxP = Math.max(0.01, ...data.runners.map((r) => r.calibrated_p ?? r.market_p ?? 0));
  const showResult = data.race.is_final;
  return (
    <div className="table-wrap">
      <table className="runners">
        <thead>
          <tr>
            {showResult && <th className="r">Arr.</th>}
            <th className="r">N°</th>
            <th>
              Cheval<span className="th-kind"><KindBadge kind="fact" short /></span>
            </th>
            <th>{data.race.discipline === "ATTELE" ? "Driver" : "Jockey"} · Entraîneur<span className="th-kind"><KindBadge kind="feature" short /></span></th>
            {trot ? (
              <>
                <th className="r">Distance</th>
                <th>Ferrure</th>
              </>
            ) : (
              <>
                <th className="r">Corde</th>
                <th className="r">Poids</th>
              </>
            )}
            <th className="r">
              Cote<span className="th-kind"><KindBadge kind="market" short /></span>
            </th>
            <th>
              Marché brut<span className="th-kind"><KindBadge kind="market" short /></span>
            </th>
            <th title="Marché corrigé du biais favori–outsider (loi de puissance ajustée en backtest)">
              Marché calibré<span className="th-kind"><KindBadge kind="market" short /></span>
            </th>
            <th title="Probabilité d'être placé, déduite du marché calibré par le modèle d'ordre de Harville">
              Placé (Harville)<span className="th-kind"><KindBadge kind="market" short /></span>
            </th>
            <th title="Probabilité implicite (1/cote) dans le temps. Pointillé : départ programmé. Après : cotes de clôture, jamais utilisées par un modèle.">
              Évolution
            </th>
            <th>
              Historique<span className="th-kind"><KindBadge kind="feature" short /></span>
            </th>
          </tr>
        </thead>
        <tbody>
          {data.runners.map((r) => {
            const out = r.status !== "PARTANT";
            return (
              <tr key={r.number} className={out ? "dim" : undefined}>
                {showResult && (
                  <td className="r num" style={{ fontWeight: 600 }}>
                    {r.finish_position ?? (out ? "NP" : "—")}
                  </td>
                )}
                <td className="r num">{r.number}</td>
                <td>
                  {r.horse_id ? <a href={href("cheval", r.horse_id)}>{r.name}</a> : r.name}
                  <div className="muted small">
                    {[r.sex && (SEX[r.sex] ?? r.sex), r.age && `${r.age} ans`].filter(Boolean).join(" · ")}
                    {out && <span className="badge warn" style={{ marginLeft: 6 }}>Non-partant</span>}
                  </div>
                </td>
                <td>
                  <div className="row" style={{ gap: 6 }}>
                    {r.jockey ?? "—"} {tally(r.jockey_stats)}
                  </div>
                  <div className="row muted small" style={{ gap: 6 }}>
                    {r.trainer ?? "—"} {tally(r.trainer_stats)}
                  </div>
                </td>
                {trot ? (
                  <>
                    <td className="r num">{r.handicap_distance ? `${int(r.handicap_distance)} m` : "—"}</td>
                    <td className="small">{r.shoeing ? SHOEING[r.shoeing] ?? r.shoeing : "—"}</td>
                  </>
                ) : (
                  <>
                    <td className="r num">{r.draw ?? "—"}</td>
                    <td className="r num">{r.weight_kg ? `${fmt(r.weight_kg, 1)} kg` : "—"}</td>
                  </>
                )}
                <td className="r num" style={{ fontWeight: 600 }}>
                  {odds(r.odds)}
                </td>
                <td>
                  <ProbBar p={r.market_p} scale={maxP} />
                </td>
                <td>
                  <ProbBar p={r.calibrated_p} scale={maxP} />
                </td>
                <td>
                  <ProbBar p={r.place_p} />
                </td>
                <td>
                  <OddsSparkline series={r.odds_series} offTime={data.race.off_time} />
                </td>
                <td>
                  <History r={r} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function Result({ data }: { data: RaceDetail }) {
  if (!data.race.is_final) return null;
  const byBet = new Map<string, typeof data.dividends>();
  for (const d of data.dividends) byBet.set(d.label, [...(byBet.get(d.label) ?? []), d]);
  return (
    <Card title="Arrivée et rapports officiels" aside={<KindBadge kind="fact" />}>
      <div className="stack">
        <div className="row">
          <span className="muted">Arrivée :</span>
          <strong className="num" style={{ fontSize: 18, letterSpacing: "0.04em" }}>
            {data.finish_order?.map((g) => g.join("=")).join(" – ") ?? "—"}
          </strong>
        </div>
        {data.dividends.length === 0 ? (
          <p className="muted small">Rapports pas encore collectés.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Pari</th>
                  <th>Combinaison</th>
                  <th className="r">Rapport pour 1 €</th>
                  <th className="r">Pour la mise de base</th>
                </tr>
              </thead>
              <tbody>
                {[...byBet.entries()].flatMap(([label, rows]) =>
                  rows.map((d, i) => (
                    <tr key={`${label}-${d.combination}-${i}`}>
                      <td>{i === 0 ? label : ""}</td>
                      <td className="num">{d.refunded ? "remboursé" : d.combination}</td>
                      <td className="r num">{euros(d.per_euro)}</td>
                      <td className="r num muted">
                        {euros(d.per_euro * d.base_stake)} <span className="small">({euros(d.base_stake)})</span>
                      </td>
                    </tr>
                  )),
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Card>
  );
}

export function Race({ day, rc }: { day: string; rc: string }) {
  const upcomingPoll = 60_000;
  const load = useApi(() => api.race(day, rc), `${day}/${rc}`, upcomingPoll);

  if (load.state === "loading") return <Loading rows={8} />;
  if (load.state === "error") return <Failure error={load.error} />;
  const data = load.data;
  const r = data.race;
  const m = minutesUntil(r.off_time);
  const w = data.conditions.weather;
  return (
    <>
      <PageHead
        crumbs={
          <>
            <a href={href("jour", r.day)}>{longDay(r.day)}</a> · R{r.meeting} {r.venue}
          </>
        }
        title={
          <span className="row" style={{ gap: 10 }}>
            {r.rc} · {r.name ?? "Course"}
          </span>
        }
        lead={
          <span className="row">
            <DisciplineBadge d={r.discipline} />
            {r.has_quinte && <span className="badge k-assoc">Quinté+</span>}
            {r.category && <span className="badge outline">{r.category.replaceAll("_", " ").toLowerCase()}</span>}
            <span className="muted">
              Départ {r.off_local} · {m > 0 ? relative(m) : r.is_final ? "arrivée officielle" : "courue"}
            </span>
          </span>
        }
      />

      <div className="stack">
        <div className="kpis">
          <Kpi label="Distance" value={r.distance_m ? `${int(r.distance_m)} m` : "—"} kind="fact" sub={data.conditions.handedness === "LEFT" ? "Corde à gauche" : data.conditions.handedness === "RIGHT" ? "Corde à droite" : undefined} />
          <Kpi label="Partants" value={data.runners.filter((x) => x.status === "PARTANT").length || "—"} kind="fact" sub={`${r.declared_runners ?? "?"} déclarés`} />
          <Kpi label="Terrain" value={r.going ? r.going.toLowerCase() : "—"} kind="fact" sub={r.going_value ? `pénétromètre ${fmt(r.going_value, 1)}` : undefined} />
          <Kpi label="Allocation" value={euros0(data.conditions.prize_eur)} kind="fact" sub={w ? `Prévision : ${w.temperature_c ?? "?"} °C, ${w.sky?.toLowerCase() ?? ""}` : undefined} />
          <Kpi
            label="Cotes à"
            value={data.market_as_of ? time(data.market_as_of) : "—"}
            kind="market"
            sub={
              data.minutes_before_off != null
                ? `T-${fmt(data.minutes_before_off, 0)} min · ${data.snapshots} instantanés`
                : `${data.snapshots} instantanés`
            }
          />
        </div>

        <Card
          title="Partants"
          aside={
            <span className="muted small">
              {data.calibration_alpha != null
                ? `Calibration α = ${fmt(data.calibration_alpha, 2)} (dernier backtest ${r.discipline_label.toLowerCase()})`
                : "Pas encore de backtest : marché calibré indisponible"}
            </span>
          }
          flush
        >
          {data.runners.length === 0 ? (
            <Empty title="Partants pas encore collectés">
              <p className="small">Le collecteur les prend dès la veille, puis toutes les 5 min dans l'heure du départ.</p>
            </Empty>
          ) : (
            <RunnersTable data={data} />
          )}
        </Card>

        <div className="grid-2">
          <Card title="Prévision du laboratoire" aside={<KindBadge kind="forecast" />}>
            <div className="empty" style={{ padding: "12px 0" }}>
              <strong>Aucun modèle fondamental évalué pour l'instant</strong>
              <p className="small" style={{ margin: 0 }}>
                Le marché calibré est la référence. Une prévision n'apparaîtra ici qu'une fois qu'un modèle aura battu le
                marché calibré hors échantillon (méthodologie §5).
              </p>
            </div>
          </Card>
          <Card title="Lire ce tableau">
            <ul className="small" style={{ margin: 0, paddingLeft: 18, color: "var(--ink-2)" }}>
              <li>
                <strong>Marché brut</strong> : 1/cote normalisé. Il contient la marge du PMU et le biais favori–outsider.
              </li>
              <li>
                <strong>Marché calibré</strong> : la barre à battre. Même information, corrigée d'un biais mesuré sur le passé.
              </li>
              <li>
                <strong>Historique</strong> : uniquement les courses <em>antérieures</em> à ce jour présentes dans la base.
              </li>
              <li>Les courbes après le pointillé sont des cotes de clôture : jamais une entrée de modèle.</li>
            </ul>
          </Card>
        </div>

        <Result data={data} />
      </div>
    </>
  );
}
