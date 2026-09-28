# Backtest — plat, hippodromes français

Généré le 2026-09-28T11:11:52+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `c1f022c4acc3`

Courses chargées : 1365 · courses évaluées (cotes complètes à l'horizon) : 1088 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 568 | 1.3079 | 0.1537 | 134106 |
| uniform | 568 | 0.6237 | 0.0733 | 30500 |
| horse_win_rate | 568 | 0.6782 | 0.0797 | 36062 |
| form | 568 | 0.7402 | 0.0870 | 42957 |
| market | 568 | 0.0096 | 0.0011 | 8 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 568 | 2.0689 | 0.8384 | 0.271 | 0.478 | 0.0129 |
| market | 568 | 2.0691 | 0.8383 | 0.271 | 0.478 | 0.0126 |
| uniform | 568 | 2.3415 | 0.8967 | 0.132 | 0.323 | 0.0000 |
| horse_win_rate | 568 | 2.3568 | 0.9001 | 0.132 | 0.317 | 0.0088 |
| form | 568 | 2.3908 | 0.9099 | 0.134 | 0.328 | 0.0164 |
| random | 568 | 2.8639 | 0.9796 | 0.099 | 0.286 | 0.0645 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market | 454 | 2.1434 | 0.8453 | 0.229 | 0.441 | 0.0114 |
| market_calibrated | 454 | 2.1434 | 0.8453 | 0.229 | 0.441 | 0.0114 |
| uniform | 454 | 2.3836 | 0.9007 | 0.148 | 0.343 | 0.0000 |
| horse_win_rate | 454 | 2.3892 | 0.9027 | 0.152 | 0.346 | 0.0025 |
| form | 454 | 2.4562 | 0.9177 | 0.110 | 0.314 | 0.0167 |
| random | 454 | 2.8116 | 0.9695 | 0.112 | 0.299 | 0.0563 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 66 | 2.0729 | 0.8213 | 0.303 | 0.485 | 0.0166 |
| market | 66 | 2.0729 | 0.8213 | 0.303 | 0.485 | 0.0174 |
| horse_win_rate | 66 | 2.3264 | 0.8947 | 0.167 | 0.363 | 0.0046 |
| uniform | 66 | 2.3460 | 0.8980 | 0.167 | 0.352 | 0.0000 |
| form | 66 | 2.4166 | 0.9123 | 0.182 | 0.360 | 0.0128 |
| random | 66 | 2.9236 | 0.9825 | 0.091 | 0.279 | 0.0544 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 568 | 0.7950 | [0.6801 ; 0.9000] | 0.0002 | oui | moins bon que la référence |
| uniform | 568 | 0.2726 | [0.2254 ; 0.3216] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 568 | 0.2878 | [0.2392 ; 0.3382] | 0.0002 | oui | moins bon que la référence |
| form | 568 | 0.3218 | [0.2636 ; 0.3866] | 0.0002 | oui | moins bon que la référence |
| market | 568 | 0.0001 | [-0.0007 ; 0.0010] | 0.7666 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 200 | 0.016 | 0.005 |
| 0.02-0.05 | 1868 | 0.037 | 0.026 |
| 0.05-0.10 | 2343 | 0.072 | 0.074 |
| 0.10-0.20 | 1324 | 0.136 | 0.162 |
| 0.20-0.30 | 257 | 0.240 | 0.222 |
| 0.30-0.50 | 160 | 0.378 | 0.319 |
| 0.50-1.00 | 42 | 0.600 | 0.548 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 219 | 0.016 | 0.005 |
| 0.02-0.05 | 1859 | 0.037 | 0.026 |
| 0.05-0.10 | 2339 | 0.072 | 0.075 |
| 0.10-0.20 | 1316 | 0.136 | 0.162 |
| 0.20-0.30 | 259 | 0.240 | 0.220 |
| 0.30-0.50 | 157 | 0.378 | 0.312 |
| 0.50-1.00 | 45 | 0.597 | 0.556 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.039** (2 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
