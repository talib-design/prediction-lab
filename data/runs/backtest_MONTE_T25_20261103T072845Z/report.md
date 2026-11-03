# Backtest — trot monté, hippodromes français

Généré le 2026-11-03T07:28:45+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `d7ae6aea3faf`

Courses chargées : 4378 · courses évaluées (cotes complètes à l'horizon) : 3321 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1422 | 1.5425 | 0.1145 | 186540 |
| uniform | 1422 | 0.8716 | 0.0647 | 59556 |
| horse_win_rate | 1422 | 0.8381 | 0.0622 | 55066 |
| form | 1422 | 0.8608 | 0.0639 | 58087 |
| market | 1422 | 0.0803 | 0.0060 | 506 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1422 | 1.9559 | 0.8102 | 0.331 | 0.533 | 0.0092 |
| market | 1422 | 1.9570 | 0.8081 | 0.331 | 0.533 | 0.0101 |
| horse_win_rate | 1422 | 2.3021 | 0.8823 | 0.191 | 0.387 | 0.0079 |
| form | 1422 | 2.3906 | 0.8983 | 0.181 | 0.367 | 0.0173 |
| uniform | 1422 | 2.4045 | 0.9060 | 0.050 | 0.213 | 0.0000 |
| random | 1422 | 2.9456 | 0.9823 | 0.088 | 0.274 | 0.0618 |

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
| random | 1422 | 0.9897 | [0.9175 ; 1.0643] | 0.0002 | oui | moins bon que la référence |
| uniform | 1422 | 0.4486 | [0.4075 ; 0.4906] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1422 | 0.3462 | [0.3069 ; 0.3908] | 0.0002 | oui | moins bon que la référence |
| form | 1422 | 0.4347 | [0.3889 ; 0.4754] | 0.0002 | oui | moins bon que la référence |
| market | 1422 | 0.0011 | [-0.0025 ; 0.0048] | 0.5869 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2344 | 0.014 | 0.009 |
| 0.02-0.05 | 5035 | 0.034 | 0.028 |
| 0.05-0.10 | 4328 | 0.073 | 0.071 |
| 0.10-0.20 | 2902 | 0.140 | 0.156 |
| 0.20-0.30 | 859 | 0.243 | 0.283 |
| 0.30-0.50 | 514 | 0.380 | 0.342 |
| 0.50-1.00 | 155 | 0.602 | 0.529 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3077 | 0.013 | 0.010 |
| 0.02-0.05 | 4779 | 0.034 | 0.032 |
| 0.05-0.10 | 3949 | 0.072 | 0.077 |
| 0.10-0.20 | 2674 | 0.140 | 0.149 |
| 0.20-0.30 | 861 | 0.243 | 0.274 |
| 0.30-0.50 | 561 | 0.376 | 0.330 |
| 0.50-1.00 | 236 | 0.611 | 0.487 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
