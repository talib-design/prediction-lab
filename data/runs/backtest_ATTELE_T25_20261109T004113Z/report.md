# Backtest — trot attelé, hippodromes français

Généré le 2026-11-09T00:41:13+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `2b0987c0cdc6`

Courses chargées : 41503 · courses évaluées (cotes complètes à l'horizon) : 27429 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7721 | 1.5486 | 0.0493 | 188013 |
| uniform | 7721 | 0.9135 | 0.0291 | 65419 |
| horse_win_rate | 7721 | 0.8982 | 0.0286 | 63249 |
| form | 7721 | 0.9207 | 0.0293 | 66458 |
| market | 7721 | 0.1109 | 0.0035 | 965 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7721 | 1.9774 | 0.8096 | 0.328 | 0.529 | 0.0072 |
| market | 7721 | 1.9830 | 0.8076 | 0.328 | 0.529 | 0.0092 |
| horse_win_rate | 7721 | 2.4140 | 0.8937 | 0.191 | 0.375 | 0.0084 |
| form | 7721 | 2.4557 | 0.9027 | 0.167 | 0.355 | 0.0104 |
| uniform | 7721 | 2.5205 | 0.9169 | 0.058 | 0.230 | 0.0000 |
| random | 7721 | 3.0512 | 0.9858 | 0.083 | 0.255 | 0.0523 |

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
| random | 7721 | 1.0738 | [1.0411 ; 1.1067] | 0.0002 | oui | moins bon que la référence |
| uniform | 7721 | 0.5431 | [0.5249 ; 0.5628] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7721 | 0.4366 | [0.4178 ; 0.4565] | 0.0002 | oui | moins bon que la référence |
| form | 7721 | 0.4783 | [0.4583 ; 0.4983] | 0.0002 | oui | moins bon que la référence |
| market | 7721 | 0.0056 | [0.0035 ; 0.0080] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 19446 | 0.013 | 0.006 |
| 0.02-0.05 | 31391 | 0.034 | 0.027 |
| 0.05-0.10 | 24528 | 0.072 | 0.070 |
| 0.10-0.20 | 14778 | 0.139 | 0.162 |
| 0.20-0.30 | 4431 | 0.241 | 0.262 |
| 0.30-0.50 | 2794 | 0.379 | 0.386 |
| 0.50-1.00 | 773 | 0.595 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 25830 | 0.011 | 0.008 |
| 0.02-0.05 | 28664 | 0.033 | 0.033 |
| 0.05-0.10 | 21490 | 0.071 | 0.075 |
| 0.10-0.20 | 13201 | 0.140 | 0.161 |
| 0.20-0.30 | 4506 | 0.242 | 0.239 |
| 0.30-0.50 | 3136 | 0.380 | 0.361 |
| 0.50-1.00 | 1314 | 0.614 | 0.483 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.138** (54 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
