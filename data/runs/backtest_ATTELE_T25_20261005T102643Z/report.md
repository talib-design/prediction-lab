# Backtest — trot attelé, hippodromes français

Généré le 2026-10-05T10:26:43+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `bebc36d087d7`

Courses chargées : 17594 · courses évaluées (cotes complètes à l'horizon) : 11410 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7311 | 1.5427 | 0.0505 | 186584 |
| uniform | 7311 | 0.8978 | 0.0294 | 63198 |
| horse_win_rate | 7311 | 0.9062 | 0.0297 | 64375 |
| form | 7311 | 0.9076 | 0.0297 | 64575 |
| market | 7311 | 0.0948 | 0.0031 | 705 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7311 | 1.9725 | 0.8078 | 0.330 | 0.531 | 0.0072 |
| market | 7311 | 1.9783 | 0.8065 | 0.330 | 0.531 | 0.0091 |
| horse_win_rate | 7311 | 2.4165 | 0.8936 | 0.189 | 0.376 | 0.0114 |
| form | 7311 | 2.4493 | 0.9020 | 0.167 | 0.356 | 0.0105 |
| uniform | 7311 | 2.5162 | 0.9166 | 0.058 | 0.230 | 0.0000 |
| random | 7311 | 3.0459 | 0.9853 | 0.085 | 0.257 | 0.0526 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 2021 | 2.0445 | 0.8192 | 0.300 | 0.506 | 0.0084 |
| market | 2021 | 2.0495 | 0.8183 | 0.300 | 0.506 | 0.0088 |
| horse_win_rate | 2021 | 2.4988 | 0.9052 | 0.168 | 0.335 | 0.0103 |
| form | 2021 | 2.5561 | 0.9148 | 0.148 | 0.326 | 0.0141 |
| uniform | 2021 | 2.5612 | 0.9206 | 0.069 | 0.236 | 0.0000 |
| random | 2021 | 3.0649 | 0.9820 | 0.089 | 0.257 | 0.0484 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 2078 | 2.0207 | 0.8168 | 0.310 | 0.514 | 0.0087 |
| market | 2078 | 2.0236 | 0.8143 | 0.310 | 0.514 | 0.0095 |
| horse_win_rate | 2078 | 2.4849 | 0.9040 | 0.172 | 0.357 | 0.0144 |
| form | 2078 | 2.4944 | 0.9084 | 0.165 | 0.346 | 0.0120 |
| uniform | 2078 | 2.5535 | 0.9204 | 0.068 | 0.238 | 0.0000 |
| random | 2078 | 3.1166 | 0.9889 | 0.083 | 0.252 | 0.0500 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 7311 | 1.0734 | [1.0417 ; 1.1078] | 0.0002 | oui | moins bon que la référence |
| uniform | 7311 | 0.5437 | [0.5249 ; 0.5630] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7311 | 0.4440 | [0.4240 ; 0.4648] | 0.0002 | oui | moins bon que la référence |
| form | 7311 | 0.4768 | [0.4562 ; 0.4972] | 0.0002 | oui | moins bon que la référence |
| market | 7311 | 0.0059 | [0.0039 ; 0.0079] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 18108 | 0.013 | 0.006 |
| 0.02-0.05 | 29671 | 0.034 | 0.027 |
| 0.05-0.10 | 23186 | 0.072 | 0.071 |
| 0.10-0.20 | 13993 | 0.139 | 0.161 |
| 0.20-0.30 | 4195 | 0.241 | 0.263 |
| 0.30-0.50 | 2650 | 0.379 | 0.389 |
| 0.50-1.00 | 737 | 0.596 | 0.528 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 23211 | 0.011 | 0.007 |
| 0.02-0.05 | 27558 | 0.033 | 0.031 |
| 0.05-0.10 | 20688 | 0.072 | 0.076 |
| 0.10-0.20 | 12718 | 0.140 | 0.159 |
| 0.20-0.30 | 4261 | 0.242 | 0.241 |
| 0.30-0.50 | 2910 | 0.380 | 0.367 |
| 0.50-1.00 | 1194 | 0.610 | 0.494 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.122** (22 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
