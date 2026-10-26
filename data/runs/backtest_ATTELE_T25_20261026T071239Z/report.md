# Backtest — trot attelé, hippodromes français

Généré le 2026-10-26T07:12:39+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `76c15b4a7a58`

Courses chargées : 41226 · courses évaluées (cotes complètes à l'horizon) : 27250 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7542 | 1.5501 | 0.0500 | 188379 |
| uniform | 7542 | 0.9129 | 0.0294 | 65336 |
| horse_win_rate | 7542 | 0.8958 | 0.0289 | 62913 |
| form | 7542 | 0.9188 | 0.0296 | 66180 |
| market | 7542 | 0.1109 | 0.0036 | 965 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7542 | 1.9745 | 0.8088 | 0.329 | 0.530 | 0.0072 |
| market | 7542 | 1.9803 | 0.8069 | 0.329 | 0.530 | 0.0092 |
| horse_win_rate | 7542 | 2.4110 | 0.8932 | 0.192 | 0.376 | 0.0084 |
| form | 7542 | 2.4524 | 0.9022 | 0.168 | 0.356 | 0.0103 |
| uniform | 7542 | 2.5183 | 0.9168 | 0.058 | 0.231 | 0.0000 |
| random | 7542 | 3.0493 | 0.9856 | 0.084 | 0.256 | 0.0524 |

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
| random | 7542 | 1.0748 | [1.0408 ; 1.1107] | 0.0002 | oui | moins bon que la référence |
| uniform | 7542 | 0.5438 | [0.5237 ; 0.5639] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7542 | 0.4365 | [0.4173 ; 0.4568] | 0.0002 | oui | moins bon que la référence |
| form | 7542 | 0.4780 | [0.4565 ; 0.4998] | 0.0002 | oui | moins bon que la référence |
| market | 7542 | 0.0058 | [0.0034 ; 0.0082] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 18821 | 0.013 | 0.005 |
| 0.02-0.05 | 30625 | 0.034 | 0.027 |
| 0.05-0.10 | 23949 | 0.072 | 0.071 |
| 0.10-0.20 | 14446 | 0.139 | 0.161 |
| 0.20-0.30 | 4325 | 0.241 | 0.263 |
| 0.30-0.50 | 2728 | 0.379 | 0.388 |
| 0.50-1.00 | 759 | 0.595 | 0.528 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 25036 | 0.011 | 0.008 |
| 0.02-0.05 | 27987 | 0.033 | 0.033 |
| 0.05-0.10 | 20976 | 0.071 | 0.076 |
| 0.10-0.20 | 12903 | 0.140 | 0.160 |
| 0.20-0.30 | 4404 | 0.242 | 0.240 |
| 0.30-0.50 | 3059 | 0.380 | 0.362 |
| 0.50-1.00 | 1288 | 0.614 | 0.486 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.138** (54 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
