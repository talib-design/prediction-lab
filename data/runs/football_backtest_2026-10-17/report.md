# Football — backtest walk-forward (2026-10-17)

Chaque match est prévu avec des données strictement antérieures au bloc de 14 jours qui le contient (refit par division et par bloc). Référence : la cote de clôture Pinnacle. Une prévision qui ne bat pas le marché n'a pas de valeur ajoutée, quelle que soit sa précision apparente.

## Réglages

- Divisions : E0, SP1, D1, I1, F1
- Saisons de test : 2018 à 2026 (début de saison)
- Demi-vie 365 jours, ridge 8.0, fenêtre 1095 jours

## Volume

- Matchs prévus : 14474
- Dont avec cote de clôture Pinnacle exploitable : 13335
- Dernière cote de clôture Pinnacle présente : 2026-01-14

## Scores (plus bas = mieux), moyenne et IC 95 % par bootstrap par blocs

Mêmes matchs pour toutes les lignes (ceux qui ont une cote de clôture).

| Source | Log loss | RPS |
|---|---:|---:|
| Modèle (Dixon–Coles) | 0.9893 [0.9826 ; 0.9961] | 0.2013 [0.1994 ; 0.2033] |
| Cote de clôture Pinnacle, marge retirée (proportionnelle) | 0.9683 [0.9606 ; 0.9761] | 0.1948 [0.1928 ; 0.1970] |
| Cote de clôture Pinnacle, marge retirée (puissance) | 0.9682 [0.9603 ; 0.9763] | 0.1948 [0.1927 ; 0.1970] |
| Fréquences domicile/nul/extérieur (3 ans) | 1.0746 [1.0706 ; 1.0788] | 0.2306 [0.2293 ; 0.2319] |

## Modèle contre références (différence de score, négative = modèle meilleur)

| Référence | Métrique | Différence [IC 95 %] | p | Verdict |
|---|---|---:|---:|---|
| Cote de clôture Pinnacle, marge retirée (proportionnelle) | log_loss | +0.0210 [+0.0182 ; +0.0240] | 0.000 | le modèle fait moins bien |
| Cote de clôture Pinnacle, marge retirée (proportionnelle) | rps | +0.0065 [+0.0056 ; +0.0074] | 0.000 | le modèle fait moins bien |
| Cote de clôture Pinnacle, marge retirée (puissance) | log_loss | +0.0211 [+0.0181 ; +0.0242] | 0.000 | le modèle fait moins bien |
| Cote de clôture Pinnacle, marge retirée (puissance) | rps | +0.0065 [+0.0056 ; +0.0075] | 0.000 | le modèle fait moins bien |
| Fréquences domicile/nul/extérieur (3 ans) | log_loss | -0.0853 [-0.0907 ; -0.0799] | 0.000 | le modèle fait mieux |
| Fréquences domicile/nul/extérieur (3 ans) | rps | -0.0293 [-0.0311 ; -0.0275] | 0.000 | le modèle fait mieux |

## Par division

| Division | Matchs | Log loss modèle | Log loss marché |
|---|---:|---:|---:|
| E0 | 2849 | 0.9692 | 0.9507 |
| F1 | 2547 | 1.0105 | 0.9876 |
| SP1 | 2828 | 0.9917 | 0.9724 |
| I1 | 2838 | 0.9836 | 0.9607 |
| D1 | 2273 | 0.9949 | 0.9733 |

## Plus/moins de 2,5 buts

11457 matchs. Log loss modèle 0.6797, marché 0.6685 — le modèle fait moins bien.

## Référence 2 : cote de clôture moyenne des bookmakers (AvgC)

12666 matchs, saisons 2019 à 2026 (la colonne n'existe qu'à partir de 2019/20 dans les fichiers ; marge retirée par la méthode proportionnelle). Elle subsiste quand Pinnacle a disparu des fichiers, et c'est elle que la Ligue des champions en direct utilisera (moyenne des cotes sans marge).

| Source | Log loss | RPS |
|---|---:|---:|
| Modèle (Dixon–Coles) | 0.9911 [0.9844 ; 0.9980] | 0.2020 [0.2000 ; 0.2040] |
| Cote de clôture moyenne des bookmakers, marge retirée | 0.9710 [0.9636 ; 0.9789] | 0.1958 [0.1936 ; 0.1979] |
| Fréquences domicile/nul/extérieur (3 ans) | 1.0751 [1.0710 ; 1.0792] | 0.2310 [0.2297 ; 0.2322] |

| Modèle contre moyenne | Différence [IC 95 %] | p | Verdict |
|---|---:|---:|---|
| log_loss | +0.0200 [+0.0171 ; +0.0231] | 0.000 | le modèle fait moins bien |
| rps | +0.0063 [+0.0053 ; +0.0072] | 0.000 | le modèle fait moins bien |

| Saison | Matchs | Log loss modèle | Log loss moyenne bookmakers |
|---|---:|---:|---:|
| 2019 | 1711 | 0.9894 | 0.9740 |
| 2020 | 1812 | 1.0007 | 0.9770 |
| 2021 | 1817 | 0.9937 | 0.9771 |
| 2022 | 1811 | 0.9960 | 0.9774 |
| 2023 | 1743 | 0.9781 | 0.9546 |
| 2024 | 1745 | 0.9867 | 0.9616 |
| 2025 | 1743 | 0.9957 | 0.9776 |
| 2026 | 284 | 0.9697 | 0.9543 |

Pinnacle contre moyenne, mêmes 11528 matchs (négatif = Pinnacle meilleur) : log loss -0.0002 (p = 0.242), RPS -0.0000 (p = 0.677).

## Calibration (probabilité annoncée contre fréquence observée)

Détail par tranche dans `report.json`.

## Limites

- La cote de clôture contient déjà compositions, blessures et météo connues avant le match : ce modèle n'en utilise aucune. S'il perd contre elle, c'est le résultat attendu.
- Les cotes Pinnacle viennent des fichiers football-data.co.uk. Elles s'arrêtent dans les fichiers à la date indiquée plus haut (2026-01-14) ; la cause n'est pas vérifiée. Au-delà, seule la référence 2 (moyenne des bookmakers) existe.
- Ligue des champions : aucun résultat de coupe d'Europe dans ces fichiers. Les forces d'équipes sont donc estimées par championnat, sans lien entre championnats.
