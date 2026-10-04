# Simulation de paris fictifs — trot attelé, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-04T06:32:55+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `3bf2260e1e27` · courses évaluées : 7843, dont 7730 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP favori | 7204 | 7204 | 6715 | -6.8 % | [-8.5 % ; -5.0 %] | 59.1 % | 0 % | perte significative |
| SP top market_calibrated | 7204 | 7204 | 6700 | -7.0 % | [-8.7 % ; -5.3 %] | 59.0 % | 0 % | perte significative |
| SG favori | 7204 | 7204 | 6386 | -11.4 % | [-14.2 % ; -8.3 %] | 32.9 % | 0 % | perte significative |
| SG top market_calibrated | 7204 | 7204 | 6386 | -11.4 % | [-14.2 % ; -8.3 %] | 32.9 % | 0 % | perte significative |
| Quinté horse_win_rate | 309 | 618 | 515 | -16.6 % | [-80.4 % ; +100.3 %] | 12.0 % | 68 % | indéterminé |
| SP top horse_win_rate | 7204 | 7204 | 5935 | -17.6 % | [-20.5 % ; -14.7 %] | 40.4 % | 0 % | perte significative |
| SG top horse_win_rate | 7204 | 7204 | 5858 | -18.7 % | [-25.5 % ; -12.0 %] | 18.4 % | 2 % | perte significative |
| SP top form | 7204 | 7204 | 5844 | -18.9 % | [-21.4 % ; -16.0 %] | 41.3 % | 0 % | perte significative |
| SG top form | 7204 | 7204 | 5339 | -25.9 % | [-31.3 % ; -19.5 %] | 16.7 % | 2 % | perte significative |
| SP hasard | 7204 | 7204 | 5066 | -29.7 % | [-33.2 % ; -26.0 %] | 24.5 % | 0 % | perte significative |
| Tiercé favoris | 309 | 309 | 211 | -31.7 % | [-67.5 % ; +15.3 %] | 6.5 % | 23 % | indéterminé |
| Tiercé market_calibrated | 309 | 309 | 211 | -31.7 % | [-67.5 % ; +15.3 %] | 6.5 % | 23 % | indéterminé |
| SG hasard | 7204 | 7204 | 4642 | -35.6 % | [-43.6 % ; -26.2 %] | 8.0 % | 3 % | perte significative |
| SG valeur horse_win_rate | 7204 | 43446 | 26025 | -40.1 % | [-44.6 % ; -35.8 %] | 19.6 % | 1 % | perte significative |
| SG valeur form | 7204 | 45745 | 26630 | -41.8 % | [-45.9 % ; -37.3 %] | 18.9 % | 1 % | perte significative |
| Quinté favoris | 309 | 618 | 326 | -47.3 % | [-57.6 % ; -37.5 %] | 30.4 % | 6 % | perte significative |
| Quinté market_calibrated | 309 | 618 | 326 | -47.3 % | [-57.6 % ; -37.5 %] | 30.4 % | 6 % | perte significative |
| Quinté form | 309 | 618 | 236 | -61.8 % | [-81.7 % ; -34.5 %] | 11.3 % | 25 % | perte significative |
| Quinté hasard | 309 | 618 | 199 | -67.7 % | [-99.2 % ; -11.6 %] | 1.6 % | 78 % | perte significative |
| Tiercé form | 309 | 309 | 79 | -74.6 % | [-98.1 % ; -39.7 %] | 1.6 % | 47 % | perte significative |
| Tiercé horse_win_rate | 309 | 309 | 22 | -92.9 % | [-100.0 % ; -80.2 %] | 0.6 % | 60 % | perte significative |
| Tiercé hasard | 309 | 309 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase validation

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Tiercé favoris | 29 | 29 | 48 | +64.8 % | [-75.2 % ; +317.9 %] | 13.8 % | 73 % | indéterminé |
| Tiercé market_calibrated | 29 | 29 | 48 | +64.8 % | [-75.2 % ; +317.9 %] | 13.8 % | 73 % | indéterminé |
| SG top form | 526 | 526 | 559 | +6.3 % | [-40.8 % ; +66.4 %] | 11.2 % | 18 % | indéterminé |
| SP favori | 526 | 526 | 495 | -5.8 % | [-13.5 % ; +1.8 %] | 58.7 % | 1 % | indéterminé |
| SP top market_calibrated | 526 | 526 | 495 | -5.8 % | [-13.5 % ; +1.8 %] | 58.7 % | 1 % | indéterminé |
| SG top horse_win_rate | 526 | 526 | 487 | -7.4 % | [-52.0 % ; +50.8 %] | 9.9 % | 20 % | indéterminé |
| SG favori | 526 | 526 | 456 | -13.4 % | [-23.4 % ; -3.0 %] | 32.5 % | 2 % | perte significative |
| SG top market_calibrated | 526 | 526 | 456 | -13.4 % | [-23.4 % ; -3.0 %] | 32.5 % | 2 % | perte significative |
| SP top horse_win_rate | 526 | 526 | 443 | -15.8 % | [-31.7 % ; +1.0 %] | 29.8 % | 3 % | indéterminé |
| SP top form | 526 | 526 | 437 | -16.9 % | [-31.3 % ; -2.7 %] | 31.9 % | 3 % | perte significative |
| SG valeur form | 526 | 3810 | 2721 | -28.6 % | [-47.9 % ; -8.4 %] | 18.8 % | 7 % | perte significative |
| SG valeur horse_win_rate | 526 | 4029 | 2851 | -29.2 % | [-47.4 % ; -11.1 %] | 17.1 % | 7 % | perte significative |
| SP hasard | 526 | 526 | 372 | -29.2 % | [-43.1 % ; -14.6 %] | 22.4 % | 5 % | perte significative |
| SG hasard | 526 | 526 | 371 | -29.5 % | [-59.5 % ; +5.8 %] | 6.3 % | 13 % | indéterminé |
| Quinté favoris | 29 | 58 | 34 | -40.7 % | [-63.8 % ; -16.2 %] | 37.9 % | 13 % | perte significative |
| Quinté market_calibrated | 29 | 58 | 34 | -40.7 % | [-63.8 % ; -16.2 %] | 37.9 % | 13 % | perte significative |
| Quinté form | 29 | 58 | 19 | -67.9 % | [-90.3 % ; -40.7 %] | 17.2 % | 33 % | perte significative |
| Tiercé form | 29 | 29 | 9 | -68.3 % | [-100.0 % ; -4.8 %] | 3.4 % | 100 % | perte significative |
| Quinté hasard | 29 | 58 | 3 | -95.5 % | [-100.0 % ; -86.6 %] | 3.4 % | 100 % | perte significative |
| Tiercé hasard | 29 | 29 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 29 | 29 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Quinté horse_win_rate | 29 | 58 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place

Marché calibré, phase test. Si « prévu » dépasse « observé » sur les fortes probabilités, Harville surestime les favoris pour les places (biais connu).

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.0-0.1 | 29557 | 0.055 | 0.061 |
| 0.1-0.2 | 23471 | 0.145 | 0.177 |
| 0.2-0.3 | 14113 | 0.247 | 0.276 |
| 0.3-0.4 | 8376 | 0.346 | 0.359 |
| 0.4-0.5 | 5612 | 0.446 | 0.445 |
| 0.5-0.6 | 3892 | 0.547 | 0.487 |
| 0.6-0.8 | 4658 | 0.688 | 0.560 |
| 0.8-1.0 | 2815 | 0.896 | 0.690 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
