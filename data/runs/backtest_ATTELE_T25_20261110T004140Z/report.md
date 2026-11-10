# Backtest — trot attelé, hippodromes français

Généré le 2026-11-10T00:41:40+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `51a06f6a368e`

Courses chargées : 41518 · courses évaluées (cotes complètes à l'horizon) : 27436 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7728 | 1.5486 | 0.0493 | 188024 |
| uniform | 7728 | 0.9134 | 0.0291 | 65403 |
| horse_win_rate | 7728 | 0.8980 | 0.0286 | 63227 |
| form | 7728 | 0.9204 | 0.0293 | 66419 |
| market | 7728 | 0.1109 | 0.0035 | 965 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7728 | 1.9773 | 0.8096 | 0.328 | 0.530 | 0.0072 |
| market | 7728 | 1.9829 | 0.8076 | 0.328 | 0.530 | 0.0092 |
| horse_win_rate | 7728 | 2.4143 | 0.8937 | 0.190 | 0.374 | 0.0084 |
| form | 7728 | 2.4557 | 0.9026 | 0.167 | 0.355 | 0.0103 |
| uniform | 7728 | 2.5206 | 0.9169 | 0.058 | 0.230 | 0.0000 |
| random | 7728 | 3.0510 | 0.9857 | 0.083 | 0.255 | 0.0522 |

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
| random | 7728 | 1.0737 | [1.0423 ; 1.1065] | 0.0002 | oui | moins bon que la référence |
| uniform | 7728 | 0.5433 | [0.5235 ; 0.5618] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7728 | 0.4371 | [0.4174 ; 0.4570] | 0.0002 | oui | moins bon que la référence |
| form | 7728 | 0.4784 | [0.4581 ; 0.4979] | 0.0002 | oui | moins bon que la référence |
| market | 7728 | 0.0056 | [0.0034 ; 0.0079] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 19477 | 0.013 | 0.005 |
| 0.02-0.05 | 31418 | 0.034 | 0.027 |
| 0.05-0.10 | 24542 | 0.072 | 0.071 |
| 0.10-0.20 | 14794 | 0.139 | 0.162 |
| 0.20-0.30 | 4438 | 0.241 | 0.262 |
| 0.30-0.50 | 2795 | 0.379 | 0.387 |
| 0.50-1.00 | 774 | 0.595 | 0.525 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 25872 | 0.011 | 0.008 |
| 0.02-0.05 | 28683 | 0.033 | 0.033 |
| 0.05-0.10 | 21501 | 0.071 | 0.075 |
| 0.10-0.20 | 13216 | 0.140 | 0.161 |
| 0.20-0.30 | 4513 | 0.242 | 0.239 |
| 0.30-0.50 | 3137 | 0.380 | 0.361 |
| 0.50-1.00 | 1316 | 0.614 | 0.483 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.138** (54 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
