# Backtest — trot monté, hippodromes français

Généré le 2026-10-25T09:52:18+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `8706aa1fd659`

Courses chargées : 4350 · courses évaluées (cotes complètes à l'horizon) : 3304 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1405 | 1.5429 | 0.1153 | 186625 |
| uniform | 1405 | 0.8736 | 0.0653 | 59830 |
| horse_win_rate | 1405 | 0.8382 | 0.0626 | 55080 |
| form | 1405 | 0.8616 | 0.0644 | 58205 |
| market | 1405 | 0.0806 | 0.0060 | 510 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1405 | 1.9553 | 0.8098 | 0.333 | 0.534 | 0.0090 |
| market | 1405 | 1.9563 | 0.8078 | 0.333 | 0.534 | 0.0100 |
| horse_win_rate | 1405 | 2.3002 | 0.8820 | 0.191 | 0.387 | 0.0081 |
| form | 1405 | 2.3886 | 0.8980 | 0.182 | 0.368 | 0.0172 |
| uniform | 1405 | 2.4029 | 0.9058 | 0.051 | 0.213 | 0.0000 |
| random | 1405 | 2.9430 | 0.9821 | 0.088 | 0.274 | 0.0619 |

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
| random | 1405 | 0.9877 | [0.9145 ; 1.0653] | 0.0002 | oui | moins bon que la référence |
| uniform | 1405 | 0.4476 | [0.4067 ; 0.4889] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1405 | 0.3449 | [0.3053 ; 0.3874] | 0.0002 | oui | moins bon que la référence |
| form | 1405 | 0.4333 | [0.3894 ; 0.4741] | 0.0002 | oui | moins bon que la référence |
| market | 1405 | 0.0010 | [-0.0027 ; 0.0046] | 0.6255 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 2302 | 0.014 | 0.009 |
| 0.02-0.05 | 4969 | 0.034 | 0.028 |
| 0.05-0.10 | 4271 | 0.073 | 0.071 |
| 0.10-0.20 | 2862 | 0.140 | 0.155 |
| 0.20-0.30 | 851 | 0.243 | 0.284 |
| 0.30-0.50 | 508 | 0.380 | 0.343 |
| 0.50-1.00 | 154 | 0.603 | 0.526 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 3025 | 0.013 | 0.010 |
| 0.02-0.05 | 4717 | 0.034 | 0.032 |
| 0.05-0.10 | 3899 | 0.072 | 0.077 |
| 0.10-0.20 | 2634 | 0.140 | 0.148 |
| 0.20-0.30 | 853 | 0.243 | 0.275 |
| 0.30-0.50 | 555 | 0.376 | 0.330 |
| 0.50-1.00 | 234 | 0.611 | 0.487 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.093** (6 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
