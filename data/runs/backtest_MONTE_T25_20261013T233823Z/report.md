# Backtest — trot monté, hippodromes français

Généré le 2026-10-13T23:38:23+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `9b807113d627`

Courses chargées : 4319 · courses évaluées (cotes complètes à l'horizon) : 3279 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1380 | 1.5482 | 0.1167 | 187918 |
| uniform | 1380 | 0.8741 | 0.0659 | 59906 |
| horse_win_rate | 1380 | 0.8382 | 0.0632 | 55077 |
| form | 1380 | 0.8631 | 0.0651 | 58402 |
| market | 1380 | 0.0808 | 0.0061 | 513 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1380 | 1.9551 | 0.8098 | 0.332 | 0.533 | 0.0091 |
| market | 1380 | 1.9559 | 0.8077 | 0.332 | 0.533 | 0.0101 |
| horse_win_rate | 1380 | 2.3021 | 0.8826 | 0.190 | 0.386 | 0.0083 |
| form | 1380 | 2.3893 | 0.8982 | 0.183 | 0.367 | 0.0176 |
| uniform | 1380 | 2.4013 | 0.9056 | 0.051 | 0.214 | 0.0000 |
| random | 1380 | 2.9441 | 0.9820 | 0.089 | 0.275 | 0.0616 |

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
| random | 1380 | 0.9891 | [0.9132 ; 1.0691] | 0.0002 | oui | moins bon que la référence |
| uniform | 1380 | 0.4463 | [0.4061 ; 0.4866] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1380 | 0.3471 | [0.3069 ; 0.3893] | 0.0002 | oui | moins bon que la référence |
| form | 1380 | 0.4343 | [0.3872 ; 0.4773] | 0.0002 | oui | moins bon que la référence |
| market | 1380 | 0.0008 | [-0.0028 ; 0.0046] | 0.6775 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2247 | 0.014 | 0.009 |
| 0.02-0.05 | 4877 | 0.034 | 0.028 |
| 0.05-0.10 | 4193 | 0.073 | 0.070 |
| 0.10-0.20 | 2803 | 0.140 | 0.156 |
| 0.20-0.30 | 838 | 0.243 | 0.282 |
| 0.30-0.50 | 501 | 0.380 | 0.345 |
| 0.50-1.00 | 151 | 0.604 | 0.523 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2961 | 0.013 | 0.010 |
| 0.02-0.05 | 4626 | 0.034 | 0.032 |
| 0.05-0.10 | 3827 | 0.072 | 0.077 |
| 0.10-0.20 | 2579 | 0.140 | 0.149 |
| 0.20-0.30 | 842 | 0.243 | 0.276 |
| 0.30-0.50 | 545 | 0.377 | 0.328 |
| 0.50-1.00 | 230 | 0.612 | 0.487 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
