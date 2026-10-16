# Backtest — trot monté, hippodromes français

Généré le 2026-10-16T23:41:33+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `d01235bbf296`

Courses chargées : 4327 · courses évaluées (cotes complètes à l'horizon) : 3287 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1388 | 1.5464 | 0.1162 | 187476 |
| uniform | 1388 | 0.8746 | 0.0657 | 59967 |
| horse_win_rate | 1388 | 0.8384 | 0.0630 | 55112 |
| form | 1388 | 0.8621 | 0.0648 | 58271 |
| market | 1388 | 0.0808 | 0.0061 | 512 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1388 | 1.9558 | 0.8099 | 0.332 | 0.533 | 0.0091 |
| market | 1388 | 1.9566 | 0.8078 | 0.332 | 0.533 | 0.0100 |
| horse_win_rate | 1388 | 2.3031 | 0.8828 | 0.189 | 0.385 | 0.0082 |
| form | 1388 | 2.3889 | 0.8982 | 0.182 | 0.368 | 0.0175 |
| uniform | 1388 | 2.4021 | 0.9057 | 0.050 | 0.214 | 0.0000 |
| random | 1388 | 2.9455 | 0.9823 | 0.089 | 0.274 | 0.0618 |

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
| random | 1388 | 0.9896 | [0.9200 ; 1.0649] | 0.0002 | oui | moins bon que la référence |
| uniform | 1388 | 0.4463 | [0.4040 ; 0.4870] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1388 | 0.3473 | [0.3076 ; 0.3891] | 0.0002 | oui | moins bon que la référence |
| form | 1388 | 0.4331 | [0.3884 ; 0.4768] | 0.0002 | oui | moins bon que la référence |
| market | 1388 | 0.0008 | [-0.0028 ; 0.0045] | 0.6689 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2266 | 0.014 | 0.009 |
| 0.02-0.05 | 4912 | 0.034 | 0.028 |
| 0.05-0.10 | 4215 | 0.073 | 0.071 |
| 0.10-0.20 | 2824 | 0.140 | 0.156 |
| 0.20-0.30 | 841 | 0.243 | 0.282 |
| 0.30-0.50 | 503 | 0.380 | 0.344 |
| 0.50-1.00 | 152 | 0.604 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2982 | 0.013 | 0.010 |
| 0.02-0.05 | 4659 | 0.034 | 0.032 |
| 0.05-0.10 | 3851 | 0.072 | 0.077 |
| 0.10-0.20 | 2598 | 0.140 | 0.149 |
| 0.20-0.30 | 844 | 0.243 | 0.275 |
| 0.30-0.50 | 547 | 0.376 | 0.329 |
| 0.50-1.00 | 232 | 0.611 | 0.487 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
