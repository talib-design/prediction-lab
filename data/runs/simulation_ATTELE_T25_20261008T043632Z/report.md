# Simulation de paris fictifs — trot attelé, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-08T04:36:32+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `8630727d2f9a` · courses évaluées : 16131, dont 15985 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP top market_calibrated | 7224 | 7224 | 6731 | -6.8 % | [-8.5 % ; -4.9 %] | 59.0 % | 0 % | perte significative |
| SP favori | 7224 | 7224 | 6725 | -6.9 % | [-8.6 % ; -5.0 %] | 59.0 % | 0 % | perte significative |
| SG favori | 7224 | 7224 | 6398 | -11.4 % | [-14.4 % ; -8.1 %] | 32.9 % | 0 % | perte significative |
| SG top market_calibrated | 7224 | 7224 | 6398 | -11.4 % | [-14.4 % ; -8.1 %] | 32.9 % | 0 % | perte significative |
| SP top horse_win_rate | 7224 | 7224 | 5978 | -17.3 % | [-20.4 % ; -14.1 %] | 40.3 % | 0 % | perte significative |
| SP top form | 7224 | 7224 | 5817 | -19.5 % | [-22.0 % ; -16.4 %] | 40.9 % | 0 % | perte significative |
| SG top horse_win_rate | 7224 | 7224 | 5715 | -20.9 % | [-26.0 % ; -15.5 %] | 19.1 % | 1 % | perte significative |
| SG top form | 7224 | 7224 | 5184 | -28.2 % | [-33.8 % ; -21.9 %] | 16.6 % | 2 % | perte significative |
| Quinté horse_win_rate | 311 | 622 | 446 | -28.3 % | [-78.0 % ; +48.0 %] | 12.2 % | 39 % | indéterminé |
| SP hasard | 7224 | 7224 | 5084 | -29.6 % | [-33.3 % ; -26.2 %] | 24.5 % | 0 % | perte significative |
| Tiercé favoris | 311 | 311 | 211 | -32.1 % | [-67.5 % ; +14.5 %] | 6.4 % | 23 % | indéterminé |
| Tiercé market_calibrated | 311 | 311 | 211 | -32.1 % | [-67.5 % ; +14.5 %] | 6.4 % | 23 % | indéterminé |
| SG hasard | 7224 | 7224 | 4642 | -35.7 % | [-44.4 % ; -26.1 %] | 8.0 % | 3 % | perte significative |
| SG valeur horse_win_rate | 7224 | 43722 | 26575 | -39.2 % | [-43.6 % ; -34.6 %] | 19.4 % | 1 % | perte significative |
| SG valeur form | 7224 | 45992 | 26726 | -41.9 % | [-46.0 % ; -37.8 %] | 18.6 % | 1 % | perte significative |
| Quinté favoris | 311 | 622 | 326 | -47.7 % | [-57.8 % ; -37.5 %] | 30.2 % | 6 % | perte significative |
| Quinté market_calibrated | 311 | 622 | 326 | -47.7 % | [-57.8 % ; -37.5 %] | 30.2 % | 6 % | perte significative |
| Quinté form | 311 | 622 | 220 | -64.7 % | [-84.0 % ; -36.8 %] | 10.9 % | 27 % | perte significative |
| Quinté hasard | 311 | 622 | 199 | -67.9 % | [-99.2 % ; -11.7 %] | 1.6 % | 78 % | perte significative |
| Tiercé horse_win_rate | 311 | 311 | 97 | -68.8 % | [-96.5 % ; -30.6 %] | 1.3 % | 44 % | perte significative |
| Tiercé form | 311 | 311 | 95 | -69.4 % | [-95.1 % ; -34.8 %] | 1.9 % | 39 % | perte significative |
| Tiercé hasard | 311 | 311 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase train

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP top market_calibrated | 6697 | 6697 | 6263 | -6.5 % | [-8.5 % ; -4.7 %] | 57.1 % | 0 % | perte significative |
| SP favori | 6697 | 6697 | 6261 | -6.5 % | [-8.5 % ; -4.7 %] | 57.1 % | 0 % | perte significative |
| SG favori | 6697 | 6697 | 5648 | -15.7 % | [-19.1 % ; -12.2 %] | 30.5 % | 0 % | perte significative |
| SG top market_calibrated | 6697 | 6697 | 5648 | -15.7 % | [-19.1 % ; -12.2 %] | 30.5 % | 0 % | perte significative |
| SP top horse_win_rate | 6697 | 6697 | 5423 | -19.0 % | [-21.8 % ; -15.8 %] | 38.2 % | 0 % | perte significative |
| SP top form | 6697 | 6697 | 5264 | -21.4 % | [-24.1 % ; -18.6 %] | 38.8 % | 0 % | perte significative |
| SG top horse_win_rate | 6697 | 6697 | 4968 | -25.8 % | [-31.1 % ; -19.9 %] | 17.6 % | 1 % | perte significative |
| SG top form | 6697 | 6697 | 4830 | -27.9 % | [-33.6 % ; -21.9 %] | 15.8 % | 1 % | perte significative |
| SP hasard | 6697 | 6697 | 4691 | -30.0 % | [-33.8 % ; -25.7 %] | 23.2 % | 0 % | perte significative |
| SG hasard | 6697 | 6697 | 4274 | -36.2 % | [-44.5 % ; -26.2 %] | 7.4 % | 3 % | perte significative |
| Quinté favoris | 305 | 610 | 378 | -38.0 % | [-51.3 % ; -24.3 %] | 32.1 % | 8 % | perte significative |
| Quinté market_calibrated | 305 | 610 | 378 | -38.0 % | [-51.3 % ; -24.3 %] | 32.1 % | 8 % | perte significative |
| SG valeur form | 6697 | 42616 | 25582 | -40.0 % | [-44.4 % ; -35.8 %] | 19.1 % | 1 % | perte significative |
| SG valeur horse_win_rate | 6696 | 40540 | 23993 | -40.8 % | [-45.0 % ; -36.7 %] | 19.1 % | 1 % | perte significative |
| Tiercé favoris | 305 | 305 | 88 | -71.1 % | [-90.4 % ; -47.4 %] | 3.6 % | 27 % | perte significative |
| Tiercé market_calibrated | 305 | 305 | 88 | -71.1 % | [-90.4 % ; -47.4 %] | 3.6 % | 27 % | perte significative |
| Quinté form | 305 | 610 | 160 | -73.8 % | [-84.9 % ; -59.9 %] | 8.5 % | 12 % | perte significative |
| Tiercé form | 305 | 305 | 70 | -76.9 % | [-92.8 % ; -55.5 %] | 2.0 % | 29 % | perte significative |
| Quinté hasard | 305 | 610 | 101 | -83.4 % | [-94.0 % ; -67.8 %] | 3.6 % | 34 % | perte significative |
| Quinté horse_win_rate | 305 | 610 | 91 | -85.0 % | [-91.4 % ; -78.4 %] | 7.9 % | 10 % | perte significative |
| Tiercé horse_win_rate | 305 | 305 | 26 | -91.5 % | [-100.0 % ; -74.6 %] | 0.7 % | 76 % | perte significative |
| Tiercé hasard | 305 | 305 | 16 | -94.9 % | [-100.0 % ; -84.7 %] | 0.3 % | 100 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase validation

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP top market_calibrated | 2064 | 2064 | 1931 | -6.4 % | [-10.4 % ; -2.8 %] | 58.4 % | 0 % | perte significative |
| SP favori | 2064 | 2064 | 1928 | -6.6 % | [-10.5 % ; -3.0 %] | 58.3 % | 0 % | perte significative |
| SG top form | 2064 | 2064 | 1763 | -14.6 % | [-28.0 % ; +1.8 %] | 16.4 % | 4 % | indéterminé |
| SG favori | 2064 | 2064 | 1736 | -15.9 % | [-21.3 % ; -10.4 %] | 31.0 % | 1 % | perte significative |
| SG top market_calibrated | 2064 | 2064 | 1736 | -15.9 % | [-21.3 % ; -10.4 %] | 31.0 % | 1 % | perte significative |
| Tiercé favoris | 89 | 89 | 74 | -16.5 % | [-76.9 % ; +85.1 %] | 9.0 % | 47 % | indéterminé |
| Tiercé market_calibrated | 89 | 89 | 74 | -16.5 % | [-76.9 % ; +85.1 %] | 9.0 % | 47 % | indéterminé |
| SP top horse_win_rate | 2064 | 2064 | 1708 | -17.3 % | [-22.5 % ; -11.8 %] | 39.7 % | 1 % | perte significative |
| SG top horse_win_rate | 2064 | 2064 | 1641 | -20.5 % | [-31.5 % ; -8.3 %] | 18.0 % | 4 % | perte significative |
| SP top form | 2064 | 2064 | 1622 | -21.4 % | [-26.7 % ; -15.8 %] | 37.6 % | 1 % | perte significative |
| SP hasard | 2064 | 2064 | 1484 | -28.1 % | [-35.7 % ; -21.1 %] | 23.8 % | 2 % | perte significative |
| SG hasard | 2064 | 2064 | 1334 | -35.4 % | [-50.8 % ; -16.8 %] | 7.9 % | 9 % | perte significative |
| Quinté favoris | 89 | 178 | 114 | -35.7 % | [-50.6 % ; -18.4 %] | 38.2 % | 7 % | perte significative |
| Quinté market_calibrated | 89 | 178 | 114 | -35.7 % | [-50.6 % ; -18.4 %] | 38.2 % | 7 % | perte significative |
| SG valeur horse_win_rate | 2064 | 12824 | 7678 | -40.1 % | [-48.2 % ; -31.3 %] | 20.0 % | 3 % | perte significative |
| SG valeur form | 2064 | 13712 | 8111 | -40.8 % | [-48.4 % ; -32.0 %] | 18.7 % | 2 % | perte significative |
| Quinté form | 89 | 178 | 76 | -57.4 % | [-87.1 % ; -24.0 %] | 14.6 % | 31 % | perte significative |
| Quinté horse_win_rate | 89 | 178 | 27 | -84.7 % | [-94.5 % ; -74.6 %] | 10.1 % | 20 % | perte significative |
| Tiercé form | 89 | 89 | 12 | -87.1 % | [-100.0 % ; -74.2 %] | 1.1 % | 100 % | perte significative |
| Tiercé hasard | 89 | 89 | 11 | -87.5 % | [-100.0 % ; -62.6 %] | 1.1 % | 100 % | perte significative |
| Quinté hasard | 89 | 178 | 3 | -98.5 % | [-100.0 % ; -95.6 %] | 1.1 % | 100 % | perte significative |
| Tiercé horse_win_rate | 89 | 89 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place

Marché calibré, phase test. Si « prévu » dépasse « observé » sur les fortes probabilités, Harville surestime les favoris pour les places (biais connu).

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.0-0.1 | 29672 | 0.056 | 0.061 |
| 0.1-0.2 | 23531 | 0.145 | 0.177 |
| 0.2-0.3 | 14173 | 0.247 | 0.276 |
| 0.3-0.4 | 8389 | 0.346 | 0.359 |
| 0.4-0.5 | 5652 | 0.446 | 0.446 |
| 0.5-0.6 | 3879 | 0.547 | 0.484 |
| 0.6-0.8 | 4678 | 0.688 | 0.561 |
| 0.8-1.0 | 2815 | 0.896 | 0.688 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
