# Backtest — trot monté, hippodromes français

Généré le 2026-10-07T04:36:05+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `72fd7f7bc522`

Courses chargées : 2877 · courses évaluées (cotes complètes à l'horizon) : 2172 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1361 | 1.5517 | 0.1178 | 188763 |
| uniform | 1361 | 0.8809 | 0.0669 | 60843 |
| horse_win_rate | 1361 | 0.8456 | 0.0642 | 56055 |
| form | 1361 | 0.8685 | 0.0659 | 59132 |
| market | 1361 | 0.0892 | 0.0068 | 624 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1361 | 1.9566 | 0.8102 | 0.332 | 0.533 | 0.0091 |
| market | 1361 | 1.9570 | 0.8079 | 0.332 | 0.533 | 0.0102 |
| horse_win_rate | 1361 | 2.2964 | 0.8811 | 0.190 | 0.390 | 0.0094 |
| form | 1361 | 2.3870 | 0.8981 | 0.182 | 0.367 | 0.0180 |
| uniform | 1361 | 2.4008 | 0.9056 | 0.051 | 0.215 | 0.0000 |
| random | 1361 | 2.9422 | 0.9823 | 0.089 | 0.275 | 0.0617 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market | 384 | 1.9950 | 0.8134 | 0.307 | 0.505 | 0.0088 |
| market_calibrated | 384 | 1.9950 | 0.8134 | 0.307 | 0.505 | 0.0088 |
| horse_win_rate | 384 | 2.3263 | 0.8888 | 0.148 | 0.337 | 0.0057 |
| form | 384 | 2.3716 | 0.8965 | 0.159 | 0.353 | 0.0168 |
| uniform | 384 | 2.3904 | 0.9051 | 0.039 | 0.218 | 0.0000 |
| random | 384 | 2.8141 | 0.9613 | 0.135 | 0.312 | 0.0548 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 427 | 1.8660 | 0.7715 | 0.398 | 0.579 | 0.0082 |
| market | 427 | 1.8721 | 0.7725 | 0.398 | 0.579 | 0.0110 |
| horse_win_rate | 427 | 2.2653 | 0.8640 | 0.227 | 0.411 | 0.0125 |
| form | 427 | 2.3593 | 0.8824 | 0.237 | 0.412 | 0.0184 |
| uniform | 427 | 2.4452 | 0.9087 | 0.047 | 0.208 | 0.0000 |
| random | 427 | 2.8782 | 0.9736 | 0.089 | 0.281 | 0.0515 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 1361 | 0.9856 | [0.9147 ; 1.0666] | 0.0002 | oui | moins bon que la référence |
| uniform | 1361 | 0.4442 | [0.4049 ; 0.4890] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1361 | 0.3398 | [0.3006 ; 0.3843] | 0.0002 | oui | moins bon que la référence |
| form | 1361 | 0.4305 | [0.3868 ; 0.4742] | 0.0002 | oui | moins bon que la référence |
| market | 1361 | 0.0004 | [-0.0035 ; 0.0047] | 0.8442 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2206 | 0.014 | 0.010 |
| 0.02-0.05 | 4802 | 0.034 | 0.028 |
| 0.05-0.10 | 4147 | 0.073 | 0.070 |
| 0.10-0.20 | 2761 | 0.140 | 0.156 |
| 0.20-0.30 | 829 | 0.243 | 0.281 |
| 0.30-0.50 | 495 | 0.380 | 0.345 |
| 0.50-1.00 | 148 | 0.602 | 0.520 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2949 | 0.013 | 0.011 |
| 0.02-0.05 | 4546 | 0.034 | 0.032 |
| 0.05-0.10 | 3759 | 0.072 | 0.077 |
| 0.10-0.20 | 2532 | 0.140 | 0.150 |
| 0.20-0.30 | 830 | 0.243 | 0.276 |
| 0.30-0.50 | 542 | 0.377 | 0.323 |
| 0.50-1.00 | 230 | 0.613 | 0.491 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (4 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
