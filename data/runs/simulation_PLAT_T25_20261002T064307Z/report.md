# Simulation de paris fictifs — plat, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-02T06:43:07+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `28c5aae67459` · courses évaluées : 10594, dont 9916 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Tiercé favoris | 254 | 254 | 261 | +2.6 % | [-78.3 % ; +114.4 %] | 2.8 % | 38 % | indéterminé |
| Tiercé market_calibrated | 254 | 254 | 261 | +2.6 % | [-78.3 % ; +114.4 %] | 2.8 % | 38 % | indéterminé |
| SP top market_calibrated | 6270 | 6270 | 5554 | -11.4 % | [-13.6 % ; -9.2 %] | 55.8 % | 0 % | perte significative |
| SP favori | 6270 | 6270 | 5548 | -11.5 % | [-13.7 % ; -9.2 %] | 55.8 % | 0 % | perte significative |
| SG favori | 6272 | 6272 | 5450 | -13.1 % | [-17.2 % ; -8.9 %] | 26.8 % | 0 % | perte significative |
| SG top market_calibrated | 6272 | 6272 | 5450 | -13.1 % | [-17.2 % ; -8.9 %] | 26.8 % | 0 % | perte significative |
| SP top form | 6270 | 6270 | 5188 | -17.3 % | [-19.9 % ; -14.4 %] | 43.8 % | 0 % | perte significative |
| SG top form | 6272 | 6272 | 5014 | -20.1 % | [-25.1 % ; -14.8 %] | 18.4 % | 0 % | perte significative |
| SG hasard | 6272 | 6272 | 4935 | -21.3 % | [-29.2 % ; -12.8 %] | 10.5 % | 1 % | perte significative |
| SP top horse_win_rate | 6270 | 6270 | 4865 | -22.4 % | [-26.1 % ; -18.6 %] | 31.5 % | 0 % | perte significative |
| SG top horse_win_rate | 6272 | 6272 | 4852 | -22.6 % | [-30.2 % ; -15.8 %] | 12.8 % | 1 % | perte significative |
| SP hasard | 6270 | 6270 | 4848 | -22.7 % | [-27.0 % ; -18.0 %] | 27.4 % | 0 % | perte significative |
| SG valeur form | 6262 | 26032 | 19842 | -23.8 % | [-28.8 % ; -18.6 %] | 24.2 % | 1 % | perte significative |
| SG valeur horse_win_rate | 6267 | 30667 | 22656 | -26.1 % | [-30.7 % ; -21.6 %] | 22.7 % | 1 % | perte significative |
| Quinté favoris | 254 | 508 | 237 | -53.3 % | [-67.1 % ; -38.0 %] | 19.3 % | 5 % | perte significative |
| Quinté market_calibrated | 254 | 508 | 237 | -53.3 % | [-67.1 % ; -38.0 %] | 19.3 % | 5 % | perte significative |
| Tiercé form | 254 | 254 | 111 | -56.2 % | [-100.0 % ; +16.5 %] | 1.2 % | 66 % | indéterminé |
| Quinté form | 254 | 508 | 191 | -62.5 % | [-79.8 % ; -44.8 %] | 9.4 % | 14 % | perte significative |
| Quinté horse_win_rate | 254 | 508 | 153 | -69.9 % | [-89.0 % ; -46.4 %] | 4.3 % | 28 % | perte significative |
| Quinté hasard | 254 | 508 | 136 | -73.1 % | [-96.9 % ; -36.6 %] | 2.0 % | 56 % | perte significative |
| Tiercé horse_win_rate | 254 | 254 | 43 | -83.0 % | [-100.0 % ; -49.0 %] | 0.4 % | 100 % | perte significative |
| Tiercé hasard | 254 | 254 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase train

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP top market_calibrated | 1751 | 1751 | 1574 | -10.1 % | [-14.3 % ; -6.4 %] | 55.3 % | 0 % | perte significative |
| SP favori | 1751 | 1751 | 1572 | -10.2 % | [-14.3 % ; -6.4 %] | 55.3 % | 0 % | perte significative |
| SG favori | 1751 | 1751 | 1480 | -15.5 % | [-23.6 % ; -8.3 %] | 25.9 % | 1 % | perte significative |
| SG top market_calibrated | 1751 | 1751 | 1480 | -15.5 % | [-23.6 % ; -8.3 %] | 25.9 % | 1 % | perte significative |
| SP top form | 1751 | 1751 | 1445 | -17.5 % | [-23.1 % ; -12.5 %] | 41.1 % | 1 % | perte significative |
| SP top horse_win_rate | 1751 | 1751 | 1390 | -20.6 % | [-28.4 % ; -14.1 %] | 32.3 % | 2 % | perte significative |
| SP hasard | 1751 | 1751 | 1386 | -20.9 % | [-27.6 % ; -13.3 %] | 28.6 % | 1 % | perte significative |
| SG hasard | 1751 | 1751 | 1300 | -25.7 % | [-39.1 % ; -10.5 %] | 10.1 % | 4 % | perte significative |
| SG top form | 1751 | 1751 | 1258 | -28.1 % | [-37.2 % ; -17.7 %] | 15.7 % | 2 % | perte significative |
| SG valeur form | 1749 | 6991 | 4815 | -31.1 % | [-39.2 % ; -21.9 %] | 22.1 % | 2 % | perte significative |
| SG valeur horse_win_rate | 1751 | 8160 | 5492 | -32.7 % | [-40.3 % ; -24.0 %] | 21.7 % | 2 % | perte significative |
| SG top horse_win_rate | 1751 | 1751 | 1098 | -37.3 % | [-46.2 % ; -28.3 %] | 12.5 % | 2 % | perte significative |
| Tiercé favoris | 73 | 73 | 30 | -59.0 % | [-100.0 % ; -4.2 %] | 2.7 % | 67 % | perte significative |
| Tiercé market_calibrated | 73 | 73 | 30 | -59.0 % | [-100.0 % ; -4.2 %] | 2.7 % | 67 % | perte significative |
| Quinté hasard | 73 | 146 | 57 | -60.7 % | [-100.0 % ; +6.0 %] | 2.7 % | 70 % | indéterminé |
| Quinté favoris | 73 | 146 | 42 | -71.4 % | [-88.6 % ; -49.9 %] | 11.0 % | 24 % | perte significative |
| Quinté market_calibrated | 73 | 146 | 42 | -71.4 % | [-88.6 % ; -49.9 %] | 11.0 % | 24 % | perte significative |
| Quinté form | 73 | 146 | 14 | -90.4 % | [-100.0 % ; -77.9 %] | 4.1 % | 36 % | perte significative |
| Quinté horse_win_rate | 73 | 146 | 4 | -97.4 % | [-100.0 % ; -92.2 %] | 1.4 % | 100 % | perte significative |
| Tiercé hasard | 73 | 73 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 73 | 73 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé form | 73 | 73 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase validation

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP favori | 1893 | 1893 | 1688 | -10.8 % | [-14.3 % ; -6.8 %] | 55.6 % | 0 % | perte significative |
| SP top market_calibrated | 1893 | 1893 | 1687 | -10.9 % | [-14.3 % ; -6.9 %] | 55.5 % | 0 % | perte significative |
| SG favori | 1893 | 1893 | 1630 | -13.9 % | [-21.6 % ; -6.0 %] | 26.5 % | 1 % | perte significative |
| SG top market_calibrated | 1893 | 1893 | 1630 | -13.9 % | [-21.6 % ; -6.0 %] | 26.5 % | 1 % | perte significative |
| SG hasard | 1893 | 1893 | 1622 | -14.3 % | [-31.0 % ; +5.9 %] | 10.2 % | 7 % | indéterminé |
| SP top form | 1893 | 1893 | 1612 | -14.8 % | [-20.4 % ; -9.4 %] | 45.6 % | 1 % | perte significative |
| SP hasard | 1893 | 1893 | 1531 | -19.1 % | [-26.9 % ; -10.6 %] | 27.9 % | 2 % | perte significative |
| SP top horse_win_rate | 1893 | 1893 | 1464 | -22.6 % | [-28.9 % ; -16.3 %] | 31.6 % | 1 % | perte significative |
| SG top form | 1893 | 1893 | 1430 | -24.5 % | [-34.4 % ; -15.1 %] | 18.2 % | 1 % | perte significative |
| SG valeur horse_win_rate | 1892 | 8999 | 6325 | -29.7 % | [-37.1 % ; -22.5 %] | 22.4 % | 2 % | perte significative |
| SG top horse_win_rate | 1893 | 1893 | 1329 | -29.8 % | [-41.5 % ; -16.6 %] | 11.8 % | 5 % | perte significative |
| SG valeur form | 1890 | 7698 | 5331 | -30.7 % | [-38.4 % ; -23.3 %] | 22.5 % | 2 % | perte significative |
| Quinté form | 70 | 140 | 40 | -71.3 % | [-96.0 % ; -28.8 %] | 5.7 % | 48 % | perte significative |
| Quinté favoris | 70 | 140 | 31 | -77.6 % | [-91.7 % ; -61.6 %] | 10.0 % | 19 % | perte significative |
| Quinté market_calibrated | 70 | 140 | 31 | -77.6 % | [-91.7 % ; -61.6 %] | 10.0 % | 19 % | perte significative |
| Quinté hasard | 70 | 140 | 7 | -94.9 % | [-100.0 % ; -84.6 %] | 1.4 % | 100 % | perte significative |
| Tiercé favoris | 70 | 70 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé hasard | 70 | 70 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé market_calibrated | 70 | 70 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 70 | 70 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé form | 70 | 70 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Quinté horse_win_rate | 70 | 140 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place

Marché calibré, phase test. Si « prévu » dépasse « observé » sur les fortes probabilités, Harville surestime les favoris pour les places (biais connu).

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.0-0.1 | 10181 | 0.073 | 0.071 |
| 0.1-0.2 | 23827 | 0.149 | 0.151 |
| 0.2-0.3 | 16573 | 0.248 | 0.265 |
| 0.3-0.4 | 9184 | 0.345 | 0.357 |
| 0.4-0.5 | 5083 | 0.446 | 0.443 |
| 0.5-0.6 | 2992 | 0.546 | 0.520 |
| 0.6-0.8 | 2685 | 0.682 | 0.619 |
| 0.8-1.0 | 1094 | 0.887 | 0.753 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
