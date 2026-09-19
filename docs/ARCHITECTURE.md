# Architecture

## The shape of Milestone 1

```
official FDJ archive (ZIP)
        │  strict parser, three cross-checks per row
        ▼
append-only Parquet store  ──►  dataset fingerprint
        │
        ▼
HistoryView  (causally truncated: future rows are absent, not hidden)
        │
        ▼
Predictor  ──►  Forecast (inclusion probabilities)  ──►  SelectionPolicy ──► ticket
        │
        ▼
walk-forward backtest engine
        │
        ├─► descriptive channel   (uniformity, counts)       "is this unusual?"
        └─► predictive channel    (proper scores, CIs, FDR)  "does this help?"
                │
                ▼
        report.json + report.md
```

## Three decisions everything else follows from

### 1. A model returns probabilities, not numbers

`Predictor.forecast()` returns an inclusion probability for every number in every
pool. Choosing a ticket is a separate `SelectionPolicy`.

This is not stylistic. Under a fair mechanism every number has inclusion probability
`k / size`, so *every legal ticket has the same expected match count*. Match-based
evaluation therefore cannot distinguish two models, no matter how many draws are
available. Proper scoring rules can, and they need probabilities.

Scope limit: these are **marginal** probabilities. Each number is scored as a
Bernoulli outcome; the joint distribution over the C(49,5) combinations is not
modelled. A model capturing dependence between numbers while keeping the same
marginals would score identically. That restriction is deliberate — it matches what
this sample size can actually test.

### 2. Leakage is prevented by construction, not by discipline

The engine never hands a model the dataset. It builds a `HistoryView` whose arrays are
already sliced to observations strictly before the target date, and whose numpy arrays
are marked read-only. Leaking the future requires reaching outside the object you were
given, not merely forgetting a filter. The invariant is property-tested over arbitrary
cutoffs, and a deliberately cheating test model confirms it.

### 3. Observation, anomaly and forecast never merge

The report has separate sections, in a fixed order, and the descriptive section
carries an explicit disclaimer. "This pattern is unusual" and "this pattern predicts"
are different claims; the layout makes conflating them take effort.

## Storage

| What | Where | Why |
|---|---|---|
| Draw observations | Parquet, one file per game era | Typed, columnar, append-only. Thousands of rows: a database would be ceremony. |
| Forward predictions | `data/predictions.jsonl` | Hash-chained, append-only, tracked in git. |
| Hypotheses | `data/hypotheses.jsonl` | Same, with revisions rather than edits. |
| Raw archives | `data/raw/fdj/`, git-ignored | Reproducible from the manifest; no licence to redistribute. |
| Provenance | `data/raw/fdj/MANIFEST.json`, tracked | The audit trail from bytes to dataset. |

### On "immutability"

Nothing on a local filesystem is immutable. What the hash chain gives is **tamper
evidence**: an edited, deleted or reordered record breaks the chain and `verify` says
which one. Committing the ledgers to git right after writing adds an independent
timestamp, and that — not the hash — is what makes "this was written before the draw"
credible to someone who does not trust you.

## Dependencies, and what was left out

Kept: polars, numpy, scipy, pydantic, typer. Dev: pytest, hypothesis, ruff, pyright.

Deliberately absent, with reasons:

- **DuckDB** — 1 075 rows. Parquet plus polars is enough. DuckDB earns its place when
  there are thousands of *experiment results* to query, not now.
- **pandas** — two dataframe libraries means two sets of null semantics. Polars has
  stricter typing, which matters against an undocumented CSV.
- **scikit-learn, statsmodels** — no Milestone 1 baseline needs them; they are
  counting exercises. Add them when a model actually requires them.
- **Hypothesis** was *added* to the requested stack: the anti-leakage invariant needs
  property-based testing to mean anything. Three examples prove nothing.

## Security boundaries

No API key is required and none is used. `.env.example` documents the optional LLM
variables for later; `.env` is git-ignored.

The boundary that matters for the eventual business use case is already structural:
data (`data/`), computation (`src/predlab/`) and reports (`data/runs/`) are separate,
and nothing in the computation path makes a network call except
`fdj_loto.download_archive`. When LLM support arrives it will consume *reports*, never
raw observations, so confidential rows cannot be forwarded to an external API by
default.

## What this is designed to allow later, without being built now

- **Other games.** `GameSpec` already describes pools, eras and draw days as data.
  EuroMillions and Keno need a spec and a parser, not new engine code.
- **Champion / challenger.** `BacktestResult` carries model versions, configs and the
  split. Freezing a champion is a matter of recording which run defined it.
- **Synthetic benchmarks.** `run_backtest` takes arrays, not a store, so a generator
  of planted-signal datasets plugs straight in. One such generator already exists in
  the test suite as the positive control.
- **LLM agents.** They would read the report and the hypothesis registry and propose
  new `Predictor` implementations. No numerical work moves to them.
