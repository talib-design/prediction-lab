# Simulation de paris fictifs — trot attelé, hippodromes français

**Aucun pari réel.** Des tickets imaginaires, décidés à l'horizon, réglés avec les rapports officiels du PMU.

Généré le 2026-10-03T17:02:10+00:00 · horizon **T-25 min** · code 0.2.0 · empreinte `f7abbd27e71f` · courses évaluées : 7417, dont 7311 avec rapports officiels et un marché cohérent · seuil « valeur » : p × cote ≥ 1.10.

Lecture : **ROI** = gains / mises − 1 (−20 % = on récupère 80 centimes par euro). L'intervalle à 95 % vient d'un bootstrap par blocs de courses consécutives. « Part du plus gros gain » : un chiffre élevé signale un résultat porté par un seul coup.

## Phase test (décision)

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SP top market_calibrated | 7200 | 7200 | 6723 | -6.6 % | [-8.4 % ; -4.9 %] | 59.1 % | 0 % | perte significative |
| SP favori | 7200 | 7200 | 6714 | -6.8 % | [-8.4 % ; -5.0 %] | 59.1 % | 0 % | perte significative |
| SG favori | 7200 | 7200 | 6384 | -11.3 % | [-14.3 % ; -8.3 %] | 32.9 % | 0 % | perte significative |
| SG top market_calibrated | 7200 | 7200 | 6384 | -11.3 % | [-14.3 % ; -8.3 %] | 32.9 % | 0 % | perte significative |
| SP top form | 7200 | 7200 | 5840 | -18.9 % | [-21.6 % ; -16.1 %] | 41.1 % | 0 % | perte significative |
| Quinté horse_win_rate | 309 | 618 | 497 | -19.5 % | [-81.9 % ; +100.6 %] | 11.7 % | 70 % | indéterminé |
| SP top horse_win_rate | 7200 | 7200 | 5760 | -20.0 % | [-22.8 % ; -17.4 %] | 39.3 % | 0 % | perte significative |
| SG top horse_win_rate | 7200 | 7200 | 5579 | -22.5 % | [-28.4 % ; -15.9 %] | 17.8 % | 1 % | perte significative |
| SG top form | 7200 | 7200 | 5369 | -25.4 % | [-31.6 % ; -18.6 %] | 16.6 % | 2 % | perte significative |
| SP hasard | 7200 | 7200 | 5066 | -29.6 % | [-33.2 % ; -26.1 %] | 24.5 % | 0 % | perte significative |
| Tiercé favoris | 309 | 309 | 211 | -31.7 % | [-67.5 % ; +15.3 %] | 6.5 % | 23 % | indéterminé |
| Tiercé market_calibrated | 309 | 309 | 211 | -31.7 % | [-67.5 % ; +15.3 %] | 6.5 % | 23 % | indéterminé |
| SG hasard | 7200 | 7200 | 4642 | -35.5 % | [-44.2 % ; -26.1 %] | 8.0 % | 3 % | perte significative |
| SG valeur horse_win_rate | 7199 | 43915 | 26407 | -39.9 % | [-44.5 % ; -35.3 %] | 19.5 % | 1 % | perte significative |
| SG valeur form | 7200 | 45747 | 27018 | -40.9 % | [-45.1 % ; -36.5 %] | 19.2 % | 1 % | perte significative |
| Quinté favoris | 309 | 618 | 326 | -47.3 % | [-57.6 % ; -37.5 %] | 30.4 % | 6 % | perte significative |
| Quinté market_calibrated | 309 | 618 | 326 | -47.3 % | [-57.6 % ; -37.5 %] | 30.4 % | 6 % | perte significative |
| Quinté form | 309 | 618 | 245 | -60.3 % | [-81.8 % ; -34.3 %] | 11.0 % | 24 % | perte significative |
| Quinté hasard | 309 | 618 | 199 | -67.7 % | [-99.2 % ; -11.6 %] | 1.6 % | 78 % | perte significative |
| Tiercé form | 309 | 309 | 76 | -75.4 % | [-99.1 % ; -40.1 %] | 1.3 % | 49 % | perte significative |
| Tiercé horse_win_rate | 309 | 309 | 22 | -92.9 % | [-100.0 % ; -80.2 %] | 0.6 % | 60 % | perte significative |
| Tiercé hasard | 309 | 309 | 0 | -100.0 % | [-100.0 % ; -100.0 %] | 0.0 % | 0 % | perte significative |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Phase validation

| Stratégie | Courses | Mises (€) | Gains (€) | ROI | IC 95 % | Taux de réussite | Part du plus gros gain | Verdict |
|---|---:|---:|---:|---:|---|---:|---:|---|
| SG top form | 111 | 111 | 120 | +7.7 % | [-77.1 % ; +136.3 %] | 8.1 % | 47 % | indéterminé |
| SG top horse_win_rate | 111 | 111 | 114 | +3.2 % | [-79.9 % ; +133.2 %] | 7.2 % | 49 % | indéterminé |
| SP favori | 111 | 111 | 97 | -12.5 % | [-27.2 % ; -0.6 %] | 55.0 % | 2 % | perte significative |
| SP top market_calibrated | 111 | 111 | 97 | -12.5 % | [-27.2 % ; -0.6 %] | 55.0 % | 2 % | perte significative |
| SP top form | 111 | 111 | 94 | -15.2 % | [-45.5 % ; +20.5 %] | 20.7 % | 13 % | indéterminé |
| SG favori | 111 | 111 | 91 | -18.4 % | [-42.3 % ; +2.1 %] | 27.9 % | 8 % | indéterminé |
| SG top market_calibrated | 111 | 111 | 91 | -18.4 % | [-42.3 % ; +2.1 %] | 27.9 % | 8 % | indéterminé |
| SP top horse_win_rate | 111 | 111 | 78 | -30.1 % | [-57.5 % ; +0.0 %] | 18.0 % | 16 % | indéterminé |
| SP hasard | 111 | 111 | 68 | -38.6 % | [-60.5 % ; -13.3 %] | 24.3 % | 9 % | perte significative |
| SG valeur form | 111 | 846 | 517 | -38.9 % | [-79.4 % ; +19.7 %] | 13.5 % | 39 % | indéterminé |
| SG valeur horse_win_rate | 111 | 846 | 512 | -39.5 % | [-79.9 % ; +19.3 %] | 12.6 % | 40 % | indéterminé |
| SG hasard | 111 | 111 | 57 | -48.8 % | [-94.7 % ; +30.7 %] | 3.6 % | 67 % | indéterminé |
| Quinté favoris | 8 | 16 | 8 | -52.5 % | [— ; —] | 37.5 % | 39 % | échantillon trop petit |
| Quinté market_calibrated | 8 | 16 | 8 | -52.5 % | [— ; —] | 37.5 % | 39 % | échantillon trop petit |
| Tiercé favoris | 8 | 8 | 4 | -52.5 % | [— ; —] | 12.5 % | 100 % | échantillon trop petit |
| Tiercé market_calibrated | 8 | 8 | 4 | -52.5 % | [— ; —] | 12.5 % | 100 % | échantillon trop petit |
| Quinté horse_win_rate | 8 | 16 | 5 | -71.2 % | [— ; —] | 12.5 % | 100 % | échantillon trop petit |
| Quinté form | 8 | 16 | 5 | -71.2 % | [— ; —] | 12.5 % | 100 % | échantillon trop petit |
| Quinté hasard | 8 | 16 | 3 | -83.8 % | [— ; —] | 12.5 % | 100 % | échantillon trop petit |
| Tiercé hasard | 8 | 8 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Tiercé horse_win_rate | 8 | 8 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| Tiercé form | 8 | 8 | 0 | -100.0 % | [— ; —] | 0.0 % | 0 % | échantillon trop petit |
| SG valeur market_calibrated | 0 | — | — | — | — | — | — | aucun pari |

## Modèle d'ordre d'arrivée (Harville) — calibration des probabilités de place

Marché calibré, phase test. Si « prévu » dépasse « observé » sur les fortes probabilités, Harville surestime les favoris pour les places (biais connu).

| Tranche | Partants | Prévu | Observé |
|---|---:|---:|---:|
| 0.0-0.1 | 29614 | 0.055 | 0.061 |
| 0.1-0.2 | 23429 | 0.145 | 0.177 |
| 0.2-0.3 | 14060 | 0.247 | 0.277 |
| 0.3-0.4 | 8361 | 0.346 | 0.360 |
| 0.4-0.5 | 5598 | 0.446 | 0.443 |
| 0.5-0.6 | 3873 | 0.547 | 0.489 |
| 0.6-0.8 | 4664 | 0.688 | 0.559 |
| 0.8-1.0 | 2838 | 0.896 | 0.689 |

## Limites

- Décision sur la cote à T-25 min, paiement au rapport final : l'écart entre les deux fait partie de ce qui est mesuré.
- Nos mises fictives ne déplacent pas les masses ; une vraie mise, si.
- Quinté+ : une course par jour, rapports très dispersés ; il faut des milliers de tickets avant qu'un ROI veuille dire quelque chose.
- Aucun gain passé n'annonce un gain futur ; seul un verdict « gain significatif » sur la phase de test, confirmé en conditions réelles, compterait.
