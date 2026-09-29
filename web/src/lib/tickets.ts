// Plain-language names for the carnet's strategies: what was played, and why.

export const BET_LABEL: Record<string, string> = {
  SIMPLE_GAGNANT: "Gagnant",
  SIMPLE_PLACE: "Placé",
  TIERCE: "Tiercé",
  QUINTE_PLUS: "Quinté+",
};

/** "SG favori" -> "favori", "Tiercé hasard" -> "hasard", "SG valeur market_calibrated" -> "valeur". */
export function rule(strategy: string): string {
  if (strategy.includes("hasard")) return "hasard";
  if (strategy.includes("valeur")) return "valeur";
  if (strategy.includes("favori")) return "favori";
  return strategy;
}

export const RULE_HELP: Record<string, string> = {
  favori: "Témoin : le cheval le mieux coté par les parieurs 25 min avant le départ.",
  hasard: "Témoin : un cheval tiré au sort (tirage reproductible).",
  valeur: "Cheval dont la chance estimée × la cote dépasse 1,10.",
};

export const ticketTitle = (t: { bet_type: string; strategy: string }) =>
  `${BET_LABEL[t.bet_type] ?? t.bet_type} · ${rule(t.strategy)}`;
