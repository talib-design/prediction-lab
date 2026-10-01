# Backtest — trot attelé, hippodromes français

Généré le 2026-10-01T09:09:16+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `2ef750f3aa6c`

Courses chargées : 2793 · courses évaluées (cotes complètes à l'horizon) : 1898 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1898 | 1.5105 | 0.0971 | 178875 |
| uniform | 1898 | 0.8818 | 0.0567 | 60964 |
| horse_win_rate | 1898 | 0.8629 | 0.0555 | 58376 |
| form | 1898 | 0.9486 | 0.0610 | 70553 |
| market | 1898 | 0.0818 | 0.0053 | 526 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1898 | 1.9338 | 0.8018 | 0.326 | 0.532 | 0.0095 |
| market | 1898 | 1.9367 | 0.8002 | 0.326 | 0.532 | 0.0100 |
| horse_win_rate | 1898 | 2.4141 | 0.8975 | 0.162 | 0.340 | 0.0082 |
| form | 1898 | 2.4639 | 0.9031 | 0.162 | 0.348 | 0.0144 |
| uniform | 1898 | 2.4847 | 0.9140 | 0.055 | 0.232 | 0.0000 |
| random | 1898 | 2.9916 | 0.9827 | 0.089 | 0.266 | 0.0534 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 1898 | 1.0579 | [0.9948 ; 1.1227] | 0.0002 | oui | moins bon que la référence |
| uniform | 1898 | 0.5509 | [0.5171 ; 0.5860] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1898 | 0.4804 | [0.4435 ; 0.5174] | 0.0002 | oui | moins bon que la référence |
| form | 1898 | 0.5302 | [0.4924 ; 0.5682] | 0.0002 | oui | moins bon que la référence |
| market | 1898 | 0.0030 | [-0.0001 ; 0.0060] | 0.0540 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4613 | 0.013 | 0.005 |
| 0.02-0.05 | 7480 | 0.034 | 0.026 |
| 0.05-0.10 | 5581 | 0.072 | 0.076 |
| 0.10-0.20 | 3543 | 0.140 | 0.160 |
| 0.20-0.30 | 1082 | 0.240 | 0.247 |
| 0.30-0.50 | 777 | 0.378 | 0.396 |
| 0.50-1.00 | 223 | 0.602 | 0.513 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 5635 | 0.012 | 0.006 |
| 0.02-0.05 | 6994 | 0.033 | 0.029 |
| 0.05-0.10 | 5151 | 0.072 | 0.080 |
| 0.10-0.20 | 3297 | 0.140 | 0.160 |
| 0.20-0.30 | 1108 | 0.242 | 0.236 |
| 0.30-0.50 | 791 | 0.379 | 0.365 |
| 0.50-1.00 | 323 | 0.613 | 0.515 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.108** (3 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
