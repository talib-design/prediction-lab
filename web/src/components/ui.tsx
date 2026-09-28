import type { ReactNode } from "react";
import type { Discipline } from "../lib/api";

/** What kind of information a number is. Every figure on screen carries one. */
export type Kind = "fact" | "feature" | "assoc" | "forecast" | "market";

export const KIND_LABEL: Record<Kind, string> = {
  fact: "Fait observé",
  feature: "Feature",
  assoc: "Association",
  forecast: "Prévision",
  market: "Information de marché",
};

const KIND_HELP: Record<Kind, string> = {
  fact: "Constaté dans les données officielles, sans interprétation.",
  feature: "Variable calculée à partir de faits antérieurs à la course.",
  assoc: "Corrélation observée dans le passé ; n'implique aucune causalité.",
  forecast: "Probabilité produite par un modèle évalué hors échantillon.",
  market: "Ce que disent les parieurs : dérivé des cotes PMU, pas un modèle à nous.",
};

export function KindBadge({ kind, short }: { kind: Kind; short?: boolean }) {
  const label = short
    ? { fact: "Fait", feature: "Feature", assoc: "Assoc.", forecast: "Prévision", market: "Marché" }[kind]
    : KIND_LABEL[kind];
  return (
    <span className={`badge k-${kind}`} title={KIND_HELP[kind]}>
      {label}
    </span>
  );
}

const DISCIPLINE_LABEL: Record<Discipline, string> = {
  PLAT: "Plat",
  ATTELE: "Trot attelé",
  MONTE: "Trot monté",
};

export const disciplineLabel = (d: Discipline) => DISCIPLINE_LABEL[d] ?? d;

export function DisciplineBadge({ d }: { d: Discipline }) {
  return <span className={`badge d-${d}`}>{disciplineLabel(d)}</span>;
}

export function Card({
  title,
  aside,
  children,
  flush,
}: {
  title?: ReactNode;
  aside?: ReactNode;
  children: ReactNode;
  flush?: boolean;
}) {
  return (
    <section className="card">
      {title != null && (
        <header className="card-head">
          <h2>{title}</h2>
          {aside}
        </header>
      )}
      {flush ? children : <div className="card-body">{children}</div>}
    </section>
  );
}

export function Kpi({
  label,
  value,
  sub,
  kind,
}: {
  label: string;
  value: ReactNode;
  sub?: ReactNode;
  kind?: Kind;
}) {
  return (
    <div className="card kpi">
      <div className="row" style={{ justifyContent: "space-between" }}>
        <span className="kpi-label">{label}</span>
        {kind && <KindBadge kind={kind} short />}
      </div>
      <div className="kpi-value">{value}</div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  );
}

export function Empty({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="empty">
      <strong>{title}</strong>
      {children}
    </div>
  );
}

export function Loading({ rows = 4 }: { rows?: number }) {
  return (
    <div className="card card-body stack" aria-busy="true" aria-label="Chargement">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="skeleton" style={{ width: `${90 - i * 12}%` }} />
      ))}
    </div>
  );
}

export function Failure({ error }: { error: Error }) {
  const down = error.message.includes("Failed to fetch") || error.message.includes("NetworkError");
  return (
    <div className="card">
      <Empty title={down ? "Le serveur ne répond pas" : "Erreur"}>
        {down ? (
          <p className="small">
            Lancez <code className="mono">uv run predlab dashboard</code> dans le Terminal, puis rechargez.
          </p>
        ) : (
          <p className="small">{error.message}</p>
        )}
      </Empty>
    </div>
  );
}

export function PageHead({
  crumbs,
  title,
  lead,
  aside,
}: {
  crumbs?: ReactNode;
  title: ReactNode;
  lead?: ReactNode;
  aside?: ReactNode;
}) {
  return (
    <div className="page-head">
      <div>
        {crumbs && <div className="crumbs">{crumbs}</div>}
        <h1>{title}</h1>
        {lead && <p>{lead}</p>}
      </div>
      {aside}
    </div>
  );
}

export function Segmented<T extends string>({
  value,
  options,
  onChange,
  label,
}: {
  value: T;
  options: { value: T; label: ReactNode }[];
  onChange: (v: T) => void;
  label: string;
}) {
  return (
    <div className="segmented" role="group" aria-label={label}>
      {options.map((o) => (
        <button key={o.value} aria-pressed={o.value === value} onClick={() => onChange(o.value)}>
          {o.label}
        </button>
      ))}
    </div>
  );
}
