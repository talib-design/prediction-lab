# Backtest — trot attelé, hippodromes français

Généré le 2026-11-12T07:52:48+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `055c3795f50c`

Courses chargées : 41564 · courses évaluées (cotes complètes à l'horizon) : 27460 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7752 | 1.5487 | 0.0492 | 188029 |
| uniform | 7752 | 0.9131 | 0.0290 | 65360 |
| horse_win_rate | 7752 | 0.8977 | 0.0285 | 63177 |
| form | 7752 | 0.9200 | 0.0293 | 66354 |
| market | 7752 | 0.1108 | 0.0035 | 964 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7752 | 1.9776 | 0.8096 | 0.327 | 0.529 | 0.0072 |
| market | 7752 | 1.9832 | 0.8076 | 0.327 | 0.529 | 0.0091 |
| horse_win_rate | 7752 | 2.4142 | 0.8937 | 0.191 | 0.374 | 0.0084 |
| form | 7752 | 2.4557 | 0.9027 | 0.166 | 0.354 | 0.0103 |
| uniform | 7752 | 2.5207 | 0.9169 | 0.058 | 0.230 | 0.0000 |
| random | 7752 | 3.0511 | 0.9857 | 0.084 | 0.255 | 0.0522 |

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
| random | 7752 | 1.0735 | [1.0414 ; 1.1086] | 0.0002 | oui | moins bon que la référence |
| uniform | 7752 | 0.5431 | [0.5254 ; 0.5617] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7752 | 0.4366 | [0.4181 ; 0.4564] | 0.0002 | oui | moins bon que la référence |
| form | 7752 | 0.4782 | [0.4585 ; 0.4977] | 0.0002 | oui | moins bon que la référence |
| market | 7752 | 0.0056 | [0.0035 ; 0.0078] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 19537 | 0.013 | 0.005 |
| 0.02-0.05 | 31521 | 0.034 | 0.027 |
| 0.05-0.10 | 24615 | 0.072 | 0.071 |
| 0.10-0.20 | 14850 | 0.139 | 0.162 |
| 0.20-0.30 | 4447 | 0.241 | 0.262 |
| 0.30-0.50 | 2802 | 0.379 | 0.386 |
| 0.50-1.00 | 777 | 0.595 | 0.527 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 25950 | 0.011 | 0.008 |
| 0.02-0.05 | 28781 | 0.033 | 0.033 |
| 0.05-0.10 | 21563 | 0.071 | 0.075 |
| 0.10-0.20 | 13267 | 0.140 | 0.160 |
| 0.20-0.30 | 4522 | 0.242 | 0.239 |
| 0.30-0.50 | 3146 | 0.380 | 0.361 |
| 0.50-1.00 | 1320 | 0.614 | 0.484 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.138** (54 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
