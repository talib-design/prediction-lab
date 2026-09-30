# Simulation de paris fictifs — plat, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-09-30T04:55:54+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `e732bf3a4b39` · courses évaluées : 10335, dont 9653 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Tiercé favoris | 254 | 254 | 261 | +2.6 % | [-78.3 % ; +114.4 %] | 2.8 % | 38 % | indéterminé |
| Tiercé market_calibrated | 254 | 254 | 261 | +2.6 % | [-78.3 % ; +114.4 %] | 2.8 % | 38 % | indéterminé |
| SP favori | 6255 | 6255 | 5537 | -11.5 % | [-13.6 % ; -9.2 %] | 55.8 % | 0 % | perte significative |
| SP top market_calibrated | 6255 | 6255 | 5529 | -11.6 % | [-13.7 % ; -9.3 %] | 55.7 % | 0 % | perte significative |
| SG favori | 6257 | 6257 | 5441 | -13.0 % | [-17.2 % ; -8.9 %] | 26.8 % | 0 % | perte significative |
| SG top market_calibrated | 6257 | 6257 | 5441 | -13.0 % | [-17.2 % ; -8.9 %] | 26.8 % | 0 % | perte significative |
| SP top form | 6255 | 6255 | 5173 | -17.3 % | [-20.3 % ; -14.4 %] | 43.8 % | 0 % | perte significative |
| SG top form | 6257 | 6257 | 4989 | -20.3 % | [-25.4 % ; -14.8 %] | 18.4 % | 0 % | perte significative |
| SP top horse_win_rate | 6255 | 6255 | 4935 | -21.1 % | [-25.0 % ; -17.7 %] | 31.6 % | 0 % | perte significative |
| SG top horse_win_rate | 6257 | 6257 | 4928 | -21.2 % | [-28.4 % ; -14.1 %] | 12.8 % | 1 % | perte significative |
| SG hasard | 6257 | 6257 | 4922 | -21.3 % | [-29.6 % ; -13.3 %] | 10.5 % | 1 % | perte significative |
| SP hasard | 6255 | 6255 | 4838 | -22.6 % | [-27.0 % ; -18.3 %] | 27.5 % | 0 % | perte significative |
| SG valeur form | 6247 | 25985 | 19776 | -23.9 % | [-28.9 % ; -18.7 %] | 24.2 % | 1 % | perte significative |
| SG valeur horse_win_rate | 6252 | 30649 | 22599 | -26.3 % | [-30.8 % ; -21.4 %] | 22.8 % | 1 % | perte significative |
| Quinté favoris | 254 | 508 | 237 | -53.3 % | [-67.1 % ; -38.0 %] | 19.3 % | 5 % | perte significative |
| Quinté market_calibrated | 254 | 508 | 237 | -53.3 % | [-67.1 % ; -38.0 %] | 19.3 % | 5 % | perte significative |
| Tiercé form | 254 | 254 | 111 | -56.2 % | [-100.0 % ; +16.5 %] | 1.2 % | 66 % | indéterminé |
| Quinté form | 254 | 508 | 191 | -62.5 % | [-79.8 % ; -44.8 %] | 9.4 % | 14 % | perte significative |
| Quinté horse_win_rate | 254 | 508 | 144 | -71.7 % | [-90.5 % ; -48.5 %] | 3.9 % | 30 % | perte significative |
| Quinté hasard | 254 | 508 | 136 | -73.1 % | [-96.9 % ; -36.6 %] | 2.0 % | 56 % | perte significative |
| Tiercé horse_win_rate | 254 | 254 | 43 | -83.0 % | [-100.0 % ; -49.0 %] | 0.4 % | 100 % | perte significative |
| Tiercé hasard | 254 | 254 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase validation

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP favori | 3396 | 3396 | 3034 | -10.7 % | [-13.4 % ; -7.8 %] | 55.2 % | 0 % | perte significative |
| SP top market_calibrated | 3396 | 3396 | 3030 | -10.8 % | [-13.5 % ; -7.9 %] | 55.2 % | 0 % | perte significative |
| SG favori | 3396 | 3396 | 2872 | -15.4 % | [-21.2 % ; -9.5 %] | 26.1 % | 0 % | perte significative |
| SG top market_calibrated | 3396 | 3396 | 2872 | -15.4 % | [-21.2 % ; -9.5 %] | 26.1 % | 0 % | perte significative |
| SP top form | 3396 | 3396 | 2810 | -17.3 % | [-21.0 % ; -13.3 %] | 43.4 % | 1 % | perte significative |
| SG hasard | 3396 | 3396 | 2743 | -19.2 % | [-30.4 % ; -6.8 %] | 10.3 % | 4 % | perte significative |
| SP hasard | 3396 | 3396 | 2707 | -20.3 % | [-25.6 % ; -14.1 %] | 28.3 % | 1 % | perte significative |
| SP top horse_win_rate | 3396 | 3396 | 2640 | -22.3 % | [-27.0 % ; -17.2 %] | 32.4 % | 1 % | perte significative |
| SG top form | 3396 | 3396 | 2483 | -26.9 % | [-32.9 % ; -20.5 %] | 16.9 % | 1 % | perte significative |
| SG top horse_win_rate | 3396 | 3396 | 2416 | -28.9 % | [-37.1 % ; -19.8 %] | 12.9 % | 3 % | perte significative |
| SG valeur form | 3392 | 13639 | 9572 | -29.8 % | [-35.4 % ; -24.2 %] | 22.7 % | 1 % | perte significative |
| SG valeur horse_win_rate | 3394 | 15843 | 11005 | -30.5 % | [-35.8 % ; -24.8 %] | 22.2 % | 1 % | perte significative |
| Quinté hasard | 134 | 268 | 65 | -75.9 % | [-100.0 % ; -35.7 %] | 2.2 % | 62 % | perte significative |
| Quinté favoris | 134 | 268 | 59 | -77.9 % | [-88.1 % ; -66.0 %] | 9.7 % | 12 % | perte significative |
| Quinté market_calibrated | 134 | 268 | 59 | -77.9 % | [-88.1 % ; -66.0 %] | 9.7 % | 12 % | perte significative |
| Quinté form | 134 | 268 | 45 | -83.1 % | [-97.9 % ; -61.0 %] | 3.7 % | 42 % | perte significative |
| Tiercé favoris | 134 | 134 | 10 | -92.6 % | [-100.0 % ; -77.8 %] | 0.7 % | 100 % | perte significative |
| Tiercé market_calibrated | 134 | 134 | 10 | -92.6 % | [-100.0 % ; -77.8 %] | 0.7 % | 100 % | perte significative |
| Quinté horse_win_rate | 134 | 268 | 12 | -95.6 % | [-100.0 % ; -88.2 %] | 1.5 % | 68 % | perte significative |
| Tiercé hasard | 134 | 134 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 134 | 134 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé form | 134 | 134 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place

Marché calibré, phase test. Si « prévu » dépasse « observé » sur les fortes probabilités, Harville surestime les favoris pour les places (biais connu).

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.0-0.1 | 10042 | 0.073 | 0.070 |
| 0.1-0.2 | 23802 | 0.149 | 0.151 |
| 0.2-0.3 | 16660 | 0.247 | 0.265 |
| 0.3-0.4 | 9179 | 0.345 | 0.358 |
| 0.4-0.5 | 5077 | 0.445 | 0.443 |
| 0.5-0.6 | 2979 | 0.546 | 0.521 |
| 0.6-0.8 | 2645 | 0.682 | 0.623 |
| 0.8-1.0 | 1078 | 0.886 | 0.753 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
