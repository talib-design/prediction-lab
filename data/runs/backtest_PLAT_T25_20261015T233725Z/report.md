# Backtest — plat, hippodromes français

Généré le 2026-10-15T23:37:25+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `4e3f031c1567`

Courses chargées : 27736 · courses évaluées (cotes complètes à l'horizon) : 24218 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6576 | 1.4379 | 0.0496 | 162094 |
| uniform | 6576 | 0.7016 | 0.0242 | 38591 |
| horse_win_rate | 6576 | 0.7843 | 0.0271 | 48221 |
| form | 6576 | 0.6725 | 0.0232 | 35458 |
| market | 6576 | 0.0551 | 0.0019 | 239 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6576 | 2.0929 | 0.8383 | 0.270 | 0.471 | 0.0068 |
| market | 6576 | 2.0942 | 0.8376 | 0.270 | 0.471 | 0.0067 |
| form | 6576 | 2.2734 | 0.8812 | 0.184 | 0.385 | 0.0069 |
| uniform | 6576 | 2.3698 | 0.9006 | 0.129 | 0.321 | 0.0000 |
| horse_win_rate | 6576 | 2.3947 | 0.9019 | 0.132 | 0.320 | 0.0134 |
| random | 6576 | 2.9364 | 0.9842 | 0.093 | 0.279 | 0.0610 |

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
| random | 6576 | 0.8436 | [0.8088 ; 0.8803] | 0.0002 | oui | moins bon que la référence |
| uniform | 6576 | 0.2770 | [0.2598 ; 0.2946] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6576 | 0.3018 | [0.2837 ; 0.3206] | 0.0002 | oui | moins bon que la référence |
| form | 6576 | 0.1806 | [0.1649 ; 0.1974] | 0.0002 | oui | moins bon que la référence |
| market | 6576 | 0.0013 | [0.0000 ; 0.0027] | 0.0396 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2981 | 0.016 | 0.010 |
| 0.02-0.05 | 22269 | 0.036 | 0.029 |
| 0.05-0.10 | 27861 | 0.072 | 0.074 |
| 0.10-0.20 | 15271 | 0.136 | 0.147 |
| 0.20-0.30 | 3224 | 0.239 | 0.256 |
| 0.30-0.50 | 1502 | 0.380 | 0.357 |
| 0.50-1.00 | 465 | 0.607 | 0.529 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4448 | 0.015 | 0.010 |
| 0.02-0.05 | 22477 | 0.035 | 0.031 |
| 0.05-0.10 | 26373 | 0.072 | 0.075 |
| 0.10-0.20 | 14556 | 0.137 | 0.145 |
| 0.20-0.30 | 3441 | 0.239 | 0.249 |
| 0.30-0.50 | 1653 | 0.377 | 0.333 |
| 0.50-1.00 | 625 | 0.614 | 0.509 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.085** (48 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
