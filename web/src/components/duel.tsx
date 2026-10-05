import { euros } from "../lib/format";

/** "+3,20 €" / "−1,00 €": the sign always shown, a real minus. */
export const signed = (x: number) => `${x >= 0 ? "+" : "−"}${euros(Math.abs(x))}`;

/** "+70,5 %", one decimal, French comma. */
export const pct1 = (r: number | null | undefined) =>
  r == null ? "—" : `${r >= 0 ? "+" : "−"}${Math.abs(r * 100).toFixed(1).replace(".", ",")} %`;

export const plural = (n: number) => (n > 1 ? "s" : "");

/** Who came out ahead, decided to the cent as on the server. */
export const duelState = (diff: number): "ahead" | "behind" | "same" => {
  const cents = Math.round(diff * 100);
  return cents > 0 ? "ahead" : cents < 0 ? "behind" : "same";
};

/** By how much the model beats (or trails) the favourite on the same races. */
export function DeltaChip({ diff }: { diff: number }) {
  const state = duelState(diff);
  if (state === "same") return <span className="delta-chip same">à égalité avec le favori</span>;
  return (
    <span className={`delta-chip ${state}`}>
      <span aria-hidden>{state === "ahead" ? "▲" : "▼"}</span> {signed(diff)} pour le modèle
    </span>
  );
}
