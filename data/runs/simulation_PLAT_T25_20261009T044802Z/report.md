# Simulation de paris fictifs — plat, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-09T04:48:02+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `27b3cdc06ffc` · courses évaluées : 24132, dont 23620 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Tiercé favoris | 257 | 257 | 268 | +4.2 % | [-77.2 % ; +105.8 %] | 3.1 % | 37 % | indéterminé |
| Tiercé market_calibrated | 257 | 257 | 268 | +4.2 % | [-77.2 % ; +105.8 %] | 3.1 % | 37 % | indéterminé |
| SP top market_calibrated | 6364 | 6364 | 5639 | -11.4 % | [-13.6 % ; -9.3 %] | 55.9 % | 0 % | perte significative |
| SP favori | 6364 | 6364 | 5638 | -11.4 % | [-13.6 % ; -9.3 %] | 55.9 % | 0 % | perte significative |
| SG favori | 6366 | 6366 | 5552 | -12.8 % | [-16.7 % ; -8.7 %] | 26.9 % | 0 % | perte significative |
| SG top market_calibrated | 6366 | 6366 | 5552 | -12.8 % | [-16.7 % ; -8.7 %] | 26.9 % | 0 % | perte significative |
| SP top form | 6364 | 6364 | 5275 | -17.1 % | [-19.7 % ; -14.5 %] | 44.0 % | 0 % | perte significative |
| SG top horse_win_rate | 6366 | 6366 | 5127 | -19.5 % | [-27.0 % ; -12.5 %] | 13.3 % | 1 % | perte significative |
| SG top form | 6366 | 6366 | 5051 | -20.7 % | [-25.7 % ; -15.5 %] | 18.4 % | 0 % | perte significative |
| SG hasard | 6366 | 6366 | 5049 | -20.7 % | [-28.9 % ; -13.1 %] | 10.6 % | 1 % | perte significative |
| SP top horse_win_rate | 6364 | 6364 | 4978 | -21.8 % | [-25.7 % ; -18.0 %] | 31.4 % | 0 % | perte significative |
| SP hasard | 6364 | 6364 | 4907 | -22.9 % | [-27.1 % ; -18.5 %] | 27.4 % | 0 % | perte significative |
| SG valeur form | 6356 | 26463 | 20196 | -23.7 % | [-28.6 % ; -18.6 %] | 24.3 % | 1 % | perte significative |
| SG valeur horse_win_rate | 6362 | 31277 | 23734 | -24.1 % | [-28.9 % ; -19.5 %] | 22.8 % | 1 % | perte significative |
| Quinté favoris | 257 | 514 | 240 | -53.3 % | [-66.5 % ; -39.1 %] | 19.5 % | 5 % | perte significative |
| Quinté market_calibrated | 257 | 514 | 240 | -53.3 % | [-66.5 % ; -39.1 %] | 19.5 % | 5 % | perte significative |
| Tiercé form | 257 | 257 | 111 | -56.7 % | [-100.0 % ; +9.7 %] | 1.2 % | 66 % | indéterminé |
| Quinté form | 257 | 514 | 191 | -62.9 % | [-78.5 % ; -44.1 %] | 9.3 % | 14 % | perte significative |
| Quinté hasard | 257 | 514 | 136 | -73.5 % | [-96.3 % ; -37.0 %] | 1.9 % | 56 % | perte significative |
| Quinté horse_win_rate | 257 | 514 | 109 | -78.9 % | [-94.9 % ; -58.6 %] | 2.3 % | 30 % | perte significative |
| Tiercé hasard | 257 | 257 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 257 | 257 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase train

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Tiercé form | 616 | 616 | 620 | +0.7 % | [-87.7 % ; +146.7 %] | 1.0 % | 61 % | indéterminé |
| SP favori | 15360 | 15360 | 13442 | -12.5 % | [-13.7 % ; -11.2 %] | 54.8 % | 0 % | perte significative |
| SP top market_calibrated | 15360 | 15360 | 13438 | -12.5 % | [-13.8 % ; -11.2 %] | 54.8 % | 0 % | perte significative |
| SG favori | 15360 | 15360 | 13125 | -14.6 % | [-16.9 % ; -12.0 %] | 26.8 % | 0 % | perte significative |
| SG top market_calibrated | 15360 | 15360 | 13125 | -14.6 % | [-16.9 % ; -12.0 %] | 26.8 % | 0 % | perte significative |
| SP top form | 15360 | 15360 | 12752 | -17.0 % | [-18.7 % ; -15.2 %] | 43.7 % | 0 % | perte significative |
| SG top form | 15360 | 15360 | 12531 | -18.4 % | [-21.8 % ; -14.8 %] | 18.7 % | 0 % | perte significative |
| SP top horse_win_rate | 15360 | 15360 | 12070 | -21.4 % | [-23.7 % ; -19.1 %] | 33.0 % | 0 % | perte significative |
| SG hasard | 15360 | 15360 | 12055 | -21.5 % | [-26.5 % ; -16.2 %] | 10.2 % | 1 % | perte significative |
| SP hasard | 15360 | 15360 | 11924 | -22.4 % | [-25.0 % ; -19.9 %] | 28.0 % | 0 % | perte significative |
| SG top horse_win_rate | 15360 | 15360 | 11876 | -22.7 % | [-26.9 % ; -18.4 %] | 13.4 % | 0 % | perte significative |
| SG valeur form | 15328 | 61576 | 45532 | -26.1 % | [-29.0 % ; -23.0 %] | 23.2 % | 0 % | perte significative |
| SG valeur horse_win_rate | 15351 | 72150 | 52987 | -26.6 % | [-29.5 % ; -23.3 %] | 22.1 % | 0 % | perte significative |
| Tiercé favoris | 616 | 616 | 306 | -50.3 % | [-73.2 % ; -22.5 %] | 2.8 % | 16 % | perte significative |
| Tiercé market_calibrated | 616 | 616 | 306 | -50.3 % | [-73.2 % ; -22.5 %] | 2.8 % | 16 % | perte significative |
| Quinté form | 616 | 1232 | 607 | -50.7 % | [-84.5 % ; +10.6 %] | 4.9 % | 54 % | indéterminé |
| Quinté favoris | 616 | 1232 | 351 | -71.5 % | [-78.9 % ; -62.6 %] | 10.2 % | 7 % | perte significative |
| Quinté market_calibrated | 616 | 1232 | 351 | -71.5 % | [-78.9 % ; -62.6 %] | 10.2 % | 7 % | perte significative |
| Quinté hasard | 616 | 1232 | 293 | -76.2 % | [-88.3 % ; -61.1 %] | 2.9 % | 22 % | perte significative |
| Tiercé horse_win_rate | 616 | 616 | 66 | -89.2 % | [-100.0 % ; -67.6 %] | 0.2 % | 100 % | perte significative |
| Quinté horse_win_rate | 616 | 1232 | 114 | -90.7 % | [-96.8 % ; -82.8 %] | 1.6 % | 26 % | perte significative |
| Tiercé hasard | 616 | 616 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase validation

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP top market_calibrated | 1893 | 1893 | 1690 | -10.7 % | [-14.2 % ; -6.7 %] | 55.6 % | 0 % | perte significative |
| SP favori | 1893 | 1893 | 1688 | -10.8 % | [-14.3 % ; -6.8 %] | 55.6 % | 0 % | perte significative |
| SG favori | 1893 | 1893 | 1630 | -13.9 % | [-21.6 % ; -6.0 %] | 26.5 % | 1 % | perte significative |
| SG top market_calibrated | 1893 | 1893 | 1630 | -13.9 % | [-21.6 % ; -6.0 %] | 26.5 % | 1 % | perte significative |
| SG hasard | 1893 | 1893 | 1622 | -14.3 % | [-31.0 % ; +5.9 %] | 10.2 % | 7 % | indéterminé |
| SG top horse_win_rate | 1893 | 1893 | 1591 | -16.0 % | [-31.2 % ; +0.0 %] | 13.2 % | 4 % | indéterminé |
| SP top form | 1893 | 1893 | 1582 | -16.4 % | [-21.3 % ; -11.6 %] | 45.6 % | 0 % | perte significative |
| SP hasard | 1893 | 1893 | 1531 | -19.1 % | [-26.9 % ; -10.6 %] | 27.9 % | 2 % | perte significative |
| SP top horse_win_rate | 1893 | 1893 | 1524 | -19.5 % | [-26.0 % ; -13.3 %] | 33.7 % | 1 % | perte significative |
| SG top form | 1893 | 1893 | 1381 | -27.0 % | [-35.8 % ; -17.5 %] | 18.0 % | 1 % | perte significative |
| SG valeur horse_win_rate | 1893 | 9002 | 6339 | -29.6 % | [-37.4 % ; -22.0 %] | 21.2 % | 2 % | perte significative |
| SG valeur form | 1888 | 7697 | 5407 | -29.8 % | [-37.7 % ; -22.1 %] | 22.7 % | 2 % | perte significative |
| Quinté form | 70 | 140 | 53 | -61.9 % | [-90.9 % ; -18.0 %] | 7.1 % | 36 % | perte significative |
| Quinté favoris | 70 | 140 | 31 | -77.6 % | [-91.7 % ; -61.6 %] | 10.0 % | 19 % | perte significative |
| Quinté market_calibrated | 70 | 140 | 31 | -77.6 % | [-91.7 % ; -61.6 %] | 10.0 % | 19 % | perte significative |
| Quinté horse_win_rate | 70 | 140 | 27 | -80.9 % | [-100.0 % ; -55.1 %] | 2.9 % | 67 % | perte significative |
| Quinté hasard | 70 | 140 | 7 | -94.9 % | [-100.0 % ; -84.6 %] | 1.4 % | 100 % | perte significative |
| Tiercé favoris | 70 | 70 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé hasard | 70 | 70 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé market_calibrated | 70 | 70 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 70 | 70 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé form | 70 | 70 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place

Marché calibré, phase test. Si « prévu » dépasse « observé » sur les fortes probabilités, Harville surestime les favoris pour les places (biais connu).

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.0-0.1 | 10510 | 0.073 | 0.071 |
| 0.1-0.2 | 24060 | 0.149 | 0.152 |
| 0.2-0.3 | 16677 | 0.248 | 0.266 |
| 0.3-0.4 | 9275 | 0.345 | 0.357 |
| 0.4-0.5 | 5164 | 0.445 | 0.444 |
| 0.5-0.6 | 3055 | 0.546 | 0.517 |
| 0.6-0.8 | 2741 | 0.682 | 0.618 |
| 0.8-1.0 | 1151 | 0.887 | 0.751 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
