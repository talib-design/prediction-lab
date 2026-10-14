# Backtest — trot monté, hippodromes français

Généré le 2026-10-14T23:38:28+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `e500dba1a7f6`

Courses chargées : 4323 · courses évaluées (cotes complètes à l'horizon) : 3283 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1384 | 1.5472 | 0.1165 | 187680 |
| uniform | 1384 | 0.8735 | 0.0657 | 59817 |
| horse_win_rate | 1384 | 0.8372 | 0.0630 | 54952 |
| form | 1384 | 0.8624 | 0.0649 | 58314 |
| market | 1384 | 0.0808 | 0.0061 | 512 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1384 | 1.9567 | 0.8104 | 0.331 | 0.532 | 0.0093 |
| market | 1384 | 1.9574 | 0.8083 | 0.331 | 0.532 | 0.0100 |
| horse_win_rate | 1384 | 2.3034 | 0.8829 | 0.189 | 0.385 | 0.0082 |
| form | 1384 | 2.3897 | 0.8984 | 0.182 | 0.367 | 0.0175 |
| uniform | 1384 | 2.4018 | 0.9057 | 0.051 | 0.214 | 0.0000 |
| random | 1384 | 2.9464 | 0.9822 | 0.089 | 0.274 | 0.0617 |

### train

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1472 | 1.9750 | 0.8122 | 0.312 | 0.516 | 0.0103 |
| market | 1472 | 1.9753 | 0.8116 | 0.312 | 0.516 | 0.0096 |
| horse_win_rate | 1472 | 2.3366 | 0.8899 | 0.181 | 0.365 | 0.0090 |
| form | 1472 | 2.3528 | 0.8911 | 0.194 | 0.379 | 0.0150 |
| uniform | 1472 | 2.4103 | 0.9074 | 0.043 | 0.212 | 0.0000 |
| random | 1472 | 2.8851 | 0.9737 | 0.113 | 0.293 | 0.0567 |

### validation

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 427 | 1.8641 | 0.7713 | 0.398 | 0.579 | 0.0064 |
| market | 427 | 1.8721 | 0.7725 | 0.398 | 0.579 | 0.0110 |
| horse_win_rate | 427 | 2.2808 | 0.8704 | 0.206 | 0.400 | 0.0096 |
| form | 427 | 2.3568 | 0.8817 | 0.239 | 0.411 | 0.0133 |
| uniform | 427 | 2.4452 | 0.9087 | 0.047 | 0.208 | 0.0000 |
| random | 427 | 2.8782 | 0.9736 | 0.089 | 0.281 | 0.0515 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 1384 | 0.9897 | [0.9159 ; 1.0689] | 0.0002 | oui | moins bon que la référence |
| uniform | 1384 | 0.4451 | [0.4050 ; 0.4874] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1384 | 0.3467 | [0.3066 ; 0.3896] | 0.0002 | oui | moins bon que la référence |
| form | 1384 | 0.4331 | [0.3877 ; 0.4775] | 0.0002 | oui | moins bon que la référence |
| market | 1384 | 0.0008 | [-0.0027 ; 0.0047] | 0.7127 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2255 | 0.014 | 0.009 |
| 0.02-0.05 | 4894 | 0.034 | 0.028 |
| 0.05-0.10 | 4208 | 0.073 | 0.071 |
| 0.10-0.20 | 2813 | 0.140 | 0.156 |
| 0.20-0.30 | 839 | 0.243 | 0.281 |
| 0.30-0.50 | 503 | 0.380 | 0.344 |
| 0.50-1.00 | 151 | 0.604 | 0.523 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2971 | 0.013 | 0.010 |
| 0.02-0.05 | 4641 | 0.034 | 0.032 |
| 0.05-0.10 | 3843 | 0.072 | 0.078 |
| 0.10-0.20 | 2588 | 0.140 | 0.149 |
| 0.20-0.30 | 843 | 0.243 | 0.275 |
| 0.30-0.50 | 546 | 0.377 | 0.328 |
| 0.50-1.00 | 231 | 0.611 | 0.485 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
