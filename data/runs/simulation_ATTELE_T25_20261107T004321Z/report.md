# Simulation de paris fictifs — trot attelé, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-11-07T00:43:21+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `5fa684598919` · courses évaluées : 27400, dont 27216 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP favori | 7583 | 7583 | 7059 | -6.9 % | [-8.6 % ; -5.2 %] | 59.0 % | 0 % | perte significative |
| SP top market_calibrated | 7583 | 7583 | 7048 | -7.1 % | [-8.8 % ; -5.3 %] | 58.9 % | 0 % | perte significative |
| SG favori | 7584 | 7584 | 6702 | -11.6 % | [-14.5 % ; -8.7 %] | 32.7 % | 0 % | perte significative |
| SG top market_calibrated | 7584 | 7584 | 6702 | -11.6 % | [-14.5 % ; -8.7 %] | 32.7 % | 0 % | perte significative |
| SP top horse_win_rate | 7583 | 7583 | 6322 | -16.6 % | [-19.7 % ; -13.7 %] | 39.9 % | 0 % | perte significative |
| SG top horse_win_rate | 7584 | 7584 | 6232 | -17.8 % | [-23.8 % ; -11.5 %] | 19.1 % | 1 % | perte significative |
| SP top form | 7583 | 7583 | 6115 | -19.4 % | [-22.0 % ; -16.7 %] | 40.9 % | 0 % | perte significative |
| SG top form | 7584 | 7584 | 5541 | -26.9 % | [-32.5 % ; -20.9 %] | 16.6 % | 2 % | perte significative |
| SP hasard | 7583 | 7583 | 5334 | -29.7 % | [-33.3 % ; -26.1 %] | 24.5 % | 0 % | perte significative |
| SG hasard | 7584 | 7584 | 5028 | -33.7 % | [-42.0 % ; -24.3 %] | 8.1 % | 3 % | perte significative |
| Tiercé favoris | 322 | 322 | 211 | -34.4 % | [-68.0 % ; +11.3 %] | 6.2 % | 23 % | indéterminé |
| Tiercé market_calibrated | 322 | 322 | 211 | -34.4 % | [-68.0 % ; +11.3 %] | 6.2 % | 23 % | indéterminé |
| SG valeur horse_win_rate | 7584 | 46606 | 28501 | -38.8 % | [-43.0 % ; -34.4 %] | 19.2 % | 1 % | perte significative |
| SG valeur form | 7584 | 48524 | 28330 | -41.6 % | [-45.7 % ; -37.5 %] | 18.6 % | 1 % | perte significative |
| Quinté favoris | 322 | 644 | 343 | -46.8 % | [-57.5 % ; -37.1 %] | 30.7 % | 6 % | perte significative |
| Quinté market_calibrated | 322 | 644 | 343 | -46.8 % | [-57.5 % ; -37.1 %] | 30.7 % | 6 % | perte significative |
| Quinté form | 322 | 644 | 222 | -65.5 % | [-84.0 % ; -41.6 %] | 10.9 % | 26 % | perte significative |
| Tiercé horse_win_rate | 322 | 322 | 103 | -67.9 % | [-96.6 % ; -29.3 %] | 1.2 % | 41 % | perte significative |
| Quinté hasard | 322 | 644 | 199 | -69.0 % | [-99.3 % ; -14.7 %] | 1.6 % | 78 % | perte significative |
| Tiercé form | 322 | 322 | 95 | -70.4 % | [-93.9 % ; -35.7 %] | 1.9 % | 39 % | perte significative |
| Quinté horse_win_rate | 322 | 644 | 183 | -71.5 % | [-79.8 % ; -62.0 %] | 12.1 % | 7 % | perte significative |
| Tiercé hasard | 322 | 322 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase train

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP favori | 17565 | 17565 | 16215 | -7.7 % | [-8.9 % ; -6.4 %] | 57.5 % | 0 % | perte significative |
| SP top market_calibrated | 17565 | 17565 | 16209 | -7.7 % | [-9.0 % ; -6.5 %] | 57.5 % | 0 % | perte significative |
| SG favori | 17565 | 17565 | 15150 | -13.7 % | [-15.9 % ; -11.5 %] | 31.6 % | 0 % | perte significative |
| SG top market_calibrated | 17565 | 17565 | 15150 | -13.7 % | [-15.9 % ; -11.5 %] | 31.6 % | 0 % | perte significative |
| SP top horse_win_rate | 17565 | 17565 | 14508 | -17.4 % | [-19.4 % ; -15.4 %] | 40.1 % | 0 % | perte significative |
| Quinté favoris | 793 | 1586 | 1298 | -18.2 % | [-51.0 % ; +40.6 %] | 29.5 % | 34 % | indéterminé |
| Quinté market_calibrated | 793 | 1586 | 1298 | -18.2 % | [-51.0 % ; +40.6 %] | 29.5 % | 34 % | indéterminé |
| SG top horse_win_rate | 17565 | 17565 | 14307 | -18.5 % | [-22.8 % ; -14.0 %] | 19.1 % | 1 % | perte significative |
| SP top form | 17565 | 17565 | 13830 | -21.3 % | [-22.9 % ; -19.5 %] | 40.0 % | 0 % | perte significative |
| SG top form | 17565 | 17565 | 13048 | -25.7 % | [-29.8 % ; -21.6 %] | 16.8 % | 1 % | perte significative |
| Quinté form | 793 | 1586 | 1164 | -26.6 % | [-74.7 % ; +50.3 %] | 9.8 % | 44 % | indéterminé |
| SP hasard | 17565 | 17565 | 12807 | -27.1 % | [-29.8 % ; -24.5 %] | 23.9 % | 0 % | perte significative |
| SG hasard | 17565 | 17565 | 11712 | -33.3 % | [-38.9 % ; -27.1 %] | 7.6 % | 1 % | perte significative |
| SG valeur horse_win_rate | 17561 | 105575 | 65418 | -38.0 % | [-40.8 % ; -35.3 %] | 19.1 % | 0 % | perte significative |
| SG valeur form | 17564 | 111867 | 64813 | -42.1 % | [-44.7 % ; -39.3 %] | 18.4 % | 0 % | perte significative |
| Tiercé favoris | 793 | 793 | 433 | -45.3 % | [-69.3 % ; -22.2 %] | 5.0 % | 9 % | perte significative |
| Tiercé market_calibrated | 793 | 793 | 433 | -45.3 % | [-69.3 % ; -22.2 %] | 5.0 % | 9 % | perte significative |
| Tiercé horse_win_rate | 793 | 793 | 308 | -61.1 % | [-83.3 % ; -33.2 %] | 1.8 % | 18 % | perte significative |
| Tiercé form | 793 | 793 | 250 | -68.5 % | [-94.2 % ; -22.0 %] | 1.3 % | 66 % | perte significative |
| Quinté horse_win_rate | 793 | 1586 | 431 | -72.8 % | [-82.0 % ; -60.8 %] | 9.7 % | 14 % | perte significative |
| Quinté hasard | 793 | 1586 | 424 | -73.3 % | [-88.1 % ; -51.1 %] | 4.0 % | 32 % | perte significative |
| Tiercé hasard | 793 | 793 | 24 | -97.0 % | [-100.0 % ; -92.1 %] | 0.3 % | 66 % | perte significative |
| SG valeur market_calibrated | 1 | 1 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |

## Phase validation

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Tiercé horse_win_rate | 89 | 89 | 91 | +2.6 % | [-100.0 % ; +77.2 %] | 2.2 % | 73 % | indéterminé |
| SP top market_calibrated | 2064 | 2064 | 1931 | -6.4 % | [-10.3 % ; -2.7 %] | 58.4 % | 0 % | perte significative |
| SP favori | 2064 | 2064 | 1928 | -6.6 % | [-10.5 % ; -3.0 %] | 58.3 % | 0 % | perte significative |
| SG top form | 2064 | 2064 | 1764 | -14.5 % | [-27.9 % ; +2.0 %] | 16.4 % | 4 % | indéterminé |
| SG favori | 2064 | 2064 | 1736 | -15.9 % | [-21.3 % ; -10.4 %] | 31.0 % | 1 % | perte significative |
| SG top market_calibrated | 2064 | 2064 | 1736 | -15.9 % | [-21.3 % ; -10.4 %] | 31.0 % | 1 % | perte significative |
| SP top horse_win_rate | 2064 | 2064 | 1724 | -16.5 % | [-22.1 % ; -11.0 %] | 39.5 % | 1 % | perte significative |
| Tiercé favoris | 89 | 89 | 74 | -16.5 % | [-76.9 % ; +85.1 %] | 9.0 % | 47 % | indéterminé |
| Tiercé market_calibrated | 89 | 89 | 74 | -16.5 % | [-76.9 % ; +85.1 %] | 9.0 % | 47 % | indéterminé |
| SG top horse_win_rate | 2064 | 2064 | 1634 | -20.8 % | [-31.4 % ; -9.3 %] | 18.0 % | 4 % | perte significative |
| SP top form | 2064 | 2064 | 1622 | -21.4 % | [-26.7 % ; -15.8 %] | 37.6 % | 1 % | perte significative |
| SP hasard | 2064 | 2064 | 1484 | -28.1 % | [-35.7 % ; -21.1 %] | 23.8 % | 2 % | perte significative |
| SG hasard | 2064 | 2064 | 1334 | -35.4 % | [-50.8 % ; -16.8 %] | 7.9 % | 9 % | perte significative |
| Quinté favoris | 89 | 178 | 114 | -35.7 % | [-50.6 % ; -18.4 %] | 38.2 % | 7 % | perte significative |
| Quinté market_calibrated | 89 | 178 | 114 | -35.7 % | [-50.6 % ; -18.4 %] | 38.2 % | 7 % | perte significative |
| SG valeur form | 2064 | 13720 | 8111 | -40.9 % | [-48.5 % ; -32.0 %] | 18.7 % | 2 % | perte significative |
| SG valeur horse_win_rate | 2064 | 13127 | 7732 | -41.1 % | [-48.8 % ; -32.8 %] | 19.2 % | 3 % | perte significative |
| Quinté form | 89 | 178 | 76 | -57.4 % | [-87.1 % ; -24.0 %] | 14.6 % | 31 % | perte significative |
| Quinté horse_win_rate | 89 | 178 | 35 | -80.1 % | [-91.9 % ; -67.5 %] | 10.1 % | 18 % | perte significative |
| Tiercé form | 89 | 89 | 12 | -87.1 % | [-100.0 % ; -74.2 %] | 1.1 % | 100 % | perte significative |
| Tiercé hasard | 89 | 89 | 11 | -87.5 % | [-100.0 % ; -62.6 %] | 1.1 % | 100 % | perte significative |
| Quinté hasard | 89 | 178 | 3 | -98.5 % | [-100.0 % ; -95.6 %] | 1.1 % | 100 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place

Marché calibré, phase test. Si « prévu » dépasse « observé » sur les fortes probabilités, Harville surestime les favoris pour les places (biais connu).

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.0-0.1 | 31972 | 0.055 | 0.062 |
| 0.1-0.2 | 24416 | 0.145 | 0.178 |
| 0.2-0.3 | 14673 | 0.247 | 0.277 |
| 0.3-0.4 | 8730 | 0.346 | 0.359 |
| 0.4-0.5 | 5853 | 0.446 | 0.442 |
| 0.5-0.6 | 4085 | 0.547 | 0.482 |
| 0.6-0.8 | 4976 | 0.689 | 0.558 |
| 0.8-1.0 | 3036 | 0.897 | 0.689 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
