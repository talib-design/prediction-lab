# Backtest — trot monté, hippodromes français

Généré le 2026-11-05T00:45:57+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `05dcb36f5fa9`

Courses chargées : 4383 · courses évaluées (cotes complètes à l'horizon) : 3326 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1427 | 1.5406 | 0.1142 | 186090 |
| uniform | 1427 | 0.8703 | 0.0645 | 59387 |
| horse_win_rate | 1427 | 0.8378 | 0.0621 | 55025 |
| form | 1427 | 0.8605 | 0.0638 | 58056 |
| market | 1427 | 0.0802 | 0.0059 | 505 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1427 | 1.9559 | 0.8103 | 0.330 | 0.532 | 0.0093 |
| market | 1427 | 1.9570 | 0.8083 | 0.330 | 0.532 | 0.0102 |
| horse_win_rate | 1427 | 2.3028 | 0.8824 | 0.190 | 0.386 | 0.0079 |
| form | 1427 | 2.3898 | 0.8981 | 0.181 | 0.367 | 0.0172 |
| uniform | 1427 | 2.4049 | 0.9060 | 0.050 | 0.212 | 0.0000 |
| random | 1427 | 2.9457 | 0.9823 | 0.088 | 0.274 | 0.0619 |

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
| random | 1427 | 0.9898 | [0.9176 ; 1.0631] | 0.0002 | oui | moins bon que la référence |
| uniform | 1427 | 0.4490 | [0.4079 ; 0.4906] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1427 | 0.3469 | [0.3078 ; 0.3900] | 0.0002 | oui | moins bon que la référence |
| form | 1427 | 0.4339 | [0.3903 ; 0.4757] | 0.0002 | oui | moins bon que la référence |
| market | 1427 | 0.0011 | [-0.0025 ; 0.0049] | 0.5587 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2351 | 0.014 | 0.009 |
| 0.02-0.05 | 5055 | 0.034 | 0.028 |
| 0.05-0.10 | 4345 | 0.073 | 0.071 |
| 0.10-0.20 | 2917 | 0.140 | 0.156 |
| 0.20-0.30 | 863 | 0.243 | 0.282 |
| 0.30-0.50 | 514 | 0.380 | 0.342 |
| 0.50-1.00 | 155 | 0.602 | 0.529 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3087 | 0.013 | 0.010 |
| 0.02-0.05 | 4796 | 0.034 | 0.031 |
| 0.05-0.10 | 3966 | 0.072 | 0.077 |
| 0.10-0.20 | 2688 | 0.140 | 0.150 |
| 0.20-0.30 | 864 | 0.243 | 0.273 |
| 0.30-0.50 | 563 | 0.376 | 0.329 |
| 0.50-1.00 | 236 | 0.611 | 0.487 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
