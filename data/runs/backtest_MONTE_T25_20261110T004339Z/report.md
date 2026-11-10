# Backtest — trot monté, hippodromes français

Généré le 2026-11-10T00:43:39+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `40170a71f1df`

Courses chargées : 4396 · courses évaluées (cotes complètes à l'horizon) : 3336 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1437 | 1.5453 | 0.1141 | 187217 |
| uniform | 1437 | 0.8722 | 0.0644 | 59643 |
| horse_win_rate | 1437 | 0.8393 | 0.0620 | 55228 |
| form | 1437 | 0.8618 | 0.0637 | 58228 |
| market | 1437 | 0.0805 | 0.0059 | 508 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1437 | 1.9593 | 0.8111 | 0.330 | 0.531 | 0.0091 |
| market | 1437 | 1.9602 | 0.8090 | 0.330 | 0.531 | 0.0099 |
| horse_win_rate | 1437 | 2.3025 | 0.8824 | 0.190 | 0.386 | 0.0078 |
| form | 1437 | 2.3927 | 0.8984 | 0.180 | 0.366 | 0.0173 |
| uniform | 1437 | 2.4055 | 0.9061 | 0.050 | 0.213 | 0.0000 |
| random | 1437 | 2.9496 | 0.9823 | 0.088 | 0.274 | 0.0617 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1472 | 1.9750 | 0.8122 | 0.312 | 0.516 | 0.0103 |
| market | 1472 | 1.9753 | 0.8116 | 0.312 | 0.516 | 0.0096 |
| horse_win_rate | 1472 | 2.3366 | 0.8899 | 0.181 | 0.365 | 0.0090 |
| form | 1472 | 2.3528 | 0.8911 | 0.194 | 0.379 | 0.0150 |
| uniform | 1472 | 2.4103 | 0.9074 | 0.043 | 0.212 | 0.0000 |
| random | 1472 | 2.8851 | 0.9737 | 0.113 | 0.293 | 0.0567 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 427 | 1.8641 | 0.7713 | 0.398 | 0.579 | 0.0064 |
| market | 427 | 1.8721 | 0.7725 | 0.398 | 0.579 | 0.0110 |
| horse_win_rate | 427 | 2.2808 | 0.8704 | 0.206 | 0.400 | 0.0096 |
| form | 427 | 2.3568 | 0.8817 | 0.239 | 0.411 | 0.0133 |
| uniform | 427 | 2.4452 | 0.9087 | 0.047 | 0.208 | 0.0000 |
| random | 427 | 2.8782 | 0.9736 | 0.089 | 0.281 | 0.0515 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 1437 | 0.9903 | [0.9161 ; 1.0644] | 0.0002 | oui | moins bon que la référence |
| uniform | 1437 | 0.4462 | [0.4072 ; 0.4897] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1437 | 0.3432 | [0.3052 ; 0.3847] | 0.0002 | oui | moins bon que la référence |
| form | 1437 | 0.4334 | [0.3894 ; 0.4747] | 0.0002 | oui | moins bon que la référence |
| market | 1437 | 0.0009 | [-0.0025 ; 0.0048] | 0.6723 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2377 | 0.014 | 0.009 |
| 0.02-0.05 | 5092 | 0.034 | 0.028 |
| 0.05-0.10 | 4373 | 0.073 | 0.071 |
| 0.10-0.20 | 2937 | 0.139 | 0.156 |
| 0.20-0.30 | 871 | 0.243 | 0.281 |
| 0.30-0.50 | 517 | 0.380 | 0.342 |
| 0.50-1.00 | 156 | 0.603 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3117 | 0.013 | 0.010 |
| 0.02-0.05 | 4832 | 0.034 | 0.032 |
| 0.05-0.10 | 3991 | 0.072 | 0.078 |
| 0.10-0.20 | 2707 | 0.140 | 0.149 |
| 0.20-0.30 | 872 | 0.243 | 0.272 |
| 0.30-0.50 | 567 | 0.376 | 0.330 |
| 0.50-1.00 | 237 | 0.611 | 0.485 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
