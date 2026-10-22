# Backtest — trot attelé, hippodromes français

Généré le 2026-10-22T23:41:45+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `b010c064b9fd`

Courses chargées : 41126 · courses évaluées (cotes complètes à l'horizon) : 27207 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 7499 | 1.5504 | 0.0501 | 188452 |
| uniform | 7499 | 0.9127 | 0.0295 | 65311 |
| horse_win_rate | 7499 | 0.8962 | 0.0290 | 62971 |
| form | 7499 | 0.9196 | 0.0297 | 66302 |
| market | 7499 | 0.1109 | 0.0036 | 965 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 7499 | 1.9733 | 0.8086 | 0.329 | 0.531 | 0.0072 |
| market | 7499 | 1.9792 | 0.8067 | 0.329 | 0.531 | 0.0092 |
| horse_win_rate | 7499 | 2.4097 | 0.8930 | 0.192 | 0.376 | 0.0083 |
| form | 7499 | 2.4515 | 0.9022 | 0.168 | 0.356 | 0.0103 |
| uniform | 7499 | 2.5178 | 0.9167 | 0.059 | 0.231 | 0.0000 |
| random | 7499 | 3.0501 | 0.9857 | 0.085 | 0.256 | 0.0525 |

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
| random | 7499 | 1.0768 | [1.0453 ; 1.1119] | 0.0002 | oui | moins bon que la référence |
| uniform | 7499 | 0.5446 | [0.5254 ; 0.5644] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 7499 | 0.4364 | [0.4168 ; 0.4561] | 0.0002 | oui | moins bon que la référence |
| form | 7499 | 0.4782 | [0.4576 ; 0.4992] | 0.0002 | oui | moins bon que la référence |
| market | 7499 | 0.0059 | [0.0036 ; 0.0082] | 0.0002 | oui | moins bon que la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 18708 | 0.013 | 0.005 |
| 0.02-0.05 | 30437 | 0.034 | 0.027 |
| 0.05-0.10 | 23789 | 0.072 | 0.071 |
| 0.10-0.20 | 14355 | 0.139 | 0.161 |
| 0.20-0.30 | 4304 | 0.241 | 0.264 |
| 0.30-0.50 | 2718 | 0.379 | 0.388 |
| 0.50-1.00 | 755 | 0.596 | 0.528 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 24884 | 0.011 | 0.008 |
| 0.02-0.05 | 27814 | 0.033 | 0.033 |
| 0.05-0.10 | 20838 | 0.071 | 0.076 |
| 0.10-0.20 | 12821 | 0.140 | 0.160 |
| 0.20-0.30 | 4382 | 0.242 | 0.241 |
| 0.30-0.50 | 3046 | 0.381 | 0.362 |
| 0.50-1.00 | 1281 | 0.614 | 0.486 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.138** (54 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
