# Backtest — trot attelé, hippodromes français

Généré le 2026-11-04T07:07:10+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `ad878497e48e`

Courses chargées : 41424 · courses évaluées (cotes complètes à l'horizon) : 27374 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7666 | 1.5502 | 0.0496 | 188405 |
| uniform | 7666 | 0.9139 | 0.0292 | 65481 |
| horse_win_rate | 7666 | 0.8975 | 0.0287 | 63156 |
| form | 7666 | 0.9207 | 0.0294 | 66453 |
| market | 7666 | 0.1110 | 0.0035 | 966 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7666 | 1.9769 | 0.8091 | 0.328 | 0.530 | 0.0071 |
| market | 7666 | 1.9825 | 0.8072 | 0.328 | 0.530 | 0.0091 |
| horse_win_rate | 7666 | 2.4122 | 0.8934 | 0.191 | 0.375 | 0.0084 |
| form | 7666 | 2.4547 | 0.9025 | 0.167 | 0.355 | 0.0103 |
| uniform | 7666 | 2.5197 | 0.9168 | 0.059 | 0.230 | 0.0000 |
| random | 7666 | 3.0508 | 0.9857 | 0.084 | 0.255 | 0.0524 |

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
| random | 7666 | 1.0739 | [1.0402 ; 1.1078] | 0.0002 | oui | moins bon que la référence |
| uniform | 7666 | 0.5428 | [0.5228 ; 0.5618] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7666 | 0.4354 | [0.4160 ; 0.4544] | 0.0002 | oui | moins bon que la référence |
| form | 7666 | 0.4778 | [0.4566 ; 0.4979] | 0.0002 | oui | moins bon que la référence |
| market | 7666 | 0.0057 | [0.0034 ; 0.0079] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 19222 | 0.013 | 0.006 |
| 0.02-0.05 | 31159 | 0.034 | 0.027 |
| 0.05-0.10 | 24371 | 0.072 | 0.070 |
| 0.10-0.20 | 14674 | 0.139 | 0.161 |
| 0.20-0.30 | 4394 | 0.241 | 0.262 |
| 0.30-0.50 | 2770 | 0.379 | 0.388 |
| 0.50-1.00 | 770 | 0.595 | 0.528 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 25548 | 0.011 | 0.008 |
| 0.02-0.05 | 28459 | 0.033 | 0.033 |
| 0.05-0.10 | 21356 | 0.071 | 0.075 |
| 0.10-0.20 | 13110 | 0.140 | 0.160 |
| 0.20-0.30 | 4470 | 0.242 | 0.239 |
| 0.30-0.50 | 3111 | 0.380 | 0.361 |
| 0.50-1.00 | 1306 | 0.614 | 0.486 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.138** (54 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
