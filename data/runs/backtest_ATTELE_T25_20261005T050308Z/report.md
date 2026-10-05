# Backtest — trot attelé, hippodromes français

Généré le 2026-10-05T05:03:08+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `e7bd23fdbf7f`

Courses chargées : 12491 · courses évaluées (cotes complètes à l'horizon) : 8103 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7311 | 1.5436 | 0.0505 | 186796 |
| uniform | 7311 | 0.8993 | 0.0294 | 63407 |
| horse_win_rate | 7311 | 0.9137 | 0.0299 | 65457 |
| form | 7311 | 0.9182 | 0.0301 | 66101 |
| market | 7311 | 0.0965 | 0.0032 | 730 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7311 | 1.9725 | 0.8079 | 0.330 | 0.531 | 0.0072 |
| market | 7311 | 1.9783 | 0.8065 | 0.330 | 0.531 | 0.0091 |
| horse_win_rate | 7311 | 2.4278 | 0.8962 | 0.184 | 0.370 | 0.0120 |
| form | 7311 | 2.4517 | 0.9022 | 0.168 | 0.357 | 0.0107 |
| uniform | 7311 | 2.5162 | 0.9166 | 0.058 | 0.230 | 0.0000 |
| random | 7311 | 3.0459 | 0.9853 | 0.085 | 0.257 | 0.0526 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 792 | 2.0668 | 0.8173 | 0.312 | 0.509 | 0.0079 |
| market | 792 | 2.0680 | 0.8168 | 0.312 | 0.509 | 0.0083 |
| horse_win_rate | 792 | 2.5889 | 0.9198 | 0.121 | 0.285 | 0.0067 |
| uniform | 792 | 2.6125 | 0.9255 | 0.064 | 0.225 | 0.0000 |
| form | 792 | 2.6437 | 0.9262 | 0.134 | 0.299 | 0.0160 |
| random | 792 | 3.1982 | 0.9869 | 0.082 | 0.251 | 0.0476 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 7311 | 1.0734 | [1.0416 ; 1.1077] | 0.0002 | oui | moins bon que la référence |
| uniform | 7311 | 0.5437 | [0.5248 ; 0.5630] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7311 | 0.4553 | [0.4353 ; 0.4754] | 0.0002 | oui | moins bon que la référence |
| form | 7311 | 0.4792 | [0.4576 ; 0.5002] | 0.0002 | oui | moins bon que la référence |
| market | 7311 | 0.0058 | [0.0038 ; 0.0079] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 18108 | 0.013 | 0.006 |
| 0.02-0.05 | 29671 | 0.034 | 0.027 |
| 0.05-0.10 | 23186 | 0.072 | 0.071 |
| 0.10-0.20 | 13993 | 0.139 | 0.161 |
| 0.20-0.30 | 4195 | 0.241 | 0.263 |
| 0.30-0.50 | 2650 | 0.379 | 0.389 |
| 0.50-1.00 | 737 | 0.596 | 0.528 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 23300 | 0.011 | 0.007 |
| 0.02-0.05 | 27518 | 0.033 | 0.032 |
| 0.05-0.10 | 20655 | 0.072 | 0.076 |
| 0.10-0.20 | 12697 | 0.140 | 0.159 |
| 0.20-0.30 | 4259 | 0.242 | 0.241 |
| 0.30-0.50 | 2913 | 0.380 | 0.366 |
| 0.50-1.00 | 1198 | 0.611 | 0.495 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.125** (16 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
