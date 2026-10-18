# Backtest — plat, hippodromes français

Généré le 2026-10-18T23:37:41+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `99e74e8229ca`

Courses chargées : 27781 · courses évaluées (cotes complètes à l'horizon) : 24261 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6619 | 1.4376 | 0.0495 | 162034 |
| uniform | 6619 | 0.7022 | 0.0242 | 38656 |
| horse_win_rate | 6619 | 0.7848 | 0.0270 | 48293 |
| form | 6619 | 0.6719 | 0.0231 | 35391 |
| market | 6619 | 0.0551 | 0.0019 | 239 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6619 | 2.0913 | 0.8378 | 0.270 | 0.472 | 0.0067 |
| market | 6619 | 2.0927 | 0.8371 | 0.270 | 0.472 | 0.0066 |
| form | 6619 | 2.2717 | 0.8809 | 0.185 | 0.386 | 0.0068 |
| uniform | 6619 | 2.3691 | 0.9005 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6619 | 2.3937 | 0.9018 | 0.133 | 0.320 | 0.0134 |
| random | 6619 | 2.9339 | 0.9840 | 0.094 | 0.279 | 0.0609 |

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
| random | 6619 | 0.8426 | [0.8087 ; 0.8789] | 0.0002 | oui | moins bon que la référence |
| uniform | 6619 | 0.2778 | [0.2606 ; 0.2948] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6619 | 0.3024 | [0.2842 ; 0.3208] | 0.0002 | oui | moins bon que la référence |
| form | 6619 | 0.1804 | [0.1646 ; 0.1984] | 0.0002 | oui | moins bon que la référence |
| market | 6619 | 0.0014 | [0.0001 ; 0.0027] | 0.0338 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2994 | 0.016 | 0.010 |
| 0.02-0.05 | 22385 | 0.036 | 0.029 |
| 0.05-0.10 | 28011 | 0.072 | 0.074 |
| 0.10-0.20 | 15374 | 0.136 | 0.147 |
| 0.20-0.30 | 3246 | 0.239 | 0.256 |
| 0.30-0.50 | 1517 | 0.380 | 0.359 |
| 0.50-1.00 | 470 | 0.607 | 0.530 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4475 | 0.015 | 0.010 |
| 0.02-0.05 | 22591 | 0.035 | 0.031 |
| 0.05-0.10 | 26513 | 0.072 | 0.076 |
| 0.10-0.20 | 14656 | 0.137 | 0.145 |
| 0.20-0.30 | 3463 | 0.239 | 0.249 |
| 0.30-0.50 | 1665 | 0.377 | 0.334 |
| 0.50-1.00 | 634 | 0.614 | 0.513 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.085** (48 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
