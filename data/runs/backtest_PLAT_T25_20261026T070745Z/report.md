# Backtest — plat, hippodromes français

Généré le 2026-10-26T07:07:45+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `764511572a31`

Courses chargées : 27874 · courses évaluées (cotes complètes à l'horizon) : 24346 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6704 | 1.4364 | 0.0491 | 161764 |
| uniform | 6704 | 0.7012 | 0.0240 | 38553 |
| horse_win_rate | 6704 | 0.7847 | 0.0268 | 48274 |
| form | 6704 | 0.6713 | 0.0230 | 35336 |
| market | 6704 | 0.0551 | 0.0019 | 238 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6704 | 2.0930 | 0.8384 | 0.269 | 0.471 | 0.0067 |
| market | 6704 | 2.0943 | 0.8376 | 0.269 | 0.471 | 0.0066 |
| form | 6704 | 2.2725 | 0.8810 | 0.184 | 0.385 | 0.0069 |
| uniform | 6704 | 2.3687 | 0.9005 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6704 | 2.3929 | 0.9016 | 0.133 | 0.320 | 0.0133 |
| random | 6704 | 2.9341 | 0.9839 | 0.094 | 0.280 | 0.0610 |

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
| random | 6704 | 0.8410 | [0.8081 ; 0.8770] | 0.0002 | oui | moins bon que la référence |
| uniform | 6704 | 0.2756 | [0.2587 ; 0.2921] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6704 | 0.2999 | [0.2815 ; 0.3188] | 0.0002 | oui | moins bon que la référence |
| form | 6704 | 0.1795 | [0.1631 ; 0.1973] | 0.0002 | oui | moins bon que la référence |
| market | 6704 | 0.0012 | [-0.0000 ; 0.0025] | 0.0450 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3022 | 0.016 | 0.011 |
| 0.02-0.05 | 22639 | 0.036 | 0.029 |
| 0.05-0.10 | 28384 | 0.072 | 0.074 |
| 0.10-0.20 | 15576 | 0.136 | 0.147 |
| 0.20-0.30 | 3289 | 0.239 | 0.255 |
| 0.30-0.50 | 1533 | 0.380 | 0.358 |
| 0.50-1.00 | 477 | 0.606 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4517 | 0.015 | 0.010 |
| 0.02-0.05 | 22849 | 0.035 | 0.031 |
| 0.05-0.10 | 26869 | 0.072 | 0.075 |
| 0.10-0.20 | 14853 | 0.137 | 0.145 |
| 0.20-0.30 | 3507 | 0.239 | 0.248 |
| 0.30-0.50 | 1684 | 0.377 | 0.333 |
| 0.50-1.00 | 641 | 0.614 | 0.510 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.085** (48 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
