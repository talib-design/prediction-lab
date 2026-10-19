# Backtest — plat, hippodromes français

Généré le 2026-10-19T23:37:44+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `ff3392660b7d`

Courses chargées : 27790 · courses évaluées (cotes complètes à l'horizon) : 24270 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6628 | 1.4377 | 0.0494 | 162042 |
| uniform | 6628 | 0.7023 | 0.0242 | 38670 |
| horse_win_rate | 6628 | 0.7848 | 0.0270 | 48294 |
| form | 6628 | 0.6718 | 0.0231 | 35381 |
| market | 6628 | 0.0551 | 0.0019 | 239 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6628 | 2.0921 | 0.8380 | 0.270 | 0.471 | 0.0067 |
| market | 6628 | 2.0934 | 0.8373 | 0.270 | 0.471 | 0.0066 |
| form | 6628 | 2.2725 | 0.8810 | 0.184 | 0.385 | 0.0068 |
| uniform | 6628 | 2.3693 | 0.9005 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6628 | 2.3941 | 0.9018 | 0.132 | 0.320 | 0.0134 |
| random | 6628 | 2.9349 | 0.9840 | 0.094 | 0.279 | 0.0610 |

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
| random | 6628 | 0.8428 | [0.8073 ; 0.8796] | 0.0002 | oui | moins bon que la référence |
| uniform | 6628 | 0.2773 | [0.2609 ; 0.2952] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6628 | 0.3020 | [0.2839 ; 0.3217] | 0.0002 | oui | moins bon que la référence |
| form | 6628 | 0.1805 | [0.1642 ; 0.1988] | 0.0002 | oui | moins bon que la référence |
| market | 6628 | 0.0013 | [0.0001 ; 0.0027] | 0.0380 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3000 | 0.016 | 0.010 |
| 0.02-0.05 | 22433 | 0.036 | 0.029 |
| 0.05-0.10 | 28056 | 0.072 | 0.074 |
| 0.10-0.20 | 15391 | 0.136 | 0.146 |
| 0.20-0.30 | 3248 | 0.239 | 0.256 |
| 0.30-0.50 | 1517 | 0.380 | 0.359 |
| 0.50-1.00 | 472 | 0.607 | 0.530 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4485 | 0.015 | 0.010 |
| 0.02-0.05 | 22636 | 0.035 | 0.031 |
| 0.05-0.10 | 26555 | 0.072 | 0.076 |
| 0.10-0.20 | 14675 | 0.137 | 0.145 |
| 0.20-0.30 | 3465 | 0.239 | 0.248 |
| 0.30-0.50 | 1665 | 0.377 | 0.334 |
| 0.50-1.00 | 636 | 0.614 | 0.513 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.085** (48 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
