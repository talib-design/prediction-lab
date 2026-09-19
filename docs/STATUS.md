# Status — Milestone 1

Last updated: 2026-09-19.

## Headline result

Run on the official FDJ archive, 1 075 Loto draws (2019-11-06 → 2026-09-16), 875
walk-forward evaluation draws:

> **No statistically meaningful predictive signal was detected.**

Two details matter more than the headline.

**Every model that tried to use history scored *worse* than assuming fairness**, not
merely no better — and significantly so (p = 0.0002, surviving FDR):

| Model | log loss (main) | vs uniform |
|---|---|---|
| uniform / random | 0.32954 | reference |
| frequency (all history) | 0.33060 | worse |
| rolling frequency, 300 | 0.33133 | worse |
| rolling frequency, 100 | 0.33411 | worse |
| gap ("due numbers") | 0.38081 | much worse |

That ordering is exactly what noise-fitting looks like: the shorter the window, the
more noise is fitted, the worse the score. The "due number" heuristic is the worst
model tested, by a wide margin.

**The null result is bounded by power, not by evidence of fairness.** With 1 075
draws, a ball's inclusion probability would have to differ from 5/49 by **38.5%**
(Bonferroni-corrected) before we could reliably detect it. Detecting a 5% bias would
take roughly 60 000 draws — about 385 years at three draws a week. The uniformity test
did not reject (p = 0.76 main, p = 0.91 chance), and that says far less than it looks
like.

## What works

- Ingestion of the official FDJ Loto archive, verified against the live source on
  2026-09-19 and parsed byte-identically (SHA-256 `66a0f0a9…70e074`).
- Strict parser: exact header match, and three cross-checks per row (the balls must
  reproduce the source's own sorted-combination string; the stated weekday must match
  the calendar; the date must be a draw day inside the era). All 1 075 real rows pass.
- Append-only Parquet store that refuses to rewrite a recorded draw and reports
  upstream mutations separately from new rows.
- Causally truncated `HistoryView`: future rows are absent from the object a model
  receives, and the invariant is property-tested over arbitrary cutoffs.
- Five baselines: uniform, random ticket, historical frequency, rolling frequency,
  gap. Two selection policies: top-k and proportional sampling.
- Strictly chronological walk-forward backtest with a reproducible run record
  (dataset fingerprint, model versions and configs, split, seed, code version).
- Metrics: log loss, Brier, mass lift, match count, binned calibration error.
- Uncertainty: moving-block bootstrap, paired block sign-flip permutation,
  Benjamini-Hochberg FDR control.
- Power analysis (detection floor, required sample size) and a Monte-Carlo uniformity
  test whose own false-positive rate is verified at 5%.
- Machine-readable and human-readable reports, power section first.
- Immutable forward predictions in a hash-chained ledger; recording a prediction about
  a past or already-recorded draw is refused.
- Hypothesis registry with revisions; four Milestone 1 hypotheses recorded with their
  real outcomes.
- CLI covering all of the above.

## What does not yet work

- **EuroMillions and Keno.** Out of scope by design. `GameSpec` supports them; no
  parser or verified spec exists.
- **Older Loto eras** (1976, 2008, 2017, 2019-02). The archives are downloadable but
  their mechanics are unverified, so `get_spec` refuses them rather than guessing.
- **Synthetic benchmark suite.** Only the positive control in the test suite exists;
  the disappearing-signal, regime-change and seductive-false-pattern datasets from the
  brief are not built.
- **Champion / challenger promotion.** Nothing blocks it architecturally; nothing
  implements it.
- **LLM agents.** Not started, by design.
- **Per-ball testing with FDR.** The machinery exists (`benjamini_hochberg`); the
  descriptive section currently reports only the global uniformity test.
- **Automatic scoring of matured forward predictions into the report.** `predictions
  score` prints them; they do not feed back into the evaluation yet.

## Known limitations

- Scoring is on **marginals only**. A model capturing dependence between numbers while
  keeping the same marginals would score identically here.
- Log loss is clipped at 1e-6, which caps the penalty for overconfidence.
- Bootstrap uses the percentile method; BCa would be better for skewed statistics.
- Block length uses an `n**(1/3)` heuristic, not an estimated optimum.
- The FDJ endpoint is undocumented and may change without notice. The parser fails
  loudly rather than silently mis-parsing, which is the intended behaviour.
- The archives carry no licence statement; raw files are git-ignored and not
  redistributed.
- FDJ changed the player return rate on 2026-05-04. Whether this touched draw
  mechanics is **unverified** and it is a candidate regime boundary inside the era.
- One game, one era, no replication.

## How to run

```bash
cd "Prediction Lab"
uv sync

uv run predlab data fetch                 # downloads the official archive
uv run predlab data status
uv run predlab data verify

uv run predlab power                      # read this before the backtest
uv run predlab backtest                   # writes data/runs/<id>/report.{json,md}
uv run predlab report

uv run predlab predict --target 2026-09-21
uv run predlab predictions list
uv run predlab predictions verify

uv run predlab hypothesis list
```

If this machine cannot reach `sto.api.fdj.fr`, download the archive elsewhere and
pass it with `--archive path/to.zip`; it goes through identical validation.

Checks: `uv run ruff check . && uv run pyright && uv run pytest`.

## Current data source

Official FDJ archive, current era only.

- `https://www.sto.api.fdj.fr/anonymous/service-draw-info/v3/documentations/1a2b3c4d-9876-4562-b3fc-2c963f66afp6`
- ZIP containing `loto_201911.csv`; Windows-1252; `;`-separated; 50 columns with a
  trailing separator; rows in descending date order.
- 1 075 draws, 2019-11-06 → 2026-09-16. Balls 1–49 (5 per draw), chance 1–10.
- Full provenance, quirks and integrity rules: `docs/DATA_SOURCES.md`.

## Current models

| Name | What it asserts |
|---|---|
| `uniform` | `p = k / size`. Correct if the mechanism is fair. The reference. |
| `random` | A random ticket. Its probabilities are uniform — that is what "at random" means — so its score must equal `uniform`'s. Asserted in the tests as a harness check. |
| `frequency` | Probability proportional to historical counts, Laplace-smoothed. |
| `rolling_frequency_{100,300}` | The same over a recent window. |
| `gap` | The "due number" folk heuristic, implemented so it can be refuted. |

## Current test coverage

141 tests, 90% line coverage of `src/predlab`. Ruff and Pyright clean.

Measure with `uv run --with pytest-cov pytest --cov=predlab --cov-report=term-missing`.

The tests that matter most are not the unit tests:

- `test_backtest.py::test_engine_never_shows_a_model_the_target_draw` — a
  deliberately cheating model confirms the causal boundary holds.
- `test_historyview.py` — the no-leakage invariant, property-tested over arbitrary
  cutoffs rather than examples.
- `test_report.py::test_fair_data_yields_an_explicit_null_result` — on fair data the
  system must find nothing.
- `test_report.py::test_a_planted_bias_is_found` — and on planted signal it must find
  it. A system that only ever says "no" is broken, not careful.
- `test_power.py::test_uniformity_test_has_the_right_false_positive_rate` — the
  descriptive test rejects fair data 5% of the time, as a 5% test must.
- `test_cli.py` — the full pipeline, archive to report, with nothing stubbed but the
  network.

Thinnest coverage: `cli.py` (72%, mostly error paths) and the downloader, which is
untested because it is the one function that requires the network.

## Next recommended step

**Build the synthetic benchmark suite** (section 13 of the brief), before adding any
new model.

The reason is specific rather than tidy-minded. Every null result so far rests on the
claim that this harness *could* have detected a signal if one existed. That claim is
currently supported by exactly one positive control: a 60%-rate planted bias, far
above the detection floor. That proves the harness is not inert. It does not show
where its sensitivity actually ends.

The valuable experiments are the ones near the boundary:

1. **Weak hidden signal** at, just below, and just above the computed detection floor.
   If the harness finds the one the power analysis says it should and misses the one
   it says it should not, the power calculation is validated against behaviour instead
   of being trusted as algebra.
2. **Disappearing signal** — present for 500 draws, then gone. Does the rolling window
   track it, and does the report avoid reporting a dead effect as live?
3. **Seductive false pattern** — strong in-sample, absent out-of-sample. This is the
   direct test of whether the chronological split and FDR control do their job. It is
   the single most informative experiment available right now.

Only after that does adding models make sense. Until the instrument is characterised,
a new model's result cannot be interpreted.

Secondary, cheap, and worth doing alongside: verify whether the 2026-05-04 rule change
touched draw mechanics, and ingest the second-tirage block as a separate game — it
would roughly double the sample available for uniformity testing, at no cost beyond a
parser change.
