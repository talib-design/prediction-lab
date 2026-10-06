# Backtest — trot monté, hippodromes français

Généré le 2026-10-06T07:44:45+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `0c3960c8441c`

Courses chargées : 2874 · courses évaluées (cotes complètes à l'horizon) : 2169 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1358 | 1.5513 | 0.1179 | 188684 |
| uniform | 1358 | 0.8806 | 0.0669 | 60802 |
| horse_win_rate | 1358 | 0.8465 | 0.0643 | 56175 |
| form | 1358 | 0.8694 | 0.0661 | 59257 |
| market | 1358 | 0.0892 | 0.0068 | 624 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1358 | 1.9555 | 0.8099 | 0.332 | 0.533 | 0.0092 |
| market | 1358 | 1.9560 | 0.8076 | 0.332 | 0.533 | 0.0103 |
| horse_win_rate | 1358 | 2.2953 | 0.8810 | 0.189 | 0.390 | 0.0092 |
| form | 1358 | 2.3859 | 0.8979 | 0.183 | 0.367 | 0.0179 |
| uniform | 1358 | 2.4009 | 0.9056 | 0.051 | 0.215 | 0.0000 |
| random | 1358 | 2.9425 | 0.9822 | 0.088 | 0.274 | 0.0617 |

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
| random | 1358 | 0.9870 | [0.9129 ; 1.0669] | 0.0002 | oui | moins bon que la référence |
| uniform | 1358 | 0.4454 | [0.4049 ; 0.4884] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1358 | 0.3398 | [0.3004 ; 0.3869] | 0.0002 | oui | moins bon que la référence |
| form | 1358 | 0.4304 | [0.3875 ; 0.4761] | 0.0002 | oui | moins bon que la référence |
| market | 1358 | 0.0005 | [-0.0036 ; 0.0048] | 0.8118 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2205 | 0.014 | 0.010 |
| 0.02-0.05 | 4790 | 0.034 | 0.028 |
| 0.05-0.10 | 4137 | 0.073 | 0.070 |
| 0.10-0.20 | 2756 | 0.140 | 0.157 |
| 0.20-0.30 | 827 | 0.243 | 0.282 |
| 0.30-0.50 | 493 | 0.380 | 0.345 |
| 0.50-1.00 | 148 | 0.602 | 0.520 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2947 | 0.013 | 0.011 |
| 0.02-0.05 | 4532 | 0.034 | 0.032 |
| 0.05-0.10 | 3752 | 0.072 | 0.076 |
| 0.10-0.20 | 2527 | 0.140 | 0.150 |
| 0.20-0.30 | 828 | 0.243 | 0.277 |
| 0.30-0.50 | 541 | 0.377 | 0.322 |
| 0.50-1.00 | 229 | 0.613 | 0.493 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (4 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
