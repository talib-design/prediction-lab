# Backtest — trot attelé, hippodromes français

Généré le 2026-10-04T06:08:32+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `3bf2260e1e27`

Courses chargées : 11956 · courses évaluées (cotes complètes à l'horizon) : 7843 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7308 | 1.5452 | 0.0506 | 187194 |
| uniform | 7308 | 0.9017 | 0.0295 | 63739 |
| horse_win_rate | 7308 | 0.9126 | 0.0299 | 65295 |
| form | 7308 | 0.9225 | 0.0302 | 66717 |
| market | 7308 | 0.0988 | 0.0032 | 766 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7308 | 1.9724 | 0.8079 | 0.330 | 0.531 | 0.0071 |
| market | 7308 | 1.9782 | 0.8065 | 0.330 | 0.531 | 0.0092 |
| horse_win_rate | 7308 | 2.4282 | 0.8966 | 0.184 | 0.369 | 0.0120 |
| form | 7308 | 2.4546 | 0.9027 | 0.168 | 0.356 | 0.0113 |
| uniform | 7308 | 2.5161 | 0.9166 | 0.058 | 0.231 | 0.0000 |
| random | 7308 | 3.0459 | 0.9853 | 0.086 | 0.257 | 0.0526 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 535 | 2.0742 | 0.8132 | 0.325 | 0.515 | 0.0082 |
| market | 535 | 2.0743 | 0.8130 | 0.325 | 0.515 | 0.0080 |
| horse_win_rate | 535 | 2.6145 | 0.9266 | 0.099 | 0.263 | 0.0073 |
| uniform | 535 | 2.6146 | 0.9257 | 0.058 | 0.221 | 0.0000 |
| form | 535 | 2.6623 | 0.9296 | 0.112 | 0.283 | 0.0146 |
| random | 535 | 3.2507 | 0.9917 | 0.084 | 0.249 | 0.0497 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 7308 | 1.0735 | [1.0390 ; 1.1077] | 0.0002 | oui | moins bon que la référence |
| uniform | 7308 | 0.5438 | [0.5244 ; 0.5640] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7308 | 0.4559 | [0.4343 ; 0.4765] | 0.0002 | oui | moins bon que la référence |
| form | 7308 | 0.4822 | [0.4606 ; 0.5037] | 0.0002 | oui | moins bon que la référence |
| market | 7308 | 0.0058 | [0.0038 ; 0.0080] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 18100 | 0.013 | 0.006 |
| 0.02-0.05 | 29654 | 0.034 | 0.027 |
| 0.05-0.10 | 23175 | 0.072 | 0.071 |
| 0.10-0.20 | 13985 | 0.139 | 0.161 |
| 0.20-0.30 | 4194 | 0.241 | 0.263 |
| 0.30-0.50 | 2649 | 0.379 | 0.389 |
| 0.50-1.00 | 737 | 0.596 | 0.528 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 23409 | 0.011 | 0.007 |
| 0.02-0.05 | 27457 | 0.033 | 0.032 |
| 0.05-0.10 | 20571 | 0.072 | 0.076 |
| 0.10-0.20 | 12675 | 0.140 | 0.159 |
| 0.20-0.30 | 4254 | 0.242 | 0.242 |
| 0.30-0.50 | 2923 | 0.380 | 0.365 |
| 0.50-1.00 | 1205 | 0.611 | 0.494 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.125** (15 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
