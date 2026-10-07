# Simulation de paris fictifs — plat, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-07T04:33:51+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `a6a49391f9f8` · courses évaluées : 22311, dont 21770 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Tiercé favoris | 256 | 256 | 261 | +1.8 % | [-77.8 % ; +106.8 %] | 2.7 % | 38 % | indéterminé |
| Tiercé market_calibrated | 256 | 256 | 261 | +1.8 % | [-77.8 % ; +106.8 %] | 2.7 % | 38 % | indéterminé |
| SP top market_calibrated | 6337 | 6337 | 5618 | -11.3 % | [-13.4 % ; -9.2 %] | 55.9 % | 0 % | perte significative |
| SP favori | 6337 | 6337 | 5615 | -11.4 % | [-13.5 % ; -9.2 %] | 55.9 % | 0 % | perte significative |
| SG favori | 6339 | 6339 | 5538 | -12.6 % | [-16.7 % ; -8.6 %] | 26.9 % | 0 % | perte significative |
| SG top market_calibrated | 6339 | 6339 | 5538 | -12.6 % | [-16.7 % ; -8.6 %] | 26.9 % | 0 % | perte significative |
| SP top form | 6337 | 6337 | 5252 | -17.1 % | [-19.8 % ; -14.5 %] | 44.0 % | 0 % | perte significative |
| SG top horse_win_rate | 6339 | 6339 | 5184 | -18.2 % | [-26.1 % ; -11.1 %] | 13.4 % | 1 % | perte significative |
| SG top form | 6339 | 6339 | 5034 | -20.6 % | [-26.0 % ; -15.4 %] | 18.4 % | 0 % | perte significative |
| SG hasard | 6339 | 6339 | 5008 | -21.0 % | [-29.1 % ; -13.3 %] | 10.6 % | 1 % | perte significative |
| SP top horse_win_rate | 6337 | 6337 | 4976 | -21.5 % | [-25.4 % ; -17.5 %] | 31.4 % | 0 % | perte significative |
| SP hasard | 6337 | 6337 | 4896 | -22.7 % | [-27.1 % ; -18.5 %] | 27.4 % | 0 % | perte significative |
| SG valeur form | 6329 | 26361 | 20115 | -23.7 % | [-28.7 % ; -18.7 %] | 24.3 % | 1 % | perte significative |
| SG valeur horse_win_rate | 6335 | 31135 | 23725 | -23.8 % | [-28.5 % ; -19.4 %] | 22.9 % | 1 % | perte significative |
| Quinté favoris | 256 | 512 | 237 | -53.6 % | [-66.2 % ; -38.2 %] | 19.1 % | 5 % | perte significative |
| Quinté market_calibrated | 256 | 512 | 237 | -53.6 % | [-66.2 % ; -38.2 %] | 19.1 % | 5 % | perte significative |
| Tiercé form | 256 | 256 | 111 | -56.5 % | [-100.0 % ; +13.3 %] | 1.2 % | 66 % | indéterminé |
| Quinté form | 256 | 512 | 191 | -62.8 % | [-78.7 % ; -44.6 %] | 9.4 % | 14 % | perte significative |
| Quinté hasard | 256 | 512 | 136 | -73.4 % | [-96.3 % ; -35.3 %] | 2.0 % | 56 % | perte significative |
| Quinté horse_win_rate | 256 | 512 | 109 | -78.8 % | [-94.5 % ; -57.7 %] | 2.3 % | 30 % | perte significative |
| Tiercé hasard | 256 | 256 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 256 | 256 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase train

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Tiercé form | 541 | 541 | 595 | +9.9 % | [-88.1 % ; +178.3 %] | 0.9 % | 63 % | indéterminé |
| SP favori | 13537 | 13537 | 11844 | -12.5 % | [-13.9 % ; -11.1 %] | 54.7 % | 0 % | perte significative |
| SP top market_calibrated | 13537 | 13537 | 11840 | -12.5 % | [-13.9 % ; -11.2 %] | 54.7 % | 0 % | perte significative |
| SG favori | 13537 | 13537 | 11620 | -14.2 % | [-16.8 % ; -11.4 %] | 26.8 % | 0 % | perte significative |
| SG top market_calibrated | 13537 | 13537 | 11620 | -14.2 % | [-16.8 % ; -11.4 %] | 26.8 % | 0 % | perte significative |
| SP top form | 13537 | 13537 | 11201 | -17.3 % | [-19.1 % ; -15.3 %] | 43.5 % | 0 % | perte significative |
| SG top form | 13537 | 13537 | 11077 | -18.2 % | [-21.7 % ; -14.5 %] | 18.6 % | 0 % | perte significative |
| SP top horse_win_rate | 13537 | 13537 | 10770 | -20.4 % | [-23.0 % ; -18.0 %] | 33.2 % | 0 % | perte significative |
| SG top horse_win_rate | 13537 | 13537 | 10701 | -20.9 % | [-25.6 % ; -16.5 %] | 13.5 % | 0 % | perte significative |
| SG hasard | 13537 | 13537 | 10692 | -21.0 % | [-26.4 % ; -15.6 %] | 10.2 % | 1 % | perte significative |
| SP hasard | 13537 | 13537 | 10422 | -23.0 % | [-25.6 % ; -20.3 %] | 28.0 % | 0 % | perte significative |
| SG valeur form | 13510 | 54030 | 39831 | -26.3 % | [-29.3 % ; -23.1 %] | 23.2 % | 0 % | perte significative |
| SG valeur horse_win_rate | 13528 | 63252 | 45658 | -27.8 % | [-31.0 % ; -24.4 %] | 22.2 % | 0 % | perte significative |
| Quinté form | 541 | 1082 | 600 | -44.6 % | [-84.5 % ; +26.8 %] | 5.0 % | 55 % | indéterminé |
| Tiercé favoris | 541 | 541 | 268 | -50.5 % | [-76.0 % ; -20.1 %] | 2.8 % | 18 % | perte significative |
| Tiercé market_calibrated | 541 | 541 | 268 | -50.5 % | [-76.0 % ; -20.1 %] | 2.8 % | 18 % | perte significative |
| Quinté favoris | 541 | 1082 | 318 | -70.6 % | [-79.2 % ; -61.5 %] | 10.5 % | 8 % | perte significative |
| Quinté market_calibrated | 541 | 1082 | 318 | -70.6 % | [-79.2 % ; -61.5 %] | 10.5 % | 8 % | perte significative |
| Quinté hasard | 541 | 1082 | 256 | -76.3 % | [-89.1 % ; -59.2 %] | 2.6 % | 25 % | perte significative |
| Quinté horse_win_rate | 541 | 1082 | 134 | -87.6 % | [-95.4 % ; -77.8 %] | 2.2 % | 22 % | perte significative |
| Tiercé horse_win_rate | 541 | 541 | 61 | -88.8 % | [-100.0 % ; -66.3 %] | 0.2 % | 100 % | perte significative |
| Tiercé hasard | 541 | 541 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase validation

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP favori | 1893 | 1893 | 1688 | -10.8 % | [-14.3 % ; -6.8 %] | 55.6 % | 0 % | perte significative |
| SP top market_calibrated | 1893 | 1893 | 1684 | -11.0 % | [-14.4 % ; -6.9 %] | 55.5 % | 0 % | perte significative |
| SG favori | 1893 | 1893 | 1630 | -13.9 % | [-21.6 % ; -6.0 %] | 26.5 % | 1 % | perte significative |
| SG top market_calibrated | 1893 | 1893 | 1630 | -13.9 % | [-21.6 % ; -6.0 %] | 26.5 % | 1 % | perte significative |
| SG hasard | 1893 | 1893 | 1622 | -14.3 % | [-31.0 % ; +5.9 %] | 10.2 % | 7 % | indéterminé |
| SP top form | 1893 | 1893 | 1584 | -16.3 % | [-21.2 % ; -11.5 %] | 45.6 % | 0 % | perte significative |
| SP hasard | 1893 | 1893 | 1531 | -19.1 % | [-26.9 % ; -10.6 %] | 27.9 % | 2 % | perte significative |
| SG top horse_win_rate | 1893 | 1893 | 1516 | -19.9 % | [-34.6 % ; -5.0 %] | 12.9 % | 4 % | perte significative |
| SP top horse_win_rate | 1893 | 1893 | 1483 | -21.7 % | [-28.2 % ; -15.9 %] | 33.4 % | 1 % | perte significative |
| SG top form | 1893 | 1893 | 1381 | -27.0 % | [-35.8 % ; -17.5 %] | 18.0 % | 1 % | perte significative |
| SG valeur horse_win_rate | 1892 | 9014 | 6395 | -29.1 % | [-37.0 % ; -21.2 %] | 21.3 % | 2 % | perte significative |
| SG valeur form | 1888 | 7699 | 5407 | -29.8 % | [-37.7 % ; -22.2 %] | 22.7 % | 2 % | perte significative |
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
| 0.0-0.1 | 10459 | 0.073 | 0.071 |
| 0.1-0.2 | 23963 | 0.149 | 0.152 |
| 0.2-0.3 | 16627 | 0.248 | 0.265 |
| 0.3-0.4 | 9242 | 0.345 | 0.357 |
| 0.4-0.5 | 5142 | 0.446 | 0.444 |
| 0.5-0.6 | 3040 | 0.546 | 0.518 |
| 0.6-0.8 | 2727 | 0.682 | 0.617 |
| 0.8-1.0 | 1139 | 0.887 | 0.753 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
