# Statut — Phase 3 : baselines, backtest, paris fictifs, tableau de bord v0

Dernière mise à jour : 2026-10-05.

## Où on en est — 2026-10-05

- **Tourne seul** sur le Mac (launchd) : collecte toutes les 5 min (carnet et banc figés à
  T-25 puis réglés), rattrapage de jour par tranches, passe de nuit à 1 h 30 (rattrapage,
  base, puis par discipline : profil, Marché+, banc, courbe historique, labo, backtests),
  publication git. Tableau de bord : http://127.0.0.1:8790 (relancé seul au redémarrage).
- **Résultat principal à ce jour (plat)** : Marché+ v1 prévoit un peu mieux que le marché
  calibré (log loss −0,0039 sur 6 290 courses de test) mais quitte le favori sur 8,8 % des
  courses seulement ; sur 9 480 courses depuis mars 2024, favori et modèle perdent tous les
  deux (gagnant −14,2 % / −13,6 %, placé −11,3 % / −10,9 %), écart non démontré. Aucune
  tranche de favori n'est rentable ; sous 1,5 il perd 42 % du temps (−9 % en gagnant).
- **En attente de données** :
  - mouvement de cote (Marché+ v2) : 71/1 000 courses de plat suivies en direct
    (attelé 44, monté 10) ; demande le Mac éveillé pendant les réunions ;
  - trot : historique remonté à octobre 2024 ; modèle, profil, banc et critères du trot
    démarrent quand il couvre le 1er semestre 2024 ;
  - historique 2020-2023 (décision du 2026-10-05) : rattrapé après 2024, plat d'abord.
    Les tests du labo et la nouvelle cible « battre le favori » attendent qu'il soit en
    place. La passe de nuit garde le Mac éveillé (caffeinate) : la nuit du 4 au 5, Mac
    en veille, elle n'avait fait que 433 requêtes en 5 h.
- **Proposé, pas lancé** : tâche planifiée hebdomadaire où Claude relit le labo et ajoute
  des critères au catalogue ; hébergement serveur (Oracle Always Free envisagé, reporté) ;
  fichier CLAUDE.md et agents critique / hypothèses.
- **Règles inchangées** : aucun pari réel, aucune mise, aucun compte PMU ; jamais
  d'information future dans les entrées ; le marché est la référence.

## Objectif « battre le favori » — épic 1 livré le 2026-10-05

- **Moteur** (`racing/champion.py`, `racing/arena.py`, METHODOLOGY §13) : champion
  (Marché+ v1), candidats pré-enregistrés contre lui, deux filtres (prévision, argent),
  coffre à partir d'avril 2026, promotion automatique en Marché+ v2 avec réajustement.
- **Catalogue** : 15 candidats, dont 6 nouveaux (biais favori-outsider non linéaire et
  selon la taille du champ, dernière course gagnée, jeune cheval, calibration, règle de
  valeur 1,05).
- **Les tests attendent l'historique 2020** de chaque discipline.
- **Épics suivants** : 2) carnet côte à côte (ancien modèle, valeur) et graphique ;
  3) tableau de score « modèle − favori » sur la page Recherche ; 4) générateur d'idées
  hebdomadaire (tâche planifiée).

## Laboratoire des critères et étude des favoris — 2026-10-03

- **Labo** (`predlab racing lab`, chaque nuit après le banc) : 9 critères au catalogue,
  pré-enregistrés au registre puis testés une seule fois contre Marché+ v1 (règle §12).
  Page Recherche : statut, gain de prévision avec IC 99 %, effet, conclusion.
- **Mouvement de cote** (proposition 1, Marché+ v2) : impossible à tester sur
  l'historique (une seule cote avant le départ) ; pré-enregistré, testé à 1 000 courses
  suivies en direct. Il faut que le Mac soit éveillé pendant les réunions.
- **Trot** (proposition 3) : déferré des 4 et fautes passées, plus les critères communs,
  enregistrés ; testés dès que l'historique du trot couvre 2024.
- **Gros favoris** : à moins de 1,5, ils perdent 42 % du temps et rendent −9 % en
  gagnant.

## Courbe historique et choix de la période — 2026-10-03

- **Performance** : courbe historique favori contre modèle sur toutes les courses depuis
  2024 (reconstitution, cotes à T-25, modèle walk-forward), avec choix de la période
  (1S, 1M, 3M, 6M, 1A, Tout) ; les cumuls repartent de zéro au début de la période.
  Recalculée chaque nuit avec le banc (`predlab racing replay` à la main), seul le dernier
  rapport est gardé.
- **Carnet et accueil** : case « Toutes les courses (recalculé) » qui ajoute les mêmes
  choix recalculés sur toutes les courses des jours suivis, en pointillés fins ; l'échelle
  passe alors en retour sur mise (%).
- Plat : le modèle quitte le favori sur 8,8 % des courses ; écart en sa faveur, non
  significatif (voir METHODOLOGY, révision du 2026-10-03).

## Carnet simplifié, courbe jour par jour, trot accéléré — 2026-10-03

- **Carnet** : favori contre modèle Marché+, en gagnant et en placé, rien d'autre. Les
  anciens témoins (hasard, valeur, tiercé, quinté) restent dans le registre mais sortent
  des bilans.
- **Courbe des gains cumulés**, jour par jour, favori (trait plein) contre modèle
  (pointillés), sélecteur gagnant + placé / gagnant / placé : sur l'accueil, sous le
  bilan, et dans le carnet.
- **Trot** : le rattrapage avance aussi le jour, par tranches de 90 s après chaque collecte
  quand aucun départ n'est à moins de 35 min. Le modèle, le profil et le banc du trot se
  lancent seuls dès que son historique remonte au premier semestre 2024.

## Banc d'essai des stratégies — 2026-09-30

- **Banc d'essai** (`predlab racing banc`, page « Banc d'essai ») : des combinaisons de 1 à
  3 critères (cote, Marché+, âge, musique, niveau, distance, oeillères, jockey, entraîneur,
  terrain, hippodrome…) jouées fictivement à 1 € sur chaque course à venir, figées à T-25,
  avec un bilan séparé du carnet. Méthode : docs/METHODOLOGY.md §11.
- **Jauge** : les 200 meilleures combinaisons de 2024 (+18 %) font −16 % sur 2025-2026 ;
  aucune ne tient. Le banc garde donc 150 combinaisons positives chaque année 2024, 2025
  et 2026 (plus le favori en référence) ; seules les courses à venir les jugeront
  (gagnante après 300 paris, éliminée après 100 si nettement négative).
- **Nuit** : le banc est recherché à nouveau après le modèle ; le collecteur fige et règle
  les tickets toutes les 5 minutes.

## Profil des vainqueurs et modèle Marché+ — 2026-09-30

- **Profil des vainqueurs** (`predlab racing profile`) : pour chaque condition de course
  et chaque profil de partant, effet sur la cote et sur le résultat, IC 95 %, correction
  pour tests multiples, stabilité 2024 → 2026. Dans le tableau de bord : une modale
  « Profil des vainqueurs », depuis l'accueil et depuis chaque course (onglet « Cette
  course » : les conditions du jour et chaque partant dans ces conditions).
- **Marché+ v1** (`predlab racing model`) : la cote corrigée par 11 facteurs fixés à
  l'avance. Plat, test 2025-2026 : prévoit un peu mieux que le marché calibré (log loss
  −0,0037, IC [−0,0056 ; −0,0018]) mais ne gagne pas aux paris fictifs (SG −12,5 %).
- **Carnet** : trois témoins de plus (SG modèle, SP modèle, SG valeur modèle), figés à T-25.
- **Nuit** : profil et modèle recalculés avant les backtests, pour chaque discipline
  ayant au moins 300 courses exploitables (le trot suivra le rattrapage).

## Historique limité à 2024 — 2026-09-30

- **Rattrapage arrêté au 1er janvier 2024** pour toutes les disciplines (décision de Chris :
  aller plus loin ne sert à rien). Ce qui est déjà stocké est gardé. Découpage révisé
  avant tout challenger : train 1er semestre 2024, validation 2e semestre 2024, test ≥ 2025
  (docs/METHODOLOGY.md §6).

## Décisions actées (2026-09-28)

- Domaine unique : **courses hippiques, hippodromes français** : plat, puis trot attelé et
  trot monté (ajoutés le 2026-09-28). Loterie et
  emploi cadre retirés du produit, archivés sous le tag
  `archive/loterie-emploi-2026-09-28`.
- Projet **personnel, non commercial** ; objectif : apprendre à coder des agents et à
  les rendre évolutifs.
- Règles d'usage du flux PMU acceptées (docs/DATA_SOURCES.md).
- Collecteur de cotes démarré dès la Phase 1.
- Critère de réussite : battre le marché *calibré* (docs/METHODOLOGY.md §5),
  ajustable après les premiers backtests.

## Résultats de l'audit (2026-09-28)

Rapport complet : `data/audit/audit_2013-01-01_2026-09-27.md` (1 jour sur 5, 1 941 requêtes).

| Constat | Conséquence |
|---|---|
| **~3 900 à 4 750 courses de plat en France par an** (estimation ; 3 200 en 2020) | La condition est levée : **le plat est confirmé.** ~49 000 courses entre 2014 et 2025 |
| Cote REFERENCE : médiane **−30 min** avant le départ, stable **depuis 2017** ; plus tôt en 2014-2016 (−194, −172, −119 min) | **Horizon T-30 min rétro-testable à partir de 2017** (~38 000 courses). 2014-2016 : autre horizon, à traiter à part |
| Cote REFERENCE après le départ dans 0 à 5 % des cas selon l'année | Filtrer chaque cote sur son horodatage, jamais sur son type |
| Dernière cote DIRECT : après le départ dans **98 à 100 %** des cas (médiane +1,5 à +4 min) | Confirmé : cote de clôture, étalon uniquement, jamais une entrée |
| Pas de cote en 2013 ; ~40 % en 2014 | Fenêtre de backtest : 2015 → aujourd'hui |
| `idCheval` absent avant 2025, **mais reconstructible** : `NOM-MÈRE-PÈRE` exact sur 1 836/1 836 cas vérifiés ; mère et père présents à 100 % toutes années | Le risque « identifiants incohérents » tombe en grande partie |
| Valeur de handicap 58-80 %, pénétromètre 66-85 %, prévision météo ≥ 91 % dès 2014 | Handicap : probablement absent hors handicaps (à vérifier) ; terrain : prévoir le cas manquant |
| 3 programmes de début 2013 rejetés (une réunion sans hippodrome) ; janvier-mi-février 2013 vides | Phase 2 : tolérance par réunion (isoler la réunion fautive, garder le reste du jour) |

**Collecte en direct : opérationnelle.** Sur la journée du 2026-09-28, 14 instantanés
pris dans l'heure précédant chaque départ ; toutes les captures réelles passent le
parser (`parse-check` : 2 012 OK, 3 échecs = les programmes 2013 ci-dessus).

**Puissance, première estimation [hypothèse] :** une fenêtre de test d'au moins
2 ans (~8 000 courses) est nécessaire pour détecter un gain de log loss de 0,01.

## Ce qui fonctionne

- Client PMU poli (1 req/s max, retries seulement sur erreurs réseau/429/5xx, échecs
  rendus comme des résultats).
- Stockage brut adressé par contenu, manifestes chaînés par jour, détection de
  falsification des blobs et des manifestes.
- Parser programme + partants, strict sur l'identité (chemin exact en cas d'échec),
  tolérant sur le reste.
- Collecteur en direct avec politique d'instantanés testée ; `--dry-run`.
- Audit : volume estimé par année, complétude des champs, horodatage réel des cotes.
- Installation `launchd` (toutes les 5 min).
- Registre d'hypothèses, découpage chronologique, outils d'incertitude repris.
- Tests, ruff, pyright au vert.

## Ce qui n'a pas pu être vérifié ici

- Vérifié depuis : le code fonctionne contre le vrai flux depuis le Mac, `launchd`
  tourne, le `User-Agent` est accepté. Les fixtures de test restent des extraits ;
  les remplacer par des captures réelles est une tâche de Phase 2.

## Ce qui manque (phases suivantes)

Premier modèle fondamental combiné au marché, historiques jockey / entraîneur
(Phase 3 bis) ; courses à venir et registre de prédictions (Phases 4-5) ; pipeline quotidien complet
(Phase 7) ; modèles avancés et agents (Phase 8).

## Passe de nuit automatique — 2026-09-29

`predlab racing nightly` (launchd, 1 h 30, `ops/install_backfill.sh`) : rattrapage,
reconstruction de la base, backtest et paris fictifs par discipline (≥ 300 courses
exploitables), puis commit + push du carnet et des rapports. Plus aucune commande à
lancer à la main ; le tableau de bord est un service (`ops/install_dashboard.sh`).

## Première simulation réelle — 2026-09-29

Plat, test ≥ 2025, 1 051 courses réglées (sur ~10 000 : rapports encore manquants) :
favori simple gagnant −14 %, favori placé −10 %, placé au hasard −25 %, modèles naïfs
−21 à −35 % ; toutes en perte significative, comme annoncé (prélèvement ~16 %).
Corrigé le même jour : le rattrapage s'arrêtait au premier échec réseau (il saute
désormais le jour et continue, arrêt après 20 échecs d'affilée) ; la stratégie
« valeur » pariait sur des marchés incohérents (règle du marché cohérent, METHODOLOGY §9).

## Historique depuis 2023 et carnet en direct — 2026-09-28

- **Rattrapage limité à 2023** pour toutes les disciplines (décision de Chris : garder
  des chevaux encore en activité). Découpage révisé avant tout challenger : train 2023,
  validation 2024, test ≥ 2025 (METHODOLOGY §6). Rythme mesuré quand le Mac est éveillé :
  ~1 mois de plat par 5 min. Estimation : plat complet après la passe de cette nuit,
  trot en ~2 nuits de plus.
- **Carnet de paris fictifs** (`racing/carnet.py`, METHODOLOGY §9 bis) : tickets figés à
  T-25 par le collecteur, réglés au rapport officiel, registre chaîné
  `data/carnet.jsonl` (à commiter régulièrement). Page « Carnet » du tableau de bord et
  bloc sur chaque fiche course ; `uv run predlab racing carnet` pour une passe et un
  bilan, `--verify` pour contrôler la chaîne.

## Tableau de bord v0 et trot — livrés le 2026-09-28

- **Trot attelé et monté** : collectés en direct (même politique d'instantanés), rattrapés
  après le plat (`--plan PLAT:2024-01-01,ATTELE:2024-01-01,MONTE:2024-01-01`, historique limité à 2024 depuis le 2026-09-30),
  champs propres au trot (ferrure, distance de handicap, réduction kilométrique — cette
  dernière est un résultat), `--discipline` sur `backtest` et `simulate`.
- **Tableau de bord** `uv run predlab dashboard` → http://127.0.0.1:8765 : programme du
  jour par réunion (filtres discipline, Quinté+), fiche course (marché brut / calibré,
  probabilité de place, évolution des cotes, historique antérieur au jour, arrivée et
  rapports), fiche cheval, performance (backtests et paris fictifs par discipline),
  données (collecte, rattrapage, base), recherche (hypothèses). API en lecture seule
  (docs/ARCHITECTURE.md). Vérifié sur les données réelles du 2026-09-28.
- Limite connue : la fiche course calcule le marché sur la **dernière** cote avant le
  départ (souvent T-2 min), pas sur l'horizon T-25 du backtest ; c'est affiché.

## Paris fictifs — livrés le 2026-09-28 (décision de Chris : simuler comme pour le Loto)

- **Rapports officiels** : parser des `rapports-definitifs` (vérifié sur une capture
  réelle complète et sur un extrait de Quinté+), table `dividends` dans la base ;
  le collecteur les prenait déjà en direct, le rattrapage les prend désormais aussi.
- **Modèle d'ordre d'arrivée** `racing/orders.py` : probabilités de place exactes sous
  Harville, vérifiées contre une énumération complète ; ordre le plus probable pour
  tiercé et quinté.
- **Simulateur** `predlab racing simulate` : Simple gagnant et placé (favori, hasard,
  top modèle, valeur), Tiercé et Quinté+ (favoris, hasard, modèles), réglés au rapport
  réel ; ROI avec IC, taux de réussite, part du plus gros gain ; calibration des
  probabilités de place. Règles figées : docs/METHODOLOGY.md §9.

Conséquence sur le rattrapage : un rapport de plus par course, soit ~100 000 requêtes
au total au lieu de ~51 000 : **environ 6 nuits** au lieu de 3-4. Les jours déjà
complets sont revisités, seuls leurs rapports sont téléchargés.

## Phase 3 — livrée le 2026-09-28

- **Moteur walk-forward** `racing/backtest.py` : les courses sont parcourues dans
  l'ordre des instants de prédiction ; les résultats ne sont publiés au modèle
  qu'une fois connus (lendemain, règle v1). Un modèle « espion » vérifie en test qu'aucun
  résultat futur ni du jour même n'est jamais visible.
- **Séparation par les types** `racing/events.py` : la carte de course (ce qu'un
  modèle voit) n'a aucun champ de résultat ; les cotes sont filtrées sur leur
  horodatage PMU au chargement.
- **Six baselines** `racing/models.py` : aléatoire, uniforme, taux de victoire du
  cheval (rétréci), forme récente (reconstruite depuis nos données, pas la musique),
  marché brut, **marché calibré** (loi de puissance réajustée en continu).
- **Rapport** `predlab racing backtest` : puissance d'abord, scores par phase,
  comparaison au marché calibré (IC bootstrap par blocs, permutation appariée,
  correction BY), calibration du marché. Écrit dans `data/runs/`.
- **Niveau 1 du critère atteint** `predlab racing synthetic-check` : sur 10 000 courses
  synthétiques, le banc trouve un vrai avantage, corrige un biais planté, refuse un
  faux avantage (3 graines sur 3).
- Découpage pré-enregistré : train ≤ 2022, validation 2023, test ≥ 2024.

Les résultats sur données réelles ne sont interprétables qu'une fois le rattrapage
terminé : avant, la fenêtre de test est trop petite et le rapport le dit.

## Phase 2 — livrée (rattrapage en cours, 3 à 4 nuits)

Livré :

- **Rattrapage historique** `predlab racing backfill` : plat français, du plus récent
  au plus ancien jusqu'à 2015, par tranches bornées (5 h, 20 000 requêtes), reprise
  automatique, un passage par nuit (`ops/install_backfill.sh`). ~51 000 requêtes au
  total, soit 3 à 4 nuits. Les performances détaillées sont en option.
- **Base normalisée** `predlab racing build` : `data/racing.duckdb` (tables `races`,
  `runners`, `runners_enriched`, `odds`, `horses`), reconstruite entièrement depuis le
  brut, reproductible, jamais commitée.
- **Identité** : `horse_id` = `idCheval` publié, sinon `NOM-MÈRE-PÈRE` reconstruit.
- **Parser tolérant par réunion** : une réunion mal formée est isolée et signalée, le
  reste de la journée est gardé.
- **Verrou sur les manifestes** : collecteur et rattrapage peuvent écrire en même temps
  sans casser la chaîne de hash.

Point de vigilance, **mesuré le 2026-09-28** : les partants rétro-chargés viennent de
captures prises après la course ; leurs champs « d'avant-course » incluent-ils la
course elle-même ?

- **Musique : non.** Si elle incluait la course, son premier caractère égalerait la
  place d'arrivée ~100 % du temps. Mesuré : 9 à 11 % selon l'année (≈ 9 400 partants,
  2013-2026), soit le niveau du hasard.
- **Compteurs de carrière et gains :** identiques entre le dernier instantané
  d'avant-course et la capture de résultat sur les 23 partants comparés
  (2 courses du jour). Probablement figés à l'avant-course ; à confirmer sur un
  échantillon plus large avant d'en faire des entrées de modèle.

La colonne `captured_after_off` reste dans la base pour ce contrôle.

Reste en Phase 2 : remplacer les fixtures de test par des captures réelles ;
confirmer les compteurs de carrière sur plus de courses ; historique jockey /
entraîneur.

## Comment lancer

```bash
uv sync
uv run predlab racing collect --dry-run
uv run predlab racing collect
uv run predlab racing today
uv run predlab racing verify
uv run predlab racing parse-check
uv run predlab racing audit --start 2013-01-01
uv run predlab racing backfill --hours 1   # une tranche à la main
uv run predlab racing build                # reconstruit data/racing.duckdb
uv run predlab racing synthetic-check      # le banc trouve-t-il ce qu'il doit trouver ?
uv run predlab racing backtest             # baselines sur données réelles, T-25 min
uv run predlab racing simulate             # paris fictifs réglés aux rapports officiels
uv run predlab racing backtest --discipline ATTELE   # idem trot attelé (MONTE : trot monté)
bash ops/install_dashboard.sh               # tableau de bord en service : http://127.0.0.1:8790
uv run predlab racing carnet               # bilan du carnet en direct (--verify : chaîne)
uv run predlab hypothesis list
```

Vérifications : `uv run ruff check . && uv run pyright && uv run pytest`.
