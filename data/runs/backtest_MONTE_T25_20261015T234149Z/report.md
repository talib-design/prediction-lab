# Backtest — trot monté, hippodromes français

Généré le 2026-10-15T23:41:49+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `0a49103d03ca`

Courses chargées : 4326 · courses évaluées (cotes complètes à l'horizon) : 3286 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1387 | 1.5461 | 0.1162 | 187411 |
| uniform | 1387 | 0.8741 | 0.0657 | 59906 |
| horse_win_rate | 1387 | 0.8380 | 0.0630 | 55063 |
| form | 1387 | 0.8618 | 0.0648 | 58232 |
| market | 1387 | 0.0807 | 0.0061 | 512 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1387 | 1.9549 | 0.8097 | 0.332 | 0.533 | 0.0092 |
| market | 1387 | 1.9558 | 0.8076 | 0.332 | 0.533 | 0.0101 |
| horse_win_rate | 1387 | 2.3031 | 0.8827 | 0.190 | 0.386 | 0.0083 |
| form | 1387 | 2.3889 | 0.8981 | 0.182 | 0.368 | 0.0174 |
| uniform | 1387 | 2.4022 | 0.9057 | 0.050 | 0.214 | 0.0000 |
| random | 1387 | 2.9459 | 0.9823 | 0.089 | 0.274 | 0.0618 |

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
| random | 1387 | 0.9910 | [0.9196 ; 1.0649] | 0.0002 | oui | moins bon que la référence |
| uniform | 1387 | 0.4473 | [0.4044 ; 0.4859] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1387 | 0.3482 | [0.3081 ; 0.3897] | 0.0002 | oui | moins bon que la référence |
| form | 1387 | 0.4340 | [0.3883 ; 0.4767] | 0.0002 | oui | moins bon que la référence |
| market | 1387 | 0.0009 | [-0.0028 ; 0.0045] | 0.6429 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2266 | 0.014 | 0.009 |
| 0.02-0.05 | 4908 | 0.034 | 0.028 |
| 0.05-0.10 | 4213 | 0.073 | 0.071 |
| 0.10-0.20 | 2821 | 0.140 | 0.156 |
| 0.20-0.30 | 840 | 0.243 | 0.282 |
| 0.30-0.50 | 503 | 0.380 | 0.344 |
| 0.50-1.00 | 152 | 0.604 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2982 | 0.013 | 0.010 |
| 0.02-0.05 | 4655 | 0.034 | 0.032 |
| 0.05-0.10 | 3848 | 0.072 | 0.077 |
| 0.10-0.20 | 2596 | 0.140 | 0.149 |
| 0.20-0.30 | 843 | 0.243 | 0.275 |
| 0.30-0.50 | 547 | 0.376 | 0.329 |
| 0.50-1.00 | 232 | 0.611 | 0.487 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
