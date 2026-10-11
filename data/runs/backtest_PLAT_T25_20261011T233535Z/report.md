# Backtest — plat, hippodromes français

Généré le 2026-10-11T23:35:35+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `61e857d9274b`

Courses chargées : 27691 · courses évaluées (cotes complètes à l'horizon) : 24173 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6531 | 1.4388 | 0.0499 | 162302 |
| uniform | 6531 | 0.7018 | 0.0243 | 38611 |
| horse_win_rate | 6531 | 0.7842 | 0.0272 | 48209 |
| form | 6531 | 0.6730 | 0.0233 | 35513 |
| market | 6531 | 0.0552 | 0.0019 | 239 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6531 | 2.0937 | 0.8387 | 0.270 | 0.471 | 0.0069 |
| market | 6531 | 2.0950 | 0.8380 | 0.270 | 0.471 | 0.0067 |
| form | 6531 | 2.2736 | 0.8813 | 0.184 | 0.385 | 0.0069 |
| uniform | 6531 | 2.3700 | 0.9006 | 0.129 | 0.322 | 0.0000 |
| horse_win_rate | 6531 | 2.3946 | 0.9020 | 0.132 | 0.320 | 0.0133 |
| random | 6531 | 2.9377 | 0.9843 | 0.093 | 0.279 | 0.0610 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 15732 | 2.0776 | 0.8362 | 0.268 | 0.471 | 0.0060 |
| market | 15732 | 2.0791 | 0.8356 | 0.268 | 0.471 | 0.0065 |
| form | 15732 | 2.2571 | 0.8791 | 0.186 | 0.390 | 0.0067 |
| uniform | 15732 | 2.3486 | 0.8982 | 0.139 | 0.334 | 0.0000 |
| horse_win_rate | 15732 | 2.3858 | 0.9018 | 0.135 | 0.325 | 0.0164 |
| random | 15732 | 2.8617 | 0.9773 | 0.104 | 0.292 | 0.0592 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1910 | 2.0840 | 0.8344 | 0.266 | 0.468 | 0.0066 |
| market | 1910 | 2.0858 | 0.8339 | 0.266 | 0.468 | 0.0074 |
| form | 1910 | 2.2750 | 0.8814 | 0.182 | 0.383 | 0.0084 |
| uniform | 1910 | 2.3594 | 0.8980 | 0.145 | 0.341 | 0.0000 |
| horse_win_rate | 1910 | 2.3986 | 0.9010 | 0.131 | 0.320 | 0.0154 |
| random | 1910 | 2.8979 | 0.9751 | 0.106 | 0.289 | 0.0593 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 6531 | 0.8440 | [0.8121 ; 0.8813] | 0.0002 | oui | moins bon que la référence |
| uniform | 6531 | 0.2763 | [0.2603 ; 0.2941] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6531 | 0.3009 | [0.2820 ; 0.3201] | 0.0002 | oui | moins bon que la référence |
| form | 6531 | 0.1799 | [0.1632 ; 0.1975] | 0.0002 | oui | moins bon que la référence |
| market | 6531 | 0.0013 | [0.0001 ; 0.0027] | 0.0456 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2956 | 0.016 | 0.010 |
| 0.02-0.05 | 22105 | 0.036 | 0.029 |
| 0.05-0.10 | 27687 | 0.072 | 0.074 |
| 0.10-0.20 | 15172 | 0.136 | 0.147 |
| 0.20-0.30 | 3206 | 0.239 | 0.256 |
| 0.30-0.50 | 1488 | 0.380 | 0.358 |
| 0.50-1.00 | 461 | 0.607 | 0.525 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4416 | 0.015 | 0.010 |
| 0.02-0.05 | 22312 | 0.035 | 0.031 |
| 0.05-0.10 | 26206 | 0.072 | 0.076 |
| 0.10-0.20 | 14462 | 0.137 | 0.145 |
| 0.20-0.30 | 3422 | 0.239 | 0.249 |
| 0.30-0.50 | 1636 | 0.377 | 0.333 |
| 0.50-1.00 | 621 | 0.613 | 0.506 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.085** (48 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
