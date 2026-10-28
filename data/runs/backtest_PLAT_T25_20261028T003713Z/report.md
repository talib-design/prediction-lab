# Backtest — plat, hippodromes français

Généré le 2026-10-28T00:37:13+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `c0d8599b607b`

Courses chargées : 27906 · courses évaluées (cotes complètes à l'horizon) : 24378 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6736 | 1.4351 | 0.0490 | 161474 |
| uniform | 6736 | 0.7007 | 0.0239 | 38495 |
| horse_win_rate | 6736 | 0.7835 | 0.0267 | 48129 |
| form | 6736 | 0.6703 | 0.0229 | 35231 |
| market | 6736 | 0.0550 | 0.0019 | 238 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6736 | 2.0925 | 0.8382 | 0.269 | 0.471 | 0.0066 |
| market | 6736 | 2.0938 | 0.8375 | 0.269 | 0.471 | 0.0065 |
| form | 6736 | 2.2722 | 0.8809 | 0.185 | 0.385 | 0.0069 |
| uniform | 6736 | 2.3686 | 0.9005 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6736 | 2.3930 | 0.9016 | 0.132 | 0.320 | 0.0133 |
| random | 6736 | 2.9332 | 0.9839 | 0.094 | 0.280 | 0.0609 |

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
| random | 6736 | 0.8407 | [0.8086 ; 0.8758] | 0.0002 | oui | moins bon que la référence |
| uniform | 6736 | 0.2761 | [0.2593 ; 0.2932] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6736 | 0.3005 | [0.2814 ; 0.3194] | 0.0002 | oui | moins bon que la référence |
| form | 6736 | 0.1797 | [0.1633 ; 0.1963] | 0.0002 | oui | moins bon que la référence |
| market | 6736 | 0.0013 | [0.0000 ; 0.0027] | 0.0428 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3026 | 0.016 | 0.011 |
| 0.02-0.05 | 22744 | 0.036 | 0.029 |
| 0.05-0.10 | 28518 | 0.072 | 0.074 |
| 0.10-0.20 | 15659 | 0.136 | 0.147 |
| 0.20-0.30 | 3303 | 0.239 | 0.254 |
| 0.30-0.50 | 1541 | 0.380 | 0.360 |
| 0.50-1.00 | 478 | 0.606 | 0.525 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4526 | 0.015 | 0.010 |
| 0.02-0.05 | 22954 | 0.035 | 0.031 |
| 0.05-0.10 | 26998 | 0.072 | 0.075 |
| 0.10-0.20 | 14932 | 0.137 | 0.145 |
| 0.20-0.30 | 3524 | 0.239 | 0.247 |
| 0.30-0.50 | 1691 | 0.377 | 0.334 |
| 0.50-1.00 | 644 | 0.613 | 0.511 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.085** (48 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
