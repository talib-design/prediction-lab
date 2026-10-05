# Backtest — plat, hippodromes français

Généré le 2026-10-05T05:02:00+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `dfce24112cd1`

Courses chargées : 12053 · courses évaluées (cotes complètes à l'horizon) : 10636 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6437 | 1.4326 | 0.0500 | 160909 |
| uniform | 6437 | 0.6969 | 0.0243 | 38081 |
| horse_win_rate | 6437 | 0.8152 | 0.0285 | 52104 |
| form | 6437 | 0.6700 | 0.0234 | 35196 |
| market | 6437 | 0.0506 | 0.0018 | 201 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6437 | 2.0961 | 0.8388 | 0.269 | 0.470 | 0.0069 |
| market | 6437 | 2.0973 | 0.8382 | 0.269 | 0.470 | 0.0067 |
| form | 6437 | 2.2772 | 0.8819 | 0.183 | 0.384 | 0.0072 |
| uniform | 6437 | 2.3712 | 0.9007 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6437 | 2.4263 | 0.9068 | 0.128 | 0.314 | 0.0175 |
| random | 6437 | 2.9367 | 0.9842 | 0.093 | 0.279 | 0.0609 |

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
| random | 6437 | 0.8406 | [0.8067 ; 0.8783] | 0.0002 | oui | moins bon que la référence |
| uniform | 6437 | 0.2751 | [0.2585 ; 0.2933] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6437 | 0.3302 | [0.3113 ; 0.3507] | 0.0002 | oui | moins bon que la référence |
| form | 6437 | 0.1811 | [0.1642 ; 0.1986] | 0.0002 | oui | moins bon que la référence |
| market | 6437 | 0.0012 | [0.0001 ; 0.0026] | 0.0368 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2907 | 0.016 | 0.011 |
| 0.02-0.05 | 21821 | 0.036 | 0.029 |
| 0.05-0.10 | 27342 | 0.072 | 0.074 |
| 0.10-0.20 | 14967 | 0.136 | 0.146 |
| 0.20-0.30 | 3152 | 0.239 | 0.256 |
| 0.30-0.50 | 1456 | 0.380 | 0.355 |
| 0.50-1.00 | 455 | 0.606 | 0.530 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4228 | 0.015 | 0.011 |
| 0.02-0.05 | 21897 | 0.035 | 0.031 |
| 0.05-0.10 | 26105 | 0.072 | 0.075 |
| 0.10-0.20 | 14324 | 0.137 | 0.145 |
| 0.20-0.30 | 3352 | 0.238 | 0.250 |
| 0.30-0.50 | 1598 | 0.377 | 0.332 |
| 0.50-1.00 | 596 | 0.614 | 0.515 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.079** (21 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
