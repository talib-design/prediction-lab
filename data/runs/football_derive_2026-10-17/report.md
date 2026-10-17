# Déclinaisons du 1X2 : vérification (2026-10-17)

Entrée : cote de clôture moyenne des bookmakers (AvgC), marge retirée. Sortie : buts attendus par équipe, puis plus/moins de 2,5 buts, les deux marquent, score exact. Hypothèse : `fb-H8`.

Recalibrage de P(plus de 2,5) : logit corrigé = +0.1453 + 0.9165 × logit brut, ajusté sur 2019–2022 (7203 matchs) ; rho fixé à -0.05.

## Contrôle 2023–2026 (5553 matchs)

| Mesure | Brut | Recalibré | Observé |
|---|---|---|---|
| Buts par match | 2.715 | 2.851 | 2.840 |
| P(plus de 2,5) moyenne | 50.2 % | 53.5 % | 54.2 % |
| Log loss plus/moins 2,5 | 0.6702 | 0.6669 | (constante : 0.6897) |
| P(les deux marquent) moyenne | 50.5 % | 53.3 % | 55.1 % |
| Log loss les deux marquent | 0.6846 | 0.6805 | (constante : 0.6879) |

Plus/moins 2,5, brut, contre la cote de marché (5553 matchs) : différence de log loss +0.0061, IC 95 % [+0.0037 ; +0.0084], verdict « worse ».
Plus/moins 2,5, recalibré, contre la cote de marché (5553 matchs) : différence de log loss +0.0028, IC 95 % [+0.0013 ; +0.0045], verdict « worse ».

Score exact (recalibré) : le plus probable est le bon dans 13.0 % des matchs ; le score réel est parmi les 6 plus probables dans 56.9 % (masse prévue : 55.1 %).

## Critères de fb-H8 (fixés avant le calcul corrigé)

- a_biais_buts_dans_0_03 : +0.0113 → rempli
- b_borne_haute_vs_marche_sous_0_005 : +0.0045 → rempli
- c_deux_marquent_mieux_que_frequence : -0.0073 → rempli

## Par saison (recalibré)

| Saison | Matchs | Buts prévus | Buts observés | Plus 2,5 prévu | observé |
|---|---|---|---|---|---|
| 2023 | 1752 | 2.884 | 2.885 | 54.2 % | 54.9 % |
| 2024 | 1752 | 2.837 | 2.827 | 53.1 % | 53.4 % |
| 2025 | 1752 | 2.812 | 2.765 | 52.6 % | 53.0 % |
| 2026 | 297 | 2.969 | 3.094 | 56.0 % | 60.9 % |

## Limites

- Le biais brut a été vu sur 2019–2026 avant l'inscription de fb-H8 : le contrôle 2023–2026 vérifie la stabilité du réglage, il ne le confirme pas à l'aveugle.
- Le réglage vient de cinq championnats nationaux ; il peut ne pas se transférer à la Ligue des champions (fb-H8 prévoit le test sur le carnet à terme).
- Ce sont des traductions du marché, pas un signal indépendant : aucune affirmation de supériorité sur les bookmakers.
