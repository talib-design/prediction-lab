# Simulation de paris fictifs — trot attelé, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-11-14T00:51:13+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `c73408cf7286` · courses évaluées : 27494, dont 27308 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP favori | 7675 | 7675 | 7153 | -6.8 % | [-8.6 % ; -5.0 %] | 59.0 % | 0 % | perte significative |
| SP top market_calibrated | 7675 | 7675 | 7142 | -6.9 % | [-8.7 % ; -5.2 %] | 58.9 % | 0 % | perte significative |
| SG favori | 7676 | 7676 | 6764 | -11.9 % | [-14.7 % ; -8.9 %] | 32.6 % | 0 % | perte significative |
| SG top market_calibrated | 7676 | 7676 | 6764 | -11.9 % | [-14.7 % ; -8.9 %] | 32.6 % | 0 % | perte significative |
| SP top horse_win_rate | 7675 | 7675 | 6402 | -16.6 % | [-19.9 % ; -13.5 %] | 39.9 % | 0 % | perte significative |
| SG top horse_win_rate | 7676 | 7676 | 6279 | -18.2 % | [-24.2 % ; -11.4 %] | 19.0 % | 1 % | perte significative |
| SP top form | 7675 | 7675 | 6184 | -19.4 % | [-22.0 % ; -16.8 %] | 40.9 % | 0 % | perte significative |
| SG top form | 7676 | 7676 | 5577 | -27.3 % | [-33.0 % ; -21.4 %] | 16.5 % | 2 % | perte significative |
| SP hasard | 7675 | 7675 | 5376 | -30.0 % | [-33.5 % ; -26.1 %] | 24.4 % | 0 % | perte significative |
| SG hasard | 7676 | 7676 | 5052 | -34.2 % | [-42.4 % ; -24.3 %] | 8.1 % | 3 % | perte significative |
| Tiercé favoris | 325 | 325 | 211 | -35.0 % | [-69.4 % ; +10.3 %] | 6.2 % | 23 % | indéterminé |
| Tiercé market_calibrated | 325 | 325 | 211 | -35.0 % | [-69.4 % ; +10.3 %] | 6.2 % | 23 % | indéterminé |
| SG valeur horse_win_rate | 7676 | 47214 | 28896 | -38.8 % | [-42.8 % ; -34.2 %] | 19.2 % | 1 % | perte significative |
| SG valeur form | 7676 | 49182 | 28610 | -41.8 % | [-45.7 % ; -37.7 %] | 18.6 % | 1 % | perte significative |
| Quinté favoris | 325 | 650 | 352 | -45.9 % | [-56.9 % ; -36.5 %] | 30.8 % | 6 % | perte significative |
| Quinté market_calibrated | 325 | 650 | 352 | -45.9 % | [-56.9 % ; -36.5 %] | 30.8 % | 6 % | perte significative |
| Quinté form | 325 | 650 | 222 | -65.8 % | [-84.9 % ; -39.6 %] | 10.8 % | 26 % | perte significative |
| Tiercé horse_win_rate | 325 | 325 | 103 | -68.2 % | [-96.6 % ; -30.9 %] | 1.2 % | 41 % | perte significative |
| Quinté hasard | 325 | 650 | 199 | -69.3 % | [-99.3 % ; -11.7 %] | 1.5 % | 78 % | perte significative |
| Tiercé form | 325 | 325 | 95 | -70.7 % | [-94.5 % ; -37.8 %] | 1.8 % | 39 % | perte significative |
| Quinté horse_win_rate | 325 | 650 | 183 | -71.8 % | [-80.1 % ; -62.1 %] | 12.0 % | 7 % | perte significative |
| Tiercé hasard | 325 | 325 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
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
| 0.0-0.1 | 32461 | 0.055 | 0.062 |
| 0.1-0.2 | 24699 | 0.145 | 0.178 |
| 0.2-0.3 | 14850 | 0.247 | 0.277 |
| 0.3-0.4 | 8825 | 0.346 | 0.359 |
| 0.4-0.5 | 5944 | 0.446 | 0.443 |
| 0.5-0.6 | 4125 | 0.547 | 0.482 |
| 0.6-0.8 | 5052 | 0.689 | 0.559 |
| 0.8-1.0 | 3062 | 0.897 | 0.689 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
