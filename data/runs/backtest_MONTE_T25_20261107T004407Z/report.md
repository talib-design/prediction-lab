# Backtest — trot monté, hippodromes français

Généré le 2026-11-07T00:44:07+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `e958236e6c9d`

Courses chargées : 4387 · courses évaluées (cotes complètes à l'horizon) : 3330 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1431 | 1.5415 | 0.1141 | 186299 |
| uniform | 1431 | 0.8718 | 0.0645 | 59592 |
| horse_win_rate | 1431 | 0.8390 | 0.0621 | 55191 |
| form | 1431 | 0.8628 | 0.0639 | 58366 |
| market | 1431 | 0.0804 | 0.0060 | 508 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1431 | 1.9555 | 0.8102 | 0.331 | 0.533 | 0.0092 |
| market | 1431 | 1.9566 | 0.8082 | 0.331 | 0.533 | 0.0102 |
| horse_win_rate | 1431 | 2.3016 | 0.8822 | 0.191 | 0.387 | 0.0079 |
| form | 1431 | 2.3895 | 0.8979 | 0.181 | 0.367 | 0.0172 |
| uniform | 1431 | 2.4049 | 0.9060 | 0.050 | 0.213 | 0.0000 |
| random | 1431 | 2.9456 | 0.9824 | 0.088 | 0.273 | 0.0619 |

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
| random | 1431 | 0.9901 | [0.9200 ; 1.0623] | 0.0002 | oui | moins bon que la référence |
| uniform | 1431 | 0.4494 | [0.4086 ; 0.4889] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1431 | 0.3461 | [0.3093 ; 0.3898] | 0.0002 | oui | moins bon que la référence |
| form | 1431 | 0.4340 | [0.3911 ; 0.4760] | 0.0002 | oui | moins bon que la référence |
| market | 1431 | 0.0011 | [-0.0024 ; 0.0047] | 0.5645 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2357 | 0.014 | 0.009 |
| 0.02-0.05 | 5070 | 0.034 | 0.028 |
| 0.05-0.10 | 4359 | 0.073 | 0.070 |
| 0.10-0.20 | 2921 | 0.139 | 0.156 |
| 0.20-0.30 | 866 | 0.243 | 0.283 |
| 0.30-0.50 | 515 | 0.380 | 0.344 |
| 0.50-1.00 | 156 | 0.603 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3096 | 0.013 | 0.010 |
| 0.02-0.05 | 4810 | 0.034 | 0.032 |
| 0.05-0.10 | 3978 | 0.072 | 0.077 |
| 0.10-0.20 | 2692 | 0.140 | 0.150 |
| 0.20-0.30 | 866 | 0.243 | 0.274 |
| 0.30-0.50 | 565 | 0.376 | 0.331 |
| 0.50-1.00 | 237 | 0.611 | 0.485 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
