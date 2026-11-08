# Backtest — plat, hippodromes français

Généré le 2026-11-08T00:37:24+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `43d9d983e3ae`

Courses chargées : 28045 · courses évaluées (cotes complètes à l'horizon) : 24516 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6874 | 1.4324 | 0.0484 | 160852 |
| uniform | 6874 | 0.7001 | 0.0236 | 38429 |
| horse_win_rate | 6874 | 0.7834 | 0.0265 | 48120 |
| form | 6874 | 0.6699 | 0.0226 | 35180 |
| market | 6874 | 0.0550 | 0.0019 | 237 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6874 | 2.0907 | 0.8379 | 0.270 | 0.471 | 0.0066 |
| market | 6874 | 2.0921 | 0.8372 | 0.270 | 0.471 | 0.0066 |
| form | 6874 | 2.2710 | 0.8806 | 0.185 | 0.386 | 0.0067 |
| uniform | 6874 | 2.3680 | 0.9004 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6874 | 2.3920 | 0.9013 | 0.132 | 0.320 | 0.0132 |
| random | 6874 | 2.9296 | 0.9832 | 0.095 | 0.280 | 0.0609 |

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
| random | 6874 | 0.8389 | [0.8041 ; 0.8739] | 0.0002 | oui | moins bon que la référence |
| uniform | 6874 | 0.2772 | [0.2600 ; 0.2944] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6874 | 0.3012 | [0.2822 ; 0.3206] | 0.0002 | oui | moins bon que la référence |
| form | 6874 | 0.1802 | [0.1642 ; 0.1983] | 0.0002 | oui | moins bon que la référence |
| market | 6874 | 0.0014 | [0.0001 ; 0.0027] | 0.0328 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3118 | 0.016 | 0.011 |
| 0.02-0.05 | 23188 | 0.036 | 0.029 |
| 0.05-0.10 | 29035 | 0.072 | 0.073 |
| 0.10-0.20 | 15993 | 0.136 | 0.147 |
| 0.20-0.30 | 3385 | 0.239 | 0.254 |
| 0.30-0.50 | 1569 | 0.380 | 0.362 |
| 0.50-1.00 | 490 | 0.606 | 0.522 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4652 | 0.015 | 0.010 |
| 0.02-0.05 | 23394 | 0.035 | 0.031 |
| 0.05-0.10 | 27493 | 0.072 | 0.075 |
| 0.10-0.20 | 15252 | 0.137 | 0.146 |
| 0.20-0.30 | 3606 | 0.239 | 0.247 |
| 0.30-0.50 | 1724 | 0.377 | 0.337 |
| 0.50-1.00 | 657 | 0.613 | 0.508 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.086** (49 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
