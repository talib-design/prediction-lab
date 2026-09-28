const nf = (d: number) =>
  new Intl.NumberFormat("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d });

export const fmt = (x: number | null | undefined, digits = 2) =>
  x == null || Number.isNaN(x) ? "—" : nf(digits).format(x);

export const pct = (x: number | null | undefined, digits = 1) =>
  x == null || Number.isNaN(x) ? "—" : `${nf(digits).format(x * 100)} %`;

export const signedPct = (x: number | null | undefined, digits = 1) =>
  x == null || Number.isNaN(x) ? "—" : `${x >= 0 ? "+" : "−"}${nf(digits).format(Math.abs(x) * 100)} %`;

export const int = (x: number | null | undefined) =>
  x == null ? "—" : new Intl.NumberFormat("fr-FR").format(x);

export const odds = (x: number | null | undefined) => (x == null ? "—" : nf(1).format(x));

export const euros = (x: number | null | undefined) =>
  x == null
    ? "—"
    : new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(x);

export const euros0 = (x: number | null | undefined) =>
  x == null
    ? "—"
    : new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(x);

const PARIS = "Europe/Paris";

export const time = (iso: string | null | undefined) =>
  iso
    ? new Intl.DateTimeFormat("fr-FR", { hour: "2-digit", minute: "2-digit", timeZone: PARIS }).format(
        new Date(iso),
      )
    : "—";

export const longDay = (day: string) =>
  new Intl.DateTimeFormat("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${day}T00:00:00Z`));

export const shortDay = (day: string) =>
  new Intl.DateTimeFormat("fr-FR", { day: "2-digit", month: "2-digit", year: "numeric", timeZone: "UTC" }).format(
    new Date(`${day}T00:00:00Z`),
  );

export const dateTime = (iso: string | null | undefined) =>
  iso
    ? new Intl.DateTimeFormat("fr-FR", {
        day: "2-digit",
        month: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: PARIS,
      }).format(new Date(iso))
    : "—";

export function todayParis(): string {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: PARIS,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
  return parts; // en-CA gives YYYY-MM-DD
}

export function shiftDay(day: string, delta: number): string {
  const d = new Date(`${day}T12:00:00Z`);
  d.setUTCDate(d.getUTCDate() + delta);
  return d.toISOString().slice(0, 10);
}

export const minutesUntil = (iso: string) => (new Date(iso).getTime() - Date.now()) / 60000;

export function relative(minutes: number): string {
  const m = Math.round(Math.abs(minutes));
  const s = m < 60 ? `${m} min` : `${Math.floor(m / 60)} h ${String(m % 60).padStart(2, "0")}`;
  return minutes >= 0 ? `dans ${s}` : `il y a ${s}`;
}

export const MODEL_LABELS: Record<string, string> = {
  random: "Aléatoire",
  uniform: "Uniforme",
  horse_win_rate: "Taux de victoire du cheval",
  form: "Forme récente",
  market: "Marché brut",
  market_calibrated: "Marché calibré",
};

export const modelLabel = (m: string) => MODEL_LABELS[m] ?? m;

export const PHASE_LABELS: Record<string, string> = {
  train: "Entraînement",
  validation: "Validation",
  test: "Test",
  all: "Toutes",
};
