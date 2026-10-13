# Backtest — trot monté, hippodromes français

Généré le 2026-10-13T05:01:41+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `f230258bfefe`

Courses chargées : 4316 · courses évaluées (cotes complètes à l'horizon) : 3276 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1377 | 1.5479 | 0.1168 | 187841 |
| uniform | 1377 | 0.8740 | 0.0659 | 59884 |
| horse_win_rate | 1377 | 0.8385 | 0.0633 | 55117 |
| form | 1377 | 0.8639 | 0.0652 | 58506 |
| market | 1377 | 0.0808 | 0.0061 | 512 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1377 | 1.9533 | 0.8093 | 0.333 | 0.534 | 0.0092 |
| market | 1377 | 1.9542 | 0.8073 | 0.333 | 0.534 | 0.0102 |
| horse_win_rate | 1377 | 2.3013 | 0.8825 | 0.190 | 0.386 | 0.0082 |
| form | 1377 | 2.3872 | 0.8979 | 0.183 | 0.368 | 0.0174 |
| uniform | 1377 | 2.4012 | 0.9056 | 0.051 | 0.214 | 0.0000 |
| random | 1377 | 2.9436 | 0.9822 | 0.089 | 0.274 | 0.0616 |

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
| random | 1377 | 0.9904 | [0.9150 ; 1.0676] | 0.0002 | oui | moins bon que la référence |
| uniform | 1377 | 0.4480 | [0.4046 ; 0.4882] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1377 | 0.3480 | [0.3077 ; 0.3898] | 0.0002 | oui | moins bon que la référence |
| form | 1377 | 0.4340 | [0.3881 ; 0.4787] | 0.0002 | oui | moins bon que la référence |
| market | 1377 | 0.0010 | [-0.0028 ; 0.0046] | 0.6257 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2240 | 0.014 | 0.009 |
| 0.02-0.05 | 4866 | 0.034 | 0.028 |
| 0.05-0.10 | 4189 | 0.073 | 0.070 |
| 0.10-0.20 | 2792 | 0.140 | 0.157 |
| 0.20-0.30 | 837 | 0.243 | 0.282 |
| 0.30-0.50 | 500 | 0.380 | 0.346 |
| 0.50-1.00 | 151 | 0.604 | 0.523 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2953 | 0.013 | 0.010 |
| 0.02-0.05 | 4614 | 0.034 | 0.032 |
| 0.05-0.10 | 3825 | 0.072 | 0.077 |
| 0.10-0.20 | 2568 | 0.140 | 0.150 |
| 0.20-0.30 | 841 | 0.243 | 0.276 |
| 0.30-0.50 | 545 | 0.377 | 0.328 |
| 0.50-1.00 | 229 | 0.612 | 0.489 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
