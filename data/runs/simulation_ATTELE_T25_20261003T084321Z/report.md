# Simulation de paris fictifs — trot attelé, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-03T08:43:21+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `992ba1c20722` · courses évaluées : 1947, dont 1891 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP top market_calibrated | 1891 | 1891 | 1775 | -6.1 % | [-9.9 % ; -2.7 %] | 60.4 % | 0 % | perte significative |
| SP favori | 1891 | 1891 | 1773 | -6.2 % | [-10.0 % ; -2.7 %] | 60.4 % | 0 % | perte significative |
| SG favori | 1891 | 1891 | 1619 | -14.4 % | [-20.7 % ; -8.8 %] | 32.8 % | 0 % | perte significative |
| SG top market_calibrated | 1891 | 1891 | 1619 | -14.4 % | [-20.7 % ; -8.8 %] | 32.8 % | 0 % | perte significative |
| SP top horse_win_rate | 1891 | 1891 | 1572 | -16.9 % | [-23.0 % ; -10.9 %] | 38.7 % | 1 % | perte significative |
| SP top form | 1891 | 1891 | 1552 | -18.0 % | [-24.2 % ; -12.3 %] | 40.7 % | 1 % | perte significative |
| SG top horse_win_rate | 1891 | 1891 | 1495 | -20.9 % | [-35.9 % ; -5.8 %] | 16.4 % | 7 % | perte significative |
| SG top form | 1891 | 1891 | 1491 | -21.1 % | [-35.5 % ; -7.4 %] | 16.4 % | 6 % | perte significative |
| SP hasard | 1891 | 1891 | 1295 | -31.5 % | [-37.8 % ; -24.6 %] | 26.2 % | 1 % | perte significative |
| SG hasard | 1891 | 1891 | 1266 | -33.0 % | [-50.9 % ; -10.9 %] | 8.1 % | 12 % | perte significative |
| Quinté favoris | 74 | 148 | 88 | -40.3 % | [-66.1 % ; -15.9 %] | 32.4 % | 22 % | perte significative |
| Quinté market_calibrated | 74 | 148 | 88 | -40.3 % | [-66.1 % ; -15.9 %] | 32.4 % | 22 % | perte significative |
| SG valeur horse_win_rate | 1891 | 12438 | 7133 | -42.6 % | [-50.5 % ; -34.6 %] | 19.0 % | 2 % | perte significative |
| Tiercé favoris | 74 | 74 | 41 | -44.5 % | [-87.7 % ; -5.9 %] | 6.8 % | 22 % | perte significative |
| Tiercé market_calibrated | 74 | 74 | 41 | -44.5 % | [-87.7 % ; -5.9 %] | 6.8 % | 22 % | perte significative |
| SG valeur form | 1891 | 11972 | 6570 | -45.1 % | [-52.3 % ; -37.6 %] | 19.5 % | 2 % | perte significative |
| Quinté horse_win_rate | 74 | 148 | 18 | -87.8 % | [-98.5 % ; -73.1 %] | 5.4 % | 46 % | perte significative |
| Tiercé form | 74 | 74 | 9 | -88.2 % | [-100.0 % ; -64.7 %] | 1.4 % | 100 % | perte significative |
| Quinté form | 74 | 148 | 7 | -95.4 % | [-100.0 % ; -88.0 %] | 4.1 % | 35 % | perte significative |
| Quinté hasard | 74 | 148 | 2 | -98.4 % | [-100.0 % ; -95.1 %] | 1.4 % | 100 % | perte significative |
| Tiercé hasard | 74 | 74 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 74 | 74 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place

Marché calibré, phase test. Si « prévu » dépasse « observé » sur les fortes probabilités, Harville surestime les favoris pour les places (biais connu).

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.0-0.1 | 7361 | 0.057 | 0.060 |
| 0.1-0.2 | 6099 | 0.144 | 0.173 |
| 0.2-0.3 | 3727 | 0.247 | 0.278 |
| 0.3-0.4 | 2201 | 0.346 | 0.361 |
| 0.4-0.5 | 1529 | 0.448 | 0.464 |
| 0.5-0.6 | 1036 | 0.548 | 0.472 |
| 0.6-0.8 | 1259 | 0.689 | 0.586 |
| 0.8-1.0 | 772 | 0.896 | 0.699 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
