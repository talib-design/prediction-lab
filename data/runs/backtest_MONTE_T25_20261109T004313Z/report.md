# Backtest — trot monté, hippodromes français

Généré le 2026-11-09T00:43:13+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `81032bbf05e8`

Courses chargées : 4395 · courses évaluées (cotes complètes à l'horizon) : 3335 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1436 | 1.5457 | 0.1142 | 187303 |
| uniform | 1436 | 0.8717 | 0.0644 | 59571 |
| horse_win_rate | 1436 | 0.8392 | 0.0620 | 55219 |
| form | 1436 | 0.8620 | 0.0637 | 58259 |
| market | 1436 | 0.0804 | 0.0059 | 507 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1436 | 1.9581 | 0.8109 | 0.330 | 0.532 | 0.0092 |
| market | 1436 | 1.9591 | 0.8088 | 0.330 | 0.532 | 0.0100 |
| horse_win_rate | 1436 | 2.3020 | 0.8823 | 0.190 | 0.386 | 0.0078 |
| form | 1436 | 2.3912 | 0.8983 | 0.180 | 0.366 | 0.0173 |
| uniform | 1436 | 2.4054 | 0.9061 | 0.050 | 0.213 | 0.0000 |
| random | 1436 | 2.9478 | 0.9822 | 0.088 | 0.274 | 0.0617 |

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
| random | 1436 | 0.9897 | [0.9206 ; 1.0645] | 0.0002 | oui | moins bon que la référence |
| uniform | 1436 | 0.4472 | [0.4087 ; 0.4905] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1436 | 0.3438 | [0.3055 ; 0.3872] | 0.0002 | oui | moins bon que la référence |
| form | 1436 | 0.4331 | [0.3897 ; 0.4757] | 0.0002 | oui | moins bon que la référence |
| market | 1436 | 0.0010 | [-0.0025 ; 0.0049] | 0.6347 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2371 | 0.014 | 0.009 |
| 0.02-0.05 | 5089 | 0.034 | 0.028 |
| 0.05-0.10 | 4373 | 0.073 | 0.071 |
| 0.10-0.20 | 2933 | 0.139 | 0.156 |
| 0.20-0.30 | 871 | 0.243 | 0.281 |
| 0.30-0.50 | 516 | 0.380 | 0.343 |
| 0.50-1.00 | 156 | 0.603 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3111 | 0.013 | 0.010 |
| 0.02-0.05 | 4829 | 0.034 | 0.032 |
| 0.05-0.10 | 3991 | 0.072 | 0.078 |
| 0.10-0.20 | 2703 | 0.140 | 0.149 |
| 0.20-0.30 | 872 | 0.243 | 0.272 |
| 0.30-0.50 | 566 | 0.376 | 0.330 |
| 0.50-1.00 | 237 | 0.611 | 0.485 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
