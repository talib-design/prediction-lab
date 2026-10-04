# Backtest — plat, hippodromes français

Généré le 2026-10-04T05:47:59+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `2d834b8616bb`

Courses chargées : 12034 · courses évaluées (cotes complètes à l'horizon) : 10621 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6422 | 1.4329 | 0.0501 | 160976 |
| uniform | 6422 | 0.6963 | 0.0243 | 38010 |
| horse_win_rate | 6422 | 0.8149 | 0.0285 | 52066 |
| form | 6422 | 0.6693 | 0.0234 | 35119 |
| market | 6422 | 0.0505 | 0.0018 | 201 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6422 | 2.0959 | 0.8388 | 0.269 | 0.470 | 0.0069 |
| market | 6422 | 2.0971 | 0.8382 | 0.269 | 0.470 | 0.0067 |
| form | 6422 | 2.2767 | 0.8819 | 0.183 | 0.384 | 0.0072 |
| uniform | 6422 | 2.3708 | 0.9007 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6422 | 2.4257 | 0.9067 | 0.128 | 0.314 | 0.0174 |
| random | 6422 | 2.9366 | 0.9842 | 0.093 | 0.279 | 0.0609 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market | 2289 | 2.1000 | 0.8374 | 0.256 | 0.460 | 0.0061 |
| market_calibrated | 2289 | 2.1002 | 0.8381 | 0.256 | 0.460 | 0.0062 |
| form | 2289 | 2.3473 | 0.8968 | 0.150 | 0.353 | 0.0144 |
| uniform | 2289 | 2.3552 | 0.8978 | 0.131 | 0.324 | 0.0000 |
| horse_win_rate | 2289 | 2.3956 | 0.9041 | 0.132 | 0.319 | 0.0155 |
| random | 2289 | 2.8735 | 0.9804 | 0.098 | 0.285 | 0.0606 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1910 | 2.0842 | 0.8343 | 0.266 | 0.468 | 0.0063 |
| market | 1910 | 2.0858 | 0.8339 | 0.266 | 0.468 | 0.0074 |
| form | 1910 | 2.2789 | 0.8817 | 0.183 | 0.384 | 0.0086 |
| uniform | 1910 | 2.3594 | 0.8980 | 0.145 | 0.341 | 0.0000 |
| horse_win_rate | 1910 | 2.4310 | 0.9085 | 0.119 | 0.310 | 0.0239 |
| random | 1910 | 2.8979 | 0.9751 | 0.106 | 0.289 | 0.0593 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 6422 | 0.8407 | [0.8074 ; 0.8760] | 0.0002 | oui | moins bon que la référence |
| uniform | 6422 | 0.2750 | [0.2581 ; 0.2923] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6422 | 0.3299 | [0.3110 ; 0.3495] | 0.0002 | oui | moins bon que la référence |
| form | 6422 | 0.1808 | [0.1651 ; 0.1985] | 0.0002 | oui | moins bon que la référence |
| market | 6422 | 0.0013 | [0.0001 ; 0.0025] | 0.0386 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2877 | 0.016 | 0.010 |
| 0.02-0.05 | 21756 | 0.036 | 0.029 |
| 0.05-0.10 | 27292 | 0.072 | 0.074 |
| 0.10-0.20 | 14932 | 0.136 | 0.146 |
| 0.20-0.30 | 3143 | 0.239 | 0.256 |
| 0.30-0.50 | 1453 | 0.380 | 0.355 |
| 0.50-1.00 | 454 | 0.606 | 0.529 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4192 | 0.015 | 0.010 |
| 0.02-0.05 | 21832 | 0.035 | 0.031 |
| 0.05-0.10 | 26060 | 0.072 | 0.075 |
| 0.10-0.20 | 14291 | 0.137 | 0.145 |
| 0.20-0.30 | 3342 | 0.238 | 0.250 |
| 0.30-0.50 | 1596 | 0.377 | 0.331 |
| 0.50-1.00 | 594 | 0.614 | 0.515 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.079** (21 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
