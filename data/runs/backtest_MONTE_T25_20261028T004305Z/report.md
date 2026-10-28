# Backtest — trot monté, hippodromes français

Généré le 2026-10-28T00:43:05+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `1009ca4a84bb`

Courses chargées : 4360 · courses évaluées (cotes complètes à l'horizon) : 3309 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1410 | 1.5414 | 0.1149 | 186275 |
| uniform | 1410 | 0.8734 | 0.0651 | 59811 |
| horse_win_rate | 1410 | 0.8379 | 0.0625 | 55039 |
| form | 1410 | 0.8614 | 0.0642 | 58177 |
| market | 1410 | 0.0805 | 0.0060 | 509 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1410 | 1.9536 | 0.8092 | 0.333 | 0.534 | 0.0090 |
| market | 1410 | 1.9547 | 0.8073 | 0.333 | 0.534 | 0.0100 |
| horse_win_rate | 1410 | 2.3006 | 0.8821 | 0.191 | 0.387 | 0.0080 |
| form | 1410 | 2.3880 | 0.8978 | 0.182 | 0.368 | 0.0172 |
| uniform | 1410 | 2.4032 | 0.9058 | 0.050 | 0.213 | 0.0000 |
| random | 1410 | 2.9400 | 0.9817 | 0.089 | 0.274 | 0.0616 |

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
| random | 1410 | 0.9864 | [0.9120 ; 1.0652] | 0.0002 | oui | moins bon que la référence |
| uniform | 1410 | 0.4497 | [0.4075 ; 0.4858] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1410 | 0.3471 | [0.3036 ; 0.3870] | 0.0002 | oui | moins bon que la référence |
| form | 1410 | 0.4345 | [0.3908 ; 0.4731] | 0.0002 | oui | moins bon que la référence |
| market | 1410 | 0.0011 | [-0.0027 ; 0.0044] | 0.5549 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2318 | 0.014 | 0.009 |
| 0.02-0.05 | 4984 | 0.034 | 0.028 |
| 0.05-0.10 | 4284 | 0.073 | 0.071 |
| 0.10-0.20 | 2875 | 0.140 | 0.155 |
| 0.20-0.30 | 853 | 0.243 | 0.285 |
| 0.30-0.50 | 510 | 0.380 | 0.343 |
| 0.50-1.00 | 155 | 0.602 | 0.529 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3043 | 0.013 | 0.010 |
| 0.02-0.05 | 4732 | 0.034 | 0.032 |
| 0.05-0.10 | 3910 | 0.072 | 0.077 |
| 0.10-0.20 | 2647 | 0.140 | 0.148 |
| 0.20-0.30 | 855 | 0.243 | 0.276 |
| 0.30-0.50 | 557 | 0.376 | 0.330 |
| 0.50-1.00 | 235 | 0.611 | 0.489 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
