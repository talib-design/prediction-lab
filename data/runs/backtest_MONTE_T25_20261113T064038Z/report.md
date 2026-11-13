# Backtest — trot monté, hippodromes français

Généré le 2026-11-13T06:40:38+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `13565bf5fa13`

Courses chargées : 4404 · courses évaluées (cotes complètes à l'horizon) : 3343 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1444 | 1.5447 | 0.1138 | 187079 |
| uniform | 1444 | 0.8727 | 0.0643 | 59715 |
| horse_win_rate | 1444 | 0.8389 | 0.0618 | 55181 |
| form | 1444 | 0.8640 | 0.0637 | 58527 |
| market | 1444 | 0.0805 | 0.0059 | 508 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1444 | 1.9587 | 0.8107 | 0.330 | 0.531 | 0.0090 |
| market | 1444 | 1.9596 | 0.8087 | 0.330 | 0.531 | 0.0100 |
| horse_win_rate | 1444 | 2.3034 | 0.8825 | 0.190 | 0.386 | 0.0079 |
| form | 1444 | 2.3946 | 0.8987 | 0.179 | 0.366 | 0.0173 |
| uniform | 1444 | 2.4056 | 0.9061 | 0.050 | 0.213 | 0.0000 |
| random | 1444 | 2.9472 | 0.9817 | 0.090 | 0.275 | 0.0616 |

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
| random | 1444 | 0.9885 | [0.9160 ; 1.0667] | 0.0002 | oui | moins bon que la référence |
| uniform | 1444 | 0.4469 | [0.4074 ; 0.4864] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1444 | 0.3447 | [0.3032 ; 0.3859] | 0.0002 | oui | moins bon que la référence |
| form | 1444 | 0.4359 | [0.3897 ; 0.4764] | 0.0002 | oui | moins bon que la référence |
| market | 1444 | 0.0009 | [-0.0027 ; 0.0045] | 0.6301 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2386 | 0.014 | 0.009 |
| 0.02-0.05 | 5122 | 0.034 | 0.028 |
| 0.05-0.10 | 4392 | 0.073 | 0.071 |
| 0.10-0.20 | 2952 | 0.139 | 0.155 |
| 0.20-0.30 | 877 | 0.243 | 0.283 |
| 0.30-0.50 | 519 | 0.380 | 0.341 |
| 0.50-1.00 | 157 | 0.602 | 0.529 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3130 | 0.013 | 0.010 |
| 0.02-0.05 | 4859 | 0.034 | 0.032 |
| 0.05-0.10 | 4011 | 0.072 | 0.077 |
| 0.10-0.20 | 2720 | 0.140 | 0.149 |
| 0.20-0.30 | 877 | 0.243 | 0.273 |
| 0.30-0.50 | 570 | 0.376 | 0.330 |
| 0.50-1.00 | 238 | 0.611 | 0.487 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
