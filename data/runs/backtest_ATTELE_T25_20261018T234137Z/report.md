# Backtest — trot attelé, hippodromes français

Généré le 2026-10-18T23:41:37+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `ee2631107cb5`

Courses chargées : 41085 · courses évaluées (cotes complètes à l'horizon) : 27182 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7474 | 1.5513 | 0.0502 | 188684 |
| uniform | 7474 | 0.9128 | 0.0296 | 65317 |
| horse_win_rate | 7474 | 0.8959 | 0.0290 | 62930 |
| form | 7474 | 0.9193 | 0.0298 | 66250 |
| market | 7474 | 0.1109 | 0.0036 | 964 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7474 | 1.9720 | 0.8081 | 0.330 | 0.531 | 0.0071 |
| market | 7474 | 1.9780 | 0.8063 | 0.330 | 0.531 | 0.0093 |
| horse_win_rate | 7474 | 2.4085 | 0.8928 | 0.193 | 0.377 | 0.0082 |
| form | 7474 | 2.4514 | 0.9022 | 0.168 | 0.356 | 0.0103 |
| uniform | 7474 | 2.5176 | 0.9167 | 0.059 | 0.231 | 0.0000 |
| random | 7474 | 3.0506 | 0.9856 | 0.085 | 0.256 | 0.0525 |

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
| random | 7474 | 1.0786 | [1.0432 ; 1.1130] | 0.0002 | oui | moins bon que la référence |
| uniform | 7474 | 0.5457 | [0.5268 ; 0.5653] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7474 | 0.4366 | [0.4160 ; 0.4560] | 0.0002 | oui | moins bon que la référence |
| form | 7474 | 0.4795 | [0.4586 ; 0.5000] | 0.0002 | oui | moins bon que la référence |
| market | 7474 | 0.0061 | [0.0037 ; 0.0083] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 18610 | 0.013 | 0.005 |
| 0.02-0.05 | 30344 | 0.034 | 0.027 |
| 0.05-0.10 | 23711 | 0.072 | 0.071 |
| 0.10-0.20 | 14316 | 0.139 | 0.161 |
| 0.20-0.30 | 4286 | 0.241 | 0.265 |
| 0.30-0.50 | 2710 | 0.379 | 0.388 |
| 0.50-1.00 | 751 | 0.596 | 0.531 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 24769 | 0.011 | 0.008 |
| 0.02-0.05 | 27727 | 0.033 | 0.032 |
| 0.05-0.10 | 20767 | 0.071 | 0.076 |
| 0.10-0.20 | 12787 | 0.140 | 0.160 |
| 0.20-0.30 | 4369 | 0.242 | 0.241 |
| 0.30-0.50 | 3034 | 0.381 | 0.363 |
| 0.50-1.00 | 1275 | 0.614 | 0.487 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.138** (54 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
