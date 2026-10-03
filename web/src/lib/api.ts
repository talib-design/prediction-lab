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

export interface PeriodTotals {
  key: "day" | "week" | "month" | "all";
  label: string;
  start: string;
  races: number;
  settled: number;
  stake: number;
  returned: number;
  net: number;
  roi: number | null;
  pending_stake: number;
}

export interface CarnetSeries {
  strategy: string;
  label: string;
  bet: "SG" | "SP";
  pick: "favori" | "modèle";
  points: { day: string; races: number; stake: number; returned: number; net: number; cum: number }[];
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
  model_p: number | null;
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
  model_probabilities: Record<string, number> | null;
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
  model: { report: string; fitted_through: string } | null;
  finish_order: number[][] | null;
  runners: RunnerRow[];
  dividends: DividendRow[];
  snapshots: number;
  carnet: CarnetEntry | null;
  banc: BancRace | null;
}

export interface BancRace {
  frozen_at: string;
  settled: boolean;
  stake: number;
  returned: number | null;
  tickets: { strategy: string; label: string; bet: "SG" | "SP"; number: number; returned: number | null }[];
}

export interface Summary {
  bets: number;
  stake: number;
  returned: number;
  net: number;
  roi: number | null;
  low: number | null;
  high: number | null;
  p: number | null;
}

export interface BancStrategy {
  id: string;
  discipline: Discipline;
  bet: "SG" | "SP";
  bet_label: string;
  criteria: Record<string, string>;
  criteria_list: { key: string; label: string; level: string }[];
  label: string;
  reference: boolean;
  origin: string;
  added_at: string;
  exploration: {
    from?: string;
    to?: string;
    bets?: number;
    roi?: number | null;
    low?: number | null;
    high?: number | null;
    periods?: { from: string; to: string; bets: number; roi: number }[] | null;
  };
  confirmation: (Summary & { since: string; verdict: string }) | null;
  eliminated_at: string | null;
  live: Summary;
  pending: number;
  status: "en test" | "gagnante" | "éliminée" | "référence";
}

export interface BancTotals {
  tickets: number;
  stake: number;
  returned: number;
  net: number;
  roi: number | null;
}

export interface BancResponse {
  updated_at: string | null;
  gauge: Record<string, { at: string; tested: number; confirmed: number; exploration_roi: number | null; confirmation_roi: number | null }>;
  rules: { win_bets: number; kill_bets: number; kill_roi: number; target_roi: number };
  totals: { today: BancTotals; all: BancTotals; pending: number; races: number; first_day: string | null };
  counts: Record<string, number>;
  strategies: BancStrategy[];
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

/** A ratio with its 95 % interval; verdict after the multiple-testing correction. */
export interface Ratio {
  value: number | null;
  low: number | null;
  high: number | null;
  p: number | null;
  verdict: "+" | "−" | "=" | "?";
}

export interface Stability {
  avant_2025: { ratio: number | null; expected: number };
  depuis_2025: { ratio: number | null; expected: number };
  verdict: string;
}

export interface RaceLevel {
  level: string;
  races: number;
  share: number;
  favourite_win_rate: number | null;
  favourite_expected: number | null;
  favourite_vs_odds: Ratio;
  winner_median_odds: number | null;
  outsider_win_rate: number | null;
  stability: Stability;
}

export interface RunnerLevel {
  level: string;
  runners: number;
  share: number;
  races: number;
  wins: number;
  win_rate: number | null;
  placed_rate: number | null;
  result_vs_chance: Ratio;
  odds_vs_chance: number | null;
  missed_by_odds: Ratio;
  top3_vs_odds: Ratio;
  stability: Stability;
}

export interface ProfileReport {
  id: string;
  generated_at: string;
  discipline: Discipline;
  first_day: string | null;
  last_day: string | null;
  n_races: number;
  n_runners: number;
  race_factors: { key: string; label: string; levels: RaceLevel[] }[];
  runner_factors: { key: string; label: string; levels: RunnerLevel[] }[];
  tests: number;
  correction: string;
}

export interface ModelComparison {
  races: number;
  log_loss_model?: number;
  log_loss_market?: number;
  difference?: number;
  ci_low?: number;
  ci_high?: number;
  verdict?: string;
}

export interface ModelSummary {
  id: string;
  generated_at: string;
  races: { train: number; validation: number; test: number };
  lambda: number;
  market_alpha: number;
  coefficients: {
    feature: string;
    label: string;
    active: boolean;
    beta: number;
    low: number | null;
    high: number | null;
    p: number | null;
    per_sd?: number;
  }[];
  validation: ModelComparison;
  test: ModelComparison;
  test_bets: Record<string, { bets: number; roi?: number; roi_low?: number; roi_high?: number; hit_rate?: number }> | null;
}

export interface ConditionRecord {
  level: string;
  runs: number;
  wins: number;
  top3: number;
  expected_top3: number;
  elsewhere: { runs: number; wins: number; top3: number; expected_top3: number };
  lean: "+" | "−" | null;
}

export interface RaceProfile {
  race_id: string;
  discipline: Discipline;
  conditions: Record<string, string>;
  horses: Record<
    string,
    {
      name: string;
      record: {
        runs: number;
        wins: number;
        top3: number;
        expected_top3: number;
        conditions: Record<string, ConditionRecord>;
      } | null;
      levels: Record<string, string>;
    }
  >;
  profile: ProfileReport | null;
  model: ModelSummary | null;
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
  periods: () =>
    get<{
      today: string;
      periods: PeriodTotals[];
      streak: { current: number; best: number; days_played: number };
      days: { day: string; races: number; stake: number; returned: number; net: number }[];
      series: CarnetSeries[];
    }>("/carnet/periods"),
  carnet: (day?: string) => get<CarnetResponse>(day ? `/carnet?day=${day}` : "/carnet"),
  hypotheses: () => get<{ hypotheses: Hypothesis[] }>("/hypotheses"),
  profile: (discipline: Discipline) =>
    get<{ discipline: Discipline; profile: ProfileReport | null; model: ModelSummary | null }>(
      `/profile?discipline=${discipline}`,
    ),
  raceProfile: (day: string, rc: string) => get<RaceProfile>(`/races/${day}/${rc}/profile`),
  banc: () => get<BancResponse>("/banc"),
};
