# Simulation de paris fictifs — plat, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-27T00:38:07+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `2ae4d7c61ee7` · courses évaluées : 24370, dont 23857 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Tiercé favoris | 264 | 264 | 268 | +1.4 % | [-75.8 % ; +108.5 %] | 3.0 % | 37 % | indéterminé |
| Tiercé market_calibrated | 264 | 264 | 268 | +1.4 % | [-75.8 % ; +108.5 %] | 3.0 % | 37 % | indéterminé |
| SP top market_calibrated | 6601 | 6601 | 5830 | -11.7 % | [-13.8 % ; -9.5 %] | 55.7 % | 0 % | perte significative |
| SP favori | 6601 | 6601 | 5828 | -11.7 % | [-13.8 % ; -9.6 %] | 55.7 % | 0 % | perte significative |
| SG favori | 6602 | 6602 | 5728 | -13.2 % | [-17.2 % ; -9.2 %] | 26.9 % | 0 % | perte significative |
| SG top market_calibrated | 6602 | 6602 | 5728 | -13.2 % | [-17.2 % ; -9.2 %] | 26.9 % | 0 % | perte significative |
| SP top form | 6601 | 6601 | 5462 | -17.3 % | [-19.9 % ; -14.5 %] | 43.9 % | 0 % | perte significative |
| SG top horse_win_rate | 6602 | 6602 | 5296 | -19.8 % | [-27.0 % ; -12.7 %] | 13.4 % | 1 % | perte significative |
| SG hasard | 6602 | 6602 | 5228 | -20.8 % | [-28.6 % ; -13.0 %] | 10.6 % | 1 % | perte significative |
| SG top form | 6602 | 6602 | 5220 | -20.9 % | [-26.0 % ; -15.4 %] | 18.5 % | 0 % | perte significative |
| SP top horse_win_rate | 6601 | 6601 | 5153 | -21.9 % | [-25.8 % ; -18.1 %] | 31.4 % | 0 % | perte significative |
| SP hasard | 6601 | 6601 | 5076 | -23.1 % | [-27.2 % ; -19.1 %] | 27.3 % | 0 % | perte significative |
| SG valeur form | 6592 | 27404 | 20769 | -24.2 % | [-29.2 % ; -19.6 %] | 24.2 % | 1 % | perte significative |
| SG valeur horse_win_rate | 6598 | 32395 | 24527 | -24.3 % | [-28.8 % ; -19.7 %] | 22.8 % | 1 % | perte significative |
| Quinté favoris | 264 | 528 | 283 | -46.4 % | [-66.4 % ; -36.4 %] | 19.7 % | 13 % | perte significative |
| Quinté market_calibrated | 264 | 528 | 283 | -46.4 % | [-66.4 % ; -36.4 %] | 19.7 % | 13 % | perte significative |
| Tiercé form | 264 | 264 | 111 | -57.8 % | [-100.0 % ; +9.8 %] | 1.1 % | 66 % | indéterminé |
| Quinté form | 264 | 528 | 191 | -63.9 % | [-78.8 % ; -45.3 %] | 9.1 % | 14 % | perte significative |
| Quinté hasard | 264 | 528 | 136 | -74.2 % | [-96.4 % ; -38.8 %] | 1.9 % | 56 % | perte significative |
| Quinté horse_win_rate | 264 | 528 | 109 | -79.4 % | [-95.3 % ; -59.0 %] | 2.3 % | 30 % | perte significative |
| Tiercé hasard | 264 | 264 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 264 | 264 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
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
| 0.0-0.1 | 10886 | 0.073 | 0.071 |
| 0.1-0.2 | 24837 | 0.149 | 0.153 |
| 0.2-0.3 | 17280 | 0.248 | 0.265 |
| 0.3-0.4 | 9572 | 0.345 | 0.358 |
| 0.4-0.5 | 5371 | 0.445 | 0.443 |
| 0.5-0.6 | 3181 | 0.546 | 0.514 |
| 0.6-0.8 | 2850 | 0.682 | 0.617 |
| 0.8-1.0 | 1194 | 0.887 | 0.750 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
