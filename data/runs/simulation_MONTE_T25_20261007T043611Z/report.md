# Simulation de paris fictifs — trot monté, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-07T04:36:11+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `72fd7f7bc522` · courses évaluées : 2172, dont 2145 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Quinté favoris | 3 | 6 | 7 | +13.3 % | [— ; —] | 33.3 % | 100 % | échantillon trop petit |
| Quinté market_calibrated | 3 | 6 | 7 | +13.3 % | [— ; —] | 33.3 % | 100 % | échantillon trop petit |
| SP favori | 1343 | 1343 | 1221 | -9.1 % | [-13.4 % ; -4.8 %] | 59.0 % | 0 % | perte significative |
| SP top market_calibrated | 1343 | 1343 | 1221 | -9.1 % | [-13.4 % ; -4.8 %] | 59.0 % | 0 % | perte significative |
| SG favori | 1343 | 1343 | 1164 | -13.4 % | [-20.1 % ; -6.4 %] | 33.4 % | 1 % | perte significative |
| SG top market_calibrated | 1343 | 1343 | 1164 | -13.4 % | [-20.1 % ; -6.4 %] | 33.4 % | 1 % | perte significative |
| SP top horse_win_rate | 1343 | 1343 | 1104 | -17.8 % | [-24.6 % ; -9.6 %] | 42.9 % | 2 % | perte significative |
| SP top form | 1343 | 1343 | 1060 | -21.1 % | [-26.7 % ; -14.9 %] | 44.3 % | 1 % | perte significative |
| SG valeur horse_win_rate | 1343 | 7234 | 5606 | -22.5 % | [-34.1 % ; -9.7 %] | 21.4 % | 3 % | perte significative |
| SG hasard | 1343 | 1343 | 1019 | -24.1 % | [-44.1 % ; -4.0 %] | 10.0 % | 9 % | perte significative |
| SG top horse_win_rate | 1343 | 1343 | 960 | -28.5 % | [-40.8 % ; -14.9 %] | 19.0 % | 5 % | perte significative |
| SP hasard | 1343 | 1343 | 932 | -30.6 % | [-37.3 % ; -23.8 %] | 27.3 % | 1 % | perte significative |
| SG top form | 1343 | 1343 | 907 | -32.4 % | [-43.3 % ; -20.3 %] | 18.2 % | 4 % | perte significative |
| SG valeur form | 1343 | 7346 | 4787 | -34.8 % | [-44.8 % ; -23.4 %] | 18.8 % | 3 % | perte significative |
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
| 0.0-0.1 | 3940 | 0.060 | 0.060 |
| 0.1-0.2 | 3908 | 0.146 | 0.175 |
| 0.2-0.3 | 2564 | 0.248 | 0.278 |
| 0.3-0.4 | 1634 | 0.346 | 0.379 |
| 0.4-0.5 | 1176 | 0.447 | 0.440 |
| 0.5-0.6 | 762 | 0.548 | 0.534 |
| 0.6-0.8 | 898 | 0.687 | 0.558 |
| 0.8-1.0 | 506 | 0.897 | 0.678 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
