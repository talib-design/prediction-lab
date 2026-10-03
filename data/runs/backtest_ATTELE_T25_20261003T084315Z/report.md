# Backtest — trot attelé, hippodromes français

Généré le 2026-10-03T08:43:15+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `992ba1c20722`

Courses chargées : 2856 · courses évaluées (cotes complètes à l'horizon) : 1947 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1947 | 1.5113 | 0.0959 | 179066 |
| uniform | 1947 | 0.8794 | 0.0558 | 60633 |
| horse_win_rate | 1947 | 0.8625 | 0.0547 | 58321 |
| form | 1947 | 0.9479 | 0.0601 | 70440 |
| market | 1947 | 0.0774 | 0.0049 | 471 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1947 | 1.9322 | 0.8006 | 0.329 | 0.533 | 0.0095 |
| market | 1947 | 1.9359 | 0.7994 | 0.329 | 0.533 | 0.0101 |
| horse_win_rate | 1947 | 2.4144 | 0.8973 | 0.163 | 0.341 | 0.0074 |
| form | 1947 | 2.4624 | 0.9025 | 0.165 | 0.351 | 0.0133 |
| uniform | 1947 | 2.4881 | 0.9143 | 0.054 | 0.231 | 0.0000 |
| random | 1947 | 2.9938 | 0.9822 | 0.090 | 0.267 | 0.0529 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 1947 | 1.0616 | [0.9972 ; 1.1256] | 0.0002 | oui | moins bon que la référence |
| uniform | 1947 | 0.5559 | [0.5192 ; 0.5884] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1947 | 0.4822 | [0.4456 ; 0.5157] | 0.0002 | oui | moins bon que la référence |
| form | 1947 | 0.5302 | [0.4885 ; 0.5650] | 0.0002 | oui | moins bon que la référence |
| market | 1947 | 0.0037 | [0.0007 ; 0.0065] | 0.0134 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4789 | 0.013 | 0.005 |
| 0.02-0.05 | 7700 | 0.034 | 0.026 |
| 0.05-0.10 | 5736 | 0.072 | 0.077 |
| 0.10-0.20 | 3630 | 0.139 | 0.160 |
| 0.20-0.30 | 1099 | 0.240 | 0.248 |
| 0.30-0.50 | 802 | 0.378 | 0.395 |
| 0.50-1.00 | 228 | 0.601 | 0.520 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 5793 | 0.012 | 0.006 |
| 0.02-0.05 | 7212 | 0.033 | 0.029 |
| 0.05-0.10 | 5324 | 0.072 | 0.081 |
| 0.10-0.20 | 3397 | 0.140 | 0.160 |
| 0.20-0.30 | 1112 | 0.242 | 0.238 |
| 0.30-0.50 | 820 | 0.378 | 0.362 |
| 0.50-1.00 | 326 | 0.611 | 0.523 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.114** (3 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
