import { useState } from "react";
import { OddsSparkline, ProbBar } from "../components/charts";
import { Card, DisciplineBadge, Empty, Failure, KindBadge, Kpi, Loading, PageHead, Segmented } from "../components/ui";
import { api, type CarnetTicket, type RaceDetail, type RunnerRow, type Tally } from "../lib/api";
import { BET_LABEL, RULE_HELP, rule, ticketTitle } from "../lib/tickets";
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

function History({ r, lab }: { r: RunnerRow; lab: boolean }) {
  if (!r.history) return <span className="muted small">{lab ? "aucune course en base" : "—"}</span>;
  const h = r.history;
  if (!lab)
    return (
      <span className="mono small" title={`${h.runs} courses, ${h.wins} victoires, ${h.places} places (5 dernières, la plus récente à gauche)`}>
        {h.last5.map((p) => (p === "-" ? "·" : p)).join(" ")}
      </span>
    );
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

type Played = Map<number, CarnetTicket[]>;

function playedMap(data: RaceDetail): Played {
  const m: Played = new Map();
  for (const t of data.carnet?.tickets ?? []) {
    if (t.bet_type !== "SIMPLE_GAGNANT" && t.bet_type !== "SIMPLE_PLACE") continue;
    for (const n of t.numbers) m.set(n, [...(m.get(n) ?? []), t]);
  }
  return m;
}

function RunnersTable({ data, lab, played }: { data: RaceDetail; lab: boolean; played: Played }) {
  const trot = data.race.discipline !== "PLAT";
  const K = ({ k }: { k: Parameters<typeof KindBadge>[0]["kind"] }) =>
    lab ? (
      <span className="th-kind">
        <KindBadge kind={k} short />
      </span>
    ) : null;
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
              Cheval
              <K k="fact" />
            </th>
            <th>
              {data.race.discipline === "ATTELE" ? "Driver" : "Jockey"} · Entraîneur
              <K k="feature" />
            </th>
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
              Cote
              <K k="market" />
            </th>
            {lab && (
              <th>
                Marché brut
                <K k="market" />
              </th>
            )}
            <th title="Chance de gagner selon les parieurs, corrigée du biais favori–outsider">
              {lab ? "Marché calibré" : "Chance de gagner"}
              <K k="market" />
            </th>
            {lab && (
              <th title="Probabilité d'être placé, déduite du marché calibré par le modèle d'ordre de Harville">
                Placé (Harville)
                <K k="market" />
              </th>
            )}
            <th title="Probabilité implicite (1/cote) dans le temps. Pointillé : départ programmé. Après : cotes de clôture, jamais utilisées par un modèle.">
              Évolution
            </th>
            <th title="Places des 5 dernières courses en base, la plus récente à gauche">
              {lab ? "Historique" : "Dernières places"}
              <K k="feature" />
            </th>
          </tr>
        </thead>
        <tbody>
          {data.runners.map((r) => {
            const out = r.status !== "PARTANT";
            const mine = played.get(r.number);
            return (
              <tr key={r.number} className={out ? "dim" : mine ? "is-played" : undefined}>
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
                  {mine && (
                    <div className="played-mark">
                      {mine.map((t) => (
                        <span key={t.strategy} className="chip played" title={RULE_HELP[rule(t.strategy)]}>
                          joué · {ticketTitle(t)}
                        </span>
                      ))}
                    </div>
                  )}
                </td>
                <td>
                  <div className="row" style={{ gap: 6 }}>
                    {r.jockey ?? "—"} {lab && tally(r.jockey_stats)}
                  </div>
                  <div className="row muted small" style={{ gap: 6 }}>
                    {r.trainer ?? "—"} {lab && tally(r.trainer_stats)}
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
                {lab && (
                  <td>
                    <ProbBar p={r.market_p} scale={maxP} />
                  </td>
                )}
                <td>
                  <ProbBar p={r.calibrated_p ?? r.market_p} scale={maxP} />
                </td>
                {lab && (
                  <td>
                    <ProbBar p={r.place_p} />
                  </td>
                )}
                <td>
                  <OddsSparkline series={r.odds_series} offTime={data.race.off_time} />
                </td>
                <td>
                  <History r={r} lab={lab} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function horseName(data: RaceDetail, n: number): string {
  return data.runners.find((r) => r.number === n)?.name ?? "";
}

/** The first thing on the page: what the lab played, and what it paid. */
function PlayedBlock({ data }: { data: RaceDetail }) {
  const c = data.carnet;
  const m = minutesUntil(data.race.off_time);
  if (!c) {
    const at = new Date(new Date(data.race.off_time).getTime() - 25 * 60000).toISOString();
    return (
      <Card title="Ce que le labo a joué">
        <p className="small muted" style={{ margin: 0 }}>
          {m > 25
            ? `Les tickets seront figés automatiquement à ${time(at)}, 25 min avant le départ, avec les cotes connues à ce moment-là.`
            : m > 0
              ? "Les tickets sont en train d'être figés (prochaine passe du collecteur)."
              : "Course non jouée : aucun ticket n'a été figé avant le départ (Mac en veille, marché incomplet, ou course antérieure au carnet). Elle n'est jamais rattrapée."}
        </p>
      </Card>
    );
  }
  const stake = c.tickets.reduce((a, t) => a + t.stake, 0);
  const back = c.tickets.reduce((a, t) => a + (t.returned ?? 0), 0);
  return (
    <Card
      title="Ce que le labo a joué"
      aside={
        <span className="small muted">
          figé à {time(c.frozen_at)} avec les cotes de {time(c.odds_as_of)}
          {c.settled && (
            <>
              {" "}
              · misé {euros(stake)} · rapporté <strong style={{ color: "var(--ink)" }}>{euros(back)}</strong>
            </>
          )}
        </span>
      }
    >
      <div className="stack">
        <div className="lab-bet">
          {c.tickets.map((t, i) => {
            const won = c.settled && (t.returned ?? 0) > 0;
            return (
              <div key={`${t.strategy}-${i}`} className={`ticket ${won ? "won" : ""}`} title={RULE_HELP[rule(t.strategy)]}>
                <div className="ticket-head">
                  <span>
                    {BET_LABEL[t.bet_type] ?? t.bet_type} · {rule(t.strategy)}
                  </span>
                  <span className="num">{euros(t.stake)}</span>
                </div>
                <div className="ticket-horse num">
                  {t.numbers.length === 1 ? `n°${t.numbers[0]} ${horseName(data, t.numbers[0]!)}` : t.numbers.join(" – ")}
                </div>
                <div className="ticket-result">
                  {!c.settled ? (
                    <span className="muted">en attente de l'arrivée</span>
                  ) : won ? (
                    <strong>rapporte {euros(t.returned)}</strong>
                  ) : (
                    <span className="muted">perdu</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
        <p className="small muted" style={{ margin: 0 }}>
          Ce sont des <strong>témoins</strong>, pas des pronostics : aucun modèle n'a encore battu le marché, donc le labo
          joue le favori et le hasard pour mesurer ce que coûte « suivre la foule ». Aucune mise réelle.
          {c.note && ` ${c.note}.`}
        </p>
      </div>
    </Card>
  );
}

function readView(): "simple" | "labo" {
  try {
    return localStorage.getItem("predlab.view") === "labo" ? "labo" : "simple";
  } catch {
    return "simple";
  }
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
  const [view, setViewState] = useState<"simple" | "labo">(readView);
  const setView = (v: "simple" | "labo") => {
    setViewState(v);
    try {
      localStorage.setItem("predlab.view", v);
    } catch {
      /* private mode: the choice just isn't remembered */
    }
  };

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
        <PlayedBlock data={data} />

        <div className="kpis">
          <Kpi label="Distance" value={r.distance_m ? `${int(r.distance_m)} m` : "—"} kind="fact" sub={data.conditions.handedness === "LEFT" ? "Corde à gauche" : data.conditions.handedness === "RIGHT" ? "Corde à droite" : undefined} />
          <Kpi label="Partants" value={data.runners.filter((x) => x.status === "PARTANT").length || "—"} kind="fact" sub={`${r.declared_runners ?? "?"} déclarés`} />
          <Kpi label="Terrain" value={r.going ? r.going.toLowerCase() : "—"} kind="fact" sub={r.going_value ? `pénétromètre ${fmt(r.going_value, 1)}` : undefined} />
          <Kpi label="Allocation" value={euros0(data.conditions.prize_eur)} kind="fact" sub={w ? `Prévision : ${w.temperature_c ?? "?"} °C, ${w.sky?.toLowerCase() ?? ""}` : undefined} />
          <Kpi
            label="Dernières cotes"
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
            <div className="row">
              {view === "labo" && (
                <span className="muted small">
                  {data.calibration_alpha != null
                    ? `Calibration α = ${fmt(data.calibration_alpha, 2)} (dernier backtest ${r.discipline_label.toLowerCase()})`
                    : "Pas encore de backtest : marché calibré indisponible"}
                </span>
              )}
              <Segmented
                label="Niveau de détail"
                value={view}
                onChange={setView}
                options={[
                  { value: "simple", label: "Vue simple" },
                  { value: "labo", label: "Vue labo" },
                ]}
              />
            </div>
          }
          flush
        >
          {data.runners.length === 0 ? (
            <Empty title="Partants pas encore collectés">
              <p className="small">Le collecteur les prend dès la veille, puis toutes les 5 min dans l'heure du départ.</p>
            </Empty>
          ) : (
            <RunnersTable data={data} lab={view === "labo"} played={playedMap(data)} />
          )}
        </Card>

        {view === "labo" && (
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
        )}

        <Result data={data} />
      </div>
    </>
  );
}
