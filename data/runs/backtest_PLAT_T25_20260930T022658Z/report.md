# Backtest — plat, hippodromes français

Généré le 2026-09-30T02:26:58+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `e732bf3a4b39`

Courses chargées : 11732 · courses évaluées (cotes complètes à l'horizon) : 10335 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6380 | 1.4314 | 0.0502 | 160641 |
| uniform | 6380 | 0.6920 | 0.0243 | 37545 |
| horse_win_rate | 6380 | 0.8162 | 0.0286 | 52227 |
| form | 6380 | 0.6662 | 0.0234 | 34798 |
| market | 6380 | 0.0464 | 0.0016 | 169 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6380 | 2.0952 | 0.8384 | 0.269 | 0.470 | 0.0069 |
| market | 6380 | 2.0965 | 0.8378 | 0.269 | 0.470 | 0.0067 |
| form | 6380 | 2.2771 | 0.8819 | 0.183 | 0.384 | 0.0072 |
| uniform | 6380 | 2.3711 | 0.9007 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6380 | 2.4297 | 0.9072 | 0.128 | 0.314 | 0.0180 |
| random | 6380 | 2.9368 | 0.9841 | 0.093 | 0.279 | 0.0607 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 520 | 2.1345 | 0.8422 | 0.238 | 0.447 | 0.0082 |
| market | 520 | 2.1345 | 0.8422 | 0.238 | 0.447 | 0.0081 |
| uniform | 520 | 2.3788 | 0.9003 | 0.150 | 0.344 | 0.0000 |
| horse_win_rate | 520 | 2.3813 | 0.9017 | 0.154 | 0.348 | 0.0019 |
| form | 520 | 2.4512 | 0.9170 | 0.119 | 0.320 | 0.0162 |
| random | 520 | 2.8258 | 0.9711 | 0.110 | 0.297 | 0.0560 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 3435 | 2.0874 | 0.8357 | 0.262 | 0.464 | 0.0057 |
| market | 3435 | 2.0883 | 0.8356 | 0.262 | 0.464 | 0.0058 |
| form | 3435 | 2.2963 | 0.8867 | 0.171 | 0.374 | 0.0111 |
| uniform | 3435 | 2.3481 | 0.8969 | 0.137 | 0.332 | 0.0000 |
| horse_win_rate | 3435 | 2.4100 | 0.9060 | 0.130 | 0.315 | 0.0222 |
| random | 3435 | 2.8947 | 0.9792 | 0.101 | 0.286 | 0.0612 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 6380 | 0.8416 | [0.8076 ; 0.8761] | 0.0002 | oui | moins bon que la référence |
| uniform | 6380 | 0.2759 | [0.2596 ; 0.2929] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6380 | 0.3345 | [0.3153 ; 0.3547] | 0.0002 | oui | moins bon que la référence |
| form | 6380 | 0.1818 | [0.1662 ; 0.1996] | 0.0002 | oui | moins bon que la référence |
| market | 6380 | 0.0013 | [0.0002 ; 0.0024] | 0.0200 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2864 | 0.016 | 0.010 |
| 0.02-0.05 | 21622 | 0.036 | 0.029 |
| 0.05-0.10 | 27128 | 0.072 | 0.074 |
| 0.10-0.20 | 14836 | 0.136 | 0.146 |
| 0.20-0.30 | 3120 | 0.239 | 0.257 |
| 0.30-0.50 | 1442 | 0.380 | 0.355 |
| 0.50-1.00 | 450 | 0.606 | 0.533 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4058 | 0.015 | 0.011 |
| 0.02-0.05 | 21587 | 0.035 | 0.030 |
| 0.05-0.10 | 26111 | 0.072 | 0.075 |
| 0.10-0.20 | 14248 | 0.137 | 0.145 |
| 0.20-0.30 | 3310 | 0.238 | 0.250 |
| 0.30-0.50 | 1567 | 0.376 | 0.334 |
| 0.50-1.00 | 581 | 0.612 | 0.516 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.076** (20 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
