# Backtest — trot monté, hippodromes français

Généré le 2026-10-24T06:54:06+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `619651909cbc`

Courses chargées : 4347 · courses évaluées (cotes complètes à l'horizon) : 3301 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1402 | 1.5439 | 0.1155 | 186888 |
| uniform | 1402 | 0.8736 | 0.0653 | 59832 |
| horse_win_rate | 1402 | 0.8380 | 0.0627 | 55055 |
| form | 1402 | 0.8614 | 0.0644 | 58177 |
| market | 1402 | 0.0806 | 0.0060 | 510 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1402 | 1.9538 | 0.8094 | 0.334 | 0.534 | 0.0090 |
| market | 1402 | 1.9549 | 0.8074 | 0.334 | 0.534 | 0.0101 |
| horse_win_rate | 1402 | 2.3004 | 0.8821 | 0.191 | 0.387 | 0.0082 |
| form | 1402 | 2.3882 | 0.8980 | 0.183 | 0.368 | 0.0172 |
| uniform | 1402 | 2.4024 | 0.9058 | 0.050 | 0.213 | 0.0000 |
| random | 1402 | 2.9430 | 0.9820 | 0.088 | 0.274 | 0.0618 |

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
| random | 1402 | 0.9892 | [0.9177 ; 1.0678] | 0.0002 | oui | moins bon que la référence |
| uniform | 1402 | 0.4487 | [0.4071 ; 0.4885] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1402 | 0.3466 | [0.3060 ; 0.3883] | 0.0002 | oui | moins bon que la référence |
| form | 1402 | 0.4344 | [0.3901 ; 0.4750] | 0.0002 | oui | moins bon que la référence |
| market | 1402 | 0.0011 | [-0.0027 ; 0.0047] | 0.5977 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2296 | 0.014 | 0.009 |
| 0.02-0.05 | 4954 | 0.034 | 0.028 |
| 0.05-0.10 | 4261 | 0.073 | 0.071 |
| 0.10-0.20 | 2854 | 0.140 | 0.155 |
| 0.20-0.30 | 850 | 0.243 | 0.285 |
| 0.30-0.50 | 507 | 0.380 | 0.343 |
| 0.50-1.00 | 154 | 0.603 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3016 | 0.013 | 0.010 |
| 0.02-0.05 | 4704 | 0.034 | 0.032 |
| 0.05-0.10 | 3890 | 0.072 | 0.077 |
| 0.10-0.20 | 2627 | 0.140 | 0.148 |
| 0.20-0.30 | 852 | 0.243 | 0.276 |
| 0.30-0.50 | 553 | 0.376 | 0.331 |
| 0.50-1.00 | 234 | 0.611 | 0.487 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
