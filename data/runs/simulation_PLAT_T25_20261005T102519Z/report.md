# Simulation de paris fictifs — plat, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-05T10:25:19+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `3a70b939c4cc` · courses évaluées : 10923, dont 10249 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Tiercé favoris | 256 | 256 | 261 | +1.8 % | [-77.8 % ; +106.8 %] | 2.7 % | 38 % | indéterminé |
| Tiercé market_calibrated | 256 | 256 | 261 | +1.8 % | [-77.8 % ; +106.8 %] | 2.7 % | 38 % | indéterminé |
| SP top market_calibrated | 6313 | 6313 | 5586 | -11.5 % | [-13.7 % ; -9.4 %] | 55.8 % | 0 % | perte significative |
| SP favori | 6313 | 6313 | 5585 | -11.5 % | [-13.7 % ; -9.4 %] | 55.8 % | 0 % | perte significative |
| SG favori | 6315 | 6315 | 5492 | -13.0 % | [-16.8 % ; -8.9 %] | 26.8 % | 0 % | perte significative |
| SG top market_calibrated | 6315 | 6315 | 5492 | -13.0 % | [-16.8 % ; -8.9 %] | 26.8 % | 0 % | perte significative |
| SP top form | 6313 | 6313 | 5234 | -17.1 % | [-19.8 % ; -14.4 %] | 43.8 % | 0 % | perte significative |
| SG top form | 6315 | 6315 | 5040 | -20.2 % | [-25.4 % ; -14.5 %] | 18.4 % | 0 % | perte significative |
| SG hasard | 6315 | 6315 | 4974 | -21.2 % | [-29.1 % ; -13.1 %] | 10.5 % | 1 % | perte significative |
| SG top horse_win_rate | 6315 | 6315 | 4915 | -22.2 % | [-29.5 % ; -15.3 %] | 12.9 % | 1 % | perte significative |
| SP hasard | 6313 | 6313 | 4878 | -22.7 % | [-27.1 % ; -18.5 %] | 27.4 % | 0 % | perte significative |
| SP top horse_win_rate | 6313 | 6313 | 4853 | -23.1 % | [-26.7 % ; -19.4 %] | 31.2 % | 0 % | perte significative |
| SG valeur form | 6305 | 26240 | 20126 | -23.3 % | [-28.6 % ; -18.4 %] | 24.3 % | 1 % | perte significative |
| SG valeur horse_win_rate | 6311 | 30870 | 22805 | -26.1 % | [-31.0 % ; -21.5 %] | 22.7 % | 1 % | perte significative |
| Quinté favoris | 256 | 512 | 237 | -53.6 % | [-66.2 % ; -38.2 %] | 19.1 % | 5 % | perte significative |
| Quinté market_calibrated | 256 | 512 | 237 | -53.6 % | [-66.2 % ; -38.2 %] | 19.1 % | 5 % | perte significative |
| Tiercé form | 256 | 256 | 111 | -56.5 % | [-100.0 % ; +13.3 %] | 1.2 % | 66 % | indéterminé |
| Quinté form | 256 | 512 | 191 | -62.8 % | [-78.7 % ; -44.6 %] | 9.4 % | 14 % | perte significative |
| Quinté horse_win_rate | 256 | 512 | 147 | -71.4 % | [-90.3 % ; -48.0 %] | 4.3 % | 30 % | perte significative |
| Quinté hasard | 256 | 512 | 136 | -73.4 % | [-96.3 % ; -35.3 %] | 2.0 % | 56 % | perte significative |
| Tiercé horse_win_rate | 256 | 256 | 43 | -83.1 % | [-100.0 % ; -49.4 %] | 0.4 % | 100 % | perte significative |
| Tiercé hasard | 256 | 256 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase train

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP top market_calibrated | 2041 | 2041 | 1823 | -10.7 % | [-14.6 % ; -6.9 %] | 54.7 % | 0 % | perte significative |
| SP favori | 2041 | 2041 | 1822 | -10.7 % | [-14.7 % ; -7.0 %] | 54.7 % | 0 % | perte significative |
| SG favori | 2041 | 2041 | 1748 | -14.4 % | [-21.5 % ; -7.3 %] | 25.9 % | 1 % | perte significative |
| SG top market_calibrated | 2041 | 2041 | 1748 | -14.4 % | [-21.5 % ; -7.3 %] | 25.9 % | 1 % | perte significative |
| SP hasard | 2041 | 2041 | 1620 | -20.6 % | [-26.9 % ; -13.5 %] | 27.8 % | 1 % | perte significative |
| SP top horse_win_rate | 2041 | 2041 | 1613 | -21.0 % | [-27.3 % ; -14.1 %] | 32.3 % | 1 % | perte significative |
| SP top form | 2041 | 2041 | 1609 | -21.2 % | [-26.0 % ; -15.9 %] | 40.2 % | 1 % | perte significative |
| SG hasard | 2041 | 2041 | 1597 | -21.8 % | [-34.8 % ; -6.3 %] | 10.0 % | 3 % | perte significative |
| SG top horse_win_rate | 2041 | 2041 | 1517 | -25.7 % | [-36.7 % ; -14.3 %] | 13.1 % | 2 % | perte significative |
| SG top form | 2041 | 2041 | 1435 | -29.7 % | [-37.3 % ; -20.5 %] | 15.9 % | 2 % | perte significative |
| SG valeur form | 2038 | 8177 | 5538 | -32.3 % | [-39.5 % ; -23.8 %] | 21.5 % | 2 % | perte significative |
| Tiercé favoris | 80 | 80 | 54 | -33.0 % | [-100.0 % ; +54.7 %] | 3.8 % | 44 % | indéterminé |
| Tiercé market_calibrated | 80 | 80 | 54 | -33.0 % | [-100.0 % ; +54.7 %] | 3.8 % | 44 % | indéterminé |
| SG valeur horse_win_rate | 2040 | 9745 | 6503 | -33.3 % | [-39.8 % ; -24.9 %] | 21.8 % | 1 % | perte significative |
| Quinté hasard | 80 | 160 | 79 | -50.9 % | [-100.0 % ; +13.2 %] | 3.8 % | 51 % | indéterminé |
| Quinté favoris | 80 | 160 | 53 | -67.0 % | [-84.8 % ; -45.5 %] | 12.5 % | 19 % | perte significative |
| Quinté market_calibrated | 80 | 160 | 53 | -67.0 % | [-84.8 % ; -45.5 %] | 12.5 % | 19 % | perte significative |
| Quinté horse_win_rate | 80 | 160 | 30 | -81.4 % | [-97.1 % ; -59.4 %] | 5.0 % | 46 % | perte significative |
| Quinté form | 80 | 160 | 30 | -81.4 % | [-100.0 % ; -52.8 %] | 3.8 % | 68 % | perte significative |
| Tiercé hasard | 80 | 80 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 80 | 80 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé form | 80 | 80 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase validation

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP favori | 1893 | 1893 | 1688 | -10.8 % | [-14.3 % ; -6.8 %] | 55.6 % | 0 % | perte significative |
| SP top market_calibrated | 1893 | 1893 | 1683 | -11.1 % | [-14.5 % ; -7.0 %] | 55.4 % | 0 % | perte significative |
| SG favori | 1893 | 1893 | 1630 | -13.9 % | [-21.6 % ; -6.0 %] | 26.5 % | 1 % | perte significative |
| SG top market_calibrated | 1893 | 1893 | 1630 | -13.9 % | [-21.6 % ; -6.0 %] | 26.5 % | 1 % | perte significative |
| SG hasard | 1893 | 1893 | 1622 | -14.3 % | [-31.0 % ; +5.9 %] | 10.2 % | 7 % | indéterminé |
| SP top form | 1893 | 1893 | 1592 | -15.9 % | [-21.0 % ; -10.6 %] | 45.5 % | 1 % | perte significative |
| SP hasard | 1893 | 1893 | 1531 | -19.1 % | [-26.9 % ; -10.6 %] | 27.9 % | 2 % | perte significative |
| SP top horse_win_rate | 1893 | 1893 | 1433 | -24.3 % | [-30.3 % ; -18.2 %] | 31.6 % | 1 % | perte significative |
| SG top form | 1893 | 1893 | 1405 | -25.8 % | [-35.5 % ; -16.6 %] | 18.0 % | 1 % | perte significative |
| SG valeur horse_win_rate | 1892 | 9008 | 6363 | -29.4 % | [-36.4 % ; -22.3 %] | 22.4 % | 2 % | perte significative |
| SG valeur form | 1890 | 7694 | 5302 | -31.1 % | [-38.8 % ; -23.6 %] | 22.4 % | 2 % | perte significative |
| SG top horse_win_rate | 1893 | 1893 | 1280 | -32.4 % | [-43.7 % ; -19.7 %] | 11.6 % | 5 % | perte significative |
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
| 0.0-0.1 | 10282 | 0.073 | 0.071 |
| 0.1-0.2 | 23978 | 0.149 | 0.151 |
| 0.2-0.3 | 16660 | 0.248 | 0.265 |
| 0.3-0.4 | 9247 | 0.345 | 0.357 |
| 0.4-0.5 | 5117 | 0.446 | 0.444 |
| 0.5-0.6 | 3015 | 0.546 | 0.522 |
| 0.6-0.8 | 2700 | 0.682 | 0.616 |
| 0.8-1.0 | 1109 | 0.887 | 0.757 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
