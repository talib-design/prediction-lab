# Simulation de paris fictifs — trot monté, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-13T23:38:32+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `9b807113d627` · courses évaluées : 3279, dont 3239 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Quinté favoris | 3 | 6 | 7 | +13.3 % | [— ; —] | 33.3 % | 100 % | échantillon trop petit |
| Quinté market_calibrated | 3 | 6 | 7 | +13.3 % | [— ; —] | 33.3 % | 100 % | échantillon trop petit |
| SP favori | 1362 | 1362 | 1237 | -9.1 % | [-12.9 % ; -5.0 %] | 59.0 % | 0 % | perte significative |
| SP top market_calibrated | 1362 | 1362 | 1237 | -9.2 % | [-12.8 % ; -5.0 %] | 59.0 % | 0 % | perte significative |
| SG favori | 1362 | 1362 | 1177 | -13.6 % | [-20.2 % ; -6.6 %] | 33.3 % | 1 % | perte significative |
| SG top market_calibrated | 1362 | 1362 | 1177 | -13.6 % | [-20.2 % ; -6.6 %] | 33.3 % | 1 % | perte significative |
| SP top horse_win_rate | 1362 | 1362 | 1128 | -17.2 % | [-24.1 % ; -9.5 %] | 43.2 % | 2 % | perte significative |
| SG hasard | 1362 | 1362 | 1082 | -20.6 % | [-41.2 % ; -1.4 %] | 10.2 % | 8 % | perte significative |
| SP top form | 1362 | 1362 | 1079 | -20.7 % | [-26.3 % ; -15.4 %] | 44.6 % | 1 % | perte significative |
| SG valeur horse_win_rate | 1362 | 7390 | 5292 | -28.4 % | [-39.5 % ; -17.0 %] | 20.2 % | 3 % | perte significative |
| SG top horse_win_rate | 1362 | 1362 | 949 | -30.3 % | [-40.7 % ; -18.3 %] | 18.9 % | 2 % | perte significative |
| SP hasard | 1362 | 1362 | 943 | -30.7 % | [-37.4 % ; -24.1 %] | 27.2 % | 1 % | perte significative |
| SG top form | 1362 | 1362 | 917 | -32.7 % | [-43.3 % ; -20.8 %] | 18.3 % | 4 % | perte significative |
| SG valeur form | 1362 | 7454 | 4758 | -36.2 % | [-46.2 % ; -24.2 %] | 18.6 % | 3 % | perte significative |
| Tiercé favoris | 3 | 3 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Tiercé hasard | 3 | 3 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Tiercé market_calibrated | 3 | 3 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Tiercé horse_win_rate | 3 | 3 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Tiercé form | 3 | 3 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Quinté hasard | 3 | 6 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Quinté horse_win_rate | 3 | 6 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Quinté form | 3 | 6 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase train

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP top market_calibrated | 1454 | 1454 | 1293 | -11.1 % | [-15.6 % ; -7.0 %] | 57.8 % | 0 % | perte significative |
| SP favori | 1454 | 1454 | 1289 | -11.4 % | [-15.9 % ; -7.2 %] | 57.6 % | 0 % | perte significative |
| SP top horse_win_rate | 1454 | 1454 | 1232 | -15.3 % | [-21.7 % ; -8.5 %] | 42.7 % | 1 % | perte significative |
| Tiercé favoris | 3 | 3 | 2 | -16.7 % | [— ; —] | 33.3 % | 100 % | échantillon trop petit |
| Tiercé market_calibrated | 3 | 3 | 2 | -16.7 % | [— ; —] | 33.3 % | 100 % | échantillon trop petit |
| SG favori | 1454 | 1454 | 1193 | -17.9 % | [-24.5 % ; -11.1 %] | 31.3 % | 1 % | perte significative |
| SG top market_calibrated | 1454 | 1454 | 1193 | -17.9 % | [-24.5 % ; -11.1 %] | 31.3 % | 1 % | perte significative |
| SP top form | 1454 | 1454 | 1176 | -19.1 % | [-24.0 % ; -13.8 %] | 44.8 % | 1 % | perte significative |
| SG hasard | 1454 | 1454 | 1150 | -20.9 % | [-40.9 % ; -0.3 %] | 10.0 % | 7 % | perte significative |
| SG top form | 1454 | 1454 | 1099 | -24.4 % | [-34.8 % ; -13.9 %] | 19.4 % | 2 % | perte significative |
| SP hasard | 1454 | 1454 | 1087 | -25.2 % | [-33.3 % ; -17.7 %] | 28.2 % | 2 % | perte significative |
| SG top horse_win_rate | 1454 | 1454 | 1043 | -28.3 % | [-38.8 % ; -16.7 %] | 18.2 % | 4 % | perte significative |
| SG valeur form | 1453 | 7871 | 5317 | -32.4 % | [-41.4 % ; -21.9 %] | 22.5 % | 2 % | perte significative |
| SG valeur horse_win_rate | 1454 | 7923 | 5328 | -32.8 % | [-41.6 % ; -22.8 %] | 20.3 % | 2 % | perte significative |
| Quinté form | 3 | 6 | 4 | -40.0 % | [— ; —] | 33.3 % | 100 % | échantillon trop petit |
| Quinté favoris | 3 | 6 | 2 | -63.3 % | [— ; —] | 33.3 % | 100 % | échantillon trop petit |
| Quinté market_calibrated | 3 | 6 | 2 | -63.3 % | [— ; —] | 33.3 % | 100 % | échantillon trop petit |
| Tiercé hasard | 3 | 3 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Tiercé horse_win_rate | 3 | 3 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Tiercé form | 3 | 3 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Quinté hasard | 3 | 6 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Quinté horse_win_rate | 3 | 6 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase validation

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SG favori | 423 | 423 | 433 | +2.5 % | [-10.7 % ; +16.2 %] | 40.0 % | 1 % | indéterminé |
| SG top market_calibrated | 423 | 423 | 433 | +2.5 % | [-10.7 % ; +16.2 %] | 40.0 % | 1 % | indéterminé |
| SP top horse_win_rate | 423 | 423 | 415 | -1.8 % | [-14.5 % ; +13.2 %] | 47.5 % | 2 % | indéterminé |
| SG top form | 423 | 423 | 413 | -2.4 % | [-28.6 % ; +29.0 %] | 24.1 % | 7 % | indéterminé |
| SP top market_calibrated | 423 | 423 | 400 | -5.4 % | [-13.0 % ; +2.6 %] | 61.2 % | 1 % | indéterminé |
| SP favori | 423 | 423 | 398 | -5.9 % | [-13.4 % ; +1.8 %] | 61.2 % | 1 % | indéterminé |
| SP top form | 423 | 423 | 394 | -7.0 % | [-18.2 % ; +4.9 %] | 46.6 % | 4 % | indéterminé |
| SG top horse_win_rate | 423 | 423 | 332 | -21.4 % | [-42.9 % ; +7.4 %] | 20.3 % | 12 % | indéterminé |
| SP hasard | 423 | 423 | 283 | -33.2 % | [-46.6 % ; -19.3 %] | 24.1 % | 5 % | perte significative |
| SG hasard | 423 | 423 | 251 | -40.7 % | [-65.1 % ; -10.7 %] | 8.5 % | 12 % | perte significative |
| SG valeur horse_win_rate | 423 | 2440 | 1296 | -46.9 % | [-59.2 % ; -30.5 %] | 18.0 % | 8 % | perte significative |
| SG valeur form | 423 | 2452 | 1179 | -51.9 % | [-63.4 % ; -38.2 %] | 18.4 % | 6 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |
| Tiercé favoris | 0 | — | — | — | — | — | — | aucun pari |
| Tiercé hasard | 0 | — | — | — | — | — | — | aucun pari |
| Tiercé market_calibrated | 0 | — | — | — | — | — | — | aucun pari |
| Tiercé horse_win_rate | 0 | — | — | — | — | — | — | aucun pari |
| Tiercé form | 0 | — | — | — | — | — | — | aucun pari |
| Quinté favoris | 0 | — | — | — | — | — | — | aucun pari |
| Quinté hasard | 0 | — | — | — | — | — | — | aucun pari |
| Quinté market_calibrated | 0 | — | — | — | — | — | — | aucun pari |
| Quinté horse_win_rate | 0 | — | — | — | — | — | — | aucun pari |
| Quinté form | 0 | — | — | — | — | — | — | aucun pari |

## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place

Marché calibré, phase test. Si « prévu » dépasse « observé » sur les fortes probabilités, Harville surestime les favoris pour les places (biais connu).

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.0-0.1 | 3978 | 0.061 | 0.058 |
| 0.1-0.2 | 3971 | 0.146 | 0.174 |
| 0.2-0.3 | 2620 | 0.248 | 0.280 |
| 0.3-0.4 | 1663 | 0.346 | 0.382 |
| 0.4-0.5 | 1192 | 0.447 | 0.438 |
| 0.5-0.6 | 778 | 0.548 | 0.533 |
| 0.6-0.8 | 905 | 0.687 | 0.564 |
| 0.8-1.0 | 503 | 0.897 | 0.678 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
