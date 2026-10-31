# Simulation de paris fictifs — plat, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-31T07:35:46+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `a5a38a4d1f07` · courses évaluées : 24411, dont 23897 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Tiercé favoris | 265 | 265 | 268 | +1.0 % | [-75.8 % ; +109.9 %] | 3.0 % | 37 % | indéterminé |
| Tiercé market_calibrated | 265 | 265 | 268 | +1.0 % | [-75.8 % ; +109.9 %] | 3.0 % | 37 % | indéterminé |
| SP top market_calibrated | 6641 | 6641 | 5857 | -11.8 % | [-14.0 % ; -9.8 %] | 55.7 % | 0 % | perte significative |
| SP favori | 6641 | 6641 | 5855 | -11.8 % | [-14.0 % ; -9.8 %] | 55.7 % | 0 % | perte significative |
| SG favori | 6642 | 6642 | 5756 | -13.3 % | [-17.4 % ; -9.6 %] | 26.8 % | 0 % | perte significative |
| SG top market_calibrated | 6642 | 6642 | 5756 | -13.3 % | [-17.4 % ; -9.6 %] | 26.8 % | 0 % | perte significative |
| SP top form | 6641 | 6641 | 5486 | -17.4 % | [-20.0 % ; -14.6 %] | 43.8 % | 0 % | perte significative |
| SG top horse_win_rate | 6642 | 6642 | 5312 | -20.0 % | [-27.0 % ; -12.9 %] | 13.3 % | 1 % | perte significative |
| SG hasard | 6642 | 6642 | 5265 | -20.7 % | [-28.4 % ; -12.8 %] | 10.6 % | 1 % | perte significative |
| SG top form | 6642 | 6642 | 5235 | -21.2 % | [-26.3 % ; -15.7 %] | 18.5 % | 0 % | perte significative |
| SP top horse_win_rate | 6641 | 6641 | 5169 | -22.2 % | [-26.0 % ; -18.3 %] | 31.4 % | 0 % | perte significative |
| SP hasard | 6641 | 6641 | 5100 | -23.2 % | [-27.1 % ; -19.1 %] | 27.3 % | 0 % | perte significative |
| SG valeur horse_win_rate | 6638 | 32591 | 24640 | -24.4 % | [-28.8 % ; -19.9 %] | 22.8 % | 1 % | perte significative |
| SG valeur form | 6632 | 27581 | 20828 | -24.5 % | [-29.3 % ; -19.5 %] | 24.2 % | 1 % | perte significative |
| Quinté favoris | 265 | 530 | 283 | -46.6 % | [-65.8 % ; -33.8 %] | 19.6 % | 13 % | perte significative |
| Quinté market_calibrated | 265 | 530 | 283 | -46.6 % | [-65.8 % ; -33.8 %] | 19.6 % | 13 % | perte significative |
| Tiercé form | 265 | 265 | 111 | -58.0 % | [-100.0 % ; +6.4 %] | 1.1 % | 66 % | indéterminé |
| Quinté form | 265 | 530 | 191 | -64.0 % | [-79.2 % ; -44.8 %] | 9.1 % | 14 % | perte significative |
| Quinté hasard | 265 | 530 | 136 | -74.3 % | [-96.4 % ; -37.5 %] | 1.9 % | 56 % | perte significative |
| Quinté horse_win_rate | 265 | 530 | 109 | -79.5 % | [-95.3 % ; -57.8 %] | 2.3 % | 30 % | perte significative |
| Tiercé hasard | 265 | 265 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 265 | 265 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
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
| 0.0-0.1 | 10967 | 0.073 | 0.071 |
| 0.1-0.2 | 24955 | 0.149 | 0.153 |
| 0.2-0.3 | 17375 | 0.248 | 0.265 |
| 0.3-0.4 | 9647 | 0.345 | 0.358 |
| 0.4-0.5 | 5410 | 0.445 | 0.442 |
| 0.5-0.6 | 3196 | 0.546 | 0.514 |
| 0.6-0.8 | 2869 | 0.682 | 0.616 |
| 0.8-1.0 | 1202 | 0.887 | 0.751 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
