# Backtest — plat, hippodromes français

Généré le 2026-10-25T08:28:21+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `fde10b86bfcd`

Courses chargées : 27856 · courses évaluées (cotes complètes à l'horizon) : 24336 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6694 | 1.4362 | 0.0492 | 161709 |
| uniform | 6694 | 0.7014 | 0.0240 | 38569 |
| horse_win_rate | 6694 | 0.7845 | 0.0268 | 48251 |
| form | 6694 | 0.6715 | 0.0230 | 35350 |
| market | 6694 | 0.0551 | 0.0019 | 238 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6694 | 2.0936 | 0.8385 | 0.269 | 0.470 | 0.0067 |
| market | 6694 | 2.0948 | 0.8377 | 0.269 | 0.470 | 0.0066 |
| form | 6694 | 2.2730 | 0.8811 | 0.184 | 0.385 | 0.0069 |
| uniform | 6694 | 2.3689 | 0.9005 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6694 | 2.3931 | 0.9016 | 0.133 | 0.320 | 0.0133 |
| random | 6694 | 2.9348 | 0.9841 | 0.094 | 0.279 | 0.0611 |

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
| random | 6694 | 0.8412 | [0.8089 ; 0.8770] | 0.0002 | oui | moins bon que la référence |
| uniform | 6694 | 0.2753 | [0.2583 ; 0.2925] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6694 | 0.2995 | [0.2811 ; 0.3196] | 0.0002 | oui | moins bon que la référence |
| form | 6694 | 0.1794 | [0.1633 ; 0.1969] | 0.0002 | oui | moins bon que la référence |
| market | 6694 | 0.0012 | [-0.0001 ; 0.0025] | 0.0494 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3018 | 0.016 | 0.011 |
| 0.02-0.05 | 22623 | 0.036 | 0.029 |
| 0.05-0.10 | 28346 | 0.072 | 0.074 |
| 0.10-0.20 | 15551 | 0.136 | 0.147 |
| 0.20-0.30 | 3283 | 0.239 | 0.255 |
| 0.30-0.50 | 1530 | 0.380 | 0.358 |
| 0.50-1.00 | 476 | 0.606 | 0.527 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4511 | 0.015 | 0.010 |
| 0.02-0.05 | 22832 | 0.035 | 0.031 |
| 0.05-0.10 | 26834 | 0.072 | 0.076 |
| 0.10-0.20 | 14829 | 0.137 | 0.145 |
| 0.20-0.30 | 3500 | 0.239 | 0.248 |
| 0.30-0.50 | 1681 | 0.377 | 0.332 |
| 0.50-1.00 | 640 | 0.614 | 0.511 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.085** (48 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
