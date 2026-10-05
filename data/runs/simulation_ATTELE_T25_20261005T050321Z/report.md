# Simulation de paris fictifs — trot attelé, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-05T05:03:21+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `e7bd23fdbf7f` · courses évaluées : 8103, dont 7989 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP favori | 7207 | 7207 | 6715 | -6.8 % | [-8.5 % ; -5.0 %] | 59.1 % | 0 % | perte significative |
| SP top market_calibrated | 7207 | 7207 | 6713 | -6.8 % | [-8.5 % ; -5.0 %] | 59.0 % | 0 % | perte significative |
| SG favori | 7207 | 7207 | 6386 | -11.4 % | [-14.3 % ; -8.3 %] | 32.9 % | 0 % | perte significative |
| SG top market_calibrated | 7207 | 7207 | 6386 | -11.4 % | [-14.3 % ; -8.3 %] | 32.9 % | 0 % | perte significative |
| SP top form | 7207 | 7207 | 5865 | -18.6 % | [-21.5 % ; -15.7 %] | 41.2 % | 0 % | perte significative |
| SP top horse_win_rate | 7207 | 7207 | 5854 | -18.8 % | [-21.6 % ; -15.9 %] | 39.9 % | 0 % | perte significative |
| SG top horse_win_rate | 7207 | 7207 | 5669 | -21.3 % | [-27.6 % ; -15.6 %] | 18.4 % | 1 % | perte significative |
| SG top form | 7207 | 7207 | 5266 | -26.9 % | [-32.5 % ; -20.6 %] | 16.7 % | 2 % | perte significative |
| SP hasard | 7207 | 7207 | 5068 | -29.7 % | [-33.3 % ; -26.0 %] | 24.5 % | 0 % | perte significative |
| Tiercé favoris | 309 | 309 | 211 | -31.7 % | [-67.5 % ; +15.3 %] | 6.5 % | 23 % | indéterminé |
| Tiercé market_calibrated | 309 | 309 | 211 | -31.7 % | [-67.5 % ; +15.3 %] | 6.5 % | 23 % | indéterminé |
| SG hasard | 7207 | 7207 | 4642 | -35.6 % | [-43.9 % ; -26.3 %] | 8.0 % | 3 % | perte significative |
| SG valeur horse_win_rate | 7207 | 43327 | 25855 | -40.3 % | [-44.7 % ; -35.8 %] | 19.8 % | 1 % | perte significative |
| SG valeur form | 7207 | 45797 | 26827 | -41.4 % | [-45.6 % ; -37.2 %] | 19.0 % | 1 % | perte significative |
| Quinté favoris | 309 | 618 | 326 | -47.3 % | [-57.6 % ; -37.5 %] | 30.4 % | 6 % | perte significative |
| Quinté market_calibrated | 309 | 618 | 326 | -47.3 % | [-57.6 % ; -37.5 %] | 30.4 % | 6 % | perte significative |
| Quinté form | 309 | 618 | 216 | -65.0 % | [-84.0 % ; -38.5 %] | 10.7 % | 27 % | perte significative |
| Quinté hasard | 309 | 618 | 199 | -67.7 % | [-99.2 % ; -11.6 %] | 1.6 % | 78 % | perte significative |
| Quinté horse_win_rate | 309 | 618 | 177 | -71.3 % | [-82.1 % ; -58.0 %] | 12.0 % | 20 % | perte significative |
| Tiercé form | 309 | 309 | 79 | -74.6 % | [-98.1 % ; -39.7 %] | 1.6 % | 47 % | perte significative |
| Tiercé horse_win_rate | 309 | 309 | 20 | -93.7 % | [-100.0 % ; -83.8 %] | 0.6 % | 56 % | perte significative |
| Tiercé hasard | 309 | 309 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase validation

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Quinté horse_win_rate | 38 | 76 | 161 | +112.4 % | [-100.0 % ; +534.2 %] | 5.3 % | 99 % | indéterminé |
| Tiercé favoris | 38 | 38 | 62 | +62.6 % | [-70.5 % ; +275.8 %] | 13.2 % | 56 % | indéterminé |
| Tiercé market_calibrated | 38 | 38 | 62 | +62.6 % | [-70.5 % ; +275.8 %] | 13.2 % | 56 % | indéterminé |
| SP favori | 782 | 782 | 745 | -4.7 % | [-11.3 % ; +1.2 %] | 59.1 % | 1 % | indéterminé |
| SP top market_calibrated | 782 | 782 | 745 | -4.7 % | [-11.3 % ; +1.2 %] | 59.1 % | 1 % | indéterminé |
| SG favori | 782 | 782 | 666 | -14.9 % | [-23.9 % ; -4.7 %] | 31.3 % | 1 % | perte significative |
| SG top market_calibrated | 782 | 782 | 666 | -14.9 % | [-23.9 % ; -4.7 %] | 31.3 % | 1 % | perte significative |
| SP top horse_win_rate | 782 | 782 | 566 | -27.6 % | [-36.9 % ; -16.7 %] | 31.2 % | 3 % | perte significative |
| SP hasard | 782 | 782 | 551 | -29.6 % | [-41.9 % ; -15.9 %] | 22.3 % | 3 % | perte significative |
| SP top form | 782 | 782 | 534 | -31.7 % | [-39.8 % ; -22.3 %] | 33.0 % | 2 % | perte significative |
| SG top form | 782 | 782 | 480 | -38.6 % | [-52.5 % ; -21.8 %] | 13.4 % | 7 % | perte significative |
| SG hasard | 782 | 782 | 476 | -39.2 % | [-59.8 % ; -13.2 %] | 6.4 % | 10 % | perte significative |
| Quinté favoris | 38 | 76 | 45 | -40.8 % | [-60.8 % ; -21.8 %] | 39.5 % | 10 % | perte significative |
| Quinté market_calibrated | 38 | 76 | 45 | -40.8 % | [-60.8 % ; -21.8 %] | 39.5 % | 10 % | perte significative |
| SG valeur horse_win_rate | 782 | 5840 | 3454 | -40.9 % | [-54.6 % ; -25.2 %] | 16.5 % | 6 % | perte significative |
| SG valeur form | 782 | 5553 | 2947 | -46.9 % | [-59.6 % ; -32.1 %] | 16.0 % | 7 % | perte significative |
| SG top horse_win_rate | 782 | 782 | 404 | -48.4 % | [-59.3 % ; -35.6 %] | 12.1 % | 7 % | perte significative |
| Quinté form | 38 | 76 | 11 | -85.8 % | [-100.0 % ; -69.5 %] | 7.9 % | 57 % | perte significative |
| Tiercé horse_win_rate | 38 | 38 | 4 | -90.0 % | [-100.0 % ; -70.0 %] | 2.6 % | 100 % | perte significative |
| Quinté hasard | 38 | 76 | 3 | -96.6 % | [-100.0 % ; -89.7 %] | 2.6 % | 100 % | perte significative |
| Tiercé hasard | 38 | 38 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé form | 38 | 38 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place

Marché calibré, phase test. Si « prévu » dépasse « observé » sur les fortes probabilités, Harville surestime les favoris pour les places (biais connu).

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.0-0.1 | 29526 | 0.056 | 0.061 |
| 0.1-0.2 | 23502 | 0.145 | 0.177 |
| 0.2-0.3 | 14165 | 0.247 | 0.276 |
| 0.3-0.4 | 8382 | 0.346 | 0.359 |
| 0.4-0.5 | 5623 | 0.446 | 0.446 |
| 0.5-0.6 | 3893 | 0.547 | 0.485 |
| 0.6-0.8 | 4654 | 0.688 | 0.563 |
| 0.8-1.0 | 2795 | 0.896 | 0.689 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
