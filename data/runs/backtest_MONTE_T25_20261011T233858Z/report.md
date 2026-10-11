# Backtest — trot monté, hippodromes français

Généré le 2026-10-11T23:38:58+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `0f76eda48c80`

Courses chargées : 4312 · courses évaluées (cotes complètes à l'horizon) : 3272 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1373 | 1.5485 | 0.1170 | 187994 |
| uniform | 1373 | 0.8739 | 0.0660 | 59871 |
| horse_win_rate | 1373 | 0.8372 | 0.0633 | 54951 |
| form | 1373 | 0.8643 | 0.0653 | 58566 |
| market | 1373 | 0.0807 | 0.0061 | 512 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1373 | 1.9542 | 0.8093 | 0.332 | 0.533 | 0.0092 |
| market | 1373 | 1.9552 | 0.8073 | 0.332 | 0.533 | 0.0103 |
| horse_win_rate | 1373 | 2.3019 | 0.8826 | 0.191 | 0.386 | 0.0082 |
| form | 1373 | 2.3881 | 0.8980 | 0.183 | 0.368 | 0.0176 |
| uniform | 1373 | 2.4011 | 0.9056 | 0.051 | 0.214 | 0.0000 |
| random | 1373 | 2.9444 | 0.9823 | 0.089 | 0.274 | 0.0617 |

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
| random | 1373 | 0.9901 | [0.9099 ; 1.0614] | 0.0002 | oui | moins bon que la référence |
| uniform | 1373 | 0.4468 | [0.4025 ; 0.4857] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1373 | 0.3477 | [0.3070 ; 0.3914] | 0.0002 | oui | moins bon que la référence |
| form | 1373 | 0.4339 | [0.3872 ; 0.4752] | 0.0002 | oui | moins bon que la référence |
| market | 1373 | 0.0010 | [-0.0028 ; 0.0046] | 0.6333 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2228 | 0.014 | 0.009 |
| 0.02-0.05 | 4851 | 0.034 | 0.028 |
| 0.05-0.10 | 4180 | 0.073 | 0.070 |
| 0.10-0.20 | 2784 | 0.140 | 0.157 |
| 0.20-0.30 | 837 | 0.243 | 0.282 |
| 0.30-0.50 | 498 | 0.380 | 0.343 |
| 0.50-1.00 | 150 | 0.603 | 0.527 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2936 | 0.013 | 0.010 |
| 0.02-0.05 | 4603 | 0.034 | 0.032 |
| 0.05-0.10 | 3816 | 0.072 | 0.077 |
| 0.10-0.20 | 2561 | 0.140 | 0.150 |
| 0.20-0.30 | 841 | 0.243 | 0.276 |
| 0.30-0.50 | 543 | 0.376 | 0.326 |
| 0.50-1.00 | 228 | 0.611 | 0.491 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
