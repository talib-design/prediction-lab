# Backtest — trot monté, hippodromes français

Généré le 2026-10-08T04:37:00+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `ce7454ae3bdc`

Courses chargées : 2879 · courses évaluées (cotes complètes à l'horizon) : 2174 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1363 | 1.5506 | 0.1176 | 188499 |
| uniform | 1363 | 0.8814 | 0.0668 | 60903 |
| horse_win_rate | 1363 | 0.8458 | 0.0641 | 56088 |
| form | 1363 | 0.8689 | 0.0659 | 59185 |
| market | 1363 | 0.0892 | 0.0068 | 624 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1363 | 1.9551 | 0.8096 | 0.333 | 0.534 | 0.0091 |
| market | 1363 | 1.9556 | 0.8073 | 0.333 | 0.534 | 0.0102 |
| horse_win_rate | 1363 | 2.2963 | 0.8811 | 0.189 | 0.390 | 0.0093 |
| form | 1363 | 2.3870 | 0.8980 | 0.183 | 0.367 | 0.0180 |
| uniform | 1363 | 2.4008 | 0.9056 | 0.051 | 0.215 | 0.0000 |
| random | 1363 | 2.9412 | 0.9822 | 0.089 | 0.275 | 0.0616 |

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
| random | 1363 | 0.9861 | [0.9145 ; 1.0612] | 0.0002 | oui | moins bon que la référence |
| uniform | 1363 | 0.4457 | [0.4043 ; 0.4878] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1363 | 0.3412 | [0.2999 ; 0.3842] | 0.0002 | oui | moins bon que la référence |
| form | 1363 | 0.4319 | [0.3867 ; 0.4733] | 0.0002 | oui | moins bon que la référence |
| market | 1363 | 0.0005 | [-0.0035 ; 0.0047] | 0.8080 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2210 | 0.014 | 0.010 |
| 0.02-0.05 | 4810 | 0.034 | 0.028 |
| 0.05-0.10 | 4151 | 0.073 | 0.070 |
| 0.10-0.20 | 2765 | 0.140 | 0.156 |
| 0.20-0.30 | 830 | 0.243 | 0.282 |
| 0.30-0.50 | 495 | 0.380 | 0.345 |
| 0.50-1.00 | 149 | 0.602 | 0.523 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2954 | 0.013 | 0.011 |
| 0.02-0.05 | 4555 | 0.034 | 0.032 |
| 0.05-0.10 | 3762 | 0.072 | 0.077 |
| 0.10-0.20 | 2534 | 0.140 | 0.150 |
| 0.20-0.30 | 832 | 0.243 | 0.276 |
| 0.30-0.50 | 542 | 0.377 | 0.323 |
| 0.50-1.00 | 231 | 0.613 | 0.494 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (4 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
