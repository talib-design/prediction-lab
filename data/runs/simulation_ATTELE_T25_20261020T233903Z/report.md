# Simulation de paris fictifs — trot attelé, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-20T23:39:03+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `92fc1cbf36ab` · courses évaluées : 27194, dont 27011 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP favori | 7380 | 7380 | 6871 | -6.9 % | [-8.6 % ; -5.1 %] | 59.0 % | 0 % | perte significative |
| SP top market_calibrated | 7380 | 7380 | 6859 | -7.1 % | [-8.8 % ; -5.3 %] | 59.0 % | 0 % | perte significative |
| SG favori | 7381 | 7381 | 6547 | -11.3 % | [-14.1 % ; -8.2 %] | 32.9 % | 0 % | perte significative |
| SG top market_calibrated | 7381 | 7381 | 6547 | -11.3 % | [-14.1 % ; -8.2 %] | 32.9 % | 0 % | perte significative |
| SP top horse_win_rate | 7380 | 7380 | 6177 | -16.3 % | [-19.4 % ; -13.3 %] | 40.0 % | 0 % | perte significative |
| SG top horse_win_rate | 7381 | 7381 | 6122 | -17.1 % | [-23.4 % ; -10.5 %] | 19.2 % | 1 % | perte significative |
| SP top form | 7380 | 7380 | 5948 | -19.4 % | [-22.1 % ; -16.5 %] | 41.0 % | 0 % | perte significative |
| SG top form | 7381 | 7381 | 5377 | -27.2 % | [-32.7 % ; -21.0 %] | 16.7 % | 2 % | perte significative |
| SP hasard | 7380 | 7380 | 5175 | -29.9 % | [-33.4 % ; -26.4 %] | 24.5 % | 0 % | perte significative |
| Tiercé favoris | 314 | 314 | 211 | -32.8 % | [-67.5 % ; +14.9 %] | 6.4 % | 23 % | indéterminé |
| Tiercé market_calibrated | 314 | 314 | 211 | -32.8 % | [-67.5 % ; +14.9 %] | 6.4 % | 23 % | indéterminé |
| SG hasard | 7381 | 7381 | 4770 | -35.4 % | [-43.9 % ; -25.9 %] | 8.0 % | 3 % | perte significative |
| SG valeur horse_win_rate | 7381 | 45241 | 27494 | -39.2 % | [-43.8 % ; -34.4 %] | 19.1 % | 1 % | perte significative |
| SG valeur form | 7381 | 47069 | 27388 | -41.8 % | [-46.0 % ; -37.4 %] | 18.6 % | 1 % | perte significative |
| Quinté favoris | 314 | 628 | 326 | -48.2 % | [-57.9 % ; -37.8 %] | 29.9 % | 6 % | perte significative |
| Quinté market_calibrated | 314 | 628 | 326 | -48.2 % | [-57.9 % ; -37.8 %] | 29.9 % | 6 % | perte significative |
| Quinté form | 314 | 628 | 220 | -65.0 % | [-84.1 % ; -36.7 %] | 10.8 % | 27 % | perte significative |
| Tiercé horse_win_rate | 314 | 314 | 103 | -67.1 % | [-96.5 % ; -27.1 %] | 1.3 % | 41 % | perte significative |
| Quinté hasard | 314 | 628 | 199 | -68.2 % | [-99.2 % ; -12.9 %] | 1.6 % | 78 % | perte significative |
| Tiercé form | 314 | 314 | 95 | -69.7 % | [-94.3 % ; -35.1 %] | 1.9 % | 39 % | perte significative |
| Quinté horse_win_rate | 314 | 628 | 183 | -70.8 % | [-79.1 % ; -61.1 %] | 12.4 % | 7 % | perte significative |
| Tiercé hasard | 314 | 314 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
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
| 0.0-0.1 | 30949 | 0.055 | 0.062 |
| 0.1-0.2 | 23733 | 0.145 | 0.179 |
| 0.2-0.3 | 14237 | 0.247 | 0.277 |
| 0.3-0.4 | 8499 | 0.346 | 0.359 |
| 0.4-0.5 | 5710 | 0.446 | 0.443 |
| 0.5-0.6 | 3980 | 0.547 | 0.482 |
| 0.6-0.8 | 4840 | 0.689 | 0.560 |
| 0.8-1.0 | 2967 | 0.897 | 0.686 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
