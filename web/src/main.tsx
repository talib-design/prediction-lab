import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { api } from "./lib/api";
import { useApi, useRoute } from "./lib/hooks";
import { Carnet } from "./pages/Carnet";
import { Data } from "./pages/Data";
import { Horse } from "./pages/Horse";
import { Performance } from "./pages/Performance";
import { Race } from "./pages/Race";
import { Research } from "./pages/Research";
import { Today } from "./pages/Today";
import "./styles/app.css";

const NAV = [
  { to: "#/", label: "Courses", match: ["", "jour", "course", "cheval"] },
  { to: "#/carnet", label: "Carnet", match: ["carnet"] },
  { to: "#/performance", label: "Performance", match: ["performance"] },
  { to: "#/donnees", label: "Données", match: ["donnees"] },
  { to: "#/recherche", label: "Recherche", match: ["recherche"] },
];

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
  let body;
  switch (page) {
    case "course":
      body = <Race day={args[0]!} rc={args[1]!} />;
      break;
    case "cheval":
      body = <Horse id={args[0]!} />;
      break;
    case "carnet":
      body = <Carnet />;
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
          <nav className="nav" aria-label="Sections">
            {NAV.map((n) => (
              <a key={n.to} href={n.to} aria-current={n.match.includes(page) ? "page" : undefined}>
                {n.label}
              </a>
            ))}
          </nav>
          <CollectorDot />
        </div>
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
