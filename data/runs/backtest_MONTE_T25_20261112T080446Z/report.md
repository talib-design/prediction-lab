# Backtest — trot monté, hippodromes français

Généré le 2026-11-12T08:04:46+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `b8f155053c61`

Courses chargées : 4402 · courses évaluées (cotes complètes à l'horizon) : 3341 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1442 | 1.5445 | 0.1139 | 187033 |
| uniform | 1442 | 0.8726 | 0.0643 | 59695 |
| horse_win_rate | 1442 | 0.8391 | 0.0619 | 55206 |
| form | 1442 | 0.8642 | 0.0637 | 58552 |
| market | 1442 | 0.0805 | 0.0059 | 508 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1442 | 1.9597 | 0.8111 | 0.329 | 0.531 | 0.0090 |
| market | 1442 | 1.9606 | 0.8090 | 0.329 | 0.531 | 0.0100 |
| horse_win_rate | 1442 | 2.3035 | 0.8825 | 0.190 | 0.386 | 0.0079 |
| form | 1442 | 2.3951 | 0.8988 | 0.180 | 0.365 | 0.0175 |
| uniform | 1442 | 2.4054 | 0.9061 | 0.050 | 0.213 | 0.0000 |
| random | 1442 | 2.9468 | 0.9817 | 0.090 | 0.275 | 0.0616 |

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
| random | 1442 | 0.9870 | [0.9184 ; 1.0667] | 0.0002 | oui | moins bon que la référence |
| uniform | 1442 | 0.4457 | [0.4088 ; 0.4876] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1442 | 0.3438 | [0.3040 ; 0.3853] | 0.0002 | oui | moins bon que la référence |
| form | 1442 | 0.4354 | [0.3903 ; 0.4744] | 0.0002 | oui | moins bon que la référence |
| market | 1442 | 0.0008 | [-0.0025 ; 0.0046] | 0.6691 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2383 | 0.014 | 0.009 |
| 0.02-0.05 | 5112 | 0.034 | 0.028 |
| 0.05-0.10 | 4385 | 0.073 | 0.071 |
| 0.10-0.20 | 2947 | 0.139 | 0.155 |
| 0.20-0.30 | 877 | 0.243 | 0.283 |
| 0.30-0.50 | 519 | 0.380 | 0.341 |
| 0.50-1.00 | 156 | 0.603 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3126 | 0.013 | 0.010 |
| 0.02-0.05 | 4849 | 0.034 | 0.032 |
| 0.05-0.10 | 4004 | 0.072 | 0.077 |
| 0.10-0.20 | 2716 | 0.140 | 0.149 |
| 0.20-0.30 | 877 | 0.243 | 0.273 |
| 0.30-0.50 | 570 | 0.376 | 0.330 |
| 0.50-1.00 | 237 | 0.611 | 0.485 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
