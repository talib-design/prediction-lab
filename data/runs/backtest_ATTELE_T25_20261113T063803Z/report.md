# Backtest — trot attelé, hippodromes français

Généré le 2026-11-13T06:38:03+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `f9381e809f43`

Courses chargées : 41579 · courses évaluées (cotes complètes à l'horizon) : 27475 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7767 | 1.5485 | 0.0492 | 187983 |
| uniform | 7767 | 0.9134 | 0.0290 | 65416 |
| horse_win_rate | 7767 | 0.8981 | 0.0285 | 63232 |
| form | 7767 | 0.9198 | 0.0292 | 66333 |
| market | 7767 | 0.1109 | 0.0035 | 965 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7767 | 1.9782 | 0.8097 | 0.327 | 0.529 | 0.0072 |
| market | 7767 | 1.9838 | 0.8077 | 0.327 | 0.529 | 0.0091 |
| horse_win_rate | 7767 | 2.4150 | 0.8938 | 0.190 | 0.374 | 0.0085 |
| form | 7767 | 2.4562 | 0.9028 | 0.166 | 0.354 | 0.0104 |
| uniform | 7767 | 2.5209 | 0.9169 | 0.058 | 0.230 | 0.0000 |
| random | 7767 | 3.0512 | 0.9857 | 0.084 | 0.255 | 0.0522 |

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
| random | 7767 | 1.0729 | [1.0398 ; 1.1046] | 0.0002 | oui | moins bon que la référence |
| uniform | 7767 | 0.5427 | [0.5241 ; 0.5604] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7767 | 0.4368 | [0.4179 ; 0.4556] | 0.0002 | oui | moins bon que la référence |
| form | 7767 | 0.4780 | [0.4577 ; 0.4959] | 0.0002 | oui | moins bon que la référence |
| market | 7767 | 0.0056 | [0.0035 ; 0.0077] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 19572 | 0.013 | 0.006 |
| 0.02-0.05 | 31594 | 0.034 | 0.027 |
| 0.05-0.10 | 24669 | 0.072 | 0.071 |
| 0.10-0.20 | 14883 | 0.139 | 0.161 |
| 0.20-0.30 | 4454 | 0.241 | 0.262 |
| 0.30-0.50 | 2807 | 0.379 | 0.386 |
| 0.50-1.00 | 778 | 0.595 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 26003 | 0.011 | 0.008 |
| 0.02-0.05 | 28842 | 0.033 | 0.033 |
| 0.05-0.10 | 21612 | 0.071 | 0.075 |
| 0.10-0.20 | 13297 | 0.140 | 0.160 |
| 0.20-0.30 | 4530 | 0.242 | 0.239 |
| 0.30-0.50 | 3152 | 0.380 | 0.361 |
| 0.50-1.00 | 1321 | 0.614 | 0.483 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.138** (54 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
