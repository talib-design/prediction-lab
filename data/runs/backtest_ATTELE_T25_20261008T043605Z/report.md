# Backtest — trot attelé, hippodromes français

Généré le 2026-10-08T04:36:05+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `8630727d2f9a`

Courses chargées : 24996 · courses évaluées (cotes complètes à l'horizon) : 16131 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7328 | 1.5448 | 0.0505 | 187083 |
| uniform | 7328 | 0.9006 | 0.0295 | 63590 |
| horse_win_rate | 7328 | 0.8934 | 0.0292 | 62571 |
| form | 7328 | 0.9095 | 0.0297 | 64853 |
| market | 7328 | 0.0981 | 0.0032 | 755 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7328 | 1.9729 | 0.8081 | 0.330 | 0.531 | 0.0073 |
| market | 7328 | 1.9788 | 0.8067 | 0.330 | 0.531 | 0.0092 |
| horse_win_rate | 7328 | 2.4099 | 0.8927 | 0.191 | 0.377 | 0.0099 |
| form | 7328 | 2.4506 | 0.9022 | 0.167 | 0.356 | 0.0104 |
| uniform | 7328 | 2.5166 | 0.9166 | 0.059 | 0.231 | 0.0000 |
| random | 7328 | 3.0481 | 0.9855 | 0.085 | 0.257 | 0.0526 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 6725 | 2.0332 | 0.8177 | 0.305 | 0.509 | 0.0088 |
| market | 6725 | 2.0384 | 0.8163 | 0.305 | 0.509 | 0.0090 |
| horse_win_rate | 6725 | 2.4721 | 0.9012 | 0.176 | 0.357 | 0.0129 |
| form | 6725 | 2.5111 | 0.9093 | 0.158 | 0.339 | 0.0126 |
| uniform | 6725 | 2.5449 | 0.9190 | 0.060 | 0.230 | 0.0000 |
| random | 6725 | 3.0555 | 0.9816 | 0.085 | 0.257 | 0.0494 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 2078 | 2.0207 | 0.8169 | 0.310 | 0.514 | 0.0085 |
| market | 2078 | 2.0236 | 0.8143 | 0.310 | 0.514 | 0.0095 |
| horse_win_rate | 2078 | 2.4764 | 0.9018 | 0.180 | 0.365 | 0.0121 |
| form | 2078 | 2.4908 | 0.9086 | 0.164 | 0.347 | 0.0118 |
| uniform | 2078 | 2.5535 | 0.9204 | 0.068 | 0.238 | 0.0000 |
| random | 2078 | 3.1166 | 0.9889 | 0.083 | 0.252 | 0.0500 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 7328 | 1.0752 | [1.0390 ; 1.1078] | 0.0002 | oui | moins bon que la référence |
| uniform | 7328 | 0.5436 | [0.5242 ; 0.5622] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7328 | 0.4369 | [0.4172 ; 0.4561] | 0.0002 | oui | moins bon que la référence |
| form | 7328 | 0.4777 | [0.4570 ; 0.4972] | 0.0002 | oui | moins bon que la référence |
| market | 7328 | 0.0059 | [0.0038 ; 0.0079] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 18159 | 0.013 | 0.006 |
| 0.02-0.05 | 29758 | 0.034 | 0.027 |
| 0.05-0.10 | 23244 | 0.072 | 0.071 |
| 0.10-0.20 | 14034 | 0.139 | 0.161 |
| 0.20-0.30 | 4201 | 0.241 | 0.263 |
| 0.30-0.50 | 2655 | 0.379 | 0.389 |
| 0.50-1.00 | 738 | 0.596 | 0.528 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 23473 | 0.011 | 0.007 |
| 0.02-0.05 | 27545 | 0.033 | 0.032 |
| 0.05-0.10 | 20656 | 0.072 | 0.076 |
| 0.10-0.20 | 12722 | 0.140 | 0.160 |
| 0.20-0.30 | 4259 | 0.242 | 0.241 |
| 0.30-0.50 | 2924 | 0.380 | 0.366 |
| 0.50-1.00 | 1210 | 0.611 | 0.491 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.124** (32 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
