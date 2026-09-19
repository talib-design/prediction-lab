# Prediction Lab

An experimental platform for building and **honestly evaluating** predictive systems.

The first benchmark domain is the French Loto, used as a *negative control*: a
correctly operated lottery should be unpredictable from past draws alone. The goal is
not to predict it. The goal is to build a system that can tell signal from noise — and
that is allowed to conclude, in as many words, that it found nothing.

## Milestone 1 result

On the official FDJ archive (1 075 draws, 2019-11-06 → 2026-09-16, 875 walk-forward
evaluation draws):

> **No statistically meaningful predictive signal was detected.**

Every model that tried to use history scored *worse* than assuming fairness, and
significantly so. The shorter the window, the worse the score — the signature of
fitting noise. The "due number" heuristic was the worst of all.

And the part that matters just as much: with 1 075 draws, a ball's probability would
have to be off by **38.5%** before we could reliably detect it. So this is not
evidence that the Loto is fair. It is a measurement of how little we could have seen.

## Quick start

```bash
uv sync
uv run predlab data fetch      # official FDJ archive
uv run predlab power           # read this before believing any result
uv run predlab backtest
```

## Documentation

| Document | Contents |
|---|---|
| [`docs/STATUS.md`](docs/STATUS.md) | What works, what does not, how to run it, what to do next |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | The three design decisions everything follows from |
| [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) | Decision rules, fixed in advance |
| [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) | Verified provenance, file quirks, integrity checks |
| [`docs/reports/`](docs/reports/) | Generated evaluation reports |

This is a research project, not gambling advice. Nothing here predicts lottery draws,
and the results say plainly why nothing should be expected to.
