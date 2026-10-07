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

/** One side of the duel (the model or the favourite) over a period. */
export interface DuelSide {
  stake: number;
  returned: number;
  net: number;
  roi: number | null;
}

/** The model against the favourite over one period, on the same races (paired: a
 *  gagnant or placé ticket counts only if both played it). */
export interface PeriodTotals {
  key: "day" | "week" | "month" | "all";
  label: string;
  start: string;
  /** Settled races where both played. */
  races: number;
  /** Among them, races where the model chose another horse. */
  differ: number;
  model: DuelSide;
  favori: DuelSide;
  /** Model net minus favourite net. */
  diff: number;
  pending: number;
  /** The model's stake on races not settled yet. */
  pending_stake: number;
}

export type DuelState = "ahead" | "behind" | "same";

export interface DuelDay {
  day: string;
  races: number;
  differ: number;
  model_net: number;
  favori_net: number;
  diff: number;
  state: DuelState;
}

export interface CarnetSeries {
  strategy: string;
  label: string;
  bet: "SG" | "SP";
  pick: "favori" | "modèle" | "ancien" | "valeur";
  points: { day: string; races: number; stake: number; returned: number; net: number; cum: number }[];
}

export interface ReplayTotals {
  bets: number;
  returned: number;
  net: number;
  roi: number | null;
}

export interface ReplayResponse {
  discipline: Discipline | "ALL";
  available: Discipline[];
  report: {
    generated_at: string;
    method: string;
    summary: {
      races: number;
      first_day: string;
      last_day: string;
      differ: number;
      differ_share: number;
      totals: Record<string, ReplayTotals>;
      when_they_differ: Record<"SG" | "SP", { races: number; favori_net: number; modèle_net: number }>;
    } | null;
    series: CarnetSeries[];
  } | null;
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
  /** The favourite against the model on this race; null if they did not both play it. */
  duel: RaceDuel | null;
}

/** One side of a race's duel, on the paired tickets only (gagnant and/or placé). */
export interface DuelPick {
  numbers: number[];
  stake: number;
  returned: number;
  /** null until the race is settled. */
  net: number | null;
  /** Whether its simple gagnant paid; null if not paired in gagnant or not settled. */
  win: boolean | null;
}

export interface RaceDuel {
  differ: boolean;
  model: DuelPick;
  favori: DuelPick;
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

export interface LabMoney {
  races: number;
  races_where_picks_differ: number;
  roi_challenger: number | null;
  roi_champion: number | null;
  roi_favourite: number | null;
  net_difference: number;
  net_difference_low: number | null;
  net_difference_high: number | null;
}

export interface LabResult {
  difference?: number;
  ci_low?: number;
  ci_high?: number;
  level?: number;
  by_year?: Record<string, { races: number; difference: number }>;
  beta?: number;
  per_sd?: number | null;
  races: Record<string, number> | number;
  test_days?: [string, string] | null;
  tested_at: string;
  money?: LabMoney;
  tau?: number;
  bets?: number;
  roi_rule?: number | null;
  roi_favourite?: number | null;
}

export interface ScoreSide {
  stake: number;
  net: number;
  roi: number | null;
}

export interface Scoreboard {
  champion: { version: number; origin: string | null; promoted_at: string | null; features: number; tau: number; rules: string[] };
  versions: { version: number; origin: string; promoted_at: string | null; features: string[]; tau: number; evidence: Record<string, unknown> | null }[];
  attempts: { experiment: string; at: string; vault: [string, string]; passed: boolean; result: { races: number; prediction: { difference: number }; money: LabMoney } }[];
  coverage: { reference_2024: number; years: Record<string, number>; share: number; ready: boolean };
  vault: { start: string; races: number; min_races: number; used_until: string | null };
  live: { races: number; since: string | null; races_where_picks_differ: number; favori: ScoreSide; modèle: ScoreSide };
  history: {
    races: number;
    first_day: string;
    last_day: string;
    differ: number;
    differ_share: number;
    totals: Record<string, ReplayTotals>;
  } | null;
  tests: { protocol: string; total: number; by_status: Partial<Record<Hypothesis["status"], number>> };
}

export interface LabExperiment {
  experiment: string;
  candidate: string;
  label: string;
  hypothesis: string;
  discipline: Discipline;
  source: "history" | "live" | "study";
  kind?: "criterion" | "calibration" | "rule" | "study";
  fresh_from?: string | null;
  protocol?: string;
  origin: Hypothesis["origin"];
  status: Hypothesis["status"];
  registered_at: string | null;
  updated_at: string;
  conclusion: string | null;
  waiting: string | null;
  result: LabResult | null;
}

export interface FavouriteBand {
  band: string;
  races: number;
  win_rate: number | null;
  win_low: number | null;
  win_high: number | null;
  implied: number | null;
  place_rate: number | null;
  roi_sg: number | null;
  roi_sg_low: number | null;
  roi_sg_high: number | null;
  roi_sp: number | null;
  roi_sp_low: number | null;
  roi_sp_high: number | null;
  lost: number;
}

export interface LabResponse {
  objective?: string;
  scoreboard?: Partial<Record<Discipline, Scoreboard>>;
  experiments: LabExperiment[];
  favourites: Partial<Record<Discipline, { first_day: string | null; last_day: string | null; generated_at: string; bands: FavouriteBand[] }>>;
  rule: string;
  catalogue: number;
}

// ------------------------------------------------------------------ EuroMillions

export interface EmDraw {
  draw_date: string;
  balls: number[];
  stars: number[];
  balls_order?: number[];
}

export interface EmGrid {
  draw_date: string;
  logic: string;
  balls: number[];
  stars: number[];
  frozen_at: string;
  history_last_draw: string;
  history_draws: number;
  history_stale: boolean;
}

export interface EmSettledGrid {
  logic: string;
  balls: number[];
  stars: number[];
  ball_hits: number;
  star_hits: number;
  rank: number;
  payout_eur: number | null;
}

export interface EmLogicSummary {
  draws: number;
  mean_balls: number;
  z_balls: number;
  p_balls: number;
  mean_stars: number;
  z_stars: number;
  wins: number;
  paid_eur: number;
  staked_eur: number;
  roi: number;
}

export interface EmCarnetResponse {
  last_draw: EmDraw | null;
  next_draw: string | null;
  pending: EmGrid[];
  draws: { draw_date: string; balls: number[] | null; stars: number[] | null; grids: EmSettledGrid[] }[];
  summary: Record<string, EmLogicSummary>;
  chain_ok: boolean;
  agent_log: string[];
}

export interface EmTest {
  test_id: string;
  hypothesis: string;
  family: string;
  label: string;
  n_draws: number;
  statistic: number;
  p_value: number;
  q_value: number | null;
  observed: number | null;
  expected: number | null;
  decision: string | null;
  note: string;
  detail: Record<string, any>;
}

export interface EmFamilySummary {
  tests: number;
  nominal_p_lt_0_05: number;
  expected_by_chance: number;
  bh_survivors: number;
}

export interface EmControl {
  histories: number;
  tests_per_history: number;
  nominal_rate: number;
  histories_with_survivor: Record<string, number>;
  ks_p_family_b: number;
  passed: boolean;
  reasons: string[];
}

export interface EmAnalysisResponse {
  analysis: {
    created_at: string;
    n_draws: number;
    first_draw: string;
    last_draw: string;
    summary: Record<string, EmFamilySummary>;
    results: EmTest[];
    d3_popularity: EmTest[];
  } | null;
  control: EmControl | null;
  hypotheses: Hypothesis[];
}

export interface EmLogicComparison {
  logic: string;
  pool: string;
  n: number;
  logloss_diff: number;
  logloss_ci: [number, number];
  logloss_p: number;
  logloss_q: number;
  mean_matches: number;
  matches_z: number;
  matches_p: number;
  percentile_vs_players: number;
}

export interface EmPoolBlock {
  expected_matches: number;
  variance_matches: number;
  logics: EmLogicComparison[];
  witness_r1: { mean_matches: number; z: number };
  random_players: {
    players: number;
    mean_matches_quantiles: Record<string, number>;
    best: number;
    worst: number;
  };
}

export interface EmRunBlock {
  spec: string;
  n_draws_total: number;
  n_targets: number;
  first_target: string;
  last_target: string;
  pools: Record<string, EmPoolBlock>;
}

export interface EmPayoutLine {
  mean_payout_eur: number;
  ci95: [number, number];
  roi: number;
  wins: number;
  rank_counts: Record<string, number>;
  percentile_vs_players?: number;
}

export interface EmBacktestResponse {
  backtest: {
    created_at: string;
    rank_mapping_check: Record<string, number>;
    balls_2004: EmRunBlock;
    grid_2016_09: EmRunBlock;
    payouts_2016_09: {
      price_eur: number;
      n_draws: number;
      random_players: { players: number; mean_payout_quantiles: Record<string, number>; roi_median: number };
      witness_r1: EmPayoutLine;
      logics: Record<string, EmPayoutLine>;
    };
  } | null;
}

export interface EmDataResponse {
  store: { draws: number; first: string; last: string; eras: Record<string, number>; retrieved_at: string } | null;
  recent: (EmDraw & { weekday: number; jackpot_winners: number | null; jackpot_eur: number | null })[];
  archives: {
    archive: string;
    archive_sha256: string;
    csv: string;
    rows: number;
    first_draw: string;
    last_draw: string;
    encoding: string;
    url: string | null;
    recorded_at: string;
  }[];
  agent_log: string[];
  agent_errors?: string[];
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
      streak: { current: number; best: number; ahead: number; behind: number; same: number };
      days: DuelDay[];
      series: CarnetSeries[];
    }>("/carnet/periods"),
  carnet: (day?: string) => get<CarnetResponse>(day ? `/carnet?day=${day}` : "/carnet"),
  hypotheses: () => get<{ hypotheses: Hypothesis[] }>("/hypotheses"),
  lab: () => get<LabResponse>("/lab"),
  replay: (discipline: Discipline | "ALL", since?: string) =>
    get<ReplayResponse>(`/replay?discipline=${discipline}${since ? `&since=${since}` : ""}`),
  profile: (discipline: Discipline) =>
    get<{ discipline: Discipline; profile: ProfileReport | null; model: ModelSummary | null }>(
      `/profile?discipline=${discipline}`,
    ),
  raceProfile: (day: string, rc: string) => get<RaceProfile>(`/races/${day}/${rc}/profile`),
  banc: () => get<BancResponse>("/banc"),
  em: {
    carnet: () => get<EmCarnetResponse>("/euromillions/carnet"),
    analysis: () => get<EmAnalysisResponse>("/euromillions/analysis"),
    backtest: () => get<EmBacktestResponse>("/euromillions/backtest"),
    data: () => get<EmDataResponse>("/euromillions/data"),
  },
};
