# Backtest — plat, hippodromes français

Généré le 2026-11-05T00:39:06+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `5d6a4523970b`

Courses chargées : 28000 · courses évaluées (cotes complètes à l'horizon) : 24471 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6829 | 1.4324 | 0.0485 | 160848 |
| uniform | 6829 | 0.7000 | 0.0237 | 38413 |
| horse_win_rate | 6829 | 0.7833 | 0.0265 | 48108 |
| form | 6829 | 0.6700 | 0.0227 | 35189 |
| market | 6829 | 0.0549 | 0.0019 | 237 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6829 | 2.0906 | 0.8379 | 0.270 | 0.471 | 0.0067 |
| market | 6829 | 2.0919 | 0.8372 | 0.270 | 0.471 | 0.0066 |
| form | 6829 | 2.2707 | 0.8806 | 0.185 | 0.386 | 0.0068 |
| uniform | 6829 | 2.3679 | 0.9004 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6829 | 2.3919 | 0.9013 | 0.132 | 0.320 | 0.0132 |
| random | 6829 | 2.9297 | 0.9832 | 0.095 | 0.281 | 0.0608 |

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
| random | 6829 | 0.8391 | [0.8046 ; 0.8745] | 0.0002 | oui | moins bon que la référence |
| uniform | 6829 | 0.2773 | [0.2599 ; 0.2952] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6829 | 0.3013 | [0.2819 ; 0.3216] | 0.0002 | oui | moins bon que la référence |
| form | 6829 | 0.1801 | [0.1641 ; 0.1977] | 0.0002 | oui | moins bon que la référence |
| market | 6829 | 0.0014 | [0.0001 ; 0.0028] | 0.0286 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3090 | 0.016 | 0.010 |
| 0.02-0.05 | 23031 | 0.036 | 0.029 |
| 0.05-0.10 | 28856 | 0.072 | 0.074 |
| 0.10-0.20 | 15888 | 0.136 | 0.147 |
| 0.20-0.30 | 3359 | 0.239 | 0.254 |
| 0.30-0.50 | 1562 | 0.380 | 0.362 |
| 0.50-1.00 | 486 | 0.606 | 0.523 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4611 | 0.015 | 0.010 |
| 0.02-0.05 | 23239 | 0.035 | 0.031 |
| 0.05-0.10 | 27325 | 0.072 | 0.075 |
| 0.10-0.20 | 15150 | 0.137 | 0.146 |
| 0.20-0.30 | 3580 | 0.239 | 0.247 |
| 0.30-0.50 | 1714 | 0.377 | 0.336 |
| 0.50-1.00 | 653 | 0.614 | 0.508 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.085** (48 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
