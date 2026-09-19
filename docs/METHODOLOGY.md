# Methodology

Written before the first run and versioned, so that the criteria cannot drift towards
whatever the results happened to be.

## The claim being tested

*Do past Loto draws help predict the next one?*

Not: can a model be found that looks good on history. Anything can be made to look
good on history.

## Decision rule, fixed in advance

- **Metric:** mean per-number log loss on marginal inclusion probabilities. Lower is
  better. It is a proper scoring rule, so a model minimises it by being honest.
- **Reference:** the `uniform` model, `p = k / size`. This is the correct model if the
  mechanism is fair.
- **Test:** paired block sign-flip permutation on per-draw score differences,
  two-sided, 5 000 permutations.
- **Multiplicity:** Benjamini-Hochberg at q = 0.05 across every model × pool
  comparison in the run.
- **Intervals:** moving-block percentile bootstrap, 2 000 resamples, block length
  `n**(1/3)`.
- **Conclusion:** a model counts as a candidate only if it beats the reference *and*
  survives FDR. A candidate is not a finding until it survives a forward test on
  draws that did not exist when it was written.

### Why block methods rather than i.i.d.

A frequency model's forecast changes very little from one draw to the next, so its
per-draw scores are strongly autocorrelated. An i.i.d. bootstrap treats correlated
observations as independent evidence, narrows the interval, and manufactures
significance. The same argument applies to permuting single draws, hence sign-flipping
whole blocks.

### Why not match count

Under a fair mechanism every number has inclusion probability `k / size`. The expected
match count of *any* legal ticket is therefore identical. Match count is reported
because readers expect it; it decides nothing.

## Power comes first

The detection floor is computed and printed before any result. For the current era:

| n draws | Correction | Minimum detectable relative bias |
|---|---|---|
| 1 075 | none | 26.2% |
| 1 075 | Bonferroni over 49 balls | 38.5% |

Detecting a 5% relative bias would require about 60 000 draws — roughly 385 years at
three draws a week. A 1% bias would need about 1.5 million.

The consequence is stated wherever a null result appears: **"no signal detected" here
means "no enormous signal detected"**. It is not evidence of fairness. Conflating the
two would be the project's own version of the error it exists to catch.

## Uniformity testing

The classical chi-square on ball-slot counts is not quite right: exactly `k` numbers
come out of each draw, so counts are negatively dependent and their true variance is
*smaller* than multinomial. The classical test is therefore conservative — it
under-rejects, which hides bias.

Instead the null is simulated with the real mechanism (`k` distinct numbers per draw).
The test's own false-positive rate is verified in the test suite: 5% on fair data, as
it must be. Per-ball tests, when added, will be FDR-controlled — 49 tests at 5% yield
two or three "significant" balls by construction.

## Splits

Strictly chronological. Train → validation → test → forward. No shuffling anywhere.

Free parameters (window length, smoothing) are chosen on validation only. Choosing on
test and then reporting test performance is the commonest way to manufacture a result,
so the split is an object the run record carries rather than a convention someone
remembers.

## Era handling

Only `loto/2019-11` is defined, because only its mechanics were verified against data.
Pooling draws across a format change is a methodological error, not an approximation.
Older FDJ archives exist; using them requires verifying each era's rules first.

Open question, not yet resolved: FDJ changed the player return rate on 2026-05-04.
Whether that touched the draw mechanics or only the prize structure is unverified. It
is a candidate regime boundary inside the current era.

## What would change the conclusion

State this in advance, so that moving the goalposts is visible:

1. A model that beats uniform on log loss, survives FDR, **and** holds up on a forward
   window of draws recorded after the model was frozen.
2. A uniformity test that rejects at the era level and is reproduced on an independent
   era.
3. A synthetic benchmark showing the harness fails to detect a planted signal of a
   size the power analysis says it should catch — which would invalidate the null
   results rather than support them.

## Known methodological limitations

- Marginal scoring only; dependence between numbers is not modelled or tested.
- Log loss is clipped at `eps = 1e-6`, which caps how badly an overconfident model can
  be punished and therefore slightly flatters it.
- The bootstrap uses the percentile method. Efron's BCa would correct for bias and
  skew and is a known future refinement.
- The block length heuristic `n**(1/3)` is a documented default, not an optimum.
- One era, one game. Nothing here has been replicated.
