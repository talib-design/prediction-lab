# Backtest — trot attelé, hippodromes français

Généré le 2026-10-31T09:36:20+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `833dcd3c9a76`

Courses chargées : 41288 · courses évaluées (cotes complètes à l'horizon) : 27304 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7596 | 1.5505 | 0.0498 | 188478 |
| uniform | 7596 | 0.9132 | 0.0293 | 65377 |
| horse_win_rate | 7596 | 0.8973 | 0.0288 | 63125 |
| form | 7596 | 0.9200 | 0.0296 | 66354 |
| market | 7596 | 0.1109 | 0.0036 | 965 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7596 | 1.9755 | 0.8089 | 0.329 | 0.530 | 0.0071 |
| market | 7596 | 1.9813 | 0.8071 | 0.329 | 0.530 | 0.0091 |
| horse_win_rate | 7596 | 2.4118 | 0.8934 | 0.192 | 0.376 | 0.0083 |
| form | 7596 | 2.4536 | 0.9024 | 0.167 | 0.356 | 0.0103 |
| uniform | 7596 | 2.5189 | 0.9168 | 0.059 | 0.231 | 0.0000 |
| random | 7596 | 3.0495 | 0.9855 | 0.084 | 0.256 | 0.0524 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 17630 | 2.0066 | 0.8124 | 0.317 | 0.518 | 0.0082 |
| market | 17630 | 2.0136 | 0.8109 | 0.317 | 0.518 | 0.0091 |
| horse_win_rate | 17630 | 2.4315 | 0.8942 | 0.191 | 0.375 | 0.0103 |
| form | 17630 | 2.4846 | 0.9048 | 0.169 | 0.350 | 0.0117 |
| uniform | 17630 | 2.5384 | 0.9185 | 0.061 | 0.231 | 0.0000 |
| random | 17630 | 3.0627 | 0.9849 | 0.082 | 0.254 | 0.0503 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 2078 | 2.0213 | 0.8176 | 0.310 | 0.514 | 0.0080 |
| market | 2078 | 2.0236 | 0.8143 | 0.310 | 0.514 | 0.0095 |
| horse_win_rate | 2078 | 2.4804 | 0.9032 | 0.180 | 0.365 | 0.0109 |
| form | 2078 | 2.4905 | 0.9085 | 0.164 | 0.347 | 0.0117 |
| uniform | 2078 | 2.5535 | 0.9204 | 0.068 | 0.238 | 0.0000 |
| random | 2078 | 3.1166 | 0.9889 | 0.083 | 0.252 | 0.0500 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 7596 | 1.0740 | [1.0402 ; 1.1101] | 0.0002 | oui | moins bon que la référence |
| uniform | 7596 | 0.5434 | [0.5246 ; 0.5633] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7596 | 0.4363 | [0.4169 ; 0.4570] | 0.0002 | oui | moins bon que la référence |
| form | 7596 | 0.4781 | [0.4574 ; 0.4982] | 0.0002 | oui | moins bon que la référence |
| market | 7596 | 0.0058 | [0.0036 ; 0.0080] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 18995 | 0.013 | 0.005 |
| 0.02-0.05 | 30869 | 0.034 | 0.027 |
| 0.05-0.10 | 24121 | 0.072 | 0.071 |
| 0.10-0.20 | 14547 | 0.139 | 0.161 |
| 0.20-0.30 | 4357 | 0.241 | 0.263 |
| 0.30-0.50 | 2750 | 0.379 | 0.388 |
| 0.50-1.00 | 761 | 0.595 | 0.529 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 25265 | 0.011 | 0.008 |
| 0.02-0.05 | 28198 | 0.033 | 0.033 |
| 0.05-0.10 | 21129 | 0.071 | 0.075 |
| 0.10-0.20 | 12995 | 0.140 | 0.160 |
| 0.20-0.30 | 4433 | 0.242 | 0.240 |
| 0.30-0.50 | 3086 | 0.380 | 0.362 |
| 0.50-1.00 | 1294 | 0.614 | 0.486 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.138** (54 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
