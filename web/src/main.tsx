import { StrictMode, type ReactNode } from "react";
import { HorseIcon, StarBallIcon } from "./components/icons";
import { createRoot } from "react-dom/client";
import { api } from "./lib/api";
import { useApi, useRoute } from "./lib/hooks";
import { Banc } from "./pages/Banc";
import { Carnet } from "./pages/Carnet";
import { Data } from "./pages/Data";
import { Horse } from "./pages/Horse";
import { Performance } from "./pages/Performance";
import { Race } from "./pages/Race";
import { Research } from "./pages/Research";
import { Today } from "./pages/Today";
import { EmBacktest } from "./pages/em/EmBacktest";
import { EmCarnet } from "./pages/em/EmCarnet";
import { EmData } from "./pages/em/EmData";
import { EmHistory } from "./pages/em/EmHistory";
import { shortDay } from "./lib/format";
import "./styles/app.css";

type SubItem = { to: string; label: string; match: (page: string, sub: string) => boolean };
type Section = { id: string; label: string; icon: ReactNode; to: string; owns: (page: string) => boolean; items: SubItem[] };

const racing = (label: string, to: string, pages: string[]): SubItem => ({
  to,
  label,
  match: (page) => pages.includes(page),
});
const em = (label: string, sub: string): SubItem => ({
  to: sub ? `#/euromillions/${sub}` : "#/euromillions",
  label,
  match: (page, s) => page === "euromillions" && s === sub,
});

const SECTIONS: Section[] = [
  {
    id: "racing",
    label: "Courses hippiques",
    icon: <HorseIcon />,
    to: "#/",
    owns: (page) => page !== "euromillions",
    items: [
      racing("Programme", "#/", ["", "jour", "course", "cheval"]),
      racing("Carnet", "#/carnet", ["carnet"]),
      racing("Banc d'essai", "#/banc", ["banc"]),
      racing("Performance", "#/performance", ["performance"]),
      racing("Données", "#/donnees", ["donnees"]),
      racing("Recherche", "#/recherche", ["recherche"]),
    ],
  },
  {
    id: "euromillions",
    label: "EuroMillions",
    icon: <StarBallIcon />,
    to: "#/euromillions",
    owns: (page) => page === "euromillions",
    items: [
      em("Carnet", ""),
      em("Historique", "historique"),
      em("Logiques vs hasard", "logiques"),
      em("Données", "donnees"),
    ],
  },
];

function EmNextDraw() {
  const load = useApi(() => api.em.carnet(), "em-next", 600_000);
  if (load.state !== "ready" || !load.data.next_draw) return null;
  const pending = load.data.pending.length;
  return (
    <a href="#/euromillions" className="topbar-status" title="Carnet EuroMillions">
      <span className={`dot ${pending ? "live" : "stale"}`} />
      prochain tirage {shortDay(load.data.next_draw)}
      {pending ? ` · ${pending} grilles figées` : " · aucune grille figée"}
    </a>
  );
}

function CollectorDot() {
  const load = useApi(() => api.status(), "status-dot", 120_000);
  if (load.state !== "ready") return null;
  const m = load.data.minutes_since_last_capture;
  const live = m != null && m < 15;
  return (
    <a href="#/donnees" className="topbar-status" title="État du collecteur">
      <span className={`dot ${live ? "live" : "stale"}`} />
      {m == null ? "aucune capture" : live ? "collecte active" : `dernière capture il y a ${Math.round(m)} min`}
    </a>
  );
}

function App() {
  const [page = "", ...args] = useRoute();
  const section = SECTIONS.find((sec) => sec.owns(page)) ?? SECTIONS[0]!;
  let body;
  switch (page) {
    case "course":
      body = <Race day={args[0]!} rc={args[1]!} />;
      break;
    case "cheval":
      body = <Horse id={args[0]!} />;
      break;
    case "carnet":
      body = <Carnet period={args[0]} day={args[1]} />;
      break;
    case "banc":
      body = <Banc />;
      break;
    case "performance":
      body = <Performance />;
      break;
    case "donnees":
      body = <Data />;
      break;
    case "recherche":
      body = <Research />;
      break;
    case "jour":
      body = <Today day={args[0]} />;
      break;
    case "euromillions":
      body =
        args[0] === "historique" ? (
          <EmHistory />
        ) : args[0] === "logiques" ? (
          <EmBacktest />
        ) : args[0] === "donnees" ? (
          <EmData />
        ) : (
          <EmCarnet />
        );
      break;
    default:
      body = <Today />;
  }
  return (
    <>
      <header className="topbar">
        <div className="topbar-inner">
          <a href="#/" className="brand">
            <span className="brand-mark" aria-hidden>
              <svg width="14" height="14" viewBox="0 0 32 32">
                <path d="M4 24 L12 14 L18 19 L28 6" stroke="white" strokeWidth="4" fill="none" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
            Prediction Lab
          </a>
          <nav className="domains" aria-label="Domaines">
            {SECTIONS.map((sec) => (
              <a key={sec.id} href={sec.to} aria-current={sec.id === section.id ? "true" : undefined}>
                {sec.icon}
                {sec.label}
              </a>
            ))}
          </nav>
          {section.id === "euromillions" ? <EmNextDraw /> : <CollectorDot />}
        </div>
        <nav className="subnav" aria-label={`Sections ${section.label}`}>
          {section.items.map((n) => (
            <a key={n.to} href={n.to} aria-current={n.match(page, args[0] ?? "") ? "page" : undefined}>
              {n.label}
            </a>
          ))}
        </nav>
      </header>
      <main className="shell" key={page + args.join("/")}>
        {body}
      </main>
    </>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
