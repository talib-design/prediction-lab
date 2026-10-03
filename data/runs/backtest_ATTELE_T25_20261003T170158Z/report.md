# Backtest — trot attelé, hippodromes français

Généré le 2026-10-03T17:01:58+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `f7abbd27e71f`

Courses chargées : 11241 · courses évaluées (cotes complètes à l'horizon) : 7417 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7304 | 1.5470 | 0.0507 | 187616 |
| uniform | 7304 | 0.9041 | 0.0296 | 64079 |
| horse_win_rate | 7304 | 0.9100 | 0.0298 | 64920 |
| form | 7304 | 0.9355 | 0.0306 | 68612 |
| market | 7304 | 0.1041 | 0.0034 | 849 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7304 | 1.9723 | 0.8080 | 0.330 | 0.531 | 0.0072 |
| market | 7304 | 1.9779 | 0.8064 | 0.330 | 0.531 | 0.0092 |
| horse_win_rate | 7304 | 2.4334 | 0.8978 | 0.178 | 0.361 | 0.0106 |
| form | 7304 | 2.4590 | 0.9031 | 0.167 | 0.355 | 0.0112 |
| uniform | 7304 | 2.5161 | 0.9166 | 0.058 | 0.230 | 0.0000 |
| random | 7304 | 3.0458 | 0.9852 | 0.086 | 0.257 | 0.0526 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market | 113 | 2.0630 | 0.8290 | 0.283 | 0.499 | 0.0155 |
| market_calibrated | 113 | 2.0630 | 0.8290 | 0.283 | 0.499 | 0.0155 |
| form | 113 | 2.6017 | 0.9259 | 0.088 | 0.250 | 0.0028 |
| horse_win_rate | 113 | 2.6031 | 0.9253 | 0.080 | 0.247 | 0.0008 |
| uniform | 113 | 2.6042 | 0.9249 | 0.080 | 0.242 | 0.0000 |
| random | 113 | 3.1684 | 0.9919 | 0.080 | 0.251 | 0.0555 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 7304 | 1.0734 | [1.0387 ; 1.1086] | 0.0002 | oui | moins bon que la référence |
| uniform | 7304 | 0.5437 | [0.5231 ; 0.5640] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7304 | 0.4611 | [0.4411 ; 0.4804] | 0.0002 | oui | moins bon que la référence |
| form | 7304 | 0.4867 | [0.4649 ; 0.5080] | 0.0002 | oui | moins bon que la référence |
| market | 7304 | 0.0056 | [0.0034 ; 0.0079] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 18089 | 0.013 | 0.006 |
| 0.02-0.05 | 29634 | 0.034 | 0.027 |
| 0.05-0.10 | 23161 | 0.072 | 0.071 |
| 0.10-0.20 | 13977 | 0.139 | 0.161 |
| 0.20-0.30 | 4191 | 0.241 | 0.263 |
| 0.30-0.50 | 2648 | 0.379 | 0.389 |
| 0.50-1.00 | 737 | 0.596 | 0.528 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 23519 | 0.011 | 0.007 |
| 0.02-0.05 | 27365 | 0.033 | 0.032 |
| 0.05-0.10 | 20543 | 0.072 | 0.076 |
| 0.10-0.20 | 12626 | 0.140 | 0.160 |
| 0.20-0.30 | 4237 | 0.242 | 0.242 |
| 0.30-0.50 | 2938 | 0.380 | 0.365 |
| 0.50-1.00 | 1209 | 0.613 | 0.490 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.129** (14 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
