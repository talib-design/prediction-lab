# Simulation de paris fictifs — plat, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-06T07:42:33+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `589ab952ac08` · courses évaluées : 15242, dont 14620 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Tiercé favoris | 256 | 256 | 261 | +1.8 % | [-77.8 % ; +106.8 %] | 2.7 % | 38 % | indéterminé |
| Tiercé market_calibrated | 256 | 256 | 261 | +1.8 % | [-77.8 % ; +106.8 %] | 2.7 % | 38 % | indéterminé |
| SP top market_calibrated | 6329 | 6329 | 5609 | -11.4 % | [-13.5 % ; -9.2 %] | 55.8 % | 0 % | perte significative |
| SP favori | 6329 | 6329 | 5606 | -11.4 % | [-13.5 % ; -9.3 %] | 55.8 % | 0 % | perte significative |
| SG favori | 6331 | 6331 | 5531 | -12.6 % | [-16.8 % ; -8.8 %] | 26.9 % | 0 % | perte significative |
| SG top market_calibrated | 6331 | 6331 | 5531 | -12.6 % | [-16.8 % ; -8.8 %] | 26.9 % | 0 % | perte significative |
| SP top form | 6329 | 6329 | 5264 | -16.8 % | [-19.6 % ; -14.1 %] | 44.0 % | 0 % | perte significative |
| SG top horse_win_rate | 6331 | 6331 | 5196 | -17.9 % | [-25.4 % ; -10.6 %] | 13.4 % | 1 % | perte significative |
| SG top form | 6331 | 6331 | 5120 | -19.1 % | [-24.5 % ; -13.6 %] | 18.5 % | 1 % | perte significative |
| SG hasard | 6331 | 6331 | 4994 | -21.1 % | [-29.4 % ; -13.3 %] | 10.5 % | 1 % | perte significative |
| SP top horse_win_rate | 6329 | 6329 | 4971 | -21.5 % | [-25.4 % ; -17.4 %] | 31.5 % | 0 % | perte significative |
| SP hasard | 6329 | 6329 | 4891 | -22.7 % | [-27.0 % ; -18.4 %] | 27.4 % | 0 % | perte significative |
| SG valeur form | 6321 | 26334 | 20121 | -23.6 % | [-28.6 % ; -18.6 %] | 24.3 % | 1 % | perte significative |
| SG valeur horse_win_rate | 6325 | 31057 | 23627 | -23.9 % | [-28.6 % ; -19.5 %] | 22.9 % | 1 % | perte significative |
| Quinté favoris | 256 | 512 | 237 | -53.6 % | [-66.2 % ; -38.2 %] | 19.1 % | 5 % | perte significative |
| Quinté market_calibrated | 256 | 512 | 237 | -53.6 % | [-66.2 % ; -38.2 %] | 19.1 % | 5 % | perte significative |
| Tiercé form | 256 | 256 | 111 | -56.5 % | [-100.0 % ; +13.3 %] | 1.2 % | 66 % | indéterminé |
| Quinté form | 256 | 512 | 191 | -62.8 % | [-78.7 % ; -44.6 %] | 9.4 % | 14 % | perte significative |
| Quinté hasard | 256 | 512 | 136 | -73.4 % | [-96.3 % ; -35.3 %] | 2.0 % | 56 % | perte significative |
| Quinté horse_win_rate | 256 | 512 | 119 | -76.8 % | [-93.2 % ; -54.5 %] | 3.1 % | 27 % | perte significative |
| Tiercé horse_win_rate | 256 | 256 | 43 | -83.1 % | [-100.0 % ; -49.4 %] | 0.4 % | 100 % | perte significative |
| Tiercé hasard | 256 | 256 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase train

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP favori | 6396 | 6396 | 5652 | -11.6 % | [-13.7 % ; -9.5 %] | 55.1 % | 0 % | perte significative |
| SP top market_calibrated | 6396 | 6396 | 5648 | -11.7 % | [-13.7 % ; -9.6 %] | 55.1 % | 0 % | perte significative |
| SG favori | 6396 | 6396 | 5432 | -15.1 % | [-18.7 % ; -11.2 %] | 26.6 % | 0 % | perte significative |
| SG top market_calibrated | 6396 | 6396 | 5432 | -15.1 % | [-18.7 % ; -11.2 %] | 26.6 % | 0 % | perte significative |
| SP top form | 6396 | 6396 | 5400 | -15.6 % | [-18.3 % ; -12.7 %] | 43.8 % | 0 % | perte significative |
| SG top horse_win_rate | 6396 | 6396 | 5281 | -17.4 % | [-24.4 % ; -9.8 %] | 13.6 % | 1 % | perte significative |
| SG top form | 6396 | 6396 | 5248 | -18.0 % | [-23.5 % ; -12.4 %] | 18.3 % | 1 % | perte significative |
| SP top horse_win_rate | 6396 | 6396 | 5197 | -18.7 % | [-22.3 % ; -15.3 %] | 33.6 % | 0 % | perte significative |
| SP hasard | 6396 | 6396 | 4935 | -22.8 % | [-26.7 % ; -18.8 %] | 28.1 % | 1 % | perte significative |
| SG hasard | 6396 | 6396 | 4933 | -22.9 % | [-30.3 % ; -15.3 %] | 10.0 % | 1 % | perte significative |
| SG valeur form | 6380 | 25572 | 18920 | -26.0 % | [-30.7 % ; -21.3 %] | 23.3 % | 1 % | perte significative |
| SG valeur horse_win_rate | 6391 | 30078 | 21803 | -27.5 % | [-32.1 % ; -22.8 %] | 22.5 % | 1 % | perte significative |
| Tiercé favoris | 251 | 251 | 118 | -52.8 % | [-81.4 % ; -18.8 %] | 3.2 % | 20 % | perte significative |
| Tiercé market_calibrated | 251 | 251 | 118 | -52.8 % | [-81.4 % ; -18.8 %] | 3.2 % | 20 % | perte significative |
| Tiercé form | 251 | 251 | 92 | -63.3 % | [-100.0 % ; +10.2 %] | 0.4 % | 100 % | indéterminé |
| Quinté favoris | 251 | 502 | 127 | -74.8 % | [-84.7 % ; -60.9 %] | 10.0 % | 18 % | perte significative |
| Quinté market_calibrated | 251 | 502 | 127 | -74.8 % | [-84.7 % ; -60.9 %] | 10.0 % | 18 % | perte significative |
| Quinté hasard | 251 | 502 | 107 | -78.8 % | [-95.2 % ; -56.7 %] | 2.4 % | 38 % | perte significative |
| Quinté form | 251 | 502 | 98 | -80.5 % | [-90.3 % ; -68.4 %] | 5.2 % | 16 % | perte significative |
| Quinté horse_win_rate | 251 | 502 | 65 | -87.0 % | [-97.6 % ; -72.7 %] | 2.0 % | 43 % | perte significative |
| Tiercé hasard | 251 | 251 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 251 | 251 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase validation

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP top market_calibrated | 1893 | 1893 | 1692 | -10.6 % | [-14.1 % ; -6.6 %] | 55.6 % | 0 % | perte significative |
| SP favori | 1893 | 1893 | 1688 | -10.8 % | [-14.3 % ; -6.8 %] | 55.6 % | 0 % | perte significative |
| SG favori | 1893 | 1893 | 1630 | -13.9 % | [-21.6 % ; -6.0 %] | 26.5 % | 1 % | perte significative |
| SG top market_calibrated | 1893 | 1893 | 1630 | -13.9 % | [-21.6 % ; -6.0 %] | 26.5 % | 1 % | perte significative |
| SG hasard | 1893 | 1893 | 1622 | -14.3 % | [-31.0 % ; +5.9 %] | 10.2 % | 7 % | indéterminé |
| SP top form | 1893 | 1893 | 1585 | -16.3 % | [-21.2 % ; -11.4 %] | 45.6 % | 0 % | perte significative |
| SG top horse_win_rate | 1893 | 1893 | 1564 | -17.4 % | [-32.5 % ; -1.9 %] | 13.3 % | 4 % | perte significative |
| SP hasard | 1893 | 1893 | 1531 | -19.1 % | [-26.9 % ; -10.6 %] | 27.9 % | 2 % | perte significative |
| SP top horse_win_rate | 1893 | 1893 | 1495 | -21.0 % | [-28.1 % ; -14.7 %] | 33.2 % | 1 % | perte significative |
| SG top form | 1893 | 1893 | 1372 | -27.5 % | [-36.2 % ; -18.0 %] | 17.9 % | 1 % | perte significative |
| SG valeur horse_win_rate | 1891 | 9062 | 6403 | -29.3 % | [-36.7 % ; -21.9 %] | 22.1 % | 2 % | perte significative |
| SG valeur form | 1889 | 7704 | 5383 | -30.1 % | [-37.9 % ; -22.3 %] | 22.7 % | 2 % | perte significative |
| Quinté form | 70 | 140 | 53 | -61.9 % | [-90.9 % ; -18.0 %] | 7.1 % | 36 % | perte significative |
| Quinté horse_win_rate | 70 | 140 | 43 | -69.6 % | [-100.0 % ; -35.1 %] | 4.3 % | 42 % | perte significative |
| Quinté favoris | 70 | 140 | 31 | -77.6 % | [-91.7 % ; -61.6 %] | 10.0 % | 19 % | perte significative |
| Quinté market_calibrated | 70 | 140 | 31 | -77.6 % | [-91.7 % ; -61.6 %] | 10.0 % | 19 % | perte significative |
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
| 0.0-0.1 | 10383 | 0.073 | 0.071 |
| 0.1-0.2 | 23987 | 0.149 | 0.152 |
| 0.2-0.3 | 16647 | 0.248 | 0.266 |
| 0.3-0.4 | 9251 | 0.345 | 0.357 |
| 0.4-0.5 | 5130 | 0.446 | 0.444 |
| 0.5-0.6 | 3033 | 0.546 | 0.519 |
| 0.6-0.8 | 2720 | 0.682 | 0.617 |
| 0.8-1.0 | 1123 | 0.887 | 0.756 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
