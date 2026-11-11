# Backtest — trot monté, hippodromes français

Généré le 2026-11-11T10:50:38+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `9540ba9fb53e`

Courses chargées : 4400 · courses évaluées (cotes complètes à l'horizon) : 3340 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1441 | 1.5447 | 0.1139 | 187073 |
| uniform | 1441 | 0.8729 | 0.0644 | 59736 |
| horse_win_rate | 1441 | 0.8390 | 0.0619 | 55191 |
| form | 1441 | 0.8645 | 0.0638 | 58591 |
| market | 1441 | 0.0805 | 0.0059 | 508 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1441 | 1.9600 | 0.8111 | 0.330 | 0.531 | 0.0090 |
| market | 1441 | 1.9609 | 0.8090 | 0.330 | 0.531 | 0.0100 |
| horse_win_rate | 1441 | 2.3031 | 0.8824 | 0.190 | 0.386 | 0.0079 |
| form | 1441 | 2.3955 | 0.8988 | 0.180 | 0.365 | 0.0175 |
| uniform | 1441 | 2.4057 | 0.9061 | 0.050 | 0.213 | 0.0000 |
| random | 1441 | 2.9480 | 0.9819 | 0.090 | 0.274 | 0.0616 |

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
| random | 1441 | 0.9879 | [0.9166 ; 1.0632] | 0.0002 | oui | moins bon que la référence |
| uniform | 1441 | 0.4456 | [0.4050 ; 0.4869] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1441 | 0.3431 | [0.3037 ; 0.3845] | 0.0002 | oui | moins bon que la référence |
| form | 1441 | 0.4355 | [0.3918 ; 0.4739] | 0.0002 | oui | moins bon que la référence |
| market | 1441 | 0.0008 | [-0.0028 ; 0.0045] | 0.6793 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2383 | 0.014 | 0.009 |
| 0.02-0.05 | 5109 | 0.034 | 0.028 |
| 0.05-0.10 | 4383 | 0.073 | 0.071 |
| 0.10-0.20 | 2947 | 0.139 | 0.155 |
| 0.20-0.30 | 875 | 0.243 | 0.282 |
| 0.30-0.50 | 518 | 0.380 | 0.342 |
| 0.50-1.00 | 156 | 0.603 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3125 | 0.013 | 0.010 |
| 0.02-0.05 | 4847 | 0.034 | 0.032 |
| 0.05-0.10 | 4002 | 0.072 | 0.077 |
| 0.10-0.20 | 2716 | 0.140 | 0.149 |
| 0.20-0.30 | 875 | 0.243 | 0.272 |
| 0.30-0.50 | 569 | 0.376 | 0.330 |
| 0.50-1.00 | 237 | 0.611 | 0.485 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
