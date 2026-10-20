# Football — dossier de la semaine (2026-10-20T22:57 UTC)

Python calcule, le critique commente. Tous les chiffres viennent de ce dossier ; ce qui manque s'écrit « Je ne sais pas ». Aucune mise, aucun pari.

## 1. L'agent automatique

- État maintenant : Dernier passage il y a 5 min (attendu toutes les 5 min).
- Passages sur 7 jours : 10 sur 9 attendus depuis le premier passage (2026-10-20T22:11:00+00:00) ; avant, l'agent n'existait pas.
- Aucun trou de plus de 30 min sur la fenêtre.
- Journal d'erreurs : 0 ligne(s).

## 2. Captures et crédits

- calendrier : 2 ok, 0 échec(s), dernière réussie 2026-10-20T22:11
- cotes : 1 ok, 0 échec(s), dernière réussie 2026-10-20T22:11
- scores : 0 ok, 0 échec(s), dernière réussie jamais
- Crédits de cotes ce mois : 2/400

## 3. Matchs des 7 derniers jours

18 match(s) terminé(s) : 18 avant le premier passage de l'agent (impossibles à figer), 0 manqué(s) alors que l'agent tournait.

| Coup d'envoi (UTC) | Match | Statut | Avant l'agent | Figée | Réglée | Notée |
|---|---|---|---|---|---|---|
| 2026-10-14T16:45 | LASK Linz – Liverpool FC | FINISHED | oui | non | non | non |
| 2026-10-14T16:45 | Feyenoord Rotterdam – Como 1907 | FINISHED | oui | non | non | non |
| 2026-10-14T19:00 | AS Roma – Real Madrid CF | FINISHED | oui | non | non | non |
| 2026-10-14T19:00 | Manchester City FC – Paris Saint-Germain FC | FINISHED | oui | non | non | non |
| 2026-10-14T19:00 | FK Bodø/Glimt – Borussia Dortmund | FINISHED | oui | non | non | non |
| 2026-10-14T19:00 | Aston Villa FC – Fenerbahçe SK | FINISHED | oui | non | non | non |
| 2026-10-14T19:00 | Real Betis Balompié – FC Porto | FINISHED | oui | non | non | non |
| 2026-10-14T19:00 | FK Shakhtar Donetsk – PAE AEK | FINISHED | oui | non | non | non |
| 2026-10-14T19:00 | ŠK Slovan Bratislava – VfB Stuttgart | FINISHED | oui | non | non | non |
| 2026-10-20T16:45 | Sabah FK – Borussia Dortmund | FINISHED | oui | non | non | non |
| 2026-10-20T16:45 | Fenerbahçe SK – SK Slavia Praha | FINISHED | oui | non | non | non |
| 2026-10-20T19:00 | Manchester City FC – PAE AEK | FINISHED | oui | non | non | non |
| 2026-10-20T19:00 | VfB Stuttgart – Club Atlético de Madrid | FINISHED | oui | non | non | non |
| 2026-10-20T19:00 | Liverpool FC – Villarreal CF | FINISHED | oui | non | non | non |
| 2026-10-20T19:00 | AS Roma – ŠK Slovan Bratislava | FINISHED | oui | non | non | non |
| 2026-10-20T19:00 | FC Porto – PSV | FINISHED | oui | non | non | non |
| 2026-10-20T19:00 | SSC Napoli – FK Bodø/Glimt | FINISHED | oui | non | non | non |
| 2026-10-20T19:00 | Paris Saint-Germain FC – FC Barcelona | FINISHED | oui | non | non | non |

## 4. Carnet à terme

0 prévision(s) figée(s), 0 réglée(s), 0 notée(s) ; verdict fb-H8 à partir de 100.

## 5. Ce que le carnet peut voir (puissance)

- Écart-type par match de l'écart de log loss (plus/moins dérivé contre marché) : 0.062 (football_derive_2026-10-17, 5553 matchs, écart moyen +0.0028).
- Demi-largeur de l'IC 95 % avec 0 match(s) notés : non calculable ; à 100 matchs : 0.0121.
- Matchs nécessaires pour que l'IC exclue zéro si l'écart observé se confirme : 1897.

## 6. Hypothèses du registre

| Id | Statut | Révision | Conclusion |
|---|---|---:|---|
| fb-H1 | PROPOSED | 0 | — |
| fb-H2 | PROPOSED | 0 | — |
| fb-H3 | PROPOSED | 0 | — |
| fb-H4 | PROPOSED | 0 | — |
| fb-H5 | PROPOSED | 0 | — |
| fb-H6 | PROPOSED | 0 | — |
| fb-H7 | PROPOSED | 0 | — |
| fb-H8 | PROPOSED | 0 | — |
| fb-H9 | REJECTED | 1 | REJETÉE : aucun gain au-dessus de 0,001 ; gain moyen -0.00002 de log loss par match (IC 95 % [-0.00008 ; +0.00003]), p = 0.3097, p corrigé (Holm) = 1.0000, plancher de détection 0.00008, 13430 matchs de test ; témoin placebo : gain -0.00006, p = 0.5705. |
| fb-H10 | REJECTED | 1 | REJETÉE : aucun gain au-dessus de 0,001 ; gain moyen -0.00001 de log loss par match (IC 95 % [-0.00009 ; +0.00007]), p = 0.8584, p corrigé (Holm) = 1.0000, plancher de détection 0.00011, 13310 matchs de test ; témoin placebo : gain -0.00002, p = 0.5395. |
| fb-H11 | REJECTED | 1 | REJETÉE : aucun gain au-dessus de 0,001 ; gain moyen +0.00000 de log loss par match (IC 95 % [-0.00003 ; +0.00003]), p = 0.9120, p corrigé (Holm) = 1.0000, plancher de détection 0.00004, 13421 matchs de test ; témoin placebo : gain +0.00002, p = 0.7023. |
| fb-H12 | REJECTED | 1 | REJETÉE : aucun gain au-dessus de 0,001 ; gain moyen -0.00005 de log loss par match (IC 95 % [-0.00026 ; +0.00016]), p = 0.6517, p corrigé (Holm) = 1.0000, plancher de détection 0.00030, 7379 matchs de test ; témoin placebo : gain -0.00001, p = 0.8430. |
| fb-H13 | REJECTED | 1 | REJETÉE : aucun gain au-dessus de 0,001 ; gain moyen -0.00012 de log loss par match (IC 95 % [-0.00054 ; +0.00028]), p = 0.5859, p corrigé (Holm) = 1.0000, plancher de détection 0.00059, 6228 matchs de test ; témoin placebo : gain -0.00012, p = 0.2146. |
| fb-H14 | REJECTED | 1 | REJETÉE : aucun gain au-dessus de 0,001 ; gain moyen +0.00031 de log loss par match (IC 95 % [-0.00005 ; +0.00066]), p = 0.1052, plancher de détection 0.00051, 13430 matchs de test. |

## 7. Banc de signaux (marché + un signal)

Rapport `football_signals_2026-10-21` (football-signals-v1).

| Id | Signal | Verdict | Matchs test | Gain moyen | IC 95 % |
|---|---|---|---:|---:|---|
| fb-H9 | repos et calendrier | REJECTED | 13430 | -0.00002 | [-0.00008 ; +0.00003] |
| fb-H10 | forme en tirs cadrés | REJECTED | 13310 | -0.00001 | [-0.00009 ; +0.00007] |
| fb-H11 | mouvement de Pinnacle | REJECTED | 13421 | +0.00000 | [-0.00003 ; +0.00003] |
| fb-H12 | meilleure cote contre moyenne | REJECTED | 7379 | -0.00005 | [-0.00026 ; +0.00016] |
| fb-H13 | Pinnacle contre moyenne | REJECTED | 6228 | -0.00012 | [-0.00054 ; +0.00028] |
| fb-H14 | calibration du marché | REJECTED | 13430 | +0.00031 | [-0.00005 ; +0.00066] |

## 8. Structure du marché sur les bookmakers capturés

Relevé du 2026-10-20T22:11 : 9 match(s), 9 avec Pinnacle. Descriptif sur un seul relevé, à plus de 2 h du coup d'envoi : aucun verdict, aucune mise. Aucun seuil « normal » n'est établi pour ces écarts : Je ne sais pas.

| Coup d'envoi | Match | Books | Moyenne (1/N/2) | Écart-type entre books | Pinnacle − moyenne |
|---|---|---:|---|---|---|
| 2026-10-21T16:45 | Como – Manchester United | 39 | 0.435 / 0.251 / 0.314 | 0.005 / 0.005 / 0.004 | +0.003 / -0.004 / +0.001 |
| 2026-10-21T16:45 | Lille – Galatasaray | 39 | 0.438 / 0.254 / 0.308 | 0.005 / 0.005 / 0.004 | +0.000 / +0.001 / -0.002 |
| 2026-10-21T19:00 | Bayern Munich – Arsenal | 39 | 0.468 / 0.248 / 0.284 | 0.008 / 0.004 / 0.008 | -0.003 / -0.006 / +0.009 |
| 2026-10-21T19:00 | Aston Villa – Viking FK | 39 | 0.780 / 0.138 / 0.081 | 0.009 / 0.005 / 0.007 | +0.005 / -0.001 / -0.004 |
| 2026-10-21T19:00 | Club Brugge – RC Lens | 39 | 0.477 / 0.234 / 0.288 | 0.008 / 0.005 / 0.006 | +0.001 / -0.004 / +0.003 |
| 2026-10-21T19:00 | Real Betis – Feyenoord | 39 | 0.614 / 0.201 / 0.185 | 0.009 / 0.006 / 0.007 | +0.008 / -0.004 / -0.004 |
| 2026-10-21T19:00 | Inter Milan – Shakhtar Donetsk | 39 | 0.792 / 0.128 / 0.080 | 0.012 / 0.005 / 0.009 | +0.005 / -0.005 / -0.001 |
| 2026-10-21T19:00 | Sporting Lisbon – LASK | 38 | 0.803 / 0.121 / 0.076 | 0.011 / 0.005 / 0.007 | +0.002 / -0.006 / +0.003 |
| 2026-10-21T19:00 | Real Madrid – RB Leipzig | 39 | 0.765 / 0.135 / 0.100 | 0.011 / 0.006 / 0.008 | +0.002 / -0.002 / -0.000 |
