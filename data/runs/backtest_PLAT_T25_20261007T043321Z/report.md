# Backtest — plat, hippodromes français

Généré le 2026-10-07T04:33:21+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `a6a49391f9f8`

Courses chargées : 25585 · courses évaluées (cotes complètes à l'horizon) : 22311 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6462 | 1.4345 | 0.0500 | 161324 |
| uniform | 6462 | 0.7007 | 0.0244 | 38496 |
| horse_win_rate | 6462 | 0.7837 | 0.0273 | 48154 |
| form | 6462 | 0.6732 | 0.0234 | 35526 |
| market | 6462 | 0.0546 | 0.0019 | 234 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6462 | 2.0948 | 0.8387 | 0.270 | 0.471 | 0.0070 |
| market | 6462 | 2.0961 | 0.8380 | 0.270 | 0.471 | 0.0068 |
| form | 6462 | 2.2751 | 0.8814 | 0.184 | 0.385 | 0.0070 |
| uniform | 6462 | 2.3706 | 0.9007 | 0.129 | 0.322 | 0.0000 |
| horse_win_rate | 6462 | 2.3944 | 0.9019 | 0.133 | 0.320 | 0.0134 |
| random | 6462 | 2.9363 | 0.9843 | 0.093 | 0.279 | 0.0609 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 13939 | 2.0789 | 0.8367 | 0.268 | 0.471 | 0.0063 |
| market | 13939 | 2.0803 | 0.8362 | 0.268 | 0.471 | 0.0063 |
| form | 13939 | 2.2583 | 0.8797 | 0.185 | 0.388 | 0.0070 |
| uniform | 13939 | 2.3471 | 0.8981 | 0.140 | 0.334 | 0.0000 |
| horse_win_rate | 13939 | 2.3876 | 0.9023 | 0.136 | 0.325 | 0.0168 |
| random | 13939 | 2.8587 | 0.9780 | 0.104 | 0.293 | 0.0595 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1910 | 2.0840 | 0.8344 | 0.266 | 0.468 | 0.0066 |
| market | 1910 | 2.0858 | 0.8339 | 0.266 | 0.468 | 0.0074 |
| form | 1910 | 2.2749 | 0.8814 | 0.182 | 0.383 | 0.0083 |
| uniform | 1910 | 2.3594 | 0.8980 | 0.145 | 0.341 | 0.0000 |
| horse_win_rate | 1910 | 2.4020 | 0.9015 | 0.129 | 0.318 | 0.0161 |
| random | 1910 | 2.8979 | 0.9751 | 0.106 | 0.289 | 0.0593 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 6462 | 0.8415 | [0.8083 ; 0.8776] | 0.0002 | oui | moins bon que la référence |
| uniform | 6462 | 0.2758 | [0.2580 ; 0.2928] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6462 | 0.2996 | [0.2807 ; 0.3181] | 0.0002 | oui | moins bon que la référence |
| form | 6462 | 0.1803 | [0.1637 ; 0.1986] | 0.0002 | oui | moins bon que la référence |
| market | 6462 | 0.0013 | [-0.0000 ; 0.0026] | 0.0452 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2911 | 0.016 | 0.011 |
| 0.02-0.05 | 21885 | 0.036 | 0.029 |
| 0.05-0.10 | 27434 | 0.072 | 0.074 |
| 0.10-0.20 | 15021 | 0.136 | 0.146 |
| 0.20-0.30 | 3166 | 0.239 | 0.257 |
| 0.30-0.50 | 1465 | 0.380 | 0.356 |
| 0.50-1.00 | 457 | 0.607 | 0.527 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4344 | 0.015 | 0.011 |
| 0.02-0.05 | 22069 | 0.035 | 0.031 |
| 0.05-0.10 | 25998 | 0.072 | 0.076 |
| 0.10-0.20 | 14325 | 0.137 | 0.145 |
| 0.20-0.30 | 3377 | 0.238 | 0.250 |
| 0.30-0.50 | 1611 | 0.376 | 0.331 |
| 0.50-1.00 | 615 | 0.613 | 0.509 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.085** (44 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
