# Backtest — plat, hippodromes français

Généré le 2026-10-21T23:38:50+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `af60bb6c8a33`

Courses chargées : 27828 · courses évaluées (cotes complètes à l'horizon) : 24308 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6666 | 1.4381 | 0.0493 | 162137 |
| uniform | 6666 | 0.7020 | 0.0241 | 38632 |
| horse_win_rate | 6666 | 0.7850 | 0.0269 | 48311 |
| form | 6666 | 0.6720 | 0.0230 | 35400 |
| market | 6666 | 0.0551 | 0.0019 | 239 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6666 | 2.0931 | 0.8382 | 0.269 | 0.471 | 0.0066 |
| market | 6666 | 2.0943 | 0.8375 | 0.269 | 0.471 | 0.0065 |
| form | 6666 | 2.2729 | 0.8811 | 0.184 | 0.385 | 0.0068 |
| uniform | 6666 | 2.3692 | 0.9005 | 0.129 | 0.321 | 0.0000 |
| horse_win_rate | 6666 | 2.3942 | 0.9018 | 0.132 | 0.320 | 0.0134 |
| random | 6666 | 2.9361 | 0.9842 | 0.094 | 0.279 | 0.0610 |

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
| random | 6666 | 0.8431 | [0.8112 ; 0.8801] | 0.0002 | oui | moins bon que la référence |
| uniform | 6666 | 0.2761 | [0.2596 ; 0.2937] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6666 | 0.3011 | [0.2829 ; 0.3210] | 0.0002 | oui | moins bon que la référence |
| form | 6666 | 0.1799 | [0.1640 ; 0.1970] | 0.0002 | oui | moins bon que la référence |
| market | 6666 | 0.0013 | [0.0000 ; 0.0027] | 0.0438 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3010 | 0.016 | 0.011 |
| 0.02-0.05 | 22545 | 0.036 | 0.029 |
| 0.05-0.10 | 28234 | 0.072 | 0.074 |
| 0.10-0.20 | 15478 | 0.136 | 0.146 |
| 0.20-0.30 | 3270 | 0.239 | 0.255 |
| 0.30-0.50 | 1522 | 0.380 | 0.359 |
| 0.50-1.00 | 475 | 0.606 | 0.528 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4498 | 0.015 | 0.010 |
| 0.02-0.05 | 22754 | 0.035 | 0.031 |
| 0.05-0.10 | 26726 | 0.072 | 0.076 |
| 0.10-0.20 | 14759 | 0.137 | 0.145 |
| 0.20-0.30 | 3487 | 0.239 | 0.248 |
| 0.30-0.50 | 1671 | 0.377 | 0.334 |
| 0.50-1.00 | 639 | 0.614 | 0.512 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.085** (48 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
