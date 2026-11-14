# Backtest — trot monté, hippodromes français

Généré le 2026-11-14T00:52:00+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `2fea5008ad92`

Courses chargées : 4409 · courses évaluées (cotes complètes à l'horizon) : 3348 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1449 | 1.5442 | 0.1136 | 186954 |
| uniform | 1449 | 0.8725 | 0.0642 | 59680 |
| horse_win_rate | 1449 | 0.8382 | 0.0617 | 55082 |
| form | 1449 | 0.8632 | 0.0635 | 58418 |
| market | 1449 | 0.0804 | 0.0059 | 507 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1449 | 1.9576 | 0.8103 | 0.330 | 0.532 | 0.0090 |
| market | 1449 | 1.9586 | 0.8083 | 0.330 | 0.532 | 0.0099 |
| horse_win_rate | 1449 | 2.3035 | 0.8825 | 0.190 | 0.386 | 0.0079 |
| form | 1449 | 2.3937 | 0.8984 | 0.181 | 0.367 | 0.0173 |
| uniform | 1449 | 2.4052 | 0.9061 | 0.050 | 0.213 | 0.0000 |
| random | 1449 | 2.9486 | 0.9819 | 0.090 | 0.275 | 0.0617 |

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
| random | 1449 | 0.9910 | [0.9170 ; 1.0634] | 0.0002 | oui | moins bon que la référence |
| uniform | 1449 | 0.4476 | [0.4059 ; 0.4846] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1449 | 0.3459 | [0.3048 ; 0.3838] | 0.0002 | oui | moins bon que la référence |
| form | 1449 | 0.4361 | [0.3916 ; 0.4761] | 0.0002 | oui | moins bon que la référence |
| market | 1449 | 0.0010 | [-0.0028 ; 0.0045] | 0.6111 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2393 | 0.014 | 0.009 |
| 0.02-0.05 | 5136 | 0.034 | 0.028 |
| 0.05-0.10 | 4405 | 0.073 | 0.071 |
| 0.10-0.20 | 2960 | 0.139 | 0.155 |
| 0.20-0.30 | 880 | 0.243 | 0.283 |
| 0.30-0.50 | 522 | 0.380 | 0.341 |
| 0.50-1.00 | 158 | 0.602 | 0.532 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3138 | 0.013 | 0.010 |
| 0.02-0.05 | 4872 | 0.034 | 0.032 |
| 0.05-0.10 | 4025 | 0.072 | 0.078 |
| 0.10-0.20 | 2727 | 0.140 | 0.149 |
| 0.20-0.30 | 880 | 0.243 | 0.273 |
| 0.30-0.50 | 573 | 0.376 | 0.330 |
| 0.50-1.00 | 239 | 0.611 | 0.490 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
