# Backtest — trot monté, hippodromes français

Généré le 2026-10-30T00:47:28+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `7c5a28b66da4`

Courses chargées : 4364 · courses évaluées (cotes complètes à l'horizon) : 3313 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1414 | 1.5412 | 0.1148 | 186222 |
| uniform | 1414 | 0.8725 | 0.0650 | 59677 |
| horse_win_rate | 1414 | 0.8384 | 0.0624 | 55113 |
| form | 1414 | 0.8612 | 0.0641 | 58148 |
| market | 1414 | 0.0804 | 0.0060 | 508 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1414 | 1.9539 | 0.8095 | 0.332 | 0.533 | 0.0091 |
| market | 1414 | 1.9550 | 0.8075 | 0.332 | 0.533 | 0.0102 |
| horse_win_rate | 1414 | 2.3023 | 0.8823 | 0.191 | 0.387 | 0.0081 |
| form | 1414 | 2.3884 | 0.8979 | 0.182 | 0.367 | 0.0172 |
| uniform | 1414 | 2.4035 | 0.9059 | 0.050 | 0.213 | 0.0000 |
| random | 1414 | 2.9413 | 0.9818 | 0.088 | 0.274 | 0.0617 |

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
| random | 1414 | 0.9874 | [0.9125 ; 1.0618] | 0.0002 | oui | moins bon que la référence |
| uniform | 1414 | 0.4496 | [0.4087 ; 0.4858] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1414 | 0.3484 | [0.3070 ; 0.3872] | 0.0002 | oui | moins bon que la référence |
| form | 1414 | 0.4345 | [0.3910 ; 0.4730] | 0.0002 | oui | moins bon que la référence |
| market | 1414 | 0.0011 | [-0.0025 ; 0.0045] | 0.5495 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2326 | 0.014 | 0.009 |
| 0.02-0.05 | 4997 | 0.034 | 0.028 |
| 0.05-0.10 | 4299 | 0.073 | 0.070 |
| 0.10-0.20 | 2886 | 0.140 | 0.156 |
| 0.20-0.30 | 855 | 0.243 | 0.284 |
| 0.30-0.50 | 511 | 0.380 | 0.342 |
| 0.50-1.00 | 155 | 0.602 | 0.529 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3055 | 0.013 | 0.010 |
| 0.02-0.05 | 4742 | 0.034 | 0.032 |
| 0.05-0.10 | 3924 | 0.072 | 0.077 |
| 0.10-0.20 | 2657 | 0.140 | 0.149 |
| 0.20-0.30 | 857 | 0.243 | 0.275 |
| 0.30-0.50 | 559 | 0.376 | 0.329 |
| 0.50-1.00 | 235 | 0.611 | 0.489 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
