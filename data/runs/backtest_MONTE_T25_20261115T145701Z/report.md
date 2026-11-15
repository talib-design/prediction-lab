# Backtest — trot monté, hippodromes français

Généré le 2026-11-15T14:57:01+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `56817e178452`

Courses chargées : 4414 · courses évaluées (cotes complètes à l'horizon) : 3353 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1454 | 1.5459 | 0.1135 | 187361 |
| uniform | 1454 | 0.8722 | 0.0640 | 59638 |
| horse_win_rate | 1454 | 0.8384 | 0.0616 | 55105 |
| form | 1454 | 0.8622 | 0.0633 | 58286 |
| market | 1454 | 0.0803 | 0.0059 | 506 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1454 | 1.9598 | 0.8108 | 0.329 | 0.531 | 0.0088 |
| market | 1454 | 1.9607 | 0.8087 | 0.329 | 0.531 | 0.0098 |
| horse_win_rate | 1454 | 2.3045 | 0.8826 | 0.190 | 0.385 | 0.0080 |
| form | 1454 | 2.3948 | 0.8985 | 0.182 | 0.367 | 0.0173 |
| uniform | 1454 | 2.4062 | 0.9061 | 0.050 | 0.212 | 0.0000 |
| random | 1454 | 2.9523 | 0.9821 | 0.089 | 0.274 | 0.0618 |

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
| random | 1454 | 0.9925 | [0.9172 ; 1.0654] | 0.0002 | oui | moins bon que la référence |
| uniform | 1454 | 0.4464 | [0.4061 ; 0.4861] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1454 | 0.3447 | [0.3034 ; 0.3869] | 0.0002 | oui | moins bon que la référence |
| form | 1454 | 0.4350 | [0.3928 ; 0.4750] | 0.0002 | oui | moins bon que la référence |
| market | 1454 | 0.0009 | [-0.0027 ; 0.0045] | 0.6261 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2412 | 0.014 | 0.009 |
| 0.02-0.05 | 5155 | 0.034 | 0.028 |
| 0.05-0.10 | 4426 | 0.073 | 0.071 |
| 0.10-0.20 | 2974 | 0.139 | 0.155 |
| 0.20-0.30 | 882 | 0.243 | 0.282 |
| 0.30-0.50 | 522 | 0.380 | 0.341 |
| 0.50-1.00 | 158 | 0.602 | 0.532 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3158 | 0.013 | 0.010 |
| 0.02-0.05 | 4892 | 0.034 | 0.032 |
| 0.05-0.10 | 4044 | 0.072 | 0.077 |
| 0.10-0.20 | 2740 | 0.140 | 0.149 |
| 0.20-0.30 | 883 | 0.242 | 0.272 |
| 0.30-0.50 | 573 | 0.376 | 0.330 |
| 0.50-1.00 | 239 | 0.611 | 0.490 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
