// Typed client for the read-only backend (src/predlab/api/app.py). The UI never reads
// data files: everything it shows comes through these calls.

export type Discipline = "PLAT" | "ATTELE" | "MONTE";

export interface RaceSummary {
  race_id: string;
  day: string;
  rc: string;
  meeting: number;
  number: number;
  off_time: string;
  off_local: string;
  venue: string;
  discipline: Discipline;
  discipline_label: string;
  name: string | null;
  distance_m: number | null;
  category: string | null;
  declared_runners: number | null;
  status: string | null;
  status_category: string | null;
  is_final: boolean;
  has_quinte: boolean;
  going: string | null;
  going_value: number | null;
  snapshots: number;
  carnet?: CarnetState;
}

export interface CarnetState {
  state: "upcoming" | "open" | "frozen" | "settled" | "missed" | "cancelled";
  freeze_at: string;
  frozen_at?: string;
  tickets?: { strategy: string; bet_type: string; numbers: number[]; stake: number; returned: number | null }[];
  stake?: number;
  returned?: number | null;
}

export interface DayResponse {
  day: string;
  programme_retrieved_at: string | null;
  races: RaceSummary[];
  other_races: number;
}

export interface OddsPoint {
  t: string;
  kind: string;
  odds: number;
}

export interface HorseHistory {
  runs: number;
  wins: number;
  places: number;
  last5: string[];
  last_day: string;
}

export interface Tally {
  runs: number;
  wins: number;
}

export interface RunnerRow {
  number: number;
  name: string;
  horse_id: string | null;
  status: string;
  age: number | null;
  sex: string | null;
  jockey: string | null;
  trainer: string | null;
  draw: number | null;
  weight_kg: number | null;
  handicap_distance: number | null;
  shoeing: string | null;
  odds: number | null;
  market_p: number | null;
  calibrated_p: number | null;
  place_p: number | null;
  finish_position: number | null;
  odds_series: OddsPoint[];
  history: HorseHistory | null;
  jockey_stats: Tally | null;
  trainer_stats: Tally | null;
}

export interface DividendRow {
  bet_type: string;
  label: string;
  combination: string;
  per_euro: number;
  base_stake: number;
  refunded: boolean;
}

export interface CarnetTicket {
  strategy: string;
  label: string;
  bet_type: string;
  numbers: number[];
  stake: number;
  returned: number | null;
}

export interface CarnetEntry {
  race_id: string;
  day: string;
  rc: string;
  discipline: Discipline;
  venue: string | null;
  has_quinte: boolean;
  off_time: string;
  frozen_at: string;
  odds_as_of: string;
  alpha: number;
  tickets: CarnetTicket[];
  settled: boolean;
  settled_at: string | null;
  finish_order: number[][] | null;
  note: string | null;
}

export interface CarnetRow extends StrategyRow {
  label: string;
  pending: number;
}

export interface CarnetResponse {
  records: number;
  head_hash: string;
  integrity_error: string | null;
  first_day: string | null;
  days: string[];
  races: number;
  settled: number;
  summary: CarnetRow[];
  entries: CarnetEntry[];
}

export interface RaceDetail {
  race: RaceSummary;
  conditions: {
    handedness: string | null;
    age_condition: string | null;
    prize_eur: number | null;
    weather: { temperature_c: number | null; sky: string | null; wind_force: number | null } | null;
  };
  market_as_of: string | null;
  minutes_before_off: number | null;
  calibration_alpha: number | null;
  finish_order: number[][] | null;
  runners: RunnerRow[];
  dividends: DividendRow[];
  snapshots: number;
  carnet: CarnetEntry | null;
}

export interface HorseResponse {
  horse: {
    horse_id: string;
    name: string;
    sire: string | null;
    dam: string | null;
    dam_sire: string | null;
    breed: string | null;
    birth_year: number | null;
    n_races: number;
  };
  runs: {
    race_id: string;
    day: string;
    venue: string;
    discipline: Discipline;
    distance_m: number | null;
    going: string | null;
    number: number;
    position: number | null;
    status: string;
    jockey: string | null;
    trainer: string | null;
    draw: number | null;
    weight_kg: number | null;
    field: number | null;
  }[];
}

export interface ReportListItem {
  id: string;
  kind: "backtest" | "simulation";
  discipline: Discipline;
  generated_at: string | null;
  n_eligible: number | null;
}

export interface SummaryRow {
  model: string;
  n_races: number;
  log_loss: number;
  brier: number;
  top1: number;
  mrr: number;
  calibration_error: number;
}

export interface ComparisonRow {
  model: string;
  n_races: number;
  verdict: string;
  mean_difference?: number;
  ci_low?: number;
  ci_high?: number;
  p_value?: number;
  minimum_detectable_effect?: number;
  races_for_0_01?: number;
  survives_fdr?: boolean;
}

export interface CalibrationRow {
  bucket: string;
  n: number;
  mean_forecast: number;
  observed: number;
}

export interface BacktestReport {
  generated_at: string;
  discipline?: Discipline;
  horizon_minutes: number;
  n_events: number;
  n_eligible: number;
  decision_phase: string;
  reference: string;
  split: Record<string, string> | null;
  summary: Record<string, SummaryRow[]>;
  comparisons: ComparisonRow[];
  calibration: Record<string, CalibrationRow[]>;
  alpha?: number;
  alpha_refits?: number;
}

export interface StrategyRow {
  strategy: string;
  races: number;
  tickets?: number;
  stake?: number;
  returned?: number;
  net?: number;
  roi?: number;
  roi_low?: number;
  roi_high?: number;
  hit_rate?: number;
  largest_share?: number;
  verdict?: string;
}

export interface SimulationReport {
  generated_at: string;
  discipline: Discipline;
  horizon_minutes: number;
  n_eligible: number;
  n_races_with_dividends: number;
  value_threshold: number;
  decision_phase: string;
  by_phase: Record<string, StrategyRow[]>;
  place_calibration: CalibrationRow[];
}

export interface StatusResponse {
  now: string;
  captures: number;
  failed_captures: number;
  last_capture: string | null;
  minutes_since_last_capture: number | null;
  collect_log: string[];
  backfill_log: string[];
  backfill: {
    discipline: Discipline;
    label: string;
    start: string;
    days_done: number;
    days_total: number;
    oldest_done: string | null;
  }[];
  database: {
    exists: boolean;
    races?: number;
    runners?: number;
    odds?: number;
    dividends?: number;
    horses?: number;
    built_at?: string;
    missing_tables?: string[];
    by_discipline?: { discipline: Discipline; races: number; with_runners: number }[];
  };
}

export interface Hypothesis {
  hypothesis_id: string;
  revision: number;
  description: string;
  created_at: string;
  origin: "human" | "literature" | "folk_heuristic" | "automated";
  dataset: string | null;
  experiment: string | null;
  status: "PROPOSED" | "TESTING" | "REJECTED" | "INCONCLUSIVE" | "SUPPORTED";
  in_sample_result: string | null;
  out_of_sample_result: string | null;
  forward_result: string | null;
  conclusion: string | null;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`/api${path}`, { headers: { Accept: "application/json" } });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      /* not JSON */
    }
    throw new ApiError(res.status, detail);
  }
  return (await res.json()) as T;
}

export const api = {
  day: (day?: string) => get<DayResponse>(day ? `/races?day=${day}` : "/races"),
  race: (day: string, rc: string) => get<RaceDetail>(`/races/${day}/${rc}`),
  horse: (id: string) => get<HorseResponse>(`/horses/${encodeURIComponent(id)}`),
  reports: () => get<{ reports: ReportListItem[] }>("/reports"),
  report: <T>(id: string) => get<T>(`/reports/${encodeURIComponent(id)}`),
  status: () => get<StatusResponse>("/status"),
  carnet: (day?: string) => get<CarnetResponse>(day ? `/carnet?day=${day}` : "/carnet"),
  hypotheses: () => get<{ hypotheses: Hypothesis[] }>("/hypotheses"),
};
