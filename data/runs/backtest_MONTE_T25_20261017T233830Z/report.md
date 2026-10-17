# Backtest — trot monté, hippodromes français

Généré le 2026-10-17T23:38:30+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `b558eca1e2b7`

Courses chargées : 4333 · courses évaluées (cotes complètes à l'horizon) : 3290 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1391 | 1.5465 | 0.1161 | 187500 |
| uniform | 1391 | 0.8739 | 0.0656 | 59877 |
| horse_win_rate | 1391 | 0.8383 | 0.0629 | 55102 |
| form | 1391 | 0.8613 | 0.0647 | 58163 |
| market | 1391 | 0.0807 | 0.0061 | 511 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1391 | 1.9557 | 0.8100 | 0.332 | 0.533 | 0.0092 |
| market | 1391 | 1.9565 | 0.8079 | 0.332 | 0.533 | 0.0100 |
| horse_win_rate | 1391 | 2.3014 | 0.8823 | 0.191 | 0.386 | 0.0082 |
| form | 1391 | 2.3885 | 0.8981 | 0.182 | 0.368 | 0.0173 |
| uniform | 1391 | 2.4021 | 0.9057 | 0.050 | 0.214 | 0.0000 |
| random | 1391 | 2.9457 | 0.9823 | 0.088 | 0.274 | 0.0618 |

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
| random | 1391 | 0.9900 | [0.9161 ; 1.0659] | 0.0002 | oui | moins bon que la référence |
| uniform | 1391 | 0.4464 | [0.4040 ; 0.4867] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1391 | 0.3457 | [0.3087 ; 0.3890] | 0.0002 | oui | moins bon que la référence |
| form | 1391 | 0.4328 | [0.3893 ; 0.4762] | 0.0002 | oui | moins bon que la référence |
| market | 1391 | 0.0009 | [-0.0029 ; 0.0045] | 0.6563 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2271 | 0.014 | 0.009 |
| 0.02-0.05 | 4919 | 0.034 | 0.028 |
| 0.05-0.10 | 4225 | 0.073 | 0.071 |
| 0.10-0.20 | 2832 | 0.140 | 0.156 |
| 0.20-0.30 | 843 | 0.243 | 0.282 |
| 0.30-0.50 | 504 | 0.380 | 0.343 |
| 0.50-1.00 | 152 | 0.604 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2987 | 0.013 | 0.010 |
| 0.02-0.05 | 4666 | 0.034 | 0.032 |
| 0.05-0.10 | 3861 | 0.072 | 0.077 |
| 0.10-0.20 | 2605 | 0.140 | 0.149 |
| 0.20-0.30 | 847 | 0.243 | 0.275 |
| 0.30-0.50 | 548 | 0.376 | 0.328 |
| 0.50-1.00 | 232 | 0.611 | 0.487 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
