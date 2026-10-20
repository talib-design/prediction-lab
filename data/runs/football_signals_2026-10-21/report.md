# Football — signaux ajoutés au marché (football-signals-v1), 2026-10-21

Agrégats seulement. Protocole, seuils et règles de verdict : inscrits au registre chaîné (fb-H9 à fb-H14) avant ce calcul ; rien n'a été modifié après le résultat. Graine 0, 5000 permutations, blocs de matchs consécutifs triés par date.

Lecture : un « gain » est la baisse de log loss par match par rapport au marché recalibré (positif = le signal aide). Un gain non significatif n'est pas une preuve d'absence. Le plancher de détection (2,8 erreurs-types) se mesure sur le gain du modèle ajusté : quand le signal n'apporte presque rien, le modèle ajusté s'écarte à peine du marché recalibré et le plancher devient minuscule. Le chiffre à retenir est la borne haute de l'IC 95 % du gain : le meilleur gain hors échantillon que les données autorisent. Un « soutenue » n'est jamais une preuve de battre le marché : c'est un candidat à un test à terme.

| Hypothèse | Signal | Marché | Matchs test | Gain moyen | IC 95 % | p | p corrigé | Plancher | Placebo (gain, p) | Verdict |
|---|---|---|---:|---:|---|---:|---:|---:|---|---|
| fb-H9 | repos et calendrier | psc | 13430 | -0.00002 | [-0.00008 ; +0.00003] | 0.3097 | 1.0000 | 0.00008 | -0.00006, 0.570 | REJECTED |
| fb-H10 | forme en tirs cadrés | psc | 13310 | -0.00001 | [-0.00009 ; +0.00007] | 0.8584 | 1.0000 | 0.00011 | -0.00002, 0.539 | REJECTED |
| fb-H11 | mouvement de Pinnacle | psc | 13421 | +0.00000 | [-0.00003 ; +0.00003] | 0.9120 | 1.0000 | 0.00004 | +0.00002, 0.702 | REJECTED |
| fb-H12 | meilleure cote contre moyenne | avgc | 7379 | -0.00005 | [-0.00026 ; +0.00016] | 0.6517 | 1.0000 | 0.00030 | -0.00001, 0.843 | REJECTED |
| fb-H13 | Pinnacle contre moyenne | avgc | 6228 | -0.00012 | [-0.00054 ; +0.00028] | 0.5859 | 1.0000 | 0.00059 | -0.00012, 0.215 | REJECTED |
| fb-H14 | calibration du marché | psc | 13430 | +0.00031 | [-0.00005 ; +0.00066] | 0.1052 | — | 0.00051 | — | REJECTED |

## Détail par hypothèse

### fb-H9 — repos et calendrier (marché : psc)

Matchs joués : 25538 ; éligibles (toutes les entrées présentes) : 24383 ; matchs de test : 13430 (saisons 2018 et suivantes).
Log loss moyen sur le test : marché brut 0.9676, marché recalibré 0.9673, avec signal 0.9674.
Contre le marché BRUT (descriptif) : gain +0.00028, IC 95 % [-0.00008 ; +0.00065], p = 0.1362.

REJETÉE : aucun gain au-dessus de 0,001 ; gain moyen -0.00002 de log loss par match (IC 95 % [-0.00008 ; +0.00003]), p = 0.3097, p corrigé (Holm) = 1.0000, plancher de détection 0.00008, 13430 matchs de test ; témoin placebo : gain -0.00006, p = 0.5705.

| Saison | Matchs | Ajust. | Brut | Recalibré | Avec signal | Gain | b | θ (écart-type) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 1825 | 10953 | 0.9611 | 0.9611 | 0.9613 | -0.00022 | 1.063 | -0.006 |
| 2019 | 1725 | 12778 | 0.9724 | 0.9727 | 0.9727 | +0.00000 | 1.061 | -0.000 |
| 2020 | 1826 | 14503 | 0.9773 | 0.9774 | 0.9774 | -0.00004 | 1.053 | -0.002 |
| 2021 | 1826 | 16329 | 0.9758 | 0.9758 | 0.9758 | -0.00001 | 1.054 | +0.001 |
| 2022 | 1826 | 18155 | 0.9749 | 0.9751 | 0.9751 | +0.00001 | 1.052 | -0.001 |
| 2023 | 1752 | 19981 | 0.9525 | 0.9511 | 0.9511 | +0.00001 | 1.048 | -0.002 |
| 2024 | 1752 | 21733 | 0.9606 | 0.9596 | 0.9595 | +0.00013 | 1.064 | -0.002 |
| 2025 | 898 | 23485 | 0.9641 | 0.9630 | 0.9631 | -0.00011 | 1.070 | -0.007 |

### fb-H10 — forme en tirs cadrés (marché : psc)

Matchs joués : 25538 ; éligibles (toutes les entrées présentes) : 23879 ; matchs de test : 13310 (saisons 2018 et suivantes).
Log loss moyen sur le test : marché brut 0.9678, marché recalibré 0.9676, avec signal 0.9676.
Contre le marché BRUT (descriptif) : gain +0.00027, IC 95 % [-0.00014 ; +0.00066], p = 0.2000.

REJETÉE : aucun gain au-dessus de 0,001 ; gain moyen -0.00001 de log loss par match (IC 95 % [-0.00009 ; +0.00007]), p = 0.8584, p corrigé (Holm) = 1.0000, plancher de détection 0.00011, 13310 matchs de test ; témoin placebo : gain -0.00002, p = 0.5395.

| Saison | Matchs | Ajust. | Brut | Recalibré | Avec signal | Gain | b | θ (écart-type) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 1813 | 10569 | 0.9601 | 0.9601 | 0.9601 | -0.00002 | 1.064 | +0.007 |
| 2019 | 1709 | 12382 | 0.9708 | 0.9710 | 0.9710 | +0.00002 | 1.063 | +0.006 |
| 2020 | 1810 | 14091 | 0.9769 | 0.9770 | 0.9769 | +0.00004 | 1.056 | +0.006 |
| 2021 | 1806 | 15901 | 0.9765 | 0.9767 | 0.9767 | -0.00003 | 1.057 | +0.008 |
| 2022 | 1810 | 17707 | 0.9767 | 0.9768 | 0.9768 | +0.00005 | 1.054 | +0.006 |
| 2023 | 1740 | 19517 | 0.9528 | 0.9515 | 0.9515 | -0.00009 | 1.050 | +0.008 |
| 2024 | 1736 | 21257 | 0.9612 | 0.9603 | 0.9603 | +0.00000 | 1.066 | +0.005 |
| 2025 | 886 | 22993 | 0.9665 | 0.9654 | 0.9654 | -0.00004 | 1.071 | +0.005 |

### fb-H11 — mouvement de Pinnacle (marché : psc)

Matchs joués : 25538 ; éligibles (toutes les entrées présentes) : 24359 ; matchs de test : 13421 (saisons 2018 et suivantes).
Log loss moyen sur le test : marché brut 0.9676, marché recalibré 0.9673, avec signal 0.9673.
Contre le marché BRUT (descriptif) : gain +0.00031, IC 95 % [-0.00006 ; +0.00067], p = 0.1140.

REJETÉE : aucun gain au-dessus de 0,001 ; gain moyen +0.00000 de log loss par match (IC 95 % [-0.00003 ; +0.00003]), p = 0.9120, p corrigé (Holm) = 1.0000, plancher de détection 0.00004, 13421 matchs de test ; témoin placebo : gain +0.00002, p = 0.7023.

| Saison | Matchs | Ajust. | Brut | Recalibré | Avec signal | Gain | b | θ (écart-type) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 1824 | 10938 | 0.9604 | 0.9603 | 0.9604 | -0.00002 | 1.063 | +0.004 |
| 2019 | 1723 | 12762 | 0.9730 | 0.9733 | 0.9734 | -0.00002 | 1.061 | +0.002 |
| 2020 | 1822 | 14485 | 0.9768 | 0.9768 | 0.9768 | -0.00000 | 1.053 | -0.000 |
| 2021 | 1824 | 16307 | 0.9760 | 0.9760 | 0.9760 | -0.00003 | 1.054 | +0.002 |
| 2022 | 1826 | 18131 | 0.9749 | 0.9751 | 0.9751 | -0.00000 | 1.052 | -0.001 |
| 2023 | 1752 | 19957 | 0.9525 | 0.9511 | 0.9511 | +0.00001 | 1.048 | -0.001 |
| 2024 | 1752 | 21709 | 0.9606 | 0.9596 | 0.9596 | +0.00002 | 1.065 | -0.002 |
| 2025 | 898 | 23461 | 0.9641 | 0.9630 | 0.9629 | +0.00013 | 1.070 | -0.003 |

### fb-H12 — meilleure cote contre moyenne (marché : avgc)

Matchs joués : 25538 ; éligibles (toutes les entrées présentes) : 12755 ; matchs de test : 7379 (saisons 2022 et suivantes).
Log loss moyen sur le test : marché brut 0.9669, marché recalibré 0.9662, avec signal 0.9663.
Contre le marché BRUT (descriptif) : gain +0.00061, IC 95 % [-0.00014 ; +0.00132], p = 0.0810.

REJETÉE : aucun gain au-dessus de 0,001 ; gain moyen -0.00005 de log loss par match (IC 95 % [-0.00026 ; +0.00016]), p = 0.6517, p corrigé (Holm) = 1.0000, plancher de détection 0.00030, 7379 matchs de test ; témoin placebo : gain -0.00001, p = 0.8430.

| Saison | Matchs | Ajust. | Brut | Recalibré | Avec signal | Gain | b | θ (écart-type) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 1826 | 5376 | 0.9756 | 0.9768 | 0.9768 | -0.00003 | 1.053 | -0.027 |
| 2023 | 1752 | 7202 | 0.9533 | 0.9517 | 0.9519 | -0.00025 | 1.047 | -0.021 |
| 2024 | 1752 | 8954 | 0.9608 | 0.9590 | 0.9589 | +0.00007 | 1.092 | -0.004 |
| 2025 | 1752 | 10706 | 0.9774 | 0.9769 | 0.9770 | -0.00010 | 1.104 | -0.028 |
| 2026 | 297 | 12458 | 0.9672 | 0.9671 | 0.9666 | +0.00055 | 1.107 | -0.022 |

### fb-H13 — Pinnacle contre moyenne (marché : avgc)

Matchs joués : 25538 ; éligibles (toutes les entrées présentes) : 11605 ; matchs de test : 6228 (saisons 2022 et suivantes).
Log loss moyen sur le test : marché brut 0.9634, marché recalibré 0.9625, avec signal 0.9626.
Contre le marché BRUT (descriptif) : gain +0.00071, IC 95 % [-0.00016 ; +0.00149], p = 0.1006.

REJETÉE : aucun gain au-dessus de 0,001 ; gain moyen -0.00012 de log loss par match (IC 95 % [-0.00054 ; +0.00028]), p = 0.5859, p corrigé (Holm) = 1.0000, plancher de détection 0.00059, 6228 matchs de test ; témoin placebo : gain -0.00012, p = 0.2146.

| Saison | Matchs | Ajust. | Brut | Recalibré | Avec signal | Gain | b | θ (écart-type) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 1826 | 5377 | 0.9756 | 0.9768 | 0.9764 | +0.00038 | 1.053 | +0.017 |
| 2023 | 1752 | 7203 | 0.9533 | 0.9517 | 0.9517 | +0.00002 | 1.047 | +0.027 |
| 2024 | 1752 | 8955 | 0.9608 | 0.9590 | 0.9591 | -0.00014 | 1.091 | +0.025 |
| 2025 | 898 | 10707 | 0.9631 | 0.9615 | 0.9629 | -0.00138 | 1.104 | +0.021 |

### fb-H14 — calibration du marché (marché : psc)

Matchs joués : 25538 ; éligibles (toutes les entrées présentes) : 24383 ; matchs de test : 13430 (saisons 2018 et suivantes).
Log loss moyen sur le test : marché brut 0.9676, marché recalibré 0.9673, avec signal 0.9673.

REJETÉE : aucun gain au-dessus de 0,001 ; gain moyen +0.00031 de log loss par match (IC 95 % [-0.00005 ; +0.00066]), p = 0.1052, plancher de détection 0.00051, 13430 matchs de test.

| Saison | Matchs | Ajust. | Brut | Recalibré | Avec signal | Gain | b | θ (écart-type) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 1825 | 10953 | 0.9611 | 0.9611 | 0.9611 | +0.00000 | 1.063 | +0.000 |
| 2019 | 1725 | 12778 | 0.9724 | 0.9727 | 0.9727 | +0.00000 | 1.061 | +0.000 |
| 2020 | 1826 | 14503 | 0.9773 | 0.9774 | 0.9774 | +0.00000 | 1.053 | +0.000 |
| 2021 | 1826 | 16329 | 0.9758 | 0.9758 | 0.9758 | +0.00000 | 1.054 | +0.000 |
| 2022 | 1826 | 18155 | 0.9749 | 0.9751 | 0.9751 | +0.00000 | 1.052 | +0.000 |
| 2023 | 1752 | 19981 | 0.9525 | 0.9511 | 0.9511 | +0.00000 | 1.048 | +0.000 |
| 2024 | 1752 | 21733 | 0.9606 | 0.9596 | 0.9596 | +0.00000 | 1.064 | +0.000 |
| 2025 | 898 | 23485 | 0.9641 | 0.9630 | 0.9630 | +0.00000 | 1.070 | +0.000 |

