# Backtest — plat, hippodromes français

Généré le 2026-10-05T10:25:04+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `3a70b939c4cc`

Courses chargées : 12371 · courses évaluées (cotes complètes à l'horizon) : 10923 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 6438 | 1.4326 | 0.0500 | 160899 |
| uniform | 6438 | 0.6969 | 0.0243 | 38082 |
| horse_win_rate | 6438 | 0.8129 | 0.0284 | 51804 |
| form | 6438 | 0.6704 | 0.0234 | 35236 |
| market | 6438 | 0.0506 | 0.0018 | 201 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6438 | 2.0962 | 0.8389 | 0.269 | 0.470 | 0.0069 |
| market | 6438 | 2.0974 | 0.8382 | 0.269 | 0.470 | 0.0067 |
| form | 6438 | 2.2769 | 0.8819 | 0.183 | 0.384 | 0.0071 |
| uniform | 6438 | 2.3712 | 0.9007 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 6438 | 2.4250 | 0.9066 | 0.128 | 0.314 | 0.0173 |
| random | 6438 | 2.9366 | 0.9843 | 0.093 | 0.279 | 0.0609 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 2575 | 2.1175 | 0.8401 | 0.256 | 0.458 | 0.0054 |
| market | 2575 | 2.1180 | 0.8397 | 0.256 | 0.458 | 0.0056 |
| form | 2575 | 2.3512 | 0.8958 | 0.152 | 0.353 | 0.0130 |
| uniform | 2575 | 2.3733 | 0.8996 | 0.128 | 0.321 | 0.0000 |
| horse_win_rate | 2575 | 2.4185 | 0.9064 | 0.135 | 0.320 | 0.0163 |
| random | 2575 | 2.8812 | 0.9797 | 0.096 | 0.282 | 0.0590 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1910 | 2.0841 | 0.8342 | 0.266 | 0.468 | 0.0064 |
| market | 1910 | 2.0858 | 0.8339 | 0.266 | 0.468 | 0.0074 |
| form | 1910 | 2.2788 | 0.8819 | 0.182 | 0.384 | 0.0085 |
| uniform | 1910 | 2.3594 | 0.8980 | 0.145 | 0.341 | 0.0000 |
| horse_win_rate | 1910 | 2.4295 | 0.9081 | 0.118 | 0.310 | 0.0242 |
| random | 1910 | 2.8979 | 0.9751 | 0.106 | 0.289 | 0.0593 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 6438 | 0.8404 | [0.8070 ; 0.8780] | 0.0002 | oui | moins bon que la référence |
| uniform | 6438 | 0.2750 | [0.2582 ; 0.2934] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 6438 | 0.3289 | [0.3105 ; 0.3491] | 0.0002 | oui | moins bon que la référence |
| form | 6438 | 0.1807 | [0.1639 ; 0.1985] | 0.0002 | oui | moins bon que la référence |
| market | 6438 | 0.0012 | [0.0000 ; 0.0025] | 0.0444 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2908 | 0.016 | 0.011 |
| 0.02-0.05 | 21823 | 0.036 | 0.029 |
| 0.05-0.10 | 27346 | 0.072 | 0.074 |
| 0.10-0.20 | 14967 | 0.136 | 0.146 |
| 0.20-0.30 | 3152 | 0.239 | 0.256 |
| 0.30-0.50 | 1456 | 0.380 | 0.355 |
| 0.50-1.00 | 456 | 0.606 | 0.529 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4226 | 0.015 | 0.011 |
| 0.02-0.05 | 21891 | 0.035 | 0.031 |
| 0.05-0.10 | 26114 | 0.072 | 0.075 |
| 0.10-0.20 | 14326 | 0.137 | 0.145 |
| 0.20-0.30 | 3355 | 0.238 | 0.251 |
| 0.30-0.50 | 1601 | 0.377 | 0.333 |
| 0.50-1.00 | 595 | 0.614 | 0.513 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.082** (21 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
