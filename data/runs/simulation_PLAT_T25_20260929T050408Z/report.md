# Simulation de paris fictifs — plat, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-09-29T05:04:08+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `480e44ff7430` · courses évaluées : 10230, dont 1051 avec rapports officiels · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SG hasard | 1051 | 1051 | 1023 | -2.7 % | [-23.6 % ; +21.8 %] | 12.6 % | 4 % | indéterminé |
| SP top market_calibrated | 1049 | 1049 | 942 | -10.2 % | [-15.4 % ; -5.3 %] | 57.9 % | 0 % | perte significative |
| SP favori | 1049 | 1049 | 941 | -10.3 % | [-15.5 % ; -5.5 %] | 57.9 % | 0 % | perte significative |
| SG favori | 1051 | 1051 | 908 | -13.6 % | [-23.3 % ; -4.1 %] | 28.0 % | 1 % | perte significative |
| SG top market_calibrated | 1051 | 1051 | 908 | -13.6 % | [-23.3 % ; -4.1 %] | 28.0 % | 1 % | perte significative |
| SP top form | 1049 | 1049 | 827 | -21.1 % | [-28.5 % ; -14.0 %] | 41.8 % | 1 % | perte significative |
| SP top horse_win_rate | 1049 | 1049 | 813 | -22.5 % | [-31.4 % ; -13.6 %] | 32.5 % | 2 % | perte significative |
| SG valeur horse_win_rate | 1051 | 5135 | 3912 | -23.8 % | [-33.3 % ; -13.4 %] | 26.6 % | 2 % | perte significative |
| SP hasard | 1049 | 1049 | 783 | -25.4 % | [-34.7 % ; -16.2 %] | 27.5 % | 2 % | perte significative |
| SG valeur form | 1049 | 4457 | 3261 | -26.8 % | [-37.7 % ; -16.0 %] | 26.2 % | 2 % | perte significative |
| SG top form | 1051 | 1051 | 746 | -29.0 % | [-39.7 % ; -18.2 %] | 18.1 % | 2 % | perte significative |
| Tiercé hasard | 42 | 42 | 30 | -29.8 % | [-100.0 % ; +110.7 %] | 2.4 % | 100 % | indéterminé |
| SG top horse_win_rate | 1051 | 1051 | 679 | -35.4 % | [-48.3 % ; -20.8 %] | 13.1 % | 3 % | perte significative |
| SG valeur market_calibrated | 28 | 317 | 205 | -35.4 % | [-50.2 % ; -19.0 %] | 96.4 % | 15 % | perte significative |
| Quinté favoris | 42 | 84 | 35 | -58.6 % | [-89.5 % ; -40.2 %] | 19.0 % | 19 % | perte significative |
| Quinté market_calibrated | 42 | 84 | 35 | -58.6 % | [-89.5 % ; -40.2 %] | 19.0 % | 19 % | perte significative |
| Quinté horse_win_rate | 42 | 84 | 29 | -65.7 % | [-100.0 % ; -35.7 %] | 7.1 % | 39 % | perte significative |
| Quinté form | 42 | 84 | 21 | -75.5 % | [-100.0 % ; -33.1 %] | 4.8 % | 73 % | perte significative |
| Tiercé favoris | 42 | 42 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé market_calibrated | 42 | 42 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 42 | 42 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé form | 42 | 42 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Quinté hasard | 42 | 84 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |

## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place

Marché calibré, phase test. Si « prévu » dépasse « observé » sur les fortes probabilités, Harville surestime les favoris pour les places (biais connu).

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.0-0.1 | 10027 | 0.073 | 0.070 |
| 0.1-0.2 | 23746 | 0.149 | 0.151 |
| 0.2-0.3 | 16614 | 0.248 | 0.265 |
| 0.3-0.4 | 9159 | 0.345 | 0.358 |
| 0.4-0.5 | 5054 | 0.446 | 0.443 |
| 0.5-0.6 | 2970 | 0.545 | 0.522 |
| 0.6-0.8 | 2639 | 0.682 | 0.621 |
| 0.8-1.0 | 1077 | 0.887 | 0.753 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
