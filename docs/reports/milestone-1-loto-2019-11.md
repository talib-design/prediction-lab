# Prediction Lab evaluation report

**Game:** loto/2019-11  
**Generated:** 2026-09-19T15:13:21+00:00  
**Code version:** 0.1.0  
**Dataset fingerprint:** `fb978170710001d6…`  
**Draws in dataset:** 1075  
**Selection policy:** top_k

## 1. What could have been detected

Read this before the results. It bounds what any conclusion below can mean.

| Pool | Correction | Minimum detectable bias | Relative |
|---|---|---|---|
| main | uncorrected | 0.0267 | 26.2% |
| main | Bonferroni across the pool | 0.0393 | 38.5% |
| chance | uncorrected | 0.0265 | 26.5% |
| chance | Bonferroni across the pool | 0.0344 | 34.4% |

## 2. Observation — what the history looks like

Descriptive only. Nothing in this section is a claim about future draws.

| Pool | Draws | Expected count | Min | Max | chi2 | Monte-Carlo p | Uniformity rejected |
|---|---|---|---|---|---|---|---|
| main | 1075 | 109.7 | 86 | 132 | 37.96 | 0.7562 | no |
| chance | 1075 | 107.5 | 96 | 119 | 3.97 | 0.9091 | no |

## 3. Forecast — did any model help predict the next draw?

Decision metric: **log_loss** (lower is better), against the **uniform** reference. Intervals are moving-block bootstrap; p-values are paired block permutation tests; the last column applies Benjamini-Hochberg across every comparison.

| Model | Pool | Phase | n | log loss [95% CI] | Brier | Mass lift | Matches | ECE | vs ref | p | Survives FDR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| uniform | main | all | 875 | 0.32954 [0.32954, 0.32954] | 0.09163 | 1.000 | 0.512 | 0.0000 | indistinguishable | 1.0000 | no |
| random | main | all | 875 | 0.32954 [0.32954, 0.32954] | 0.09163 | 1.000 | 0.512 | 0.0000 | indistinguishable | 1.0000 | no |
| frequency | main | all | 875 | 0.33060 [0.33023, 0.33098] | 0.09182 | 0.998 | 0.472 | 0.0105 | worse | 0.0002 | yes |
| rolling_frequency_100 | main | all | 875 | 0.33411 [0.33331, 0.33495] | 0.09242 | 0.996 | 0.491 | 0.0219 | worse | 0.0002 | yes |
| rolling_frequency_300 | main | all | 875 | 0.33133 [0.33090, 0.33183] | 0.09194 | 0.997 | 0.482 | 0.0146 | worse | 0.0002 | yes |
| shrunk_frequency | main | all | 875 | 0.32955 [0.32955, 0.32957] | 0.09163 | 1.000 | 0.495 | 0.0002 | worse | 0.0002 | yes |
| shrunk_frequency_300 | main | all | 875 | 0.32956 [0.32954, 0.32958] | 0.09163 | 1.000 | 0.471 | 0.0001 | indistinguishable | 0.1346 | no |
| gap | main | all | 875 | 0.38081 [0.37682, 0.38462] | 0.10080 | 0.999 | 0.513 | 0.0713 | worse | 0.0002 | yes |
| uniform | chance | all | 875 | 0.32508 [0.32508, 0.32508] | 0.09000 | 1.000 | 0.097 | 0.0000 | indistinguishable | 1.0000 | no |
| random | chance | all | 875 | 0.32508 [0.32508, 0.32508] | 0.09000 | 1.000 | 0.097 | 0.0000 | indistinguishable | 1.0000 | no |
| frequency | chance | all | 875 | 0.32615 [0.32538, 0.32691] | 0.09019 | 0.995 | 0.102 | 0.0123 | worse | 0.0072 | yes |
| rolling_frequency_100 | chance | all | 875 | 0.32986 [0.32754, 0.33218] | 0.09078 | 0.995 | 0.105 | 0.0202 | worse | 0.0002 | yes |
| rolling_frequency_300 | chance | all | 875 | 0.32678 [0.32548, 0.32796] | 0.09029 | 0.996 | 0.103 | 0.0144 | worse | 0.0036 | yes |
| shrunk_frequency | chance | all | 875 | 0.32514 [0.32507, 0.32521] | 0.09001 | 1.000 | 0.086 | 0.0013 | indistinguishable | 0.1882 | no |
| shrunk_frequency_300 | chance | all | 875 | 0.32532 [0.32499, 0.32563] | 0.09004 | 0.999 | 0.089 | 0.0041 | indistinguishable | 0.1166 | no |
| gap | chance | all | 875 | 0.37373 [0.36571, 0.38174] | 0.09741 | 0.990 | 0.096 | 0.0701 | worse | 0.0002 | yes |

## 4. Conclusion

**No statistically meaningful predictive signal was detected.**

A null result here is bounded by statistical power, not by the absence of any bias. With this many draws only the departures listed under detection_floor could have been seen at all.

---

*Mass lift is the probability the model placed on the numbers that came out, divided by what assuming fairness would place there; 1.0 means indistinguishable from assuming fairness. Match count is reported because it is expected, but under a fair mechanism every legal ticket has the same expected match count, so it decides nothing.*
