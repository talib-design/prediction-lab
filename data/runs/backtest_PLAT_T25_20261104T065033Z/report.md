# Backtest — plat, hippodromes français

Généré le 2026-11-04T06:50:33+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `7fe5527d2852`

Courses chargées : 27992 · courses évaluées (cotes complètes à l'horizon) : 24463 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6821 | 1.4328 | 0.0486 | 160950 |
| uniform | 6821 | 0.7002 | 0.0237 | 38441 |
| horse_win_rate | 6821 | 0.7835 | 0.0266 | 48128 |
| form | 6821 | 0.6701 | 0.0227 | 35200 |
| market | 6821 | 0.0550 | 0.0019 | 237 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6821 | 2.0907 | 0.8378 | 0.270 | 0.472 | 0.0066 |
| market | 6821 | 2.0921 | 0.8371 | 0.270 | 0.472 | 0.0066 |
| form | 6821 | 2.2710 | 0.8807 | 0.185 | 0.386 | 0.0068 |
| uniform | 6821 | 2.3680 | 0.9004 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6821 | 2.3923 | 0.9014 | 0.132 | 0.320 | 0.0132 |
| random | 6821 | 2.9303 | 0.9833 | 0.095 | 0.280 | 0.0608 |

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
| random | 6821 | 0.8396 | [0.8062 ; 0.8749] | 0.0002 | oui | moins bon que la référence |
| uniform | 6821 | 0.2773 | [0.2603 ; 0.2945] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6821 | 0.3016 | [0.2830 ; 0.3208] | 0.0002 | oui | moins bon que la référence |
| form | 6821 | 0.1803 | [0.1643 ; 0.1970] | 0.0002 | oui | moins bon que la référence |
| market | 6821 | 0.0014 | [0.0001 ; 0.0027] | 0.0242 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3086 | 0.016 | 0.010 |
| 0.02-0.05 | 23005 | 0.036 | 0.029 |
| 0.05-0.10 | 28834 | 0.072 | 0.074 |
| 0.10-0.20 | 15867 | 0.136 | 0.147 |
| 0.20-0.30 | 3353 | 0.239 | 0.254 |
| 0.30-0.50 | 1560 | 0.380 | 0.362 |
| 0.50-1.00 | 485 | 0.606 | 0.524 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4602 | 0.015 | 0.010 |
| 0.02-0.05 | 23217 | 0.035 | 0.031 |
| 0.05-0.10 | 27302 | 0.072 | 0.075 |
| 0.10-0.20 | 15131 | 0.137 | 0.145 |
| 0.20-0.30 | 3574 | 0.239 | 0.247 |
| 0.30-0.50 | 1713 | 0.377 | 0.336 |
| 0.50-1.00 | 651 | 0.614 | 0.510 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.085** (48 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
