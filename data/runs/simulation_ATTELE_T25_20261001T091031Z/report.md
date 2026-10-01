# Simulation de paris fictifs — trot attelé, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-01T09:10:31+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `2ef750f3aa6c` · courses évaluées : 1898, dont 1842 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP favori | 1842 | 1842 | 1717 | -6.8 % | [-10.3 % ; -3.4 %] | 60.0 % | 0 % | perte significative |
| SP top market_calibrated | 1842 | 1842 | 1717 | -6.8 % | [-10.3 % ; -3.3 %] | 60.0 % | 0 % | perte significative |
| SG favori | 1842 | 1842 | 1562 | -15.2 % | [-20.9 % ; -9.6 %] | 32.5 % | 0 % | perte significative |
| SG top market_calibrated | 1842 | 1842 | 1562 | -15.2 % | [-20.9 % ; -9.6 %] | 32.5 % | 0 % | perte significative |
| SP top form | 1842 | 1842 | 1530 | -16.9 % | [-23.1 % ; -10.0 %] | 40.9 % | 1 % | perte significative |
| SP top horse_win_rate | 1842 | 1842 | 1481 | -19.6 % | [-25.2 % ; -13.2 %] | 38.3 % | 1 % | perte significative |
| SG top form | 1842 | 1842 | 1351 | -26.6 % | [-38.6 % ; -12.1 %] | 16.1 % | 7 % | perte significative |
| SG top horse_win_rate | 1842 | 1842 | 1286 | -30.2 % | [-39.8 % ; -19.5 %] | 16.2 % | 3 % | perte significative |
| SP hasard | 1842 | 1842 | 1267 | -31.2 % | [-38.4 % ; -24.5 %] | 26.4 % | 1 % | perte significative |
| SG hasard | 1842 | 1842 | 1060 | -42.5 % | [-54.3 % ; -28.4 %] | 8.0 % | 5 % | perte significative |
| Quinté favoris | 72 | 144 | 82 | -42.8 % | [-68.8 % ; -16.5 %] | 30.6 % | 24 % | perte significative |
| Quinté market_calibrated | 72 | 144 | 82 | -42.8 % | [-68.8 % ; -16.5 %] | 30.6 % | 24 % | perte significative |
| Tiercé favoris | 72 | 72 | 41 | -42.9 % | [-90.0 % ; -8.3 %] | 6.9 % | 22 % | perte significative |
| Tiercé market_calibrated | 72 | 72 | 41 | -42.9 % | [-90.0 % ; -8.3 %] | 6.9 % | 22 % | perte significative |
| SG valeur horse_win_rate | 1842 | 12109 | 6846 | -43.5 % | [-51.1 % ; -35.1 %] | 19.2 % | 2 % | perte significative |
| SG valeur form | 1842 | 11623 | 6253 | -46.2 % | [-53.2 % ; -38.8 %] | 19.5 % | 2 % | perte significative |
| Quinté horse_win_rate | 72 | 144 | 18 | -87.5 % | [-98.5 % ; -72.4 %] | 5.6 % | 46 % | perte significative |
| Tiercé form | 72 | 72 | 9 | -87.9 % | [-100.0 % ; -63.7 %] | 1.4 % | 100 % | perte significative |
| Quinté form | 72 | 144 | 15 | -89.7 % | [-97.8 % ; -79.3 %] | 6.9 % | 32 % | perte significative |
| Quinté hasard | 72 | 144 | 2 | -98.3 % | [-100.0 % ; -95.0 %] | 1.4 % | 100 % | perte significative |
| Tiercé hasard | 72 | 72 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 72 | 72 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place

Marché calibré, phase test. Si « prévu » dépasse « observé » sur les fortes probabilités, Harville surestime les favoris pour les places (biais connu).

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.0-0.1 | 7140 | 0.057 | 0.060 |
| 0.1-0.2 | 5921 | 0.144 | 0.175 |
| 0.2-0.3 | 3606 | 0.247 | 0.277 |
| 0.3-0.4 | 2133 | 0.346 | 0.363 |
| 0.4-0.5 | 1486 | 0.448 | 0.462 |
| 0.5-0.6 | 1017 | 0.548 | 0.473 |
| 0.6-0.8 | 1235 | 0.688 | 0.583 |
| 0.8-1.0 | 761 | 0.897 | 0.696 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
