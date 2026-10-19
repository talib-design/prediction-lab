# Backtest — trot monté, hippodromes français

Généré le 2026-10-19T23:43:34+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `dd0b4ae50e11`

Courses chargées : 4339 · courses évaluées (cotes complètes à l'horizon) : 3293 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1394 | 1.5458 | 0.1159 | 187340 |
| uniform | 1394 | 0.8742 | 0.0656 | 59915 |
| horse_win_rate | 1394 | 0.8378 | 0.0628 | 55031 |
| form | 1394 | 0.8617 | 0.0646 | 58213 |
| market | 1394 | 0.0807 | 0.0060 | 511 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1394 | 1.9544 | 0.8095 | 0.333 | 0.534 | 0.0092 |
| market | 1394 | 1.9554 | 0.8075 | 0.333 | 0.534 | 0.0101 |
| horse_win_rate | 1394 | 2.3001 | 0.8821 | 0.192 | 0.387 | 0.0081 |
| form | 1394 | 2.3885 | 0.8981 | 0.182 | 0.368 | 0.0172 |
| uniform | 1394 | 2.4019 | 0.9057 | 0.050 | 0.214 | 0.0000 |
| random | 1394 | 2.9442 | 0.9822 | 0.088 | 0.274 | 0.0619 |

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
| random | 1394 | 0.9898 | [0.9171 ; 1.0693] | 0.0002 | oui | moins bon que la référence |
| uniform | 1394 | 0.4475 | [0.4062 ; 0.4884] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1394 | 0.3457 | [0.3061 ; 0.3882] | 0.0002 | oui | moins bon que la référence |
| form | 1394 | 0.4341 | [0.3894 ; 0.4777] | 0.0002 | oui | moins bon que la référence |
| market | 1394 | 0.0010 | [-0.0028 ; 0.0045] | 0.6255 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2276 | 0.014 | 0.009 |
| 0.02-0.05 | 4928 | 0.034 | 0.028 |
| 0.05-0.10 | 4232 | 0.073 | 0.071 |
| 0.10-0.20 | 2840 | 0.140 | 0.156 |
| 0.20-0.30 | 844 | 0.243 | 0.283 |
| 0.30-0.50 | 505 | 0.380 | 0.343 |
| 0.50-1.00 | 153 | 0.603 | 0.529 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2994 | 0.013 | 0.010 |
| 0.02-0.05 | 4674 | 0.034 | 0.032 |
| 0.05-0.10 | 3867 | 0.072 | 0.077 |
| 0.10-0.20 | 2613 | 0.140 | 0.149 |
| 0.20-0.30 | 848 | 0.243 | 0.276 |
| 0.30-0.50 | 549 | 0.376 | 0.328 |
| 0.50-1.00 | 233 | 0.611 | 0.489 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
