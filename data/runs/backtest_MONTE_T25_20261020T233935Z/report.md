# Backtest — trot monté, hippodromes français

Généré le 2026-10-20T23:39:35+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `591ad7bd4498`

Courses chargées : 4342 · courses évaluées (cotes complètes à l'horizon) : 3296 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1397 | 1.5465 | 0.1159 | 187496 |
| uniform | 1397 | 0.8741 | 0.0655 | 59897 |
| horse_win_rate | 1397 | 0.8375 | 0.0627 | 54985 |
| form | 1397 | 0.8612 | 0.0645 | 58153 |
| market | 1397 | 0.0807 | 0.0060 | 511 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1397 | 1.9537 | 0.8094 | 0.334 | 0.534 | 0.0092 |
| market | 1397 | 1.9548 | 0.8074 | 0.334 | 0.534 | 0.0102 |
| horse_win_rate | 1397 | 2.2990 | 0.8818 | 0.192 | 0.388 | 0.0081 |
| form | 1397 | 2.3874 | 0.8979 | 0.183 | 0.368 | 0.0170 |
| uniform | 1397 | 2.4022 | 0.9057 | 0.050 | 0.213 | 0.0000 |
| random | 1397 | 2.9434 | 0.9820 | 0.089 | 0.274 | 0.0617 |

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
| random | 1397 | 0.9897 | [0.9175 ; 1.0659] | 0.0002 | oui | moins bon que la référence |
| uniform | 1397 | 0.4485 | [0.4056 ; 0.4905] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1397 | 0.3453 | [0.3063 ; 0.3896] | 0.0002 | oui | moins bon que la référence |
| form | 1397 | 0.4337 | [0.3894 ; 0.4750] | 0.0002 | oui | moins bon que la référence |
| market | 1397 | 0.0010 | [-0.0027 ; 0.0048] | 0.6025 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2284 | 0.014 | 0.009 |
| 0.02-0.05 | 4939 | 0.034 | 0.028 |
| 0.05-0.10 | 4243 | 0.073 | 0.071 |
| 0.10-0.20 | 2845 | 0.140 | 0.155 |
| 0.20-0.30 | 846 | 0.243 | 0.285 |
| 0.30-0.50 | 505 | 0.380 | 0.343 |
| 0.50-1.00 | 154 | 0.603 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3003 | 0.013 | 0.010 |
| 0.02-0.05 | 4687 | 0.034 | 0.032 |
| 0.05-0.10 | 3875 | 0.072 | 0.077 |
| 0.10-0.20 | 2618 | 0.140 | 0.149 |
| 0.20-0.30 | 849 | 0.243 | 0.277 |
| 0.30-0.50 | 550 | 0.376 | 0.329 |
| 0.50-1.00 | 234 | 0.611 | 0.487 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
