# Backtest — trot monté, hippodromes français

Généré le 2026-10-21T23:46:23+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `fc977c8e2f4e`

Courses chargées : 4343 · courses évaluées (cotes complètes à l'horizon) : 3297 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1398 | 1.5460 | 0.1158 | 187374 |
| uniform | 1398 | 0.8740 | 0.0655 | 59895 |
| horse_win_rate | 1398 | 0.8376 | 0.0627 | 55009 |
| form | 1398 | 0.8615 | 0.0645 | 58183 |
| market | 1398 | 0.0807 | 0.0060 | 510 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1398 | 1.9531 | 0.8093 | 0.334 | 0.534 | 0.0092 |
| market | 1398 | 1.9542 | 0.8073 | 0.334 | 0.534 | 0.0101 |
| horse_win_rate | 1398 | 2.2992 | 0.8819 | 0.192 | 0.388 | 0.0080 |
| form | 1398 | 2.3876 | 0.8980 | 0.182 | 0.368 | 0.0171 |
| uniform | 1398 | 2.4022 | 0.9057 | 0.050 | 0.213 | 0.0000 |
| random | 1398 | 2.9425 | 0.9818 | 0.089 | 0.275 | 0.0617 |

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
| random | 1398 | 0.9893 | [0.9164 ; 1.0679] | 0.0002 | oui | moins bon que la référence |
| uniform | 1398 | 0.4491 | [0.4072 ; 0.4873] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1398 | 0.3461 | [0.3067 ; 0.3873] | 0.0002 | oui | moins bon que la référence |
| form | 1398 | 0.4345 | [0.3899 ; 0.4749] | 0.0002 | oui | moins bon que la référence |
| market | 1398 | 0.0011 | [-0.0027 ; 0.0046] | 0.5937 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2287 | 0.014 | 0.009 |
| 0.02-0.05 | 4943 | 0.034 | 0.028 |
| 0.05-0.10 | 4244 | 0.073 | 0.071 |
| 0.10-0.20 | 2846 | 0.140 | 0.155 |
| 0.20-0.30 | 847 | 0.243 | 0.285 |
| 0.30-0.50 | 506 | 0.380 | 0.344 |
| 0.50-1.00 | 154 | 0.603 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3006 | 0.013 | 0.010 |
| 0.02-0.05 | 4691 | 0.034 | 0.032 |
| 0.05-0.10 | 3876 | 0.072 | 0.077 |
| 0.10-0.20 | 2619 | 0.140 | 0.149 |
| 0.20-0.30 | 850 | 0.243 | 0.276 |
| 0.30-0.50 | 551 | 0.376 | 0.330 |
| 0.50-1.00 | 234 | 0.611 | 0.487 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
