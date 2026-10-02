# Backtest — trot attelé, hippodromes français

Généré le 2026-10-02T06:43:16+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `03ecc6603895`

Courses chargées : 2807 · courses évaluées (cotes complètes à l'horizon) : 1912 · phase de décision : **test** · référence : `market_calibrated`.

## 1. Puissance

Avant tout résultat : quel écart ce jeu de données permet-il de voir ?

| Modèle vs référence | Courses | Écart-type de la différence | Effet minimal détectable | Courses pour détecter 0,01 |
|---|---:|---:|---:|---:|
| random | 1912 | 1.5099 | 0.0967 | 178742 |
| uniform | 1912 | 0.8790 | 0.0563 | 60570 |
| horse_win_rate | 1912 | 0.8608 | 0.0551 | 58092 |
| form | 1912 | 0.9466 | 0.0606 | 70257 |
| market | 1912 | 0.0796 | 0.0051 | 497 |

## 2. Scores par phase

### test

| Modèle | Courses | Log loss ↓ | Brier ↓ | Top-1 ↑ | MRR ↑ | Erreur de calibration ↓ |
|---|---:|---:|---:|---:|---:|---:|
| market_calibrated | 1912 | 1.9338 | 0.8018 | 0.326 | 0.531 | 0.0096 |
| market | 1912 | 1.9368 | 0.8002 | 0.326 | 0.531 | 0.0100 |
| horse_win_rate | 1912 | 2.4130 | 0.8971 | 0.161 | 0.339 | 0.0080 |
| form | 1912 | 2.4614 | 0.9026 | 0.163 | 0.349 | 0.0138 |
| uniform | 1912 | 2.4857 | 0.9141 | 0.054 | 0.232 | 0.0000 |
| random | 1912 | 2.9925 | 0.9825 | 0.089 | 0.266 | 0.0532 |

## 3. Comparaison à la référence (phase test)

Différence de log loss par course (modèle − référence ; négatif = mieux), IC 95 % par bootstrap en blocs, p par permutation appariée en blocs, correction Benjamini–Yekutieli sur toutes les lignes.

| Modèle | Courses | Différence | IC 95 % | p | Survit FDR | Verdict |
|---|---:|---:|---|---:|---|---|
| random | 1912 | 1.0588 | [0.9923 ; 1.1239] | 0.0002 | oui | moins bon que la référence |
| uniform | 1912 | 0.5519 | [0.5169 ; 0.5871] | 0.0002 | oui | moins bon que la référence |
| horse_win_rate | 1912 | 0.4792 | [0.4429 ; 0.5149] | 0.0002 | oui | moins bon que la référence |
| form | 1912 | 0.5276 | [0.4910 ; 0.5653] | 0.0002 | oui | moins bon que la référence |
| market | 1912 | 0.0030 | [-0.0001 ; 0.0061] | 0.0626 | non | non distinguable de la référence |

## 4. Calibration du marché (niveau partant)

**market**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 4663 | 0.013 | 0.005 |
| 0.02-0.05 | 7539 | 0.034 | 0.026 |
| 0.05-0.10 | 5624 | 0.072 | 0.077 |
| 0.10-0.20 | 3570 | 0.140 | 0.160 |
| 0.20-0.30 | 1091 | 0.240 | 0.247 |
| 0.30-0.50 | 782 | 0.378 | 0.395 |
| 0.50-1.00 | 224 | 0.602 | 0.516 |

**market_calibrated**

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.00-0.02 | 5668 | 0.012 | 0.006 |
| 0.02-0.05 | 7061 | 0.033 | 0.029 |
| 0.05-0.10 | 5201 | 0.072 | 0.081 |
| 0.10-0.20 | 3332 | 0.140 | 0.160 |
| 0.20-0.30 | 1112 | 0.242 | 0.236 |
| 0.30-0.50 | 796 | 0.379 | 0.364 |
| 0.50-1.00 | 323 | 0.612 | 0.515 |

Exposant de calibration du marché (dernier ajustement) : **α = 1.109** (3 ajustements). α > 1 : le marché sous-estime les favoris.

## 5. Limites

- Départ **programmé**, pas réel : un retard décale l'horizon effectif.
- Horodatage des cotes = celui publié par le PMU, pris pour vrai.
- Partants = ceux qui ont couru ; un retrait postérieur à l'horizon est ignoré.
- Aucun modèle fondamental n'est encore évalué : ce rapport mesure le banc et les baselines.
