# Backtest — trot monté, hippodromes français

Généré le 2026-10-05T10:27:27+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `02fee1985320`

Courses chargées : 2872 · courses évaluées (cotes complètes à l'horizon) : 2167 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1356 | 1.5497 | 0.1178 | 188295 |
| uniform | 1356 | 0.8805 | 0.0669 | 60777 |
| horse_win_rate | 1356 | 0.8467 | 0.0644 | 56200 |
| form | 1356 | 0.8699 | 0.0661 | 59323 |
| market | 1356 | 0.0892 | 0.0068 | 624 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1356 | 1.9551 | 0.8098 | 0.333 | 0.534 | 0.0092 |
| market | 1356 | 1.9556 | 0.8075 | 0.333 | 0.534 | 0.0103 |
| horse_win_rate | 1356 | 2.2954 | 0.8810 | 0.190 | 0.390 | 0.0092 |
| form | 1356 | 2.3860 | 0.8980 | 0.182 | 0.367 | 0.0179 |
| uniform | 1356 | 2.4008 | 0.9055 | 0.051 | 0.215 | 0.0000 |
| random | 1356 | 2.9423 | 0.9822 | 0.088 | 0.274 | 0.0617 |

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
| random | 1356 | 0.9873 | [0.9181 ; 1.0679] | 0.0002 | oui | moins bon que la référence |
| uniform | 1356 | 0.4457 | [0.4044 ; 0.4892] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1356 | 0.3403 | [0.3019 ; 0.3893] | 0.0002 | oui | moins bon que la référence |
| form | 1356 | 0.4310 | [0.3886 ; 0.4772] | 0.0002 | oui | moins bon que la référence |
| market | 1356 | 0.0005 | [-0.0036 ; 0.0046] | 0.8080 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2203 | 0.014 | 0.010 |
| 0.02-0.05 | 4781 | 0.034 | 0.028 |
| 0.05-0.10 | 4129 | 0.073 | 0.070 |
| 0.10-0.20 | 2754 | 0.140 | 0.157 |
| 0.20-0.30 | 825 | 0.243 | 0.281 |
| 0.30-0.50 | 492 | 0.380 | 0.346 |
| 0.50-1.00 | 148 | 0.602 | 0.520 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2945 | 0.013 | 0.011 |
| 0.02-0.05 | 4522 | 0.034 | 0.031 |
| 0.05-0.10 | 3745 | 0.072 | 0.077 |
| 0.10-0.20 | 2525 | 0.140 | 0.150 |
| 0.20-0.30 | 826 | 0.243 | 0.276 |
| 0.30-0.50 | 540 | 0.377 | 0.322 |
| 0.50-1.00 | 229 | 0.613 | 0.493 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (4 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
