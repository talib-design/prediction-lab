# Backtest — trot attelé, hippodromes français

Généré le 2026-11-02T08:15:07+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `7c22eb8916fa`

Courses chargées : 41367 · courses évaluées (cotes complètes à l'horizon) : 27346 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7638 | 1.5507 | 0.0497 | 188515 |
| uniform | 7638 | 0.9138 | 0.0293 | 65466 |
| horse_win_rate | 7638 | 0.8975 | 0.0288 | 63150 |
| form | 7638 | 0.9202 | 0.0295 | 66394 |
| market | 7638 | 0.1110 | 0.0036 | 966 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7638 | 1.9766 | 0.8092 | 0.328 | 0.530 | 0.0071 |
| market | 7638 | 1.9823 | 0.8073 | 0.328 | 0.530 | 0.0091 |
| horse_win_rate | 7638 | 2.4128 | 0.8935 | 0.191 | 0.375 | 0.0084 |
| form | 7638 | 2.4544 | 0.9025 | 0.167 | 0.355 | 0.0103 |
| uniform | 7638 | 2.5195 | 0.9169 | 0.058 | 0.230 | 0.0000 |
| random | 7638 | 3.0508 | 0.9857 | 0.084 | 0.255 | 0.0523 |

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
| random | 7638 | 1.0741 | [1.0399 ; 1.1074] | 0.0002 | oui | moins bon que la référence |
| uniform | 7638 | 0.5429 | [0.5240 ; 0.5627] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7638 | 0.4362 | [0.4172 ; 0.4558] | 0.0002 | oui | moins bon que la référence |
| form | 7638 | 0.4778 | [0.4577 ; 0.4988] | 0.0002 | oui | moins bon que la référence |
| market | 7638 | 0.0057 | [0.0035 ; 0.0080] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 19155 | 0.013 | 0.006 |
| 0.02-0.05 | 31032 | 0.034 | 0.027 |
| 0.05-0.10 | 24273 | 0.072 | 0.071 |
| 0.10-0.20 | 14621 | 0.139 | 0.161 |
| 0.20-0.30 | 4384 | 0.241 | 0.262 |
| 0.30-0.50 | 2762 | 0.379 | 0.388 |
| 0.50-1.00 | 765 | 0.595 | 0.527 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 25456 | 0.011 | 0.008 |
| 0.02-0.05 | 28343 | 0.033 | 0.033 |
| 0.05-0.10 | 21271 | 0.071 | 0.075 |
| 0.10-0.20 | 13061 | 0.140 | 0.160 |
| 0.20-0.30 | 4459 | 0.242 | 0.239 |
| 0.30-0.50 | 3102 | 0.380 | 0.362 |
| 0.50-1.00 | 1300 | 0.614 | 0.486 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.138** (54 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
