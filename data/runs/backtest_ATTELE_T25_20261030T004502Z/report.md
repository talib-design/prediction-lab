# Backtest — trot attelé, hippodromes français

Généré le 2026-10-30T00:45:02+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `8fbc1f359b31`

Courses chargées : 41275 · courses évaluées (cotes complètes à l'horizon) : 27291 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7583 | 1.5507 | 0.0499 | 188528 |
| uniform | 7583 | 0.9131 | 0.0294 | 65363 |
| horse_win_rate | 7583 | 0.8971 | 0.0288 | 63095 |
| form | 7583 | 0.9200 | 0.0296 | 66353 |
| market | 7583 | 0.1109 | 0.0036 | 965 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7583 | 1.9747 | 0.8088 | 0.329 | 0.530 | 0.0071 |
| market | 7583 | 1.9805 | 0.8069 | 0.329 | 0.530 | 0.0092 |
| horse_win_rate | 7583 | 2.4115 | 0.8933 | 0.192 | 0.376 | 0.0084 |
| form | 7583 | 2.4533 | 0.9024 | 0.167 | 0.356 | 0.0103 |
| uniform | 7583 | 2.5187 | 0.9168 | 0.058 | 0.230 | 0.0000 |
| random | 7583 | 3.0496 | 0.9855 | 0.084 | 0.256 | 0.0524 |

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
| random | 7583 | 1.0749 | [1.0402 ; 1.1101] | 0.0002 | oui | moins bon que la référence |
| uniform | 7583 | 0.5440 | [0.5249 ; 0.5641] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7583 | 0.4368 | [0.4172 ; 0.4559] | 0.0002 | oui | moins bon que la référence |
| form | 7583 | 0.4786 | [0.4578 ; 0.4986] | 0.0002 | oui | moins bon que la référence |
| market | 7583 | 0.0058 | [0.0036 ; 0.0082] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 18961 | 0.013 | 0.005 |
| 0.02-0.05 | 30792 | 0.034 | 0.027 |
| 0.05-0.10 | 24078 | 0.072 | 0.071 |
| 0.10-0.20 | 14522 | 0.139 | 0.161 |
| 0.20-0.30 | 4350 | 0.241 | 0.263 |
| 0.30-0.50 | 2745 | 0.379 | 0.388 |
| 0.50-1.00 | 761 | 0.595 | 0.529 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 25214 | 0.011 | 0.008 |
| 0.02-0.05 | 28134 | 0.033 | 0.033 |
| 0.05-0.10 | 21089 | 0.071 | 0.075 |
| 0.10-0.20 | 12972 | 0.140 | 0.160 |
| 0.20-0.30 | 4426 | 0.242 | 0.240 |
| 0.30-0.50 | 3080 | 0.380 | 0.362 |
| 0.50-1.00 | 1294 | 0.614 | 0.486 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.138** (54 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
