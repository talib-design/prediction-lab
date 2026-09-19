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
- **Multiplicity:** Benjamini-Yekutieli (the dependent form of the step-up
  procedure) at q = 0.05 across every model × pool comparison in the run. See
  *Sources* below for why the independent form would be wrong here.
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
- The bootstrap uses the percentile method. BCa would correct for bias and skew;
  the algorithm is spelled out in Efron, *Exponential Families in Theory and
  Practice*, §5.4-5.6, and porting it is a concrete task rather than a vague wish.
- The block length heuristic `n**(1/3)` is a documented default, not an optimum.
- One era, one game. Nothing here has been replicated.


## Sources consulted

These are the project's reference texts. Each entry says what was checked and what it
changed — a citation that changed nothing is noted as such rather than decorating the
page.

### What it changed

**Wasserman, *All of Statistics*, §10.7 (Multiple Testing).** States the
Benjamini-Hochberg theorem with a factor `C_m` in the step-up threshold, equal to 1
**only when the p-values are independent**, and equal to the harmonic number otherwise.

This project's comparisons are plainly not independent: every model is scored against
the same reference on the same draws, `frequency` / `rolling_100` / `rolling_300` are
computed from overlapping counts, and the two pools come from the same tirages. The
first implementation used the independent form, which would have overstated how much
evidence survives correction — precisely the failure this module exists to prevent.
`benjamini_hochberg` now defaults to the dependent (Benjamini-Yekutieli) variant.

Effect on the Milestone 1 result: **none**. The corrected form is roughly three times
stricter at m = 12, and every "worse than uniform" finding still survives it. The
error would have mattered the moment a model looked good.

**Efron, *Exponential Families in Theory and Practice*, §5.4-5.6.** The BCa interval
in full: the bias corrector `z0`, the acceleration `a`, Theorem 5.2, and the
`bcajack` / `bcapar` computational recipe. Table 5.5 shows how far percentile
intervals can sit from exact ones on a skewed statistic. This turns "BCa would be
better" from a hedge into a specified task.

### What it confirmed

**Efron, *To Think Like a Statistician*, ch. 8.** The prostate-cancer worked example
(6 033 genes, Bonferroni admitting 4, BH at 0.1 admitting 28) is the canonical
illustration of why per-ball testing needs FDR rather than 49 uncorrected tests. It
confirms the planned treatment of per-number testing; nothing changed.

**Wasserman §10.5 (permutation tests).** Notes that permutation tests are most useful
for small samples and otherwise agree with large-sample theory. At n = 875 the
asymptotic test would give a similar answer — so the justification for permuting here
is **not** small n, it is the block structure needed to respect autocorrelation.
Worth being precise about, since "we used a permutation test" is often stated as if it
were self-justifying.

**Wasserman ch. 15 and Efron §5.6 (chi-square goodness of fit).** Both use the
multinomial null. That is exactly the approximation this project deliberately avoids:
because exactly `k` numbers come out of each draw, counts are negatively dependent and
the multinomial variance is too large, making the classical test conservative in the
direction that hides bias. The Monte-Carlo null stands as a deliberate departure from
the textbook default, not an oversight.

### What the corpus does not cover

**Block resampling for dependent data.** These texts cover the i.i.d. and parametric
bootstrap. The moving-block bootstrap and the block sign-flip permutation used here
come from outside this corpus and have **not** been cross-checked against it. The
block-length heuristic `n**(1/3)` is likewise unverified. Anyone extending this
project should treat both as the weakest-supported choices in the methodology.
