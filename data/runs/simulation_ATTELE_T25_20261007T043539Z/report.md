# Simulation de paris fictifs — trot attelé, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-07T04:35:39+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `83ce80d4b2be` · courses évaluées : 11421, dont 11294 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP favori | 7218 | 7218 | 6722 | -6.9 % | [-8.5 % ; -5.0 %] | 59.0 % | 0 % | perte significative |
| SP top market_calibrated | 7218 | 7218 | 6722 | -6.9 % | [-8.6 % ; -5.0 %] | 59.0 % | 0 % | perte significative |
| SG favori | 7218 | 7218 | 6391 | -11.5 % | [-14.5 % ; -8.0 %] | 32.9 % | 0 % | perte significative |
| SG top market_calibrated | 7218 | 7218 | 6391 | -11.5 % | [-14.5 % ; -8.0 %] | 32.9 % | 0 % | perte significative |
| SP top form | 7218 | 7218 | 5798 | -19.7 % | [-22.3 % ; -16.7 %] | 40.8 % | 0 % | perte significative |
| SP top horse_win_rate | 7218 | 7218 | 5789 | -19.8 % | [-22.6 % ; -16.8 %] | 39.8 % | 0 % | perte significative |
| SG top horse_win_rate | 7218 | 7218 | 5677 | -21.4 % | [-26.6 % ; -15.6 %] | 18.9 % | 1 % | perte significative |
| SG top form | 7218 | 7218 | 5206 | -27.9 % | [-33.4 % ; -21.5 %] | 16.6 % | 2 % | perte significative |
| SP hasard | 7218 | 7218 | 5076 | -29.7 % | [-33.2 % ; -26.3 %] | 24.5 % | 0 % | perte significative |
| Tiercé favoris | 310 | 310 | 211 | -31.9 % | [-66.9 % ; +15.9 %] | 6.5 % | 23 % | indéterminé |
| Tiercé market_calibrated | 310 | 310 | 211 | -31.9 % | [-66.9 % ; +15.9 %] | 6.5 % | 23 % | indéterminé |
| SG hasard | 7218 | 7218 | 4642 | -35.7 % | [-44.2 % ; -26.3 %] | 8.0 % | 3 % | perte significative |
| SG valeur horse_win_rate | 7218 | 42814 | 26271 | -38.6 % | [-43.0 % ; -34.3 %] | 19.9 % | 1 % | perte significative |
| SG valeur form | 7218 | 45926 | 26733 | -41.8 % | [-45.9 % ; -37.7 %] | 18.7 % | 1 % | perte significative |
| Quinté favoris | 310 | 620 | 326 | -47.5 % | [-57.8 % ; -37.6 %] | 30.3 % | 6 % | perte significative |
| Quinté market_calibrated | 310 | 620 | 326 | -47.5 % | [-57.8 % ; -37.6 %] | 30.3 % | 6 % | perte significative |
| Quinté horse_win_rate | 310 | 620 | 281 | -54.6 % | [-87.4 % ; +4.9 %] | 8.7 % | 62 % | indéterminé |
| Quinté form | 310 | 620 | 220 | -64.5 % | [-83.6 % ; -36.3 %] | 11.0 % | 27 % | perte significative |
| Quinté hasard | 310 | 620 | 199 | -67.8 % | [-99.2 % ; -11.6 %] | 1.6 % | 78 % | perte significative |
| Tiercé form | 310 | 310 | 79 | -74.6 % | [-97.5 % ; -40.3 %] | 1.6 % | 47 % | perte significative |
| Tiercé horse_win_rate | 310 | 310 | 11 | -96.5 % | [-100.0 % ; -89.5 %] | 0.3 % | 100 % | perte significative |
| Tiercé hasard | 310 | 310 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase train

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Quinté form | 88 | 176 | 228 | +29.8 % | [-94.7 % ; +264.4 %] | 8.0 % | 86 % | indéterminé |
| Quinté horse_win_rate | 88 | 176 | 187 | +6.0 % | [-88.8 % ; +176.4 %] | 8.0 % | 74 % | indéterminé |
| SP top market_calibrated | 2012 | 2012 | 1909 | -5.1 % | [-8.8 % ; -1.5 %] | 57.8 % | 0 % | perte significative |
| SP favori | 2012 | 2012 | 1909 | -5.1 % | [-8.8 % ; -1.5 %] | 57.8 % | 0 % | perte significative |
| SG favori | 2012 | 2012 | 1716 | -14.7 % | [-20.5 % ; -8.8 %] | 30.1 % | 1 % | perte significative |
| SG top market_calibrated | 2012 | 2012 | 1716 | -14.7 % | [-20.5 % ; -8.8 %] | 30.1 % | 1 % | perte significative |
| SP top horse_win_rate | 2012 | 2012 | 1636 | -18.7 % | [-24.8 % ; -11.5 %] | 36.4 % | 1 % | perte significative |
| SG top horse_win_rate | 2012 | 2012 | 1578 | -21.6 % | [-34.3 % ; -7.5 %] | 16.8 % | 4 % | perte significative |
| SP top form | 2012 | 2012 | 1532 | -23.9 % | [-28.7 % ; -19.1 %] | 37.7 % | 1 % | perte significative |
| SG hasard | 2012 | 2012 | 1416 | -29.6 % | [-44.5 % ; -13.1 %] | 8.3 % | 7 % | perte significative |
| SG top form | 2012 | 2012 | 1357 | -32.5 % | [-42.8 % ; -22.4 %] | 14.8 % | 4 % | perte significative |
| SP hasard | 2012 | 2012 | 1332 | -33.8 % | [-41.1 % ; -26.7 %] | 22.9 % | 1 % | perte significative |
| Quinté favoris | 88 | 176 | 103 | -41.3 % | [-57.8 % ; -17.5 %] | 34.1 % | 12 % | perte significative |
| Quinté market_calibrated | 88 | 176 | 103 | -41.3 % | [-57.8 % ; -17.5 %] | 34.1 % | 12 % | perte significative |
| SG valeur horse_win_rate | 2012 | 13347 | 7752 | -41.9 % | [-49.7 % ; -34.1 %] | 18.2 % | 2 % | perte significative |
| SG valeur form | 2012 | 13080 | 7166 | -45.2 % | [-52.6 % ; -37.6 %] | 17.1 % | 3 % | perte significative |
| Quinté hasard | 88 | 176 | 67 | -62.0 % | [-95.2 % ; -14.1 %] | 5.7 % | 51 % | perte significative |
| Tiercé favoris | 88 | 88 | 30 | -65.8 % | [-96.7 % ; -20.9 %] | 4.5 % | 61 % | perte significative |
| Tiercé market_calibrated | 88 | 88 | 30 | -65.8 % | [-96.7 % ; -20.9 %] | 4.5 % | 61 % | perte significative |
| Tiercé form | 88 | 88 | 17 | -80.7 % | [-100.0 % ; -42.0 %] | 1.1 % | 100 % | perte significative |
| Tiercé hasard | 88 | 88 | 16 | -82.3 % | [-100.0 % ; -46.8 %] | 1.1 % | 100 % | perte significative |
| Tiercé horse_win_rate | 88 | 88 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase validation

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Tiercé form | 89 | 89 | 184 | +107.2 % | [-100.0 % ; +495.7 %] | 2.2 % | 94 % | indéterminé |
| Tiercé horse_win_rate | 89 | 89 | 94 | +5.7 % | [-100.0 % ; +217.2 %] | 2.2 % | 68 % | indéterminé |
| SP top market_calibrated | 2064 | 2064 | 1933 | -6.3 % | [-10.3 % ; -2.6 %] | 58.5 % | 0 % | perte significative |
| SP favori | 2064 | 2064 | 1928 | -6.6 % | [-10.5 % ; -3.0 %] | 58.3 % | 0 % | perte significative |
| SG top form | 2064 | 2064 | 1739 | -15.8 % | [-29.0 % ; +0.9 %] | 16.5 % | 4 % | indéterminé |
| SG favori | 2064 | 2064 | 1736 | -15.9 % | [-21.3 % ; -10.4 %] | 31.0 % | 1 % | perte significative |
| SG top market_calibrated | 2064 | 2064 | 1736 | -15.9 % | [-21.3 % ; -10.4 %] | 31.0 % | 1 % | perte significative |
| Tiercé favoris | 89 | 89 | 74 | -16.5 % | [-76.9 % ; +85.1 %] | 9.0 % | 47 % | indéterminé |
| Tiercé market_calibrated | 89 | 89 | 74 | -16.5 % | [-76.9 % ; +85.1 %] | 9.0 % | 47 % | indéterminé |
| SP top horse_win_rate | 2064 | 2064 | 1709 | -17.2 % | [-23.2 % ; -10.6 %] | 38.7 % | 1 % | perte significative |
| SP top form | 2064 | 2064 | 1575 | -23.7 % | [-28.9 % ; -18.4 %] | 37.1 % | 1 % | perte significative |
| SG top horse_win_rate | 2064 | 2064 | 1566 | -24.1 % | [-36.1 % ; -11.1 %] | 17.2 % | 4 % | perte significative |
| SP hasard | 2064 | 2064 | 1484 | -28.1 % | [-35.7 % ; -21.1 %] | 23.8 % | 2 % | perte significative |
| SG hasard | 2064 | 2064 | 1334 | -35.4 % | [-50.8 % ; -16.8 %] | 7.9 % | 9 % | perte significative |
| Quinté favoris | 89 | 178 | 114 | -35.7 % | [-50.6 % ; -18.4 %] | 38.2 % | 7 % | perte significative |
| Quinté market_calibrated | 89 | 178 | 114 | -35.7 % | [-50.6 % ; -18.4 %] | 38.2 % | 7 % | perte significative |
| SG valeur form | 2064 | 13663 | 8144 | -40.4 % | [-47.9 % ; -31.6 %] | 19.0 % | 2 % | perte significative |
| SG valeur horse_win_rate | 2064 | 12879 | 7569 | -41.2 % | [-49.3 % ; -32.1 %] | 19.7 % | 3 % | perte significative |
| Quinté form | 89 | 178 | 71 | -60.0 % | [-88.9 % ; -28.1 %] | 12.4 % | 33 % | perte significative |
| Quinté horse_win_rate | 89 | 178 | 60 | -66.5 % | [-88.0 % ; -35.8 %] | 11.2 % | 31 % | perte significative |
| Tiercé hasard | 89 | 89 | 11 | -87.5 % | [-100.0 % ; -62.6 %] | 1.1 % | 100 % | perte significative |
| Quinté hasard | 89 | 178 | 3 | -98.5 % | [-100.0 % ; -95.6 %] | 1.1 % | 100 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place

Marché calibré, phase test. Si « prévu » dépasse « observé » sur les fortes probabilités, Harville surestime les favoris pour les places (biais connu).

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.0-0.1 | 29517 | 0.056 | 0.061 |
| 0.1-0.2 | 23575 | 0.145 | 0.177 |
| 0.2-0.3 | 14227 | 0.247 | 0.276 |
| 0.3-0.4 | 8415 | 0.346 | 0.359 |
| 0.4-0.5 | 5642 | 0.446 | 0.446 |
| 0.5-0.6 | 3885 | 0.547 | 0.485 |
| 0.6-0.8 | 4658 | 0.688 | 0.564 |
| 0.8-1.0 | 2783 | 0.896 | 0.688 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
