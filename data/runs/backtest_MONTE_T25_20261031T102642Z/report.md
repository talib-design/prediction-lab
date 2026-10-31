# Backtest — trot monté, hippodromes français

Généré le 2026-10-31T10:26:42+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `e8c15a35fe99`

Courses chargées : 4367 · courses évaluées (cotes complètes à l'horizon) : 3316 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1417 | 1.5400 | 0.1145 | 185929 |
| uniform | 1417 | 0.8716 | 0.0648 | 59563 |
| horse_win_rate | 1417 | 0.8377 | 0.0623 | 55012 |
| form | 1417 | 0.8612 | 0.0641 | 58148 |
| market | 1417 | 0.0803 | 0.0060 | 507 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1417 | 1.9545 | 0.8097 | 0.332 | 0.533 | 0.0092 |
| market | 1417 | 1.9556 | 0.8077 | 0.332 | 0.533 | 0.0102 |
| horse_win_rate | 1417 | 2.3026 | 0.8824 | 0.191 | 0.386 | 0.0081 |
| form | 1417 | 2.3893 | 0.8980 | 0.181 | 0.367 | 0.0171 |
| uniform | 1417 | 2.4038 | 0.9059 | 0.050 | 0.213 | 0.0000 |
| random | 1417 | 2.9425 | 0.9821 | 0.088 | 0.274 | 0.0618 |

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
| random | 1417 | 0.9880 | [0.9167 ; 1.0623] | 0.0002 | oui | moins bon que la référence |
| uniform | 1417 | 0.4494 | [0.4087 ; 0.4883] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1417 | 0.3481 | [0.3077 ; 0.3885] | 0.0002 | oui | moins bon que la référence |
| form | 1417 | 0.4349 | [0.3894 ; 0.4742] | 0.0002 | oui | moins bon que la référence |
| market | 1417 | 0.0012 | [-0.0025 ; 0.0048] | 0.5453 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2327 | 0.014 | 0.009 |
| 0.02-0.05 | 5014 | 0.034 | 0.028 |
| 0.05-0.10 | 4308 | 0.073 | 0.071 |
| 0.10-0.20 | 2896 | 0.140 | 0.156 |
| 0.20-0.30 | 857 | 0.243 | 0.284 |
| 0.30-0.50 | 511 | 0.380 | 0.342 |
| 0.50-1.00 | 155 | 0.602 | 0.529 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3058 | 0.013 | 0.010 |
| 0.02-0.05 | 4759 | 0.034 | 0.032 |
| 0.05-0.10 | 3931 | 0.072 | 0.077 |
| 0.10-0.20 | 2667 | 0.140 | 0.149 |
| 0.20-0.30 | 859 | 0.243 | 0.275 |
| 0.30-0.50 | 559 | 0.376 | 0.329 |
| 0.50-1.00 | 235 | 0.611 | 0.489 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
