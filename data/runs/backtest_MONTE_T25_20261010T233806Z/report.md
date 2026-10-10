# Backtest — trot monté, hippodromes français

Généré le 2026-10-10T23:38:06+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `a943760470cc`

Courses chargées : 4310 · courses évaluées (cotes complètes à l'horizon) : 3270 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1371 | 1.5454 | 0.1169 | 187239 |
| uniform | 1371 | 0.8734 | 0.0660 | 59802 |
| horse_win_rate | 1371 | 0.8377 | 0.0633 | 55013 |
| form | 1371 | 0.8647 | 0.0654 | 58617 |
| market | 1371 | 0.0808 | 0.0061 | 512 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1371 | 1.9556 | 0.8099 | 0.332 | 0.533 | 0.0092 |
| market | 1371 | 1.9565 | 0.8078 | 0.332 | 0.533 | 0.0103 |
| horse_win_rate | 1371 | 2.3029 | 0.8828 | 0.190 | 0.386 | 0.0082 |
| form | 1371 | 2.3886 | 0.8981 | 0.182 | 0.367 | 0.0176 |
| uniform | 1371 | 2.4012 | 0.9056 | 0.051 | 0.215 | 0.0000 |
| random | 1371 | 2.9413 | 0.9820 | 0.089 | 0.275 | 0.0615 |

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
| random | 1371 | 0.9858 | [0.9093 ; 1.0631] | 0.0002 | oui | moins bon que la référence |
| uniform | 1371 | 0.4456 | [0.4038 ; 0.4857] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1371 | 0.3473 | [0.3054 ; 0.3888] | 0.0002 | oui | moins bon que la référence |
| form | 1371 | 0.4331 | [0.3853 ; 0.4755] | 0.0002 | oui | moins bon que la référence |
| market | 1371 | 0.0009 | [-0.0029 ; 0.0045] | 0.6623 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2222 | 0.014 | 0.009 |
| 0.02-0.05 | 4847 | 0.034 | 0.028 |
| 0.05-0.10 | 4174 | 0.073 | 0.070 |
| 0.10-0.20 | 2781 | 0.140 | 0.156 |
| 0.20-0.30 | 836 | 0.243 | 0.282 |
| 0.30-0.50 | 498 | 0.380 | 0.343 |
| 0.50-1.00 | 149 | 0.602 | 0.523 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2929 | 0.013 | 0.010 |
| 0.02-0.05 | 4600 | 0.034 | 0.032 |
| 0.05-0.10 | 3810 | 0.072 | 0.077 |
| 0.10-0.20 | 2558 | 0.140 | 0.149 |
| 0.20-0.30 | 840 | 0.243 | 0.276 |
| 0.30-0.50 | 543 | 0.376 | 0.326 |
| 0.50-1.00 | 227 | 0.611 | 0.489 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
