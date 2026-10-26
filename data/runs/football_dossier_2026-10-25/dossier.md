# Football — dossier de la semaine (2026-10-25T19:08 UTC)

Python calcule, le critique commente. Tous les chiffres viennent de ce dossier ; ce qui manque s'écrit « Je ne sais pas ». Aucune mise, aucun pari.

## 1. L'agent automatique

- État maintenant : Dernier passage il y a 2 min (attendu toutes les 5 min).
- Passages sur 7 jours : 882 sur 1404 attendus depuis le premier passage (2026-10-20T22:11:00+00:00) ; avant, l'agent n'existait pas.
- Trous de plus de 30 min (« match » = un match était à couvrir) :
  - 2026-10-25T04:48 → 2026-10-25T07:51 : 183 min, sans match
  - 2026-10-25T07:51 → 2026-10-25T09:28 : 97 min, sans match
  - 2026-10-25T09:28 → 2026-10-25T10:44 : 76 min, sans match
  - 2026-10-25T10:44 → 2026-10-25T11:59 : 75 min, sans match
  - 2026-10-25T11:59 → 2026-10-25T14:17 : 138 min, sans match
  - 2026-10-25T14:17 → 2026-10-25T14:56 : 39 min, sans match
  - 2026-10-25T14:56 → 2026-10-25T17:42 : 166 min, sans match
  - 2026-10-25T17:42 → 2026-10-25T19:06 : 84 min, sans match
- Journal d'erreurs : 0 ligne(s).

## 2. Captures et crédits

- calendrier : 112 ok, 0 échec(s), dernière réussie 2026-10-25T07:51
- cotes : 17 ok, 0 échec(s), dernière réussie 2026-10-21T21:03
- scores : 25 ok, 0 échec(s), dernière réussie 2026-10-21T21:03
- Crédits de cotes ce mois : 59/400

## 3. Matchs des 7 derniers jours

18 match(s) terminé(s) : 9 avant le premier passage de l'agent (impossibles à figer), 0 manqué(s) alors que l'agent tournait.

| Coup d'envoi (UTC) | Match | Statut | Avant l'agent | Figée | Réglée | Notée |
|---|---|---|---|---|---|---|
| 2026-10-20T16:45 | Sabah FK – Borussia Dortmund | FINISHED | oui | non | non | non |
| 2026-10-20T16:45 | Fenerbahçe SK – SK Slavia Praha | FINISHED | oui | non | non | non |
| 2026-10-20T19:00 | Manchester City FC – PAE AEK | FINISHED | oui | non | non | non |
| 2026-10-20T19:00 | VfB Stuttgart – Club Atlético de Madrid | FINISHED | oui | non | non | non |
| 2026-10-20T19:00 | Liverpool FC – Villarreal CF | FINISHED | oui | non | non | non |
| 2026-10-20T19:00 | AS Roma – ŠK Slovan Bratislava | FINISHED | oui | non | non | non |
| 2026-10-20T19:00 | FC Porto – PSV | FINISHED | oui | non | non | non |
| 2026-10-20T19:00 | SSC Napoli – FK Bodø/Glimt | FINISHED | oui | non | non | non |
| 2026-10-20T19:00 | Paris Saint-Germain FC – FC Barcelona | FINISHED | oui | non | non | non |
| 2026-10-21T16:45 | Como 1907 – Manchester United FC | FINISHED | non | oui | oui | oui |
| 2026-10-21T16:45 | Lille OSC – Galatasaray SK | FINISHED | non | oui | oui | oui |
| 2026-10-21T19:00 | Real Madrid CF – RB Leipzig | FINISHED | non | oui | oui | oui |
| 2026-10-21T19:00 | FC Internazionale Milano – FK Shakhtar Donetsk | FINISHED | non | oui | oui | oui |
| 2026-10-21T19:00 | FC Bayern München – Arsenal FC | FINISHED | non | oui | oui | oui |
| 2026-10-21T19:00 | Club Brugge KV – Racing Club de Lens | FINISHED | non | oui | oui | oui |
| 2026-10-21T19:00 | Aston Villa FC – Viking FK | FINISHED | non | oui | oui | oui |
| 2026-10-21T19:00 | Sporting Clube de Portugal – LASK Linz | FINISHED | non | oui | oui | oui |
| 2026-10-21T19:00 | Real Betis Balompié – Feyenoord Rotterdam | FINISHED | non | oui | oui | oui |

## 4. Carnet à terme

9 prévision(s) figée(s), 9 réglée(s), 9 notée(s) ; verdict fb-H8 à partir de 100.
- 1X2 : log loss marché 0.8464, labo 0.8450.
- Plus de 2,5 buts : prévu 68.2 %, observé 77.8 %, log loss 0.5920.
- Les deux marquent : prévu 62.2 %, observé 66.7 %, log loss 0.6494.

## 5. Ce que le carnet peut voir (puissance)

- Écart-type par match de l'écart de log loss (plus/moins dérivé contre marché) : 0.062 (football_derive_2026-10-17, 5553 matchs, écart moyen +0.0028).
- Demi-largeur de l'IC 95 % avec 9 match(s) notés : 0.0402 ; à 100 matchs : 0.0121.
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

Relevé du 2026-10-21T21:03 : 11 match(s), 4 avec Pinnacle. Descriptif sur un seul relevé, à plus de 2 h du coup d'envoi : aucun verdict, aucune mise. Aucun seuil « normal » n'est établi pour ces écarts : Je ne sais pas.

| Coup d'envoi | Match | Books | Moyenne (1/N/2) | Écart-type entre books | Pinnacle − moyenne |
|---|---|---:|---|---|---|
| 2026-10-21T19:00 | Bayern Munich – Arsenal | 28 | 0.096 / 0.834 / 0.070 | 0.148 / 0.180 / 0.054 | +0.076 / -0.161 / +0.085 |
| 2026-10-21T19:00 | Club Brugge – RC Lens | 3 | 0.533 / 0.244 / 0.223 | 0.282 / 0.126 / 0.156 | pas de Pinnacle |
| 2026-10-21T19:00 | Real Betis – Feyenoord | 19 | 0.916 / 0.078 / 0.006 | 0.045 / 0.039 / 0.007 | -0.084 / +0.072 / +0.012 |
| 2026-10-21T19:00 | Inter Milan – Shakhtar Donetsk | 20 | 0.886 / 0.098 / 0.017 | 0.147 / 0.107 / 0.041 | -0.080 / +0.073 / +0.007 |
| 2026-10-21T19:00 | Sporting Lisbon – LASK | 26 | 0.033 / 0.126 / 0.841 | 0.074 / 0.061 / 0.128 | -0.020 / -0.060 / +0.079 |
| 2026-10-21T19:00 | Real Madrid – RB Leipzig | 4 | 0.642 / 0.190 / 0.168 | 0.309 / 0.144 / 0.165 | pas de Pinnacle |
| 2026-11-03T20:00 | Atlético Madrid – Bayern Munich | 8 | 0.285 / 0.271 / 0.444 | 0.005 / 0.008 / 0.006 | pas de Pinnacle |
| 2026-11-03T20:00 | Villarreal – Paris Saint Germain | 10 | 0.240 / 0.247 / 0.513 | 0.003 / 0.004 / 0.003 | pas de Pinnacle |
| 2026-11-04T17:45 | AEK Athens – Real Madrid | 15 | 0.140 / 0.190 / 0.670 | 0.036 / 0.022 / 0.055 | pas de Pinnacle |
| 2026-11-04T20:00 | Slavia Praha – Arsenal | 9 | 0.128 / 0.196 / 0.677 | 0.009 / 0.005 / 0.012 | pas de Pinnacle |
| 2026-11-04T20:00 | Porto – Napoli | 17 | 0.444 / 0.267 / 0.289 | 0.041 / 0.025 / 0.016 | pas de Pinnacle |
