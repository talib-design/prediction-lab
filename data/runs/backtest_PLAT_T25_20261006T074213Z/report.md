# Backtest — plat, hippodromes français

Généré le 2026-10-06T07:42:13+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `589ab952ac08`

Courses chargées : 17344 · courses évaluées (cotes complètes à l'horizon) : 15242 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6454 | 1.4342 | 0.0500 | 161273 |
| uniform | 6454 | 0.6988 | 0.0244 | 38287 |
| horse_win_rate | 6454 | 0.7879 | 0.0275 | 48666 |
| form | 6454 | 0.6719 | 0.0234 | 35390 |
| market | 6454 | 0.0528 | 0.0018 | 219 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6454 | 2.0951 | 0.8388 | 0.270 | 0.471 | 0.0069 |
| market | 6454 | 2.0964 | 0.8381 | 0.270 | 0.471 | 0.0068 |
| form | 6454 | 2.2754 | 0.8815 | 0.184 | 0.385 | 0.0070 |
| uniform | 6454 | 2.3710 | 0.9007 | 0.129 | 0.321 | 0.0000 |
| horse_win_rate | 6454 | 2.4028 | 0.9032 | 0.133 | 0.319 | 0.0145 |
| random | 6454 | 2.9367 | 0.9842 | 0.093 | 0.279 | 0.0608 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6878 | 2.0841 | 0.8369 | 0.264 | 0.469 | 0.0054 |
| market | 6878 | 2.0849 | 0.8363 | 0.264 | 0.469 | 0.0059 |
| form | 6878 | 2.2790 | 0.8839 | 0.179 | 0.381 | 0.0089 |
| uniform | 6878 | 2.3508 | 0.8981 | 0.138 | 0.332 | 0.0000 |
| horse_win_rate | 6878 | 2.4099 | 0.9060 | 0.137 | 0.323 | 0.0185 |
| random | 6878 | 2.8497 | 0.9760 | 0.103 | 0.293 | 0.0589 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1910 | 2.0841 | 0.8343 | 0.266 | 0.468 | 0.0065 |
| market | 1910 | 2.0858 | 0.8339 | 0.266 | 0.468 | 0.0074 |
| form | 1910 | 2.2741 | 0.8812 | 0.181 | 0.383 | 0.0080 |
| uniform | 1910 | 2.3594 | 0.8980 | 0.145 | 0.341 | 0.0000 |
| horse_win_rate | 1910 | 2.4127 | 0.9031 | 0.132 | 0.319 | 0.0185 |
| random | 1910 | 2.8979 | 0.9751 | 0.106 | 0.289 | 0.0593 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 6454 | 0.8416 | [0.8078 ; 0.8764] | 0.0002 | oui | moins bon que la référence |
| uniform | 6454 | 0.2759 | [0.2581 ; 0.2923] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6454 | 0.3076 | [0.2885 ; 0.3266] | 0.0002 | oui | moins bon que la référence |
| form | 6454 | 0.1803 | [0.1636 ; 0.1976] | 0.0002 | oui | moins bon que la référence |
| market | 6454 | 0.0013 | [-0.0000 ; 0.0026] | 0.0416 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2911 | 0.016 | 0.011 |
| 0.02-0.05 | 21870 | 0.036 | 0.029 |
| 0.05-0.10 | 27412 | 0.072 | 0.074 |
| 0.10-0.20 | 15002 | 0.136 | 0.147 |
| 0.20-0.30 | 3161 | 0.239 | 0.257 |
| 0.30-0.50 | 1462 | 0.380 | 0.355 |
| 0.50-1.00 | 456 | 0.606 | 0.529 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4296 | 0.015 | 0.010 |
| 0.02-0.05 | 22000 | 0.035 | 0.031 |
| 0.05-0.10 | 26067 | 0.072 | 0.075 |
| 0.10-0.20 | 14332 | 0.137 | 0.145 |
| 0.20-0.30 | 3365 | 0.238 | 0.251 |
| 0.30-0.50 | 1608 | 0.376 | 0.331 |
| 0.50-1.00 | 606 | 0.613 | 0.513 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.082** (30 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
