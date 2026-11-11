# Backtest — plat, hippodromes français

Généré le 2026-11-11T07:37:07+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `be1ca7af96be`

Courses chargées : 28094 · courses évaluées (cotes complètes à l'horizon) : 24562 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6920 | 1.4335 | 0.0482 | 161100 |
| uniform | 6920 | 0.6999 | 0.0236 | 38406 |
| horse_win_rate | 6920 | 0.7835 | 0.0264 | 48133 |
| form | 6920 | 0.6702 | 0.0226 | 35215 |
| market | 6920 | 0.0549 | 0.0018 | 237 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6920 | 2.0900 | 0.8377 | 0.270 | 0.472 | 0.0067 |
| market | 6920 | 2.0914 | 0.8370 | 0.270 | 0.472 | 0.0067 |
| form | 6920 | 2.2710 | 0.8807 | 0.185 | 0.386 | 0.0068 |
| uniform | 6920 | 2.3678 | 0.9004 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6920 | 2.3914 | 0.9013 | 0.132 | 0.320 | 0.0133 |
| random | 6920 | 2.9298 | 0.9833 | 0.095 | 0.281 | 0.0609 |

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
| random | 6920 | 0.8398 | [0.8066 ; 0.8739] | 0.0002 | oui | moins bon que la référence |
| uniform | 6920 | 0.2779 | [0.2615 ; 0.2944] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6920 | 0.3014 | [0.2835 ; 0.3203] | 0.0002 | oui | moins bon que la référence |
| form | 6920 | 0.1810 | [0.1659 ; 0.1973] | 0.0002 | oui | moins bon que la référence |
| market | 6920 | 0.0014 | [0.0002 ; 0.0027] | 0.0268 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3138 | 0.016 | 0.011 |
| 0.02-0.05 | 23329 | 0.036 | 0.029 |
| 0.05-0.10 | 29228 | 0.072 | 0.074 |
| 0.10-0.20 | 16097 | 0.136 | 0.147 |
| 0.20-0.30 | 3409 | 0.239 | 0.255 |
| 0.30-0.50 | 1582 | 0.380 | 0.360 |
| 0.50-1.00 | 494 | 0.606 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4686 | 0.015 | 0.010 |
| 0.02-0.05 | 23532 | 0.035 | 0.031 |
| 0.05-0.10 | 27677 | 0.072 | 0.075 |
| 0.10-0.20 | 15348 | 0.137 | 0.145 |
| 0.20-0.30 | 3634 | 0.239 | 0.247 |
| 0.30-0.50 | 1739 | 0.377 | 0.335 |
| 0.50-1.00 | 661 | 0.614 | 0.511 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.086** (49 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
