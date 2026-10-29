# Backtest — trot attelé, hippodromes français

Généré le 2026-10-29T06:45:59+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `06084bab4386`

Courses chargées : 41262 · courses évaluées (cotes complètes à l'horizon) : 27278 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7570 | 1.5508 | 0.0499 | 188542 |
| uniform | 7570 | 0.9127 | 0.0294 | 65307 |
| horse_win_rate | 7570 | 0.8964 | 0.0288 | 62992 |
| form | 7570 | 0.9193 | 0.0296 | 66261 |
| market | 7570 | 0.1109 | 0.0036 | 965 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7570 | 1.9750 | 0.8090 | 0.329 | 0.530 | 0.0072 |
| market | 7570 | 1.9808 | 0.8071 | 0.329 | 0.530 | 0.0092 |
| horse_win_rate | 7570 | 2.4109 | 0.8933 | 0.192 | 0.376 | 0.0083 |
| form | 7570 | 2.4529 | 0.9023 | 0.168 | 0.356 | 0.0102 |
| uniform | 7570 | 2.5186 | 0.9168 | 0.059 | 0.231 | 0.0000 |
| random | 7570 | 3.0497 | 0.9856 | 0.084 | 0.256 | 0.0524 |

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
| random | 7570 | 1.0748 | [1.0427 ; 1.1082] | 0.0002 | oui | moins bon que la référence |
| uniform | 7570 | 0.5436 | [0.5237 ; 0.5634] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7570 | 0.4360 | [0.4172 ; 0.4559] | 0.0002 | oui | moins bon que la référence |
| form | 7570 | 0.4779 | [0.4569 ; 0.4986] | 0.0002 | oui | moins bon que la référence |
| market | 7570 | 0.0058 | [0.0034 ; 0.0083] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 18917 | 0.013 | 0.005 |
| 0.02-0.05 | 30744 | 0.034 | 0.027 |
| 0.05-0.10 | 24034 | 0.072 | 0.071 |
| 0.10-0.20 | 14497 | 0.139 | 0.161 |
| 0.20-0.30 | 4342 | 0.241 | 0.263 |
| 0.30-0.50 | 2742 | 0.379 | 0.387 |
| 0.50-1.00 | 759 | 0.595 | 0.528 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 25160 | 0.011 | 0.008 |
| 0.02-0.05 | 28088 | 0.033 | 0.033 |
| 0.05-0.10 | 21054 | 0.071 | 0.075 |
| 0.10-0.20 | 12948 | 0.140 | 0.160 |
| 0.20-0.30 | 4418 | 0.242 | 0.240 |
| 0.30-0.50 | 3076 | 0.380 | 0.361 |
| 0.50-1.00 | 1291 | 0.614 | 0.486 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.138** (54 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
