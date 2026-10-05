# Sources de données

Dernière vérification : 2026-09-28. Tout ce qui est marqué **[non vérifié]** doit être
mesuré (voir `predlab racing audit`) avant qu'on s'appuie dessus.

## PMU — flux JSON « turfinfo » (source principale)

| | |
|---|---|
| Fournisseur | PMU (Pari Mutuel Urbain) |
| Base | `https://online.turfinfo.api.pmu.fr/rest/client/{n}/programme/{JJMMAAAA}` |
| Authentification / coût | aucune / gratuit |
| Documentation, conditions, limites de débit | **aucune publiée** |
| Profondeur | des programmes avec résultats répondent pour 2013-05-05 et 2015-06-07 ; date la plus ancienne [non vérifié] |
| Officiel | c'est le flux du PMU lui-même, mais non documenté |

### Endpoints utilisés (vérifiés le 2026-09-28)

| Endpoint | Chemin | Contenu |
|---|---|---|
| Programme | `/1/programme/{date}` | réunions (hippodrome, pays, météo prévue), courses (heure de départ, distance, corde, discipline, catégorie, conditions, pénétromètre, statut, arrivée, incidents) |
| Partants | `/1/programme/{date}/R{r}/C{c}/participants` | chevaux, jockey, entraîneur, propriétaire, pedigree, corde, poids, valeur, musique, gains, arrivée, **deux cotes horodatées** |
| Performances | `/61/programme/{date}/R{r}/C{c}/performances-detaillees/pretty` | courses passées de chaque partant |
| Rapports | `/1/programme/{date}/R{r}/C{c}/rapports-definitifs` | rapports officiels par type de pari |

### Constats qui gouvernent l'usage

**Les instants sont en millisecondes epoch UTC.** `heureDepart`, `dateRapport`,
`meteo.datePrevision`. Seul `penetrometre.heureMesure` est une heure locale sans fuseau
(`"2026-09-28T09:00"`), gardée telle quelle.

**Deux cotes par partant, et la seconde est postérieure au départ.** Sur les trois
courses vérifiées à la main :

| Course | Départ (UTC) | Cote REFERENCE | Dernière cote DIRECT |
|---|---|---|---|
| 2026-09-27 R1C1 | 11:26:00 | 10:53:05 (−33 min) | 11:27:41 (**+1,7 min**) |
| 2026-09-28 R2C1 | 08:50:00 | 08:20:05 (−30 min) | 08:41:38 (−8 min, capture en direct) |
| 2015-06-07 R1C1 | [inconnu] | 10:30:41 | 12:01:44 |

**Mesuré par l'audit du 2026-09-28 (plat, 2013-2026, 1 jour sur 5) :** REFERENCE à
−30 min (médiane) depuis 2017, plus tôt en 2014-2016 ; DIRECT après le départ dans
98-100 % des cas. Détail dans `docs/STATUS.md`.

Conséquences : (1) la dernière cote directe archivée est une **cote de clôture**,
interdite comme entrée de modèle ; (2) la cote REFERENCE semble prise ~30 min avant le
départ, ce qui rendrait un horizon T-30 min rétro-testable — trois courses ne
suffisent pas, l'audit mesure la distribution par année ; (3) tout instantané plus
fin (T-1h, T-10 min) n'existe que si le collecteur le prend en direct.

**Unités déduites, pas documentées.** `handicapPoids` = dixièmes de kg (580 → 58,0) ;
gains en centimes (315100 → 3 151 €). Valeurs brutes conservées à côté des dérivées.

**Identité du cheval.** `idCheval` vaut `NOM-MÈRE-PÈRE` en 2026
(`"EAST AND WEST-LIVINGINAFANTASY-TERRITORIES"`) : une clé naturelle utile. Absent
avant 2025, mais **reconstructible exactement** à partir de `nom`, `nomMere`, `nomPere`
(1 836/1 836 cas vérifiés ; mère et père présents à 100 % de 2013 à 2026).

**Écarts vus.** Un partant de 2015 n'avait pas de cote directe. Les disqualifications
(`DISQUALIFIE_POUR_ALLURE_IRREGULIERE`, trot) et non-partants apparaissent dans
`incidents` et dans le `statut` du partant.

### Statut juridique et règles d'usage

Le PMU détient des droits de producteur de base de données et les a déjà fait valoir :
TGI de Paris, 20 juin 2007, Eturf condamnée à 120 000 € pour extraction et
republication systématiques
([Legalis](https://www.legalis.net/actualite/eturf-condamnee-pour-extraction-illicite-de-la-base-de-donnees-du-pmu/)).

Règles appliquées par ce projet, **projet personnel et non commercial** :

1. faible volume : une requête à la fois, ≥ 1 s d'écart, jamais deux fois une journée
   close (cache dans le stockage brut) ;
2. `User-Agent` explicite (`prediction-lab/… personal non-commercial research`) ;
3. données brutes **jamais commitées** (le dépôt GitHub est public) ni redistribuées ;
4. si le projet devenait un produit : licence d'abord.

Ce n'est pas un avis juridique.

### Accès réseau

Depuis les environnements Cowork (bac à sable cloud et shell de la session sur le Mac),
le domaine est refusé par la politique réseau (`403 from proxy`). Le collecteur tourne
donc depuis macOS via `launchd` (`ops/install_collector.sh`).

### Textes et avis dans le flux des partants (vérifiés le 2026-10-05)

| Champ | Contenu | Disponibilité | Usage |
|---|---|---|---|
| `commentaireApresCourse.texte` (source `DATAHIPPIQUE`) | commentaire de course par partant, en français | ~50 % des partants le lendemain, 100 % à 4-7 jours, **0 % au-delà d'un mois** (retiré du flux) | relu chaque nuit 4 à 30 jours après le départ (`predlab racing comments`), extrait dans `data/normalized/comments.parquet`, jamais commité |
| `avisEntraineur` | `POSITIF` / `NEUTRE` / `NEGATIF` | trot seulement : 82 à 100 % des partants depuis 2024 (positif ou négatif 11 à 18 %), absent en plat ; présent avant la course, identique avant et après le départ sur 190 courses | colonne `trainer_opinion` de la base, critère « Avis de l'entraîneur » ; présence en 2020-2023 [non vérifié] |

### Courses étrangères — sonde du 2026-10-05 (`predlab racing probe-foreign`)

Le programme PMU liste aussi les courses étrangères sur lesquelles le PMU prend des paris
(≈ 5 500 à 6 200 par an depuis 2024 ; plus de courses de plat qu'en France). Sonde sur
100 courses terminées depuis 2024, 42 couples pays × discipline, 300 requêtes ; rapport
agrégé : `data/lab/probe_foreign.json`.

| Mesure | Plat (60) | Attelé (30) | Monté (10) |
|---|---|---|---|
| Partants lus, parseur sans erreur | 100 % | 100 % | 100 % |
| Musique, âge, sexe, origines, jockey/driver, entraîneur, œillères | ≈ 100 % | 100 % | 100 % |
| Poids (en dixièmes de kg, comme en France), corde | 100 % | — | — |
| Valeur de handicap | 45 % (GBR, IRL, HKG, USA, AUS, ZAF, DEU…) | — | — |
| Recul (distance) / déferré | — | 100 % / 31 % | 100 % / 31 % |
| Arrivée (ordreArrivee) | 98 % | 83 % | 82 % |
| Courses passées détaillées (au moins une) | 82 % des partants, médiane 5 | 30 %, médiane 0 | 51 % |
| Cote de référence PMU | 42 % des partants | 68 % | 45 % |
| Rapports simple gagnant / placé | 40 % des courses | 63 % | 40 % |

Constats :

- **Pas de cote PMU avant le départ** sur les grands pays de plat (Royaume-Uni, Irlande,
  Hong Kong, Australie, États-Unis, Chili, Argentine…) ni sur le trot suédois ; leurs
  rapports, quand ils existent, sont de type `*_INTERNATIONAL` [non vérifié : masse
  commune avec l'organisateur local, probablement]. Ces courses servent au modèle de
  fond (sans cote), pas à mesurer « battre le favori ».
- Quand elle existe, la cote de référence est prise **30 min avant le départ**, comme en
  France.
- **Compteurs de carrière** (`nombreCourses`, gains) à 0 dans plusieurs pays (trot
  étranger, Japon, Corée, Pologne) alors que la musique montre des courses : non fiables
  là-bas ; la musique l'est.
- Code pays `AAA` = Hong Kong (Happy Valley, Sha Tin) avant l'apparition de `HKG`.
- Les captures de la sonde entrent dans la base à la reconstruction ; le modèle, le
  carnet, le banc et le labo ne lisent que `country_code = 'FRA'`.

## Autres sources

| Source | Statut | Usage prévu |
|---|---|---|
| France Galop (site) | CGU : extraction automatisée et réutilisation substantielle interdites sans autorisation écrite | **aucun scraping** ; demande d'autorisation à `webmaster@france-galop.com` si besoin |
| IFCE — Fichier des équidés (data.gouv.fr) | Licence Ouverte ; ~4 M d'équidés depuis 1976 ; nom, race, sexe, robe, naissance, pays | résolution d'identité (Phase 2) |
| Météo-France — API Données climatologiques | Licence Ouverte 2.0 ; compte requis ; 100 req/min | météo observée, analyses a posteriori |
| Open-Meteo — Historical Forecast API | CC BY 4.0 ; gratuit non commercial ; 10 000 appels/jour | prévisions archivées pour les horizons précoces |
| turf.bzh, Aspiturf, Kaggle | tiers, dérivés du PMU ; conditions [non vérifié] | non utilisés |
