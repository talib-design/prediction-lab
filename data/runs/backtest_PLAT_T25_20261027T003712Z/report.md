# Backtest — plat, hippodromes français

Généré le 2026-10-27T00:37:12+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `2ae4d7c61ee7`

Courses chargées : 27898 · courses évaluées (cotes complètes à l'horizon) : 24370 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6728 | 1.4357 | 0.0490 | 161604 |
| uniform | 6728 | 0.7008 | 0.0239 | 38509 |
| horse_win_rate | 6728 | 0.7838 | 0.0268 | 48164 |
| form | 6728 | 0.6707 | 0.0229 | 35263 |
| market | 6728 | 0.0550 | 0.0019 | 238 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6728 | 2.0922 | 0.8381 | 0.270 | 0.471 | 0.0067 |
| market | 6728 | 2.0935 | 0.8374 | 0.270 | 0.471 | 0.0065 |
| form | 6728 | 2.2718 | 0.8809 | 0.185 | 0.385 | 0.0068 |
| uniform | 6728 | 2.3684 | 0.9005 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6728 | 2.3926 | 0.9015 | 0.133 | 0.320 | 0.0133 |
| random | 6728 | 2.9333 | 0.9839 | 0.094 | 0.280 | 0.0610 |

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
| random | 6728 | 0.8411 | [0.8072 ; 0.8754] | 0.0002 | oui | moins bon que la référence |
| uniform | 6728 | 0.2763 | [0.2594 ; 0.2933] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6728 | 0.3004 | [0.2813 ; 0.3193] | 0.0002 | oui | moins bon que la référence |
| form | 6728 | 0.1796 | [0.1637 ; 0.1963] | 0.0002 | oui | moins bon que la référence |
| market | 6728 | 0.0013 | [0.0000 ; 0.0026] | 0.0414 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3023 | 0.016 | 0.011 |
| 0.02-0.05 | 22715 | 0.036 | 0.029 |
| 0.05-0.10 | 28478 | 0.072 | 0.073 |
| 0.10-0.20 | 15638 | 0.136 | 0.147 |
| 0.20-0.30 | 3300 | 0.239 | 0.254 |
| 0.30-0.50 | 1539 | 0.380 | 0.360 |
| 0.50-1.00 | 478 | 0.606 | 0.525 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4521 | 0.015 | 0.010 |
| 0.02-0.05 | 22925 | 0.035 | 0.031 |
| 0.05-0.10 | 26960 | 0.072 | 0.075 |
| 0.10-0.20 | 14912 | 0.137 | 0.145 |
| 0.20-0.30 | 3520 | 0.239 | 0.247 |
| 0.30-0.50 | 1690 | 0.377 | 0.334 |
| 0.50-1.00 | 643 | 0.613 | 0.510 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.085** (48 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
