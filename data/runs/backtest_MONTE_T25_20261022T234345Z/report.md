# Backtest — trot monté, hippodromes français

Généré le 2026-10-22T23:43:45+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `c4fa3119d391`

Courses chargées : 4345 · courses évaluées (cotes complètes à l'horizon) : 3299 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1400 | 1.5450 | 0.1156 | 187147 |
| uniform | 1400 | 0.8741 | 0.0654 | 59900 |
| horse_win_rate | 1400 | 0.8383 | 0.0627 | 55098 |
| form | 1400 | 0.8612 | 0.0644 | 58152 |
| market | 1400 | 0.0806 | 0.0060 | 510 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1400 | 1.9534 | 0.8092 | 0.334 | 0.535 | 0.0090 |
| market | 1400 | 1.9545 | 0.8073 | 0.334 | 0.535 | 0.0101 |
| horse_win_rate | 1400 | 2.3008 | 0.8821 | 0.191 | 0.387 | 0.0082 |
| form | 1400 | 2.3887 | 0.8981 | 0.182 | 0.368 | 0.0172 |
| uniform | 1400 | 2.4026 | 0.9058 | 0.050 | 0.213 | 0.0000 |
| random | 1400 | 2.9425 | 0.9819 | 0.089 | 0.274 | 0.0617 |

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
| random | 1400 | 0.9891 | [0.9171 ; 1.0669] | 0.0002 | oui | moins bon que la référence |
| uniform | 1400 | 0.4492 | [0.4089 ; 0.4890] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1400 | 0.3474 | [0.3071 ; 0.3880] | 0.0002 | oui | moins bon que la référence |
| form | 1400 | 0.4354 | [0.3900 ; 0.4764] | 0.0002 | oui | moins bon que la référence |
| market | 1400 | 0.0011 | [-0.0026 ; 0.0046] | 0.5915 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2295 | 0.014 | 0.009 |
| 0.02-0.05 | 4951 | 0.034 | 0.028 |
| 0.05-0.10 | 4252 | 0.073 | 0.071 |
| 0.10-0.20 | 2848 | 0.140 | 0.155 |
| 0.20-0.30 | 850 | 0.243 | 0.285 |
| 0.30-0.50 | 506 | 0.380 | 0.344 |
| 0.50-1.00 | 154 | 0.603 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3015 | 0.013 | 0.010 |
| 0.02-0.05 | 4699 | 0.034 | 0.032 |
| 0.05-0.10 | 3883 | 0.072 | 0.077 |
| 0.10-0.20 | 2621 | 0.140 | 0.148 |
| 0.20-0.30 | 852 | 0.243 | 0.276 |
| 0.30-0.50 | 552 | 0.376 | 0.332 |
| 0.50-1.00 | 234 | 0.611 | 0.487 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
