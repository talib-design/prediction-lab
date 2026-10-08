# Backtest — plat, hippodromes français

Généré le 2026-10-08T04:33:51+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `7c8e3c80710b`

Courses chargées : 27635 · courses évaluées (cotes complètes à l'horizon) : 24120 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6478 | 1.4364 | 0.0500 | 161754 |
| uniform | 6478 | 0.7016 | 0.0244 | 38590 |
| horse_win_rate | 6478 | 0.7846 | 0.0273 | 48258 |
| form | 6478 | 0.6736 | 0.0234 | 35576 |
| market | 6478 | 0.0552 | 0.0019 | 239 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6478 | 2.0949 | 0.8388 | 0.270 | 0.471 | 0.0069 |
| market | 6478 | 2.0961 | 0.8381 | 0.270 | 0.471 | 0.0067 |
| form | 6478 | 2.2747 | 0.8815 | 0.184 | 0.385 | 0.0069 |
| uniform | 6478 | 2.3704 | 0.9006 | 0.129 | 0.322 | 0.0000 |
| horse_win_rate | 6478 | 2.3952 | 0.9020 | 0.132 | 0.320 | 0.0134 |
| random | 6478 | 2.9374 | 0.9844 | 0.093 | 0.279 | 0.0609 |

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
| random | 6478 | 0.8425 | [0.8077 ; 0.8773] | 0.0002 | oui | moins bon que la référence |
| uniform | 6478 | 0.2755 | [0.2578 ; 0.2933] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6478 | 0.3003 | [0.2806 ; 0.3193] | 0.0002 | oui | moins bon que la référence |
| form | 6478 | 0.1798 | [0.1635 ; 0.1973] | 0.0002 | oui | moins bon que la référence |
| market | 6478 | 0.0013 | [-0.0001 ; 0.0027] | 0.0548 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2916 | 0.016 | 0.011 |
| 0.02-0.05 | 21932 | 0.036 | 0.029 |
| 0.05-0.10 | 27489 | 0.072 | 0.074 |
| 0.10-0.20 | 15059 | 0.136 | 0.147 |
| 0.20-0.30 | 3174 | 0.239 | 0.257 |
| 0.30-0.50 | 1473 | 0.380 | 0.356 |
| 0.50-1.00 | 457 | 0.607 | 0.527 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4364 | 0.015 | 0.011 |
| 0.02-0.05 | 22137 | 0.035 | 0.031 |
| 0.05-0.10 | 26022 | 0.072 | 0.076 |
| 0.10-0.20 | 14353 | 0.137 | 0.145 |
| 0.20-0.30 | 3388 | 0.238 | 0.250 |
| 0.30-0.50 | 1619 | 0.377 | 0.331 |
| 0.50-1.00 | 617 | 0.613 | 0.507 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.085** (48 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
