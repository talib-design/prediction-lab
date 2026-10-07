# Backtest — trot attelé, hippodromes français

Généré le 2026-10-07T04:35:19+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `83ce80d4b2be`

Courses chargées : 17606 · courses évaluées (cotes complètes à l'horizon) : 11421 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7322 | 1.5426 | 0.0505 | 186571 |
| uniform | 7322 | 0.8977 | 0.0294 | 63187 |
| horse_win_rate | 7322 | 0.9058 | 0.0296 | 64324 |
| form | 7322 | 0.9076 | 0.0297 | 64584 |
| market | 7322 | 0.0948 | 0.0031 | 705 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7322 | 1.9730 | 0.8079 | 0.330 | 0.531 | 0.0072 |
| market | 7322 | 1.9788 | 0.8066 | 0.330 | 0.531 | 0.0091 |
| horse_win_rate | 7322 | 2.4171 | 0.8937 | 0.189 | 0.376 | 0.0115 |
| form | 7322 | 2.4503 | 0.9021 | 0.167 | 0.356 | 0.0105 |
| uniform | 7322 | 2.5164 | 0.9166 | 0.059 | 0.231 | 0.0000 |
| random | 7322 | 3.0474 | 0.9854 | 0.085 | 0.257 | 0.0526 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 2021 | 2.0445 | 0.8192 | 0.300 | 0.506 | 0.0084 |
| market | 2021 | 2.0495 | 0.8183 | 0.300 | 0.506 | 0.0088 |
| horse_win_rate | 2021 | 2.4988 | 0.9052 | 0.168 | 0.335 | 0.0103 |
| form | 2021 | 2.5561 | 0.9148 | 0.148 | 0.326 | 0.0141 |
| uniform | 2021 | 2.5612 | 0.9206 | 0.069 | 0.236 | 0.0000 |
| random | 2021 | 3.0649 | 0.9820 | 0.089 | 0.257 | 0.0484 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 2078 | 2.0207 | 0.8168 | 0.310 | 0.514 | 0.0087 |
| market | 2078 | 2.0236 | 0.8143 | 0.310 | 0.514 | 0.0095 |
| horse_win_rate | 2078 | 2.4849 | 0.9040 | 0.172 | 0.357 | 0.0144 |
| form | 2078 | 2.4944 | 0.9084 | 0.165 | 0.346 | 0.0120 |
| uniform | 2078 | 2.5535 | 0.9204 | 0.068 | 0.238 | 0.0000 |
| random | 2078 | 3.1166 | 0.9889 | 0.083 | 0.252 | 0.0500 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 7322 | 1.0744 | [1.0395 ; 1.1075] | 0.0002 | oui | moins bon que la référence |
| uniform | 7322 | 0.5435 | [0.5245 ; 0.5636] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7322 | 0.4441 | [0.4238 ; 0.4648] | 0.0002 | oui | moins bon que la référence |
| form | 7322 | 0.4773 | [0.4562 ; 0.4977] | 0.0002 | oui | moins bon que la référence |
| market | 7322 | 0.0058 | [0.0039 ; 0.0079] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 18143 | 0.013 | 0.006 |
| 0.02-0.05 | 29728 | 0.034 | 0.027 |
| 0.05-0.10 | 23223 | 0.072 | 0.071 |
| 0.10-0.20 | 14018 | 0.139 | 0.161 |
| 0.20-0.30 | 4198 | 0.241 | 0.263 |
| 0.30-0.50 | 2654 | 0.379 | 0.389 |
| 0.50-1.00 | 738 | 0.596 | 0.528 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 23259 | 0.011 | 0.007 |
| 0.02-0.05 | 27606 | 0.033 | 0.031 |
| 0.05-0.10 | 20720 | 0.072 | 0.076 |
| 0.10-0.20 | 12743 | 0.140 | 0.159 |
| 0.20-0.30 | 4264 | 0.242 | 0.241 |
| 0.30-0.50 | 2915 | 0.380 | 0.367 |
| 0.50-1.00 | 1195 | 0.610 | 0.493 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.122** (22 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
