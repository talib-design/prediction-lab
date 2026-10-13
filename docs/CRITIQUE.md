# Journal de l'agent critique

Une entrée par semaine, la plus récente en tête (METHODOLOGY §14). Tous les chiffres
viennent du dossier de la semaine (`data/lab/dossier/dossier_<jour>.json`) ; ce qui vient
d'ailleurs (journaux) est signalé comme tel et donné sans chiffre. Aucun conseil de pari.

## Semaine du 2026-10-06 au 2026-10-12

Source : `dossier_2026-10-13` (généré le 2026-10-13 à 05:04 UTC). La « semaine » du dossier
(06 → 12/10) recouvre en partie celle de l'entrée précédente (04 → 10/10) : les courses du
06 au 10/10 sont comptées deux fois d'une entrée à l'autre.

### a. Carnet en direct : favori contre modèle

| Discipline | Période | Courses | Favori | Modèle |
|---|---|---|---|---|
| Plat | semaine | 79 | −41,60 € (−26,3 %) | −30,50 € (−19,3 %) |
| Plat | depuis le 2026-09-30 | 127 | −20,95 € (−8,2 %) | −7,55 € (−3,0 %) |
| Attelé | semaine | 77 | −22,20 € (−14,4 %) | −27,60 € (−17,9 %) |
| Attelé | depuis le 2026-10-05 | 82 | −21,90 € (−13,4 %) | −22,30 € (−13,6 %) |
| Monté | semaine | 16 | −5,60 € (−17,5 %) | −5,60 € (−17,5 %) |
| Monté | depuis le 2026-10-05 | 18 | −7,80 € (−21,7 %) | −7,80 € (−21,7 %) |

- **Plat** : mauvaise semaine pour les deux, un peu moins mauvaise pour le modèle (+11,10 €
  d'écart). Tout l'écart vient des 10 courses où les choix ont différé (favori −12,80 €,
  modèle −1,70 €). Modèle mieux sur 3 : La Cépière R5C6 (+4,40 € contre −2,00 €), Chantilly
  R4C4 (+4,30 € contre −2,00 €), Cavaillon R10C5 (+3,60 € contre −2,00 €). Moins bien sur 2 :
  Pont de Vivaux R4C5 (−2,00 € contre +0,40 €), Compiègne R4C7 (−2,00 € contre +2,80 €).
  Les 5 autres (Cavaillon R10C3, Nancy-Brabois R3C4 et R3C7, Lyon la Soie R6C5, Borély R1C8)
  perdent des deux côtés. Le 11/10, le modèle a quitté le favori sur 5 courses de plat sur 16.
- Depuis l'entrée précédente (dossier du 11/10), les deux jours du 11 et du 12/10 ont fait
  passer le favori de +0,55 € à −20,95 € et le modèle de +8,35 € à −7,55 €. Rien d'anormal :
  sur 24 courses, deux jours sans favori gagnant suffisent.
- **Attelé** : 5 courses différentes, écart −5,40 € pour le modèle, qui vient presque tout
  d'Enghien R1C5 (le favori [17] gagne : +8,10 € contre +0,60 €). Hyères R3C8 (−0,30 €
  contre −2,00 €) et Caen R1C5 (0,00 € contre −0,40 €) penchent pour le modèle ; La Capelle
  R2C5 et Rambouillet R8C7 perdent des deux côtés.
- **Monté** : mêmes choix sur les 18 courses.
- Lecture : 10 et 5 courses différentes, c'est du bruit. Au plat, le modèle tient son
  avance depuis le 30/09 (+13,40 € sur 127 courses), sans que cela prouve quoi que ce soit.
- **Je ne sais pas** quelle version (v1 ou v2) a joué chaque course du carnet plat depuis
  la promotion du 10/10 : le dossier ne le dit toujours pas.

### b. Où le modèle gagne ou perd sur l'historique (reconstitution walk-forward)

Avertissement : une quarantaine de segments par discipline, qui se recouvrent ; quand le
total est positif, beaucoup de sous-segments le sont mécaniquement, et quelques-uns sortiront
du lot par hasard. Ce sont des pistes, pas des preuves. Segments « trop peu » omis.

**Plat** — 23 254 courses (2020-03-01 → 2026-10-12), 2 906 où les choix diffèrent :
modèle − favori **+531,45 €** (IC 90 % +175,78 € à +889,25 €). Stable (+527,65 € il y a
deux nuits).

- Gagne (IC excluant 0) : favori à 5 ou plus **+542,30 €** (IC +262,57 € à +820,59 €,
  1 474) ; choix coté 5 à 10 **+610,00 €** (IC +304,85 € à +912,44 €, 1 851) ; 15 partants
  et plus +236,10 € (IC +29,57 € à +475,22 €, 904) ; 1 400 – 1 799 m +199,90 € (IC +10,93 € à
  +388,83 €, 870) ; handicap de catégorie divisé +208,90 € (IC +67,91 € à +360,56 €, 439) ;
  Chantilly +127,10 € (IC +3,09 € à +249,40 €) ; Saint-Cloud +111,20 € (IC +17,29 € à
  +199,22 €) ; T2 +228,00 € (IC +44,90 € à +414,01 €) ; PSF standard +205,10 € (IC +26,05 € à
  +420,43 €) ; terrain bon +151,40 € (IC +31,99 € à +278,39 €).
- Perd ou rien, **non démontré** : courses à conditions −120,75 € (IC −254,07 € à +23,51 €,
  559) ; favori entre 3 et 5 −59,50 € (IC −271,70 € à +146,28 €, 1 242) ; choix coté 3 à 5
  −64,10 € (IC −233,85 € à +108,45 €, 940) ; terrain collant −67,05 € (IC −154,01 € à
  +5,74 €, 158), lourd −8,60 € (IC −81,45 € à +65,82 €, 125), très souple −2,00 € (IC
  −124,47 € à +115,93 €, 332) ; 8 partants ou moins −8,90 € (IC −121,65 € à +105,44 €, 427).
- Lecture nouvelle cette semaine (hypothèses) : deux gradients. 1) Terrain : le modèle gagne
  sur sol bon et PSF, plus rien à partir du très souple. 2) Type de course : il gagne en
  handicap, perd (non démontré) en course à conditions. Les deux recoupent sans doute le
  constat de la semaine dernière (l'avance se fait dans les courses ouvertes, `open_race`) :
  les handicaps sont souvent ouverts. D'où `heavy_q` et `handicap_q` (f), jugés à part.

**Attelé** — 26 583 courses (2020-02-01 → 2026-10-12), 1 364 où les choix diffèrent :
modèle − favori +234,50 € (IC 90 % −13,72 € à +470,18 €) : **non démontré**.

- Gagne (IC excluant 0) : favori entre 3 et 5 +214,50 € (IC +15,06 € à +419,94 €, 908) ;
  choix coté 5 à 10 +218,10 € (IC +49,59 € à +399,91 €, 571) ; 2 700 m et plus +270,80 €
  (IC +71,02 € à +466,51 €, 834) ; 9 – 11 partants +117,90 € (IC +27,11 € à +204,10 €) ;
  12 – 14 partants +167,90 € (IC +19,35 € à +312,90 €) ; catégorie INCONNU +217,70 € (IC
  +51,20 € à +375,71 €) ; catégorie « autre » +100,50 € (IC +39,99 € à +163,20 €, 109) ;
  T1 +130,20 € et T3 +159,70 € (IC excluant 0 tous deux).
- Perd : **AUTOSTART −106,50 € (IC −210,10 € à −7,99 €, 263)**, toujours le seul segment non
  « trop peu » dont l'IC est entièrement sous 0. Non démontrés : moins de 2 200 m −43,80 € ;
  15 partants et plus −40,80 € ; T4 −66,30 € (IC −171,12 € à +37,85 €) ; quinté −31,60 €
  (IC −76,21 € à +13,21 €, 50) ; Enghien −48,20 € (IC −103,10 € à +3,60 €, 74).
- Rien de neuf par rapport à la semaine dernière ; `autostart_q` attend ses courses fraîches.

**Monté** — 2 916 courses (2023-02-01 → 2026-10-12), 86 où les choix diffèrent : +38,70 €
(IC −7,82 € à +90,21 €), non démontré. Segments non « trop peu » : favori 3 – 5 +25,90 €
(non démontré), 2 700 m et plus +53,20 € (IC +8,20 € à +95,61 €, 60), INCONNU +17,10 €
(non démontré). Rien à en tirer.

### c. Calibration du choix du modèle (annoncé → observé)

| Bande | Plat | Attelé | Monté |
|---|---|---|---|
| 10 – 20 % | 16,6 → 16,8 % (7 095) | 17,7 → 19,2 % (2 789) | 17,5 → 17,6 % (290) |
| 20 – 30 % | 24,5 → 24,6 % (9 022) | 25,0 → 24,5 % (9 331) | 24,9 → 29,1 % (1 074) |
| 30 – 40 % | 34,3 → 32,7 % (4 074) | 34,5 → 32,5 % (6 525) | 34,5 → 33,0 % (721) |
| 40 – 50 % | 44,3 → 45,8 % (1 827) | **44,6 → 38,7 %** (3 531) | 44,8 → 39,7 % (378) |
| 50 – 100 % | 58,7 → 54,2 % (1 232) | **61,8 → 50,4 %** (4 403) | 61,0 → 51,4 % (453) |

- Inchangé : juste sous 40 % ; au-dessus, trot trop confiant de 5,1 à 11,4 points, plat de
  4,5 points sur la dernière bande. Même réserve que la semaine dernière (le choix est le
  cheval le plus probable, sa probabilité est biaisée vers le haut par construction).
- Monté : forme en S (sous-confiant de 4,2 points à 20 – 30 %, trop confiant au-dessus de
  40 %), exactement ce que vise un terme en carré de log q. Mais `logq2` y est non concluant
  (−0,0058, IC 99 % −0,0196 à +0,0084) : l'effet va dans le bon sens, l'échantillon est
  trop petit pour trancher. La calibration τ n'y apporte rien (+0,0005).
- Plat : **je ne sais pas** si la reconstitution utilise déjà v2 (avec `logq2`) ; la
  dernière bande n'a pas bougé (58,7 → 54,3 % la semaine dernière, 58,7 → 54,2 % ici).

### d. Santé des données

1. **Passe de nuit ATTELE en échec cinq nuits de suite** (du 8 au 12/10) : les 5 erreurs
   consignées de la semaine sont toutes, d'après `data/logs/collect.log`, la même
   `AssertionError('2022-04-21/R4C1 was released before its own forecast')`. Non traité
   depuis la semaine dernière. Le backtest et les paris fictifs de l'attelé sont figés ; la
   reconstitution du dossier, elle, continue de grandir (26 554 → 26 583 courses).
2. **Batterie** (journal `keepawake.log`, hors dossier) : l'agent de veille a relâché deux
   fois, batterie presque vide, le 8/10 un instant et dans la nuit du 11 au 12/10 pendant
   plusieurs heures. La passe de nuit du 11 au 12 a tout de même commité. Le carnet du 12/10
   compte 8 courses de plat ; **je ne sais pas** si c'est le programme du lundi ou la veille.
3. **Carnet par jour** : le 06/10 (plat 1, attelé 3) est la veille du Mac déjà établie. Le
   07/10, 6 courses d'attelé seulement (13 à 16 les autres jours) : **je ne sais pas**
   pourquoi, le dossier ne donne pas la taille du programme.
4. **Monté : couverture toujours incohérente.** Le labo compte 892 courses en 2020, 1 017
   en 2021, 1 096 en 2022, mais le rattrapage monté commence au 2022-09-18 (1 479 jours) et la
   reconstitution au 2023-02-01.
5. **Messages périmés** : « En attente de l'historique 2020 de cette discipline » s'affiche
   encore à l'attelé et au monté alors que l'historique est marqué prêt.
6. **Six tests à écart exactement nul, IC compris** (+0,0000, IC +0,0000 à +0,0000) :
   `other_disc` et `last_win` à l'attelé, `last_win`, `young` et `dq_rate` au monté,
   `dq_rate` à l'attelé. `other_disc` touche pourtant une part non négligeable des partants de
   l'attelé (selon son texte au catalogue). Un λ très fort l'expliquerait ; une colonne mal
   jointe aussi. Afficher le λ retenu par test lèverait le doute.
7. **Intervalles qui bougent d'une nuit à l'autre** à écart égal : favori ≥ 5 au plat,
   +542,30 € les deux fois, IC +259,89 € à +815,75 € le 11/10 et +262,57 € à +820,59 € le
   13/10. Bootstrap sans graine fixe, probablement. Sans conséquence, sauf pour les segments
   dont la borne frôle 0 (Chantilly +3,09 €, 1 400 – 1 799 m +10,93 €) : ils peuvent changer
   de côté d'une nuit à l'autre.
8. Catégorie INCONNU toujours massive au trot (11 254 courses sur 26 583 à l'attelé,
   2 024 sur 2 916 au monté). Rattrapage : plat 2 473 jours, attelé 2 466 (depuis le
   2020-01-01), monté 1 479 (depuis le 2022-09-18).

### e. Labo

- **Plat** (champion Marché+ v2, 12 facteurs) : `class_drop` retenu (−0,0015, IC 99 %
  −0,0027 à −0,0001 ; +50 € sur 129 courses différentes), attend le coffre : 35/600 courses
  depuis le 10/10. Testés contre v2 depuis, tous non concluants : `fls_field` (+0,0001),
  `last_win` (−0,0003), `young` (+0,0004), `duo` (+0,0001), `jockey_change` (+0,0007),
  `musique_top3` (+0,0000), `blinkers_first` (−0,0006). Bilan : 1 retenu, 8 non concluants,
  3 proposés, 2 en test. Règle de valeur 1,05 : 100/600 courses fraîches. `open_race` :
  0/1 000 depuis le 13/10.
- **Attelé** (champion v1) : 2 retenus, 13 non concluants, 2 en test ; coffre 79/600 depuis
  le 09/10 (un essai consommé, `deferre4` refusé). **`trainer_opinion`** passe le filtre
  prévision (−0,0005, IC 99 % −0,0010 à −0,0000, gain chaque année) puis échoue au filtre
  argent : −31 € face au champion **sur 39 courses où les choix diffèrent**. Sur 39 courses,
  ce chiffre ne distingue rien du hasard ; c'est la règle §13 telle qu'écrite, mais elle
  rejette sur du bruit un critère qui prévoit mieux (voir question 4). Les deux critères du
  générateur d'idées du 11/10 (`other_disc`, `usual_q`) sont non concluants. `autostart_q` :
  0/1 000. Règle de valeur : 85/600.
- **Monté** (champion v1) : 12 non concluants, 2 proposés, 2 en test ; aucun retenu, donc le
  coffre (540/600 depuis le 01/04) n'a pas d'usage en vue. Règle de valeur : 21/600.

### f. Pistes

Critères a posteriori ajoutés au catalogue (jugés seulement sur des courses courues à partir
du 2026-10-15, une fois 1 000 courses fraîches réunies) :

1. `heavy_q` (plat) — log q × [terrain très souple, lourd ou collant] : le modèle bat le
   favori sur sol bon et PSF, plus du tout sur sol lourd ; la cote n'y a peut-être pas la
   même fiabilité.
2. `handicap_q` (plat) — log q × [catégorie contient HANDICAP] : gain en handicap, perte non
   démontrée en course à conditions. Recoupe en partie `open_race` : si les deux passent,
   ce sera probablement le même effet vu deux fois.

Questions pour Chris :

1. L'erreur de nuit attelé (`2022-04-21/R4C1`) dure depuis cinq nuits. On la traite ?
2. Monté : d'où viennent les courses 2020-2022 du labo, si le rattrapage commence le
   2022-09-18 ? (question restée ouverte)
3. Carnet plat : peut-on ajouter la version du modèle à chaque ticket ? Sans elle, impossible
   de juger v2 en direct.
4. Filtre argent : veux-tu un minimum de courses différentes (par exemple celui des
   segments du dossier, 50) en dessous duquel le filtre argent ne peut pas rejeter ? À
   pré-enregistrer pour les candidats futurs seulement, sans toucher aux verdicts rendus.
5. Le Mac a manqué de batterie deux fois cette semaine : peut-il rester branché ?

## Semaine du 2026-10-04 au 2026-10-10

Source : `dossier_2026-10-11` (généré le 2026-10-10 à 23:38 UTC). Première entrée du journal.

### a. Carnet en direct : favori contre modèle

| Discipline | Période | Courses | Favori | Modèle |
|---|---|---|---|---|
| Plat | semaine | 76 | +10,85 € (+7,1 %) | +18,65 € (+12,3 %) |
| Plat | depuis le 2026-09-30 | 103 | +0,55 € (+0,3 %) | +8,35 € (+4,0 %) |
| Attelé | semaine = depuis le 2026-10-05 | 53 | −12,70 € (−12,0 %) | −13,10 € (−12,4 %) |
| Monté | semaine = depuis le 2026-10-05 | 12 | −6,10 € (−25,4 %) | −6,10 € (−25,4 %) |

- **Plat** : les choix ont différé sur 7 courses. Le modèle fait mieux sur 4 (Le Mans R3C2,
  Deauville R4C2, La Cépière R5C6, Chantilly R4C4), moins bien sur 3 (ParisLongchamp R1C3,
  Pont de Vivaux R4C5, Compiègne R4C7). Ces 7 courses font à elles seules tout l'écart de la
  semaine : +4,60 € pour le modèle contre −3,20 € pour le favori, soit +7,80 €. Avant la
  semaine (27 courses), les deux étaient à égalité (−10,30 € chacun).
- **Attelé** : 5 courses différentes. Modèle mieux sur 3 (Enghien R1C3 +3,00 € contre
  −2,00 € ; Hyères R3C8 ; Caen R1C5), égal sur La Capelle R2C5, nettement moins bien sur
  Enghien R1C5 (le favori [17] gagne : +8,10 € contre +0,60 €). Cette seule course fait
  basculer la semaine du côté du favori (−0,40 € d'écart au total).
- **Monté** : mêmes choix sur les 12 courses.
- Lecture : 7 et 5 courses différentes, c'est du bruit. Le carnet ne dira quelque chose
  qu'avec des centaines de courses où les choix diffèrent.
- Au plat, le champion est devenu Marché+ v2 pendant la semaine (voir e). Le dossier ne dit
  pas quelle version a joué chaque course du carnet : **je ne sais pas** quelle part de la
  semaine revient à v2.

### b. Où le modèle gagne ou perd sur l'historique (reconstitution walk-forward)

Avertissement : le dossier découpe chaque discipline en une quarantaine de segments, qui se
recouvrent (les mêmes courses tombent dans « favori ≥ 5 », « 15 partants et plus », « handicap »…).
Quand le total est positif, beaucoup de sous-segments le sont aussi mécaniquement, et
quelques-uns sortiront du lot par hasard. Ce qui suit, ce sont des pistes, pas des preuves.
Les segments marqués « trop peu » (moins de 50 courses où les choix diffèrent) sont omis.

**Plat** — 23 232 courses (2020-03-01 → 2026-10-10), 2 902 où les choix diffèrent :
modèle − favori **+527,65 €** (IC 90 % +164,54 € à +891,06 €). L'intervalle exclut 0.

- Gagne : favori à 5 ou plus, **+542,30 €** (IC +259,89 € à +815,75 €, 1 473 courses
  différentes) ; choix du modèle coté 5 à 10, **+610,00 €** (IC +298,10 € à +920,71 €,
  1 850). Autres segments dont l'IC exclut 0 : 15 partants et plus +236,10 € (IC +10,83 € à
  +439,73 €) ; 1 400 – 1 799 m +196,10 € (IC +11,88 € à +399,01 €) ; handicap de catégorie
  divisé +208,90 € (IC +51,90 € à +358,43 €) ; Chantilly +127,10 € (IC +1,61 € à
  +242,62 €) ; Saint-Cloud +111,20 € (IC +15,39 € à +196,24 €) ; T2 +228,00 € (IC +38,19 € à
  +415,72 €) ; PSF standard +205,10 € (IC +2,50 € à +395,26 €) ; terrain bon +151,40 € (IC
  +31,66 € à +275,91 €). Plusieurs bornes basses frôlent 0 (Chantilly, PSF standard).
- Perd, **non démontré** (IC contient 0) : courses à conditions −120,75 € (IC −255,81 € à
  +21,23 €, 557) ; favori entre 3 et 5 −63,30 € (IC −265,21 € à +149,75 €, 1 241) ; choix
  coté 3 à 5 −67,90 € (IC −245,51 € à +100,05 €, 938) ; terrain collant −67,05 € (IC
  −152,45 € à +6,96 €, 158).
- Lecture : l'avance du plat tient presque entièrement à un geste — quitter un favori peu
  net (≥ 5) pour un cheval coté 5 à 10. Quand le modèle quitte un favori de 3 à 5 pour un
  autre cheval de 3 à 5, il ne gagne rien. C'est cohérent avec les handicaps et les grands
  champs positifs (ce sont souvent les mêmes courses). D'où le critère `open_race` (f).

**Attelé** — 26 554 courses (2020-02-01 → 2026-10-10), 1 363 où les choix diffèrent :
modèle − favori +234,50 € (IC 90 % −16,70 € à +472,83 €) : **non démontré**.

- Gagne : favori entre 3 et 5 +214,50 € (IC +24,00 € à +403,86 €, 907) ; choix coté 5 à 10
  +218,10 € (IC +45,16 € à +395,25 €, 570) ; 2 700 m et plus +270,80 € (IC +67,70 € à
  +459,84 €, 833) ; 9 – 11 partants +117,90 € (IC +28,79 € à +205,62 €) ; 12 – 14 partants
  +167,90 € (IC +13,72 € à +322,95 €) ; catégorie INCONNU +217,70 € (IC +40,44 € à
  +382,27 €) ; T1 +130,20 € ; T3 +159,70 € (IC excluant 0 tous deux).
- Perd : **AUTOSTART −106,50 € (IC −210,53 € à −5,59 €, 263)** — le seul segment fourni
  dont l'IC est entièrement sous 0, toutes disciplines confondues. Non démontrés : moins de
  2 200 m −43,80 € (IC −131,77 € à +40,11 €) ; 15 partants et plus −40,80 € (IC −189,91 € à
  +118,20 €) ; T4 −66,30 € (IC −176,84 € à +46,81 €) ; quinté −31,60 € (IC −74,93 € à
  +15,10 €, 50) ; Enghien −48,20 € (IC −106,40 € à +7,80 €, 74).
- Lecture (hypothèse) : longues distances positives, courtes distances et autostart
  négatifs — probablement les mêmes courses vues sous deux angles. D'où le critère
  `autostart_q` (f).

**Monté** — 2 910 courses (2023-02-01 → 2026-10-10), 86 où les choix diffèrent : +38,70 €
(IC −13,13 € à +88,42 €), non démontré. Seuls segments non « trop peu » : favori 3 – 5
+25,90 € (non démontré), 2 700 m et plus +53,20 € (IC +10,10 € à +96,80 €, 60 courses —
juste au-dessus du seuil), catégorie INCONNU +17,10 € (non démontré). Rien à en tirer.

### c. Calibration du choix du modèle (annoncé → observé)

| Bande | Plat | Attelé | Monté |
|---|---|---|---|
| 10 – 20 % | 16,6 → 16,9 % (7 090) | 17,7 → 19,2 % (2 785) | 17,5 → 17,6 % (290) |
| 20 – 30 % | 24,5 → 24,6 % (9 012) | 25,0 → 24,5 % (9 317) | 24,9 → 29,2 % (1 072) |
| 30 – 40 % | 34,3 → 32,7 % (4 070) | 34,5 → 32,5 % (6 521) | 34,5 → 32,9 % (720) |
| 40 – 50 % | 44,3 → 45,8 % (1 825) | **44,6 → 38,6 %** (3 529) | 44,8 → 39,5 % (377) |
| 50 – 100 % | 58,7 → 54,3 % (1 231) | **61,8 → 50,3 %** (4 398) | 60,9 → 51,4 % (451) |

- Sous 40 %, le modèle est juste partout. Au-dessus, le trot est trop confiant de 5,3 à
  11,5 points ; le plat de 4,4 points sur la dernière bande seulement.
- Deux réserves. 1) Le choix du modèle est son cheval le plus probable : sa probabilité est
  biaisée vers le haut par construction (effet « malédiction du vainqueur »), une partie
  de l'écart est donc attendue. 2) La calibration globale (p ∝ p^τ) n'apporte rien à
  l'attelé (+0,0001, IC 99 % −0,0008 à +0,0010) : l'erreur n'est pas uniforme, elle se
  concentre sur les gros favoris. C'est précisément ce que vise `logq2`, retenu à l'attelé
  avec le plus gros gain du labo (−0,0114) et qui attend le coffre.
- Bande 0 – 10 % : 3 courses par discipline, sans intérêt.

### d. Santé des données

1. **Passe de nuit ATTELE en échec trois nuits de suite** (les 3 erreurs consignées de la
   semaine). D'après `data/logs/collect.log`, les nuits du 8, 9 et 10/10 s'arrêtent sur
   `AssertionError('2022-04-21/R4C1 was released before its own forecast')`
   (`racing/backtest.py`, garde-fou contre la fuite d'information). Le backtest et les
   paris fictifs de l'attelé ne sont plus mis à jour depuis ; profil, Marché+, banc et labo
   tournent encore. **Je ne sais pas** si la reconstitution attelé du dossier est touchée.
   Priorité 1 : soit une course de 2022 mal datée par le rattrapage, soit un bug.
2. **Carnet maigre les 4 et 6/10** : plat 5 et attelé 1 le 4/10 ; plat 1 et attelé 3 le
   6/10 (contre 9 à 17 au plat du 7 au 10/10). Le 4/10, le journal de collecte montre des
   erreurs réseau (DNS, réseau injoignable) ; le 6/10, c'est la veille du Mac déjà établie
   dans STATUS (correctif `keepawake` installé le soir même). Depuis le 7/10, volumes
   normaux. Le 8/10 l'agent `keepawake` a relâché un instant (batterie presque vide) puis
   repris sur secteur.
3. **Monté : couverture incohérente.** Le labo déclare l'historique 2020-2023 prêt et
   compte 892 courses en 2020, 1 017 en 2021, mais le rattrapage monté ne remonte qu'au
   2022-09-18 et la reconstitution commence au 2023-02-01. Une des deux mesures est fausse.
4. **Messages périmés** : attelé et monté affichent « En attente de l'historique 2020 de
   cette discipline » alors que l'historique est marqué prêt.
5. **Catégorie INCONNU massive au trot** : 11 242 courses sur 26 554 à l'attelé, 2 021 sur
   2 910 au monté (801 au plat). Le champ mélange catégorie et type de départ (AUTOSTART,
   NATIONALE_AUTOSTART…) ; des autostarts se cachent peut-être dans INCONNU.
6. **Rattrapage** : plat 2 470 jours complets, attelé 2 463 (les deux depuis 2020-01-01),
   monté 1 477 (depuis 2022-09-18). D'après le journal, la passe de rattrapage du 10/10 n'a
   rien ramené et s'est arrêtée sur « réseau indisponible » côté attelé ; à surveiller si
   cela se répète.
7. Trois tests affichent un écart exactement nul, IC compris (last_win et dq_rate à
   l'attelé, musique_top3 au monté). J'ai vérifié que ces colonnes varient bien sur les
   courses récentes : c'est plus probablement un fort lissage (λ élevé) arrondi à
   4 décimales qu'une colonne vide. Afficher le λ retenu lèverait le doute.

### e. Labo

- **Plat — promotion** : `logq2` (biais favori-outsider non linéaire) a été retenu
  (log loss −0,0044, IC 99 % −0,0078 à −0,0006, gain chaque année) puis promu : le champion
  est **Marché+ v2** (12 facteurs). Le coffre a été consommé et repart du 2026-10-10
  (12/600 courses). Point faible : le filtre argent repose sur +12 € et 59 courses où les
  choix diffèrent — c'est mince, comme le §13 l'admet.
- Réenregistrés contre v2 : `class_drop` **retenu** (−0,0015, IC 99 % −0,0027 à −0,0001 ;
  +50 € sur 129 courses différentes), attend le coffre ; `blinkers_first` (−0,0006) et
  `dist_change` (+0,0001) non concluants. Bilan plat : 1 retenu, 2 non concluants,
  7 proposés, 1 en test. Règle de valeur 1,05 : 78/600 courses fraîches.
- **Attelé** : champion v1. `deferre4` retenu sur le test (−0,0030, IC 99 % −0,0060 à
  −0,0005, +57 € sur 243 courses différentes) puis **refusé au coffre** (2 121 courses du
  01/04 au 08/10/2026 : log loss −0,0005, argent −23 €). Exemple d'école de retour vers la
  moyenne : le coffre a fait son travail. `logq2` retenu (−0,0114, IC 99 % −0,0162 à
  −0,0065, +22 € sur 68 courses différentes), attend le coffre (33/600). 10 non concluants.
- **Monté** : champion v1, 6 non concluants, 8 en test, coffre 534/600 (aucun essai).

### f. Pistes

Critères a posteriori ajoutés au catalogue (jugés seulement sur des courses courues à partir
du 2026-10-13, une fois 1 000 courses fraîches réunies) :

1. `autostart_q` (attelé) — log q × [catégorie contient AUTOSTART] : laisse le modèle
   pondérer la cote différemment derrière l'autostart, seul segment où il perd nettement.
2. `open_race` (plat) — log q × (log de la plus petite cote de la course − log 3) : laisse
   le modèle se fier moins à la cote quand le favori est peu net, là où se fait toute son
   avance.

Questions pour Chris :

1. L'erreur de nuit attelé (`2022-04-21/R4C1`) : veux-tu qu'on la traite en priorité ?
   Elle bloque le backtest attelé depuis le 8/10.
2. Monté : d'où viennent les courses 2020-2022 comptées par le labo, si le rattrapage
   commence le 2022-09-18 ?
3. Peut-on extraire le type de départ (autostart / volte) séparément de la catégorie ? Ce
   serait plus propre qu'`autostart_q` (ce serait alors un nouveau critère, pas une
   révision).
4. Depuis la promotion du 10/10, le carnet plat joue-t-il v2 et v1 côte à côte ? Le dossier
   ne permet pas de le savoir ; un champ « version » par course dans le carnet aiderait.
