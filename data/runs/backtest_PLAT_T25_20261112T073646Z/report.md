# Backtest — plat, hippodromes français

Généré le 2026-11-12T07:36:46+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `b2680d220a40`

Courses chargées : 28111 · courses évaluées (cotes complètes à l'horizon) : 24579 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6937 | 1.4332 | 0.0482 | 161037 |
| uniform | 6937 | 0.7002 | 0.0235 | 38440 |
| horse_win_rate | 6937 | 0.7837 | 0.0263 | 48152 |
| form | 6937 | 0.6701 | 0.0225 | 35203 |
| market | 6937 | 0.0549 | 0.0018 | 237 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6937 | 2.0909 | 0.8379 | 0.270 | 0.471 | 0.0067 |
| market | 6937 | 2.0923 | 0.8372 | 0.270 | 0.471 | 0.0066 |
| form | 6937 | 2.2714 | 0.8808 | 0.185 | 0.386 | 0.0069 |
| uniform | 6937 | 2.3681 | 0.9005 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6937 | 2.3921 | 0.9014 | 0.132 | 0.320 | 0.0134 |
| random | 6937 | 2.9293 | 0.9833 | 0.095 | 0.281 | 0.0608 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 15732 | 2.0776 | 0.8362 | 0.268 | 0.471 | 0.0060 |
| market | 15732 | 2.0791 | 0.8356 | 0.268 | 0.471 | 0.0065 |
| form | 15732 | 2.2571 | 0.8791 | 0.186 | 0.390 | 0.0067 |
| uniform | 15732 | 2.3486 | 0.8982 | 0.139 | 0.334 | 0.0000 |
| horse_win_rate | 15732 | 2.3858 | 0.9018 | 0.135 | 0.325 | 0.0164 |
| random | 15732 | 2.8617 | 0.9773 | 0.104 | 0.292 | 0.0592 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1910 | 2.0840 | 0.8344 | 0.266 | 0.468 | 0.0066 |
| market | 1910 | 2.0858 | 0.8339 | 0.266 | 0.468 | 0.0074 |
| form | 1910 | 2.2750 | 0.8814 | 0.182 | 0.383 | 0.0084 |
| uniform | 1910 | 2.3594 | 0.8980 | 0.145 | 0.341 | 0.0000 |
| horse_win_rate | 1910 | 2.3986 | 0.9010 | 0.131 | 0.320 | 0.0154 |
| random | 1910 | 2.8979 | 0.9751 | 0.106 | 0.289 | 0.0593 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 6937 | 0.8384 | [0.8042 ; 0.8737] | 0.0002 | oui | moins bon que la référence |
| uniform | 6937 | 0.2771 | [0.2602 ; 0.2938] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6937 | 0.3011 | [0.2828 ; 0.3196] | 0.0002 | oui | moins bon que la référence |
| form | 6937 | 0.1804 | [0.1652 ; 0.1977] | 0.0002 | oui | moins bon que la référence |
| market | 6937 | 0.0014 | [0.0000 ; 0.0026] | 0.0298 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3151 | 0.016 | 0.010 |
| 0.02-0.05 | 23397 | 0.036 | 0.029 |
| 0.05-0.10 | 29301 | 0.072 | 0.074 |
| 0.10-0.20 | 16135 | 0.136 | 0.147 |
| 0.20-0.30 | 3419 | 0.239 | 0.255 |
| 0.30-0.50 | 1585 | 0.379 | 0.360 |
| 0.50-1.00 | 495 | 0.606 | 0.525 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4705 | 0.015 | 0.010 |
| 0.02-0.05 | 23596 | 0.035 | 0.031 |
| 0.05-0.10 | 27747 | 0.072 | 0.075 |
| 0.10-0.20 | 15387 | 0.137 | 0.145 |
| 0.20-0.30 | 3643 | 0.239 | 0.247 |
| 0.30-0.50 | 1743 | 0.377 | 0.335 |
| 0.50-1.00 | 662 | 0.614 | 0.511 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.086** (49 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
