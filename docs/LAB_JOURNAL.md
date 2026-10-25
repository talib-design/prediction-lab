# Journal du labo

Tenu chaque dimanche par le générateur d'idées (METHODOLOGY §13). Entrée la plus
récente en tête. Les critères ajoutés ici sont écrits sans aucun regard sur leur lien
avec les résultats ; ils sont pré-enregistrés puis testés une seule fois par la passe
de nuit.

## 2026-10-25

### Critères ajoutés (2)

- **`accessit` — Abonné aux places** (plat, attelé, monté ; origine automatisée).
  log((victoires + 3) / (victoires attendues + 3)) − log((places dans les 3 + 3) /
  (places attendues + 3)) sur le passé du cheval strictement antérieur au jour (`h_wins`,
  `h_exp`, `h_top3`, `h_exp3`), 0 sans passé. Négatif pour le cheval souvent placé mais
  rarement vainqueur, positif pour celui « qui sait gagner ». Pourquoi : le public lit la
  musique en places ; la cote gagnant sépare peut-être mal ces deux profils. Aucun critère
  ni facteur ne sépare victoire et place pour le cheval : `f_form` compte des places
  gagnées sur la cote, `musique_top3` les places seules, `last_win` la dernière course.
  Sens non présumé. Présence (colonne seule, depuis 2025) : non nul pour 90 % des partants
  du plat, 93 % de l'attelé, 81 % du monté ; écart-type 0,2.
- **`weight_dist` — Le poids pèse plus sur la distance** (plat ; origine automatisée).
  Écart du poids porté au poids moyen de la course (kg, `weight_diff`) × (distance − 2 000)
  / 1 000, 0 si poids inconnu. Pourquoi : croyance turfiste classique (un kilo coûte plus
  sur la distance qu'au sprint) ; `f_weight` donne au poids le même effet partout. La cote
  n'entre pas dans la mesure. Sens non présumé. Présence : non nul pour 82 % des partants
  du plat depuis 2025 (1 % à 99 % : −3,0 à +3,0). Attelé exclu (pas de poids).

Écartés avant écriture : femme jockey (au plat, où s'applique la décharge, aucun nom de
jockey ne porte « Mme » ou « Mlle » : non détectable ; présent au trot, 3 % à l'attelé,
22 % au monté, sans hypothèse nette), préférence du cheval pour la distance (aucun
historique par distance), forme récente de l'entraîneur (les cumuls n'ont pas de fenêtre
récente), nombre de partants de l'entraîneur sur la réunion (ne se calcule pas pour une
course à venir vue seule), cheval peu exposé (voisin de `young` et `f_new`).

Vérifications : ruff, format, pyright sur `racing/lab.py`, tests arena / lab / facteurs
(23 tests, le critère se calcule aussi pour une course à venir) : tout passe.

### Labo de la semaine (2026-10-18 → 2026-10-25, registre `data/hypotheses.jsonl`)

- **Promotions** : aucune. Champions inchangés : plat Marché+ v2 (v1 + `logq2`), attelé
  et monté Marché+ v1.
- **Essais au coffre** : aucun. Toujours en attente de courses jamais utilisées :
  `class_drop` plat contre v2 (186/600), `logq2` attelé contre v1 (185/600).
- **Retenus** : aucun nouveau. **Rejetés** : aucun.
- **Non concluants (testés dans la passe du 2026-10-18 au soir)** :
  - `second_string` : plat −0,0003 (IC 99 % −0,0008 à +0,0002), attelé −0,0000
    (−0,0001 à +0,0001), monté −0,0000 (−0,0008 à +0,0008) ;
  - `self_driven` : attelé −0,0005 (−0,0015 à +0,0006), monté +0,0001 (−0,0003 à
    +0,0006).
- **En cours** (passe du 2026-10-25) : règle `value105` (plat 255/600, attelé 215/600,
  monté 49/600 courses fraîches) ; mouvement de cote `drift` (plat 342, attelé 296,
  monté 63 courses suivies en direct sur 1 000) ; critères a posteriori de l'agent
  critique en attente de leurs courses fraîches.

### Historique 2020 (`data/raw/pmu/backfill_done_v2*.json`)

- Plat : 2 485 jours, le plus ancien 2020-01-01, le plus récent 2026-10-22.
- Attelé : 2 478 jours, le plus ancien 2020-01-01.
- Monté : 1 492 jours, le plus ancien **toujours 2022-09-18** (+7 jours en une semaine,
  tous récents). Le journal de nuit montre encore « MONTE — backfill : 6 requêtes,
  0 courses, … jusqu'au 2024-01-23, échecs : 6 » et, à l'attelé, des passages arrêtés sur
  « réseau indisponible (20 échecs d'affilée) » au 2021-05-12. Je ne sais pas pourquoi le
  monté ne descend pas sous 2022-09-18.

## 2026-10-18

### Critères ajoutés (2)

- **`self_driven` — L'entraîneur drive ou monte lui-même** (attelé, monté ; origine
  automatisée). 1 si le jockey ou driver et l'entraîneur sont la même personne (même
  initiale et même nom, après retrait de « Sté. Ent. », « Mme », « Mlle », « (S) »), 0
  sinon. Pourquoi : au trot, mener soi-même son cheval ou le confier à un catch-driver
  connu est un choix de l'entourage ; le public suit les grands noms de drivers, peut-être
  plus que le choix ne le mérite. Aucun critère ni facteur ne lit ce fait : `duo` mesure
  la réussite passée d'un couple jockey-entraîneur, `f_jockey` celle du driver seul. Sens
  non présumé. Appariement des noms contrôlé à l'oeil (« A. ANGOT » = « Alexandre
  ANGOT » ; « J.ET. ABRIVARD » ≠ « M. ABRIVARD »). Présence (colonne seule, depuis
  2025) : 30 % des partants de l'attelé, 5 % du monté ; plat exclu (0,7 %).
- **`second_string` — Second couteau de l'écurie** (plat, attelé, monté ; origine
  automatisée). 1 si l'entraîneur a au moins deux partants dans la course et que ce cheval
  n'a pas la plus petite cote à 25 min parmi eux, 0 sinon. Pourquoi : le public se porte
  sur le premier choix supposé de l'écurie et néglige les autres ; aucun critère du
  catalogue ne regarde les autres partants du même entraîneur. Sens non présumé.
  Calculable pour une course à venir (tout se lit dans la course elle-même). Présence :
  10 % des partants du plat, 8 % de l'attelé, 5 % du monté depuis 2025.

Écartés avant écriture : réussite du cheval sur l'hippodrome du jour (aucune colonne
d'historique par hippodrome ; un calcul dans le tableau ne se referait pas pour une course
à venir), tendance de la musique (voisine de `musique_top3`, `last_win`, `f_form`),
sexe en course mixte (déjà décrit par le banc via `sex_cat`, sans hypothèse nette),
toute pondération de la cote selon la classe, le terrain, la distance ou le type de
départ (domaine des critères a posteriori de l'agent critique).

Vérifications : ruff, format, pyright sur `racing/lab.py`, tests arena / lab / facteurs
(23 tests, le critère se calcule aussi pour une course à venir) : tout passe.

### Labo de la semaine (2026-10-11 → 2026-10-18, registre `data/hypotheses.jsonl`)

- **Promotions** : aucune. Champions inchangés : plat Marché+ v2 (v1 + `logq2`),
  attelé et monté Marché+ v1.
- **Essais au coffre** : aucun (coffre consommé jusqu'au 2026-10-09 au plat, au
  2026-10-08 à l'attelé, jamais au monté).
- **Retenus** : aucun nouveau. Toujours en attente du coffre (passe du 2026-10-17) :
  `class_drop` plat contre v2 (96/600 courses jamais utilisées), `logq2` attelé contre
  v1 (116/600).
- **Rejetés** : aucun.
- **Non concluants (testés cette semaine)** :
  - plat contre v2 : `jockey_change`, `duo`, `musique_top3`, `fls_field`, `last_win`,
    `young`, `calibration`, `other_disc`, `usual_q` (−0,0008, IC 99 % −0,0025 à
    +0,0006) ;
  - attelé : `trainer_opinion` (prévoit mieux, −0,0005, IC 99 % −0,0010 à −0,0000, gain
    chaque année, mais −31 € face au choix du champion sur 5 116 courses : filtre argent),
    `other_disc`, `usual_q` ;
  - monté : `dq_rate`, `logq2` (−0,0058, IC 99 % −0,0196 à +0,0084), `fls_field`,
    `last_win`, `young`, `calibration`, `trainer_opinion`, `other_disc`, `usual_q`.
- **En cours** : règle `value105` (plat 165/600, attelé 146/600, monté 35/600 courses
  fraîches au 2026-10-17) ; mouvement de cote `drift` (plat 254, attelé 233, monté
  50 courses suivies en direct sur 1 000) ; critères a posteriori de l'agent critique en
  attente de leurs courses fraîches.

### Historique 2020 (`data/raw/pmu/backfill_done_v2*.json`)

- Plat : 2 478 jours, le plus ancien 2020-01-01, le plus récent 2026-10-15.
- Attelé : 2 471 jours, le plus ancien 2020-01-01.
- Monté : 1 485 jours, le plus ancien **toujours 2022-09-18** : aucun jour plus ancien
  ajouté depuis le 2026-10-11 (+7 jours, tous récents). Le journal de nuit
  (`data/logs/backfill.out.log`) montre chaque nuit « MONTE — backfill: 6 requêtes,
  0 courses, 0 jours complétés, jusqu'au 2024-01-23, arrêt : done, échecs : 6 ». Cause
  non examinée : je ne sais pas pourquoi le rattrapage du monté ne descend pas sous
  2022-09-18. À l'attelé, les dernières nuits, un passage sur deux s'arrête aussi sur
  « réseau indisponible (20 échecs d'affilée) » au 2021-05-12, sans effet visible sur le
  total.

## 2026-10-11

### Critères ajoutés (2)

- **`other_disc` — Vient d'une autre discipline** (plat, attelé, monté ; origine
  automatisée). Part des 5 dernières courses de la musique courues dans une autre
  discipline que celle du jour (obstacle h/s/c/f pour un cheval de plat, monté pour un
  trotteur d'attelé, attelé pour un trotteur de monté). Pourquoi : le public lit les
  chiffres de la musique sans regarder la lettre de discipline ; un 3e en haies ou en
  monté ne vaut pas un 3e dans la discipline du jour. Aucun critère du catalogue n'utilise
  la lettre de discipline (`musique_top3`, `dq_rate`, `last_win` ne lisent que les
  chiffres). Sens non présumé. Présence vérifiée (colonne seule) : non nulle pour
  environ 2 % des partants du plat, 9 % de l'attelé, 50 % du monté depuis 2025.
- **`usual_q` — Cote inhabituelle pour ce cheval** (plat, attelé, monté ; origine
  automatisée). log de la probabilité de la cote à 25 min moins log de la probabilité
  moyenne des courses passées du cheval (`h_exp / h_n`, strictement avant le jour),
  bornée à ±3, 0 sans passé. Pourquoi : idée de sur-réaction du marché à l'information
  récente ; ni la forme (`f_form`, places gagnées sur la cote) ni la catégorie
  (`class_drop`) ne mesurent l'écart entre la cote du jour et la réputation du cheval
  sur le marché. Limite connue : non corrigée de la taille des champs passés. Présence :
  non nulle pour 71 à 84 % des partants selon la discipline.

Écartés avant écriture : popularité du jockey (redondante avec `f_jockey`, qui mesure
déjà victoires / victoires attendues), retrait des oeillères et âge avancé (voisins de
`blinkers_first` et `young`), tout ce qui touche à l'autostart ou à la netteté du
favori (domaine des critères a posteriori de l'agent critique).

Vérifications : ruff, format, pyright sur `racing/lab.py`, tests arena / lab / facteurs
(le critère se calcule aussi pour une course à venir) : tout passe.

### Labo de la semaine (2026-10-04 → 2026-10-11, registre `data/hypotheses.jsonl`)

- **Promotion — plat : Marché+ v2** le 2026-10-10 à 04 h 34 UTC = v1 + `logq2` (biais
  favori-outsider non linéaire). Test : log loss −0,0044 (IC 99 % −0,0078 à −0,0006),
  gain chaque année, +12 € face au champion sur 4 362 courses. Coffre (2026-04-01 →
  2026-10-09, 2 021 courses) : −0,0091 (IC 99 % −0,0146 à −0,0038), +6,7 €. Les autres
  critères du plat ont été réenregistrés contre v2.
- **Retenus, en attente du coffre** (coffre consommé jusqu'au 2026-10-09 au plat et au
  2026-10-08 à l'attelé ; il faut au moins 600 courses nouvelles) :
  - `class_drop` plat contre v2 : −0,0015 (IC 99 % −0,0027 à −0,0001), +50 € sur
    4 362 courses ;
  - `logq2` attelé contre v1 : −0,0114 (IC 99 % −0,0162 à −0,0065), +22 € sur
    5 116 courses.
- **Essai au coffre manqué** : `deferre4` attelé (retenu au test : −0,0030, +57 €) ;
  au coffre, −0,0005 (IC 99 % −0,0055 à +0,0044) et −23,2 € sur 2 121 courses : non promu.
- **Non concluants** : plat contre v1 — `class_drop` (prévoit mieux mais −6 € : filtre
  argent), `dist_change`, `blinkers_first`, `jockey_change`, `duo`, `musique_top3`,
  `fls_field`, `last_win` ; plat contre v2 — `dist_change`, `blinkers_first` ; attelé —
  `class_drop`, `dist_change`, `jockey_change`, `duo`, `musique_top3`, `dq_rate`,
  `fls_field`, `last_win`, `young`, `calibration` ; monté — `class_drop`,
  `dist_change`, `jockey_change`, `duo`, `musique_top3`, `deferre4`.
- **Rejetés cette semaine** : aucun.
- **En cours** : plat v2 — 7 critères pré-enregistrés à tester (`jockey_change`, `duo`,
  `musique_top3`, `fls_field`, `last_win`, `young`, `calibration`), règle `value105` ;
  attelé — `trainer_opinion`, `value105` ; monté — `dq_rate`, `logq2`, `fls_field`,
  `last_win`, `young`, `calibration`, `trainer_opinion`, `value105` ; mouvement de cote
  (`drift`) dans les trois disciplines, en attente de 1 000 courses suivies en direct.

### Historique 2020 (`data/raw/pmu/backfill_done_v2*.json`)

- Plat : 2 471 jours, le plus ancien 2020-01-01 (2020-2023 complet : 1 461 jours).
- Attelé : 2 464 jours, le plus ancien 2020-01-01 (1 455 jours avant 2024).
- Monté : 1 478 jours, le plus ancien 2022-09-18 : rattrapage en cours.
