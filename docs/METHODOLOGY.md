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



## Methodological audit against the reference corpus

Every choice in this document was re-checked against the project's five reference
texts. Each row says what was checked and what changed. A source that changed nothing
is recorded as such rather than cited for decoration.

| Choice | Source | Outcome |
|---|---|---|
| FDR correction | Wasserman §10.7 | **Changed.** Was wrong. |
| Smoothing constant `alpha` | Wasserman §11.6; Efron, *Think Like a Statistician*, app. A.3 | **Changed.** Replaced by an estimated one. |
| Frequency estimation | Efron §1.6 + app. A.2; Wasserman §12.7 | **Changed.** New model added. |
| Bootstrap interval method | Efron, *Exponential Families*, §5.4-5.6 | Confirmed as a known gap; now specified. |
| Uniformity test | Wasserman ch. 15; Efron §5.6 | Confirmed our departure is deliberate. |
| Permutation test | Wasserman §10.5 | Confirmed, but our reason was wrong. |
| Power framing | Efron ch. 8; Wasserman §10.8 | Confirmed, with a sharper wording. |
| Block resampling | — | **Not covered by the corpus.** |
| Anomaly reporting | Efron ch. 8 (winner's curse) | New requirement for work not yet built. |

### Changed: FDR correction was using the wrong form

Wasserman states the Benjamini-Hochberg theorem with a factor `C_m` in the step-up
threshold, equal to 1 **only when the p-values are independent**, and to the harmonic
number otherwise.

Ours are not independent: every model is scored against the same reference on the same
draws, `frequency` / `rolling_100` / `rolling_300` share overlapping counts, and both
pools come from the same tirages. The original implementation used the independent
form and would have overstated surviving evidence — the exact failure this module
exists to prevent. Now defaults to the dependent (Benjamini-Yekutieli) variant, about
three times stricter at m = 12.

Effect on the Milestone 1 verdict: none. Every finding survived the stricter form. The
error would have mattered the first time something looked good.

### Changed: `alpha = 1` was an arbitrary prior, and arbitrary was avoidable

Laplace smoothing with `alpha = 1` is a flat Beta(1, 1) prior on each number. Fisher's
objection applies — a flat prior on `p` is not flat on a reparametrisation of `p`, so
"uninformative" was doing unearned work. Jeffreys' prior for a Bernoulli is
Beta(1/2, 1/2), i.e. `alpha = 0.5` (Wasserman §11.6).

Worse, `alpha` was never chosen on validation, contradicting this document's own rule
about free parameters. Rather than tune an arbitrary constant, the next finding removes
the need for one.

### Changed: the frequency model was committing a known, named error

Efron's baseball example (*To Think Like a Statistician*, §1.6, appendix A.2): a set of
noisy parallel estimates is **more spread out than the truth**, because noise
exaggerates differences. Wasserman §12.7 gives the decision-theoretic version — for
k ≥ 3 the raw estimates are inadmissible, and shrinkage strictly improves total
squared error.

Estimating 49 ball probabilities from a few hundred appearances each is precisely that
setting, and `FrequencyPredictor` takes the exaggerated spread at face value. Its
measured behaviour — reliably *worse* than assuming fairness — is what that error looks
like when scored.

`ShrunkFrequencyPredictor` applies the James-Stein rule, estimating from the data how
much of the observed spread to keep::

    js[i] = M + [1 - (K - 3) * V / S] * (x[i] - M)

On the real Loto history the raw factor is **negative** for both pools (main: -0.088;
chance: -0.588): the observed spread of ball frequencies is *smaller* than pure
binomial noise would produce. Clamped at zero by the positive-part rule, the model
collapses exactly onto uniform.

Measured effect, main pool, 875 walk-forward draws:

| Model | log loss | Calibration error | vs uniform |
|---|---|---|---|
| uniform | 0.32954 | 0.0000 | reference |
| frequency (`alpha = 1`) | 0.33060 | 0.0105 | worse, p = 0.0002 |
| shrunk_frequency | 0.32955 | 0.0002 | worse, p = 0.0002 |
| shrunk_frequency_300 | 0.32956 | 0.0001 | indistinguishable, p = 0.135 |

Shrinkage recovers essentially all of the loss the naive model incurred, and cuts
calibration error by a factor of 50. The residual gap on the full-history variant is
the cost of the small positive shrinkage retained in early windows — even a little
misplaced confidence is still paid for.

This is the single most useful thing the corpus contributed: it named the error, gave
the correction, and the correction behaved exactly as predicted on real data.

### Confirmed, with a sharper reason: the permutation test

Wasserman §10.5 notes that permutation tests are most useful for **small** samples and
otherwise agree with large-sample theory. At n = 875 an asymptotic test would give a
similar answer. So the justification here is **not** sample size — it is the block
structure needed to respect autocorrelation. Worth stating precisely, because "we used
a permutation test" is often offered as if it were self-justifying.

### Confirmed: the null result's wording

Wasserman, on goodness-of-fit: failing to reject does not mean the model is correct;
the test may simply have lacked power. Efron ch. 8 frames power = 0.80 as "an 80%
chance of finding something interesting, so it was worth running".

That is exactly the argument this project's reports make, and it is reassuring to find
it stated in the same terms rather than invented here.

### Confirmed: the uniformity test is a deliberate departure

Wasserman ch. 15 and Efron §5.6 both use the multinomial chi-square null. That is the
approximation this project avoids on purpose: exactly `k` numbers come out per draw, so
counts are negatively dependent and the multinomial variance is too large, making the
classical test conservative in the direction that hides bias. Our Monte-Carlo null
stands.

The empirical evidence sits in the shrinkage numbers above: the observed spread is
0.881 of what an independent-slot model predicts for the main pool, close to the
theoretical ratio `(1 - k/N) / (1 - 1/N) = 0.917`.

### New requirement: the winner's curse

Efron ch. 8 (the prostate data) on selection bias: the winner of a "bigness contest"
among many candidates has a biased-upward estimate, because both merit and luck
contributed. Tweedie's formula estimates and removes that bias.

This project does not yet report per-ball findings, but as soon as the descriptive
channel says "number 17 is the most frequent", that frequency is a selection-biased
estimate and reporting it raw would be the winner's curse in plain sight. Recorded as
a requirement for the anomaly channel before it is built.

### Not covered by the corpus

**Block resampling for dependent data.** These texts cover the i.i.d. and parametric
bootstrap only. The moving-block bootstrap, the block sign-flip permutation, and the
`n**(1/3)` block-length heuristic all come from outside this corpus and have **not**
been cross-checked against it. They remain the weakest-supported choices in the
methodology, and anyone extending this project should treat them as such.

**Proper scoring rules.** Log loss and the Brier score as *decision criteria*, and the
`eps = 1e-6` clipping that keeps log loss finite, are not addressed by these five
books. Unverified.
