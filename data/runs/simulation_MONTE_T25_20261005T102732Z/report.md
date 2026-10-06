# Simulation de paris fictifs — trot monté, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-05T10:27:32+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `02fee1985320` · courses évaluées : 2167, dont 2140 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Quinté favoris | 3 | 6 | 7 | +13.3 % | [— ; —] | 33.3 % | 100 % | échantillon trop petit |
| Quinté market_calibrated | 3 | 6 | 7 | +13.3 % | [— ; —] | 33.3 % | 100 % | échantillon trop petit |
| SP favori | 1338 | 1338 | 1214 | -9.2 % | [-13.2 % ; -4.9 %] | 59.0 % | 0 % | perte significative |
| SP top market_calibrated | 1338 | 1338 | 1214 | -9.3 % | [-13.2 % ; -4.9 %] | 59.0 % | 0 % | perte significative |
| SG favori | 1338 | 1338 | 1160 | -13.3 % | [-19.8 % ; -5.8 %] | 33.4 % | 1 % | perte significative |
| SG top market_calibrated | 1338 | 1338 | 1160 | -13.3 % | [-19.8 % ; -5.8 %] | 33.4 % | 1 % | perte significative |
| SP top horse_win_rate | 1338 | 1338 | 1097 | -18.0 % | [-24.6 % ; -9.4 %] | 42.8 % | 2 % | perte significative |
| SP top form | 1338 | 1338 | 1054 | -21.2 % | [-26.6 % ; -14.8 %] | 44.2 % | 1 % | perte significative |
| SG valeur horse_win_rate | 1338 | 7211 | 5592 | -22.5 % | [-35.2 % ; -10.5 %] | 21.4 % | 3 % | perte significative |
| SG hasard | 1338 | 1338 | 1019 | -23.8 % | [-45.8 % ; -4.6 %] | 10.0 % | 9 % | perte significative |
| SG top horse_win_rate | 1338 | 1338 | 957 | -28.5 % | [-40.8 % ; -14.1 %] | 19.0 % | 5 % | perte significative |
| SP hasard | 1338 | 1338 | 929 | -30.6 % | [-37.6 % ; -23.6 %] | 27.4 % | 1 % | perte significative |
| SG top form | 1338 | 1338 | 902 | -32.5 % | [-42.9 % ; -20.5 %] | 18.2 % | 4 % | perte significative |
| SG valeur form | 1338 | 7323 | 4787 | -34.6 % | [-45.5 % ; -24.2 %] | 18.8 % | 3 % | perte significative |
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
| SP favori | 379 | 379 | 341 | -9.9 % | [-17.8 % ; -0.4 %] | 58.8 % | 1 % | perte significative |
| SP top market_calibrated | 379 | 379 | 341 | -9.9 % | [-17.8 % ; -0.4 %] | 58.8 % | 1 % | perte significative |
| SP top horse_win_rate | 379 | 379 | 337 | -11.1 % | [-25.9 % ; +3.0 %] | 40.6 % | 5 % | indéterminé |
| SP top form | 379 | 379 | 329 | -13.2 % | [-27.3 % ; +0.5 %] | 43.5 % | 5 % | indéterminé |
| SG hasard | 379 | 379 | 312 | -17.7 % | [-47.0 % ; +19.0 %] | 12.1 % | 11 % | indéterminé |
| SG favori | 379 | 379 | 304 | -19.9 % | [-32.3 % ; -4.2 %] | 30.9 % | 2 % | perte significative |
| SG top market_calibrated | 379 | 379 | 304 | -19.9 % | [-32.3 % ; -4.2 %] | 30.9 % | 2 % | perte significative |
| SG top form | 379 | 379 | 279 | -26.3 % | [-52.6 % ; +2.3 %] | 16.1 % | 15 % | indéterminé |
| SP hasard | 379 | 379 | 277 | -26.8 % | [-38.4 % ; -14.1 %] | 29.3 % | 4 % | perte significative |
| SG top horse_win_rate | 379 | 379 | 269 | -28.9 % | [-57.5 % ; +0.3 %] | 15.0 % | 16 % | indéterminé |
| SG valeur form | 379 | 2030 | 1434 | -29.4 % | [-47.3 % ; -10.6 %] | 23.7 % | 6 % | perte significative |
| SG valeur horse_win_rate | 379 | 2089 | 1434 | -31.3 % | [-49.9 % ; -12.2 %] | 20.8 % | 6 % | perte significative |
| Tiercé favoris | 1 | 1 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Tiercé hasard | 1 | 1 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Tiercé market_calibrated | 1 | 1 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Tiercé horse_win_rate | 1 | 1 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Tiercé form | 1 | 1 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Quinté favoris | 1 | 2 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Quinté hasard | 1 | 2 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Quinté market_calibrated | 1 | 2 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Quinté horse_win_rate | 1 | 2 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Quinté form | 1 | 2 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase validation

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SG top form | 423 | 423 | 447 | +5.7 % | [-26.1 % ; +43.4 %] | 23.9 % | 8 % | indéterminé |
| SG favori | 423 | 423 | 433 | +2.5 % | [-10.7 % ; +16.2 %] | 40.0 % | 1 % | indéterminé |
| SG top market_calibrated | 423 | 423 | 433 | +2.5 % | [-10.7 % ; +16.2 %] | 40.0 % | 1 % | indéterminé |
| SP favori | 423 | 423 | 398 | -5.9 % | [-13.4 % ; +1.8 %] | 61.2 % | 1 % | indéterminé |
| SP top market_calibrated | 423 | 423 | 398 | -5.9 % | [-13.4 % ; +1.8 %] | 61.2 % | 1 % | indéterminé |
| SP top horse_win_rate | 423 | 423 | 394 | -6.9 % | [-17.6 % ; +7.2 %] | 48.5 % | 2 % | indéterminé |
| SP top form | 423 | 423 | 383 | -9.4 % | [-20.3 % ; +3.1 %] | 46.8 % | 4 % | indéterminé |
| SG top horse_win_rate | 423 | 423 | 353 | -16.5 % | [-37.3 % ; +9.9 %] | 22.7 % | 11 % | indéterminé |
| SP hasard | 423 | 423 | 283 | -33.2 % | [-46.6 % ; -19.3 %] | 24.1 % | 5 % | perte significative |
| SG hasard | 423 | 423 | 251 | -40.7 % | [-65.1 % ; -10.7 %] | 8.5 % | 12 % | perte significative |
| SG valeur horse_win_rate | 422 | 2456 | 1346 | -45.2 % | [-57.6 % ; -29.7 %] | 18.7 % | 8 % | perte significative |
| SG valeur form | 423 | 2457 | 1195 | -51.4 % | [-62.9 % ; -37.5 %] | 19.1 % | 6 % | perte significative |
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
| 0.0-0.1 | 3932 | 0.060 | 0.060 |
| 0.1-0.2 | 3888 | 0.146 | 0.175 |
| 0.2-0.3 | 2551 | 0.248 | 0.278 |
| 0.3-0.4 | 1631 | 0.346 | 0.379 |
| 0.4-0.5 | 1172 | 0.447 | 0.441 |
| 0.5-0.6 | 760 | 0.548 | 0.534 |
| 0.6-0.8 | 893 | 0.687 | 0.557 |
| 0.8-1.0 | 505 | 0.897 | 0.677 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
