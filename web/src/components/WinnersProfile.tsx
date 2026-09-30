import { useEffect, useRef, useState } from "react";
import {
  api,
  type ConditionRecord,
  type Discipline,
  type ModelSummary,
  type ProfileReport,
  type RaceProfile,
  type Ratio,
} from "../lib/api";
import { fmt, int, pct, shortDay } from "../lib/format";
import { useApi } from "../lib/hooks";
import { Empty, Failure, Loading, Segmented, disciplineLabel } from "./ui";

export type Tab = "race" | "conditions" | "runners" | "model";

/* ------------------------------------------------------------------ building blocks */

/** ×1,12 on a log scale centred on 1, with its 95 % interval. Not colour-only: the
 *  verdict is also written as a sign next to it. */
function RatioBar({ r, range = 1.35 }: { r: Ratio; range?: number }) {
  if (r.value == null) return <span className="muted">—</span>;
  const W = 84;
  const span = Math.log(range);
  const x = (v: number) => W / 2 + (Math.max(-span, Math.min(span, Math.log(Math.max(v, 1e-3)))) / span) * (W / 2);
  const strong = r.verdict === "+" || r.verdict === "−";
  return (
    <span className="ratio" title={ratioTitle(r)}>
      <svg width={W} height={14} aria-hidden>
        <line x1={W / 2} x2={W / 2} y1={1} y2={13} className="ratio-axis" />
        {r.low != null && r.high != null && (
          <line x1={x(r.low)} x2={x(r.high)} y1={7} y2={7} className="ratio-ci" />
        )}
        <circle cx={x(r.value)} cy={7} r={3.5} className={strong ? "ratio-dot strong" : "ratio-dot"} />
      </svg>
      <span className={`num ${strong ? "ratio-strong" : "muted"}`}>×{fmt(r.value, 2)}</span>
      <Verdict v={r.verdict} />
    </span>
  );
}

function ratioTitle(r: Ratio) {
  const ci = r.low != null && r.high != null ? ` (IC 95 % : ${fmt(r.low, 2)} à ${fmt(r.high, 2)})` : " (trop peu de données pour un intervalle)";
  const v =
    r.verdict === "+" ? "Effet positif confirmé." : r.verdict === "−" ? "Effet négatif confirmé." : "Pas d'effet démontré.";
  return `×${fmt(r.value, 2)}${ci}. ${v}`;
}

function Verdict({ v }: { v: Ratio["verdict"] | "+" | "−" | null | undefined }) {
  if (v === "+") return <span className="verdict pos" aria-label="effet positif">▲</span>;
  if (v === "−") return <span className="verdict neg" aria-label="effet négatif">▼</span>;
  return <span className="verdict none" aria-hidden />;
}

function Stable({ s }: { s: { verdict: string } }) {
  const label = s.verdict === "même sens" ? "stable" : s.verdict === "sens opposés" ? "instable" : "peu de données";
  return (
    <span className={`small ${s.verdict === "même sens" ? "" : "muted"}`} title={`2024 puis 2025-2026 : ${s.verdict}`}>
      {label}
    </span>
  );
}

/* ------------------------------------------------------------------------ tab panes */

// Levels this rare say nothing: hidden, and said so under the table.
const MIN_RACES = 30;
const MIN_RUNNERS = 200;
const UNKNOWN = new Set(["Non mesuré", "Inconnue", "Inconnu"]);

function RareNote({ hidden }: { hidden: number }) {
  if (hidden === 0) return null;
  return (
    <p className="small muted" style={{ margin: 0 }}>
      {hidden} niveau{hidden > 1 ? "x" : ""} trop rare{hidden > 1 ? "s" : ""} masqué{hidden > 1 ? "s" : ""} (moins de{" "}
      {MIN_RACES} courses ou {MIN_RUNNERS} partants).
    </p>
  );
}

function RacePane({ data }: { data: RaceProfile }) {
  const factors = data.profile?.race_factors ?? [];
  const labelOf = (key: string) => factors.find((f) => f.key === key)?.label ?? key;
  const levelOf = (key: string) => factors.find((f) => f.key === key)?.levels.find((l) => l.level === data.conditions[key]);
  const horses = Object.entries(data.horses).sort((a, b) => Number(a[0]) - Number(b[0]));
  const cols: [string, string][] = [
    ["going_cat", "Ce terrain"],
    ["temp_band", "Cette température"],
    ["dist_band", "Cette distance"],
  ];
  const shown = cols.filter(
    ([key]) => !(key === "going_cat" && data.discipline !== "PLAT") && !UNKNOWN.has(data.conditions[key] ?? ""),
  );
  return (
    <div className="stack">
      <section>
        <h3 className="modal-h3">Les conditions du jour</h3>
        <div className="cond-grid">
          {Object.keys(data.conditions).map((key) => {
            const lv = levelOf(key);
            return (
              <div key={key} className="cond">
                <span className="kpi-label">{labelOf(key)}</span>
                <strong>{data.conditions[key]}</strong>
                {UNKNOWN.has(data.conditions[key] ?? "") ? (
                  <span className="small muted">
                    {key === "going_cat" ? "pas encore publié : le PMU le mesure le jour même" : "pas de prévision publiée"}
                  </span>
                ) : lv && lv.races >= MIN_RACES && lv.favourite_win_rate != null && (
                  <span className="small muted">
                    favori gagnant {pct(lv.favourite_win_rate, 0)} des {int(lv.races)} courses
                    {lv.favourite_vs_odds.verdict === "+" && " — plus souvent que sa cote"}
                    {lv.favourite_vs_odds.verdict === "−" && " — moins souvent que sa cote"}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </section>
      <section>
        <h3 className="modal-h3">Les partants dans ces conditions</h3>
        <p className="small muted modal-lead">
          Depuis 2024, avant ce jour. « Top 3 » : arrivées dans les trois premiers, comparées à ce que leur cote annonçait
          ce jour-là. ▲ / ▼ : le cheval fait nettement mieux / moins bien dans cette condition qu'ailleurs (au moins 3
          courses de chaque côté). Indicatif : quelques courses ne prouvent rien.
        </p>
        <div className="table-wrap">
          <table className="compact">
            <thead>
              <tr>
                <th className="r">N°</th>
                <th>Cheval</th>
                <th className="r">Courses</th>
                {shown.map(([key, label]) => (
                  <th key={key}>
                    {label}
                    <span className="th-sub">{data.conditions[key]}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {horses.map(([n, h]) => (
                <tr key={n}>
                  <td className="r num">{n}</td>
                  <td>{h.name}</td>
                  <td className="r num">
                    {h.record ? (
                      <span title={`${h.record.wins} victoires, ${h.record.top3} top 3 (${fmt(h.record.expected_top3, 1)} attendus par la cote)`}>
                        {h.record.runs}
                      </span>
                    ) : (
                      <span className="muted">0</span>
                    )}
                  </td>
                  {shown.map(([key]) => (
                    <td key={key}>
                      <CondCell c={h.record?.conditions[key]} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function CondCell({ c }: { c: ConditionRecord | undefined }) {
  if (!c || c.runs === 0) return <span className="muted small">jamais couru</span>;
  const title = `Ici : ${c.runs} courses, ${c.top3} top 3 pour ${fmt(c.expected_top3, 1)} attendus. Ailleurs : ${c.elsewhere.runs} courses, ${c.elsewhere.top3} top 3 pour ${fmt(c.elsewhere.expected_top3, 1)} attendus.`;
  return (
    <span className="cond-cell" title={title}>
      <span className="num">
        {c.top3}/{c.runs} top 3
      </span>
      <span className="muted small num"> ({fmt(c.expected_top3, 1)} att.)</span>
      <Verdict v={c.lean} />
    </span>
  );
}

function ConditionsPane({ profile, current }: { profile: ProfileReport; current?: Record<string, string> }) {
  const keep = (lv: { level: string; races: number }, key: string) => lv.races >= MIN_RACES || current?.[key] === lv.level;
  const hidden = profile.race_factors.reduce((n, f) => n + f.levels.filter((lv) => !keep(lv, f.key)).length, 0);
  return (
    <div className="stack">
      <p className="small muted modal-lead">
        Il y a un gagnant dans chaque course : une condition de course (le froid, la pluie…) ne fait pas « gagner plus ».
        Elle change <em>qui</em> gagne. On regarde donc si le favori gagne plus ou moins souvent que sa cote ne le
        disait, et à quelle cote gagne le vainqueur.
      </p>
      <div className="table-wrap">
        <table className="compact profile">
          <thead>
            <tr>
              <th>Condition</th>
              <th className="r">Courses</th>
              <th className="r">Favori gagnant</th>
              <th className="r" title="La chance moyenne que la cote donnait au favori">Sa cote disait</th>
              <th>Favori vs sa cote</th>
              <th className="r" title="Cote médiane du cheval gagnant">Cote du gagnant</th>
              <th className="r" title="Part des courses gagnées par un cheval hors des 3 premières cotes">Surprises</th>
              <th>2024 → 2026</th>
            </tr>
          </thead>
          {profile.race_factors.map((f) => (
            <tbody key={f.key}>
              <tr className="group">
                <td colSpan={8}>{f.label}</td>
              </tr>
              {f.levels.filter((lv) => keep(lv, f.key)).map((lv) => (
                <tr key={lv.level} className={current?.[f.key] === lv.level ? "is-current" : undefined}>
                  <td>
                    {lv.level}
                    {current?.[f.key] === lv.level && <span className="chip played tiny">cette course</span>}
                  </td>
                  <td className="r num">{int(lv.races)}</td>
                  <td className="r num">{pct(lv.favourite_win_rate, 0)}</td>
                  <td className="r num muted">{pct(lv.favourite_expected, 0)}</td>
                  <td>
                    <RatioBar r={lv.favourite_vs_odds} />
                  </td>
                  <td className="r num">{fmt(lv.winner_median_odds, 1)}</td>
                  <td className="r num">{pct(lv.outsider_win_rate, 0)}</td>
                  <td>
                    <Stable s={lv.stability} />
                  </td>
                </tr>
              ))}
            </tbody>
          ))}
        </table>
      </div>
      <RareNote hidden={hidden} />
    </div>
  );
}

function RunnersPane({ profile }: { profile: ProfileReport }) {
  const hidden = profile.runner_factors.reduce((n, f) => n + f.levels.filter((lv) => lv.runners < MIN_RUNNERS).length, 0);
  const factors = profile.runner_factors
    .map((f) => ({ ...f, levels: f.levels.filter((lv) => lv.runners >= MIN_RUNNERS) }))
    .filter((f) => f.levels.length > 1);
  return (
    <div className="stack">
      <p className="small muted modal-lead">
        <strong>Gagne</strong> : victoires comparées au pur hasard (1 chance sur le nombre de partants).{" "}
        <strong>Les parieurs</strong> : combien la cote les favorise déjà. <strong>Ce que la cote a raté</strong> :
        victoires comparées à ce que la cote annonçait — la seule colonne qu'un parieur pourrait exploiter.{" "}
        <strong>Top 3 vs cote</strong> : même lecture pour les trois premières places.
      </p>
      <div className="table-wrap">
        <table className="compact profile">
          <thead>
            <tr>
              <th>Profil</th>
              <th className="r">Partants</th>
              <th>Gagne</th>
              <th className="r">Les parieurs</th>
              <th>Ce que la cote a raté</th>
              <th>Top 3 vs cote</th>
              <th>2024 → 2026</th>
            </tr>
          </thead>
          {factors.map((f) => (
            <tbody key={f.key}>
              <tr className="group">
                <td colSpan={7}>{f.label}</td>
              </tr>
              {f.levels.map((lv) => (
                <tr key={lv.level}>
                  <td>{lv.level}</td>
                  <td className="r num">
                    <span title={`${int(lv.wins)} victoires`}>{int(lv.runners)}</span>
                  </td>
                  <td>
                    <RatioBar r={lv.result_vs_chance} />
                  </td>
                  <td className="r num muted">{lv.odds_vs_chance == null ? "—" : `×${fmt(lv.odds_vs_chance, 2)}`}</td>
                  <td>
                    <RatioBar r={lv.missed_by_odds} />
                  </td>
                  <td>
                    <RatioBar r={lv.top3_vs_odds} />
                  </td>
                  <td>
                    <Stable s={lv.stability} />
                  </td>
                </tr>
              ))}
            </tbody>
          ))}
        </table>
      </div>
      <RareNote hidden={hidden} />
    </div>
  );
}

function ModelPane({ model }: { model: ModelSummary | null }) {
  if (!model)
    return (
      <Empty title="Pas encore de modèle pour cette discipline">
        <p className="small">Il est ajusté chaque nuit dès qu'il y a au moins 300 courses d'apprentissage.</p>
      </Empty>
    );
  const t = model.test;
  const bets = model.test_bets ?? {};
  return (
    <div className="stack">
      <p className="small muted modal-lead">
        Marché+ part de la cote et y ajoute des facteurs, tous choisis avant de regarder les résultats. Chaque barre dit
        ce qu'un facteur apporte <em>à cote égale</em> : ×1,00 = la cote l'intégrait déjà. Appris sur{" "}
        {int(model.races.train)} courses (1er semestre 2024), réglé sur {int(model.races.validation)}, jugé sur{" "}
        {int(model.races.test)} courses depuis 2025.
      </p>
      {t.difference != null && (
        <div className={`callout ${t.ci_high != null && t.ci_high < 0 ? "strong" : ""}`}>
          <strong>Test 2025-2026 : {t.verdict}.</strong>{" "}
          <span className="small">
            Écart de log loss {fmt(t.difference, 4)} par course (IC 95 % {fmt(t.ci_low, 4)} à {fmt(t.ci_high, 4)}) :
            négatif = meilleur que la cote seule. Un écart réel mais petit ne suffit pas à battre la marge du PMU (~16 %).
          </span>
        </div>
      )}
      <div className="table-wrap">
        <table className="compact">
          <thead>
            <tr>
              <th>Facteur</th>
              <th>Effet à cote égale (par écart-type)</th>
              <th className="r">p</th>
            </tr>
          </thead>
          <tbody>
            {model.coefficients
              .filter((c) => c.feature !== "log_q")
              .map((c) => (
                <tr key={c.feature} className={c.active ? undefined : "dim"}>
                  <td>{c.label}</td>
                  <td>
                    {c.active ? (
                      <RatioBar
                        range={1.12}
                        r={{
                          value: Math.exp(c.beta),
                          low: c.low == null ? null : Math.exp(c.low),
                          high: c.high == null ? null : Math.exp(c.high),
                          p: c.p,
                          verdict: c.low != null && c.low > 0 ? "+" : c.high != null && c.high < 0 ? "−" : "=",
                        }}
                      />
                    ) : (
                      <span className="muted small">sans objet dans cette discipline</span>
                    )}
                  </td>
                  <td className="r num muted">{c.p == null ? "—" : fmt(c.p, 3)}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
      {Object.keys(bets).length > 0 && (
        <div className="table-wrap">
          <table className="compact">
            <thead>
              <tr>
                <th>Paris fictifs à 1 € (test)</th>
                <th className="r">Paris</th>
                <th className="r">Retour</th>
                <th className="r">IC 95 %</th>
                <th className="r">Réussite</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(bets).map(([name, b]) => (
                <tr key={name}>
                  <td>{name}</td>
                  <td className="r num">{int(b.bets)}</td>
                  <td className="r num">{b.roi == null ? "—" : `${b.roi >= 0 ? "+" : "−"}${fmt(Math.abs(b.roi) * 100, 1)} %`}</td>
                  <td className="r num muted">
                    {b.roi_low == null || b.roi_high == null ? "—" : `${fmt(b.roi_low * 100, 0)} à ${fmt(b.roi_high * 100, 0)} %`}
                  </td>
                  <td className="r num">{pct(b.hit_rate ?? null, 0)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ---------------------------------------------------------------------------- modal */

type Props = { open: boolean; onClose: () => void; initialTab?: Tab } & (
  | { race: { day: string; rc: string; label: string }; discipline?: undefined }
  | { race?: undefined; discipline: Discipline }
);

function Body(props: Props & { tab: Tab }) {
  const [discipline, setDiscipline] = useState<Discipline>(props.discipline ?? "PLAT");
  const key = props.race ? `rp:${props.race.day}/${props.race.rc}` : `p:${discipline}`;
  const load = useApi<{ profile: ProfileReport | null; model: ModelSummary | null; race?: RaceProfile }>(
    () =>
      props.race
        ? api.raceProfile(props.race.day, props.race.rc).then((race) => ({ profile: race.profile, model: race.model, race }))
        : api.profile(discipline),
    key,
  );
  const picker = !props.race && (
    <Segmented<Discipline>
      label="Discipline"
      value={discipline}
      onChange={setDiscipline}
      options={(["PLAT", "ATTELE", "MONTE"] as Discipline[]).map((d) => ({ value: d, label: disciplineLabel(d) }))}
    />
  );
  if (load.state === "loading") return <Loading rows={6} />;
  if (load.state === "error") return <Failure error={load.error} />;
  const { profile, model, race } = load.data;
  const empty = (
    <Empty title="Profil pas encore calculé">
      <p className="small">
        Il est calculé chaque nuit par la passe automatique, ou à la main avec{" "}
        <code className="mono">uv run predlab racing profile --discipline {race?.discipline ?? discipline}</code>.
      </p>
    </Empty>
  );
  return (
    <div className="stack">
      {picker}
      {profile && (
        <p className="small muted" style={{ margin: 0 }}>
          {int(profile.n_races)} courses, {int(profile.n_runners)} partants, du {shortDay(profile.first_day ?? "")} au{" "}
          {shortDay(profile.last_day ?? "")} · cotes 25 min avant le départ · {profile.tests} tests, corrigés pour les
          tests multiples (▲ / ▼ = effet qui survit à la correction).
        </p>
      )}
      {props.tab === "race" && race && <RacePane data={race} />}
      {props.tab === "conditions" && (profile ? <ConditionsPane profile={profile} current={race?.conditions} /> : empty)}
      {props.tab === "runners" && (profile ? <RunnersPane profile={profile} /> : empty)}
      {props.tab === "model" && <ModelPane model={model} />}
    </div>
  );
}

export function WinnersProfile(props: Props) {
  const ref = useRef<HTMLDialogElement>(null);
  const [tab, setTab] = useState<Tab>(props.race ? "race" : "conditions");

  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (props.open && !d.open) {
      setTab(props.initialTab ?? (props.race ? "race" : "conditions"));
      d.showModal();
    }
    if (!props.open && d.open) d.close();
  }, [props.open, props.initialTab, props.race]);

  const tabs: { value: Tab; label: string }[] = [
    ...(props.race ? [{ value: "race" as Tab, label: "Cette course" }] : []),
    { value: "conditions", label: "Conditions de course" },
    { value: "runners", label: "Profil des partants" },
    { value: "model", label: "Modèle Marché+" },
  ];

  return (
    <dialog
      ref={ref}
      className="modal"
      aria-labelledby="wp-title"
      onClose={props.onClose}
      onClick={(e) => {
        if (e.target === ref.current) props.onClose(); // click on the backdrop
      }}
    >
      <div className="modal-frame">
        <header className="modal-head">
          <div>
            <h2 id="wp-title">Profil des vainqueurs</h2>
            <p className="small muted" style={{ margin: 0 }}>
              {props.race ? props.race.label : "Ce qui distingue les gagnants, et ce que la cote en savait déjà"}
            </p>
          </div>
          <button className="btn icon" aria-label="Fermer" onClick={props.onClose} autoFocus>
            ✕
          </button>
        </header>
        <div className="modal-tabs">
          <Segmented<Tab> label="Section" value={tab} onChange={setTab} options={tabs} />
        </div>
        <div className="modal-body">{props.open && <Body {...props} tab={tab} />}</div>
      </div>
    </dialog>
  );
}

export function ProfileButton({ onClick }: { onClick: () => void }) {
  return (
    <button className="btn" onClick={onClick} aria-haspopup="dialog">
      Profil des vainqueurs
    </button>
  );
}
