# Simulation de paris fictifs — trot attelé, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-02T06:43:21+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `03ecc6603895` · courses évaluées : 1912, dont 1856 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP top market_calibrated | 1856 | 1856 | 1735 | -6.5 % | [-10.2 % ; -3.4 %] | 60.2 % | 0 % | perte significative |
| SP favori | 1856 | 1856 | 1733 | -6.6 % | [-10.4 % ; -3.5 %] | 60.1 % | 0 % | perte significative |
| SG favori | 1856 | 1856 | 1572 | -15.3 % | [-21.0 % ; -9.6 %] | 32.5 % | 0 % | perte significative |
| SG top market_calibrated | 1856 | 1856 | 1572 | -15.3 % | [-21.0 % ; -9.6 %] | 32.5 % | 0 % | perte significative |
| SP top form | 1856 | 1856 | 1531 | -17.5 % | [-23.6 % ; -11.0 %] | 40.7 % | 1 % | perte significative |
| SP top horse_win_rate | 1856 | 1856 | 1502 | -19.1 % | [-24.5 % ; -12.7 %] | 38.3 % | 1 % | perte significative |
| SG top form | 1856 | 1856 | 1371 | -26.1 % | [-38.6 % ; -11.6 %] | 16.2 % | 7 % | perte significative |
| SP hasard | 1856 | 1856 | 1281 | -31.0 % | [-38.1 % ; -24.3 %] | 26.5 % | 1 % | perte significative |
| SG top horse_win_rate | 1856 | 1856 | 1268 | -31.7 % | [-41.1 % ; -21.3 %] | 16.1 % | 3 % | perte significative |
| SG hasard | 1856 | 1856 | 1067 | -42.5 % | [-54.5 % ; -28.9 %] | 8.0 % | 5 % | perte significative |
| Quinté favoris | 72 | 144 | 82 | -42.8 % | [-68.8 % ; -16.5 %] | 30.6 % | 24 % | perte significative |
| Quinté market_calibrated | 72 | 144 | 82 | -42.8 % | [-68.8 % ; -16.5 %] | 30.6 % | 24 % | perte significative |
| Tiercé favoris | 72 | 72 | 41 | -42.9 % | [-90.0 % ; -8.3 %] | 6.9 % | 22 % | perte significative |
| Tiercé market_calibrated | 72 | 72 | 41 | -42.9 % | [-90.0 % ; -8.3 %] | 6.9 % | 22 % | perte significative |
| SG valeur horse_win_rate | 1856 | 12198 | 6842 | -43.9 % | [-51.1 % ; -35.6 %] | 19.0 % | 2 % | perte significative |
| SG valeur form | 1856 | 11726 | 6331 | -46.0 % | [-52.6 % ; -38.3 %] | 19.5 % | 2 % | perte significative |
| Quinté horse_win_rate | 72 | 144 | 18 | -87.5 % | [-98.5 % ; -72.4 %] | 5.6 % | 46 % | perte significative |
| Tiercé form | 72 | 72 | 9 | -87.9 % | [-100.0 % ; -63.7 %] | 1.4 % | 100 % | perte significative |
| Quinté form | 72 | 144 | 12 | -91.9 % | [-98.5 % ; -82.2 %] | 5.6 % | 41 % | perte significative |
| Quinté hasard | 72 | 144 | 2 | -98.3 % | [-100.0 % ; -95.0 %] | 1.4 % | 100 % | perte significative |
| Tiercé hasard | 72 | 72 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| Tiercé horse_win_rate | 72 | 72 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place

Marché calibré, phase test. Si « prévu » dépasse « observé » sur les fortes probabilités, Harville surestime les favoris pour les places (biais connu).

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.0-0.1 | 7191 | 0.057 | 0.060 |
| 0.1-0.2 | 5971 | 0.144 | 0.174 |
| 0.2-0.3 | 3649 | 0.247 | 0.278 |
| 0.3-0.4 | 2153 | 0.346 | 0.361 |
| 0.4-0.5 | 1505 | 0.448 | 0.462 |
| 0.5-0.6 | 1021 | 0.548 | 0.473 |
| 0.6-0.8 | 1243 | 0.689 | 0.584 |
| 0.8-1.0 | 760 | 0.896 | 0.696 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
