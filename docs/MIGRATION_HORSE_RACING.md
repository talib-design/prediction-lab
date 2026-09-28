# Analyse de migration — Prediction Lab → courses hippiques

Rédigée le 2026-09-28. Statut : **validée le 2026-09-28**, Phase 1 en cours
(voir `docs/STATUS.md`).

> **Décisions de Chris (2026-09-28).** Ne garder que les courses : loterie *et* emploi
> cadre archivés (tag `archive/loterie-emploi-2026-09-28`) puis retirés. Projet
> purement personnel, pour apprendre à coder des agents évolutifs. Règles d'usage PMU
> acceptées. Collecteur de cotes dès la Phase 1. Critère de réussite « marché
> calibré », ajustable ensuite.
>
> **Correction après vérification (même jour).** Plus bas, la cote REFERENCE est
> décrite comme « du matin ». C'est faux sur les courses vérifiées ensuite : elle est
> prise ~30 min avant le départ, et la dernière cote DIRECT est horodatée *après* le
> départ. Voir `docs/DATA_SOURCES.md`.

Question centrale désormais :

> Peut-on estimer l'issue des courses hippiques mieux que des baselines statistiques
> simples et que le marché lui-même, en n'utilisant que l'information réellement
> disponible avant la course ?

Conventions de ce document : **[vérifié]** = contrôlé aujourd'hui sur la source ou dans
le code ; **[non vérifié]** = impossible à contrôler, dit comme tel ; **[hypothèse]** =
mon jugement ou une estimation, pas un fait.

---

## 0. Trois constats de l'inspection qui modifient le plan

1. **Le dépôt contient trois volets, pas un.** À côté du moteur loterie, il y a un
   prévisionniste complet de séries temporelles sur l'*emploi cadre* (`src/predlab/ts/`,
   sources France Travail, DARES, INSEE) et une tâche planifiée GitHub Actions
   (`collect-offers.yml`) qui commite chaque jour à 04:10 UTC dans le dépôt public. Ce
   n'est ni de la loterie ni des courses. **Son sort relève de ta décision** (voir §D.3).
   Quel que soit ton choix, la migration ne doit pas casser `predlab collect …`, sinon
   cette tâche échoue dès le lendemain matin.
2. **L'expérience « Loto 1 mois » n'est pas versionnée et elle est à l'arrêt.**
   `experiments/loto-1-mois/` n'est pas commité ; ses deux tâches planifiées sont
   désactivées (dernière modification ce matin, 05:40 UTC) après un seul tirage noté.
   Elle doit être archivée comme expérience incomplète, avec une ligne qui le dit, et
   non abandonnée en silence.
3. **Aucun des deux shells Cowork n'atteint le PMU.** Le bac à sable cloud comme le
   shell de cette session sur ton Mac ont reçu `403 from proxy` sur
   `online.turfinfo.api.pmu.fr` (politique réseau). WebFetch, lui, a pu le lire : c'est
   ainsi que la source a été vérifiée. Conséquence : les collecteurs devront tourner
   depuis ton propre terminal macOS / `launchd`, **pas** depuis des tâches planifiées
   Cowork — sauf si tu ajoutes le domaine à la liste blanche réseau de l'organisation
   (Paramètres admin → Capabilities).

Intendance : un `git status` que j'ai lancé a laissé un `.git/index.lock` vide. Je l'ai
renommé en `.git/index.lock.stale-from-claude-2026-09-28` (pas de droit de suppression
dans cette session) ; git est débloqué et tu peux supprimer ce fichier.

---

## A. Inventaire du projet actuel [vérifié]

| Élément | État |
|---|---|
| Historique | 26 commits, du 2026-09-19 au 2026-09-21. Remote `github.com/talib-design/prediction-lab` (décrit comme public dans le fichier du workflow). Non commité : modification de `.gitignore`, `experiments/`. |
| Stack | Python 3.12 (épinglé), uv, polars, numpy, scipy, pydantic, typer. Dev : pytest, hypothesis, ruff, pyright. Ni pandas, ni scikit-learn, ni base de données. |
| Taille | ~7 900 lignes dans `src/predlab`, ~3 400 lignes de tests, 247 fonctions de test. |
| Front-end | Aucun. La seule interface est un rapport HTML statique généré (`ts/html.py`). |
| Serveur d'API | Aucun. Tout passe par la CLI (`predlab …`, typer, 988 lignes). |
| Couche LLM | Aucune. Deux variables en commentaire dans `.env.example`. |
| Registre de modèles / champion–challenger | Aucun. Nom, version et configuration du modèle sont enregistrés à chaque run ; rien ne promeut ni ne fige. |
| Registres (ledgers) | `predictions.jsonl` (1), `hypotheses.jsonl` (9), `offers.jsonl` (14), `forecasts.jsonl` (5) — tous chaînés par hash. |

Carte des modules :

| Module | Rôle | Volet |
|---|---|---|
| `core/hashing.py` | SHA-256, JSON canonique, registre append-only chaîné par hash avec `verify()` | générique |
| `core/dotenv.py`, `core/paths.py` | chargement des identifiants, redirection des chemins pour les tests | générique |
| `core/historyview.py` | historique tronqué causalement (lignes futures absentes, tableaux en lecture seule) | forme loterie, idée générique |
| `core/gamespec.py` | boules, ères et jours de tirage des loteries | loterie |
| `data/store.py` | stockage Parquet append-only, détecte les modifications rétroactives de la source, manifeste d'archive | forme loterie, idée générique |
| `data/sources/fdj_loto.py` | parser FDJ strict | loterie |
| `data/sources/francetravail.py`, `dares.py`, `insee.py` | sources marché de l'emploi | emploi |
| `models/base.py` | protocole `Predictor`, `Forecast`, `normalise_to_k` (écrêtage + redistribution pour sommer à k) | forme loterie, cœur générique |
| `models/baselines.py`, `models/selection.py` | uniforme / fréquence / fréquence rétrécie / écart ; politiques de grille | loterie |
| `backtest/splits.py` | `TimeSplit` train/validation/test par date | générique |
| `backtest/engine.py` | moteur walk-forward, empreinte du jeu de données, trace de run reproductible | forme loterie, idée générique |
| `eval/metrics.py` | log loss, Brier, erreur de calibration sur les marginales d'inclusion | partiellement générique |
| `eval/uncertainty.py` | bootstrap par blocs mobiles, test de permutation apparié par blocs, FDR BH / BY | générique |
| `eval/power.py` | seuil de détection, taille d'échantillon requise, test d'uniformité | loterie |
| `eval/report.py` | rapport avec la puissance en premier, descriptif et prédictif séparés | contenu loterie, structure générique |
| `benchmarks/*` | historiques synthétiques à vérité connue, balayage de puissance | forme loterie, idée générique |
| `registry/predictions.py` | prédictions forward, refuse le rétrospectif, remplace sans éditer | forme loterie, cœur générique |
| `registry/hypotheses.py` | registre d'hypothèses avec révisions et statut INCONCLUSIVE | générique |
| `ts/*` | prévision par quantiles, MASE/pinball/couverture, rapport HTML, scénarios | emploi |

---

## B. Réutilisable tel quel

| Composant | Pourquoi il se transpose sans changement |
|---|---|
| `core/hashing.py` | Indépendant du domaine. Devient la colonne vertébrale des manifestes de capture brute et du registre de prédictions. |
| `core/dotenv.py`, `core/paths.py` | Indépendants du domaine (paths reçoit de nouvelles entrées, pas une réécriture). |
| `registry/hypotheses.py` | Uniquement des champs texte libres ; fonctionne dès aujourd'hui pour des hypothèses hippiques. Les 9 enregistrements existants restent comme historique. |
| `backtest/splits.py` | Découpage chronologique par date ; valable pour les courses. |
| `eval/uncertainty.py` | Travaille sur des tableaux de scores par unité. Un ajout nécessaire (rééchantillonnage par grappe = journée de courses, voir C), pas une réécriture. |
| Configuration des tests et de l'outillage | pytest `filterwarnings=error`, hypothesis, ruff, pyright, version uv épinglée. |
| Méthodologie | Règles de décision fixées à l'avance, puissance avant résultats, malédiction du vainqueur, rétrécissement (shrinkage), INCONCLUSIVE ≠ REJECTED. C'est l'actif le plus précieux du dépôt. |
| Patron CLI | typer avec sous-applications ; erreurs sous forme de phrases, pas de traces de pile. |
| Patrons de client HTTP de `francetravail.py` | fournisseur de jeton, retry, secrets masqués des reprs — modèle pour les connecteurs. |

## C. Adaptable (refactoriser, garder l'idée)

| Aujourd'hui | Devient | Ce qui change |
|---|---|---|
| `HistoryView` (coupé par **date**) | `PointInTimeView` (coupé par **horodatage + instant de connaissance**) | Plusieurs courses par jour : un résultat n'est utilisable qu'après avoir été *connu*, pas après sa date. Chaque fait porte `event_time` et `known_at` ; la vue filtre sur `known_at < prediction_time`. Les tests de propriété et le test du « modèle tricheur » sont portés, pas jetés. |
| `models/base.Forecast` (probabilités d'inclusion sommant à k) | `RaceForecast` : `p_win` par partant sommant à 1, `p_top3` optionnel sommant à min(3, n) | `normalise_to_k` est réutilisé tel quel (k=1 et k=3). |
| `backtest/engine.py` | walk-forward générique sur événements | Parcourt les courses dans l'ordre des heures de départ, à un horizon donné ; stocke les probabilités par partant ; même logique d'empreinte et de trace de run. |
| `eval/metrics.py` | métriques de course | Ajouts : log loss multinomiale par course (−log p du gagnant), Brier sur les partants, précision top-1, rappel top-3, MRR, corrélation de rang, fiabilité par tranche. On garde `expected_calibration_error`. |
| `eval/uncertainty.py` | + bootstrap par grappes | Les courses d'une même journée ou réunion partagent terrain, météo et conditions de marché : rééchantillonner par journée, pas par course. |
| `eval/power.py` | « combien de courses pour détecter un Δ de log loss contre le marché » | Puissance sur différences appariées au lieu de l'uniformité des loteries. |
| `eval/report.py` | rapport hippique | Même ordre : puissance, descriptif, prédictif, comparaison au marché, limites. |
| `data/store.py` + `ArchiveManifest` | stockage brut + stockage normalisé | JSON brut conservé, adressé par contenu, avec un manifeste ; la détection des modifications est essentielle (distancements, résultats amendés). |
| `registry/predictions.py` | prédictions forward de courses | Enregistrement strictement avant le départ ; ajoute `prediction_time`, `race_start_time`, `data_cutoff`, `odds_snapshot_time`, `model_version`, `feature_version`, `horizon`. `HindsightError` et la logique de remplacement sont conservées. |
| `benchmarks/generators.py` | courses synthétiques | Simuler des courses à partir de forces connues (Plackett–Luce) et d'un marché simulé, pour prouver que le banc trouve un avantage planté et refuse un faux. |
| Raisonnement de `collect-offers.yml` | collecteur d'instantanés de cotes | Même argument que pour France Travail : un instantané de cotes avant course non capturé aujourd'hui ne le sera jamais. Environnement d'exécution différent (local, voir §0.3) et **aucun commit de données PMU dans un dépôt public**. |
| `cli.py` | découpé par domaine | Une sous-application par zone (`racing data`, `racing backtest`, `racing predict`…). |

## D. Composants spécifiques à la loterie

### D.1 À retirer du produit actif
`core/gamespec.py`, `data/sources/fdj_loto.py`, `models/baselines.py`,
`models/selection.py`, les parties loterie de `eval/power.py`,
`benchmarks/generators.py` et `benchmarks/sweep.py` (en forme loterie), et leurs tests
(`test_gamespec`, `test_fdj_parser`, `fdj_fixture`, `test_selection`, `test_models`,
`test_power`, `test_sweep`, `test_benchmarks`, parties loterie de `test_report` /
`test_cli`). Données : `data/raw/fdj/`, `data/processed/loto_*.parquet`,
`data/runs/loto_*`.

### D.2 Comment archiver — options

| Option | Avantages | Risques | Recommandation |
|---|---|---|---|
| **1. Tag git `lottery-m1-final` + retrait de `main` ; on garde `docs/reports/milestone-1*.md` et le registre d'hypothèses** | Arbre propre, rien de perdu (un checkout du tag reproduit le M1), aucune maintenance | Le code du M1 ne tourne plus depuis `main` | **Recommandée** |
| 2. Déplacer dans `legacy/lottery/` en package, tests conservés | Toujours exécutable | Chaque refactor du code partagé doit le garder au vert : on paie à vie pour une question close | Seulement si tu veux relancer le M1 régulièrement |
| 3. Laisser en place | Zéro effort | Deux domaines dans un même espace de noms ; le brief l'interdit | Non |

`experiments/loto-1-mois/` : le commiter une fois en l'état (avec `historique.csv`
toujours ignoré, comme le prévoit la modification actuelle du `.gitignore`), ajouter à
`BILAN.md` une ligne disant que l'expérience a été arrêtée après 1 tirage sur 14 le
2026-09-28, puis la retirer avec le reste sous le tag.

### D.3 Le volet *emploi cadre* — décision requise de ta part

| Option | Conséquence |
|---|---|
| **A. Le garder comme package frère `predlab.ts`, intact** | La tâche planifiée continue de collecter des données irremplaçables ; le travail hippique évite `ts/`. Le moins coûteux. |
| B. Le séparer dans son propre dépôt | Séparation nette ; il faut déplacer le workflow et les secrets. |
| C. Le geler (désactiver la tâche planifiée) | Perte d'une série de données impossible à reconstituer ensuite (documenté dans `DATA_SOURCES.md`). |

Je recommande **A** maintenant, et B plus tard s'il continue de vivre. Ce n'est pas du
code loterie et le brief ne le mentionnait pas : je n'y toucherai pas sans ta réponse.

---

## E. Architecture cible

```
                 ┌──────────── sources ────────────┐
JSON PMU turfinfo · IFCE équidés · météo (prévisions archivées / observations)
                 │ collecteur → capture brute (octets, url, retrieved_at, sha256)
                 ▼
     STOCKAGE BRUT  data/raw/<source>/AAAA/MM/JJ/*.json.gz   + manifest.jsonl (chaîné)
                 │ parser (versionné) → validateur (strict ; échoue bruyamment)
                 ▼
 STOCKAGE NORMALISÉ  DuckDB (+ exports Parquet)   bitemporel : event_time, known_at, source_ref
   réunions · courses · partants · résultats · instantanés_cotes · chevaux · personnes · météo
                 │ résolution d'identité (cheval, jockey, entraîneur)
                 ▼
   FEATURES  constructeurs point-in-time, feature_version  ← PointInTimeView(prediction_time)
                 ▼
   MODÈLES  baselines → champion / challengers (registre)
                 ▼
   PRÉDICTIONS  registre immuable (par horizon) ──► notation après résultat officiel
                 ▼
   ÉVALUATION  backtests walk-forward · métriques · calibration · puissance · rapports
                 ▼
   API  FastAPI, REST en lecture seule  ──►  WEB  React + TypeScript + Vite
```

Arborescence proposée (cœur indépendant du domaine, les courses comme un domaine) :

```
src/predlab/
  core/       hashing, dotenv, paths, clock (fuseau horaire explicite), ids
  registry/   hypotheses, predictions, models (champion/challenger), experiments
  backtest/   splits, engine (générique sur événements)
  eval/       uncertainty, metrics_prob, calibration, power, report
  racing/
    domain.py         Meeting, Race, Runner, Horse, Person, Result, OddsSnapshot (pydantic)
    sources/pmu/      client, collector, parser, validators
    sources/weather/  …
    sources/ifce/     fichier de référence des équidés
    store/            raw.py, normalized.py (DuckDB)
    identity.py
    features/         constructeurs + FEATURE_VERSION
    models/           baselines, market, conditional_logit, …
    pipeline/         jobs : plan_day, snapshot_odds, freeze, collect_results, score
  api/        application FastAPI, schémas de réponse
  ts/         emploi cadre (si option A)
web/          React + TS + Vite
```

Renommages de domaine : Draw → **Race** ; prédiction loterie → **RaceForecast** ;
probabilité d'inclusion d'un numéro → **probabilité d'un partant** ; résultat de tirage
→ **RaceResult** ; GameSpec → supprimé (la structure d'une course est de la donnée :
partants, distance, terrain…) ; adaptateur de jeu → **connecteur de source**.

Pourquoi DuckDB maintenant : `ARCHITECTURE.md` l'avait écarté pour 1 075 lignes de
loterie en disant qu'il gagnerait sa place à l'échelle. Les courses, ce sont des
dizaines de milliers de courses, des centaines de milliers de lignes partants et des
jointures permanentes (forme d'un jockey à un instant donné). C'est le moment.
**[hypothèse de volume, mesurée en Phase 1]**

### E.1 Modèle temporel — ce qui décide si les résultats veulent dire quelque chose

- Chaque fait stocké porte `event_time` (quand il s'est produit) et `known_at` (quand
  il était disponible). Pour les captures en direct, `known_at = retrieved_at`. Pour
  l'historique rétro-chargé, `known_at` est **prudent par règle** : en v1, le résultat
  d'une course est réputé connu au début du jour suivant. Cela interdit d'utiliser les
  résultats des courses plus tôt dans la journée — une petite perte d'information pour
  un gain de sûreté important. Assoupli plus tard seulement avec des délais de
  publication mesurés.
- Horizons : le schéma accepte n'importe quel horizon ; la v1 n'implémente que ceux
  que les données permettent honnêtement :
  - **T-matin** : les cotes « de référence » du PMU portent leur propre horodatage
    (échantillon 2015 : 10:30 UTC). Rétro-chargeable.
  - **T-clôture** : dernières cotes « directes » avant le départ. Rétro-chargeable,
    mais **utilisable seulement comme étalon**, jamais comme entrée d'un modèle qui
    prédit plus tôt.
  - **T-1h, T-10min** : nécessitent nos propres instantanés → uniquement vers
    l'avant, à partir du jour où le collecteur démarre.
- Météo : la météo **observée** est connue après coup pour une prédiction à T-24h. Les
  features doivent utiliser des prévisions telles qu'émises avant `prediction_time`
  (prévisions archivées), ou être réservées aux horizons tardifs.
- Non-partants : une prédiction faite à T-24h peut inclure un cheval retiré ensuite.
  La notation renormalise sur les partants effectifs, et le registre garde l'original.

### E.2 Baselines (Phase 3)

| # | Baseline | Définition |
|---|---|---|
| 1 | Aléatoire | permutation aléatoire ; probabilités uniformes — contrôle du banc (doit scorer comme 2) |
| 2 | Uniforme par partant | p = 1/n_partants |
| 3 | Taux de victoire historique | taux de victoire rétréci (Bayes empirique) par cheval, repli sur jockey/entraîneur |
| 4 | Forme simple du cheval | à partir des places récentes (musique / courses passées), jours depuis la dernière course |
| 5a | Marché, brut | p_i = (1/cote_i) / Σ_j (1/cote_j), par course, à l'horizon correspondant |
| 5b | Marché, calibré | 5a avec correction du biais favori–outsider, ajustée sur le train uniquement |

5b compte : le biais favori–outsider est bien documenté dans la littérature sur les
marchés de paris, donc les probabilités implicites brutes sont un épouvantail
*battable*. La barre honnête, c'est le marché calibré. Normaliser par course supprime le
niveau de la marge sans coder en dur un taux de prélèvement, lequel a d'ailleurs changé
en 2025 sur les paris *Simple* sur pmu.fr (annoncé par le PMU, chiffres
[non vérifiés]) — une frontière de régime candidate.

### E.3 Ce que « réussir » doit vouloir dire, fixé à l'avance [hypothèse]

Remplacer le marché est improbable. La cible de recherche réaliste, dans la lignée de
Bolton & Chapman (1986) et Benter (1994), est : **un modèle fondamental combiné au
marché améliore, hors échantillon, la log loss du marché calibré seul**, avec un test
apparié par grappes qui survit à la correction des comparaisons multiples. Ordre de
grandeur de puissance : détecter un gain de log loss de 0,01 par course avec un
écart-type apparié de 0,3 demande ≈7 000 courses ; 0,005 en demande ≈28 000. Ces
écarts-types sont des suppositions — la Phase 3 les mesure.

### E.4 Sortie du modèle (par partant)

`cheval · p_win · p_top3 (si pris en charge) · intervalle (bootstrap sur les
ajustements du modèle) · p_marché · modèle_moins_marché · principaux facteurs`, plus au
niveau de la course `prediction_time · data_cutoff · odds_snapshot_time ·
model_version · feature_version`. Déduire le top-3 des probabilités de victoire par la
formule de Harville est connu pour surestimer les favoris ; prévoir plutôt un modèle
Plackett–Luce ou un modèle top-3 direct.

---

## F. Sources de données

### F.1 Synthèse

| Source | Rôle | Officielle | Accès / coût | Statut juridique | Usage |
|---|---|---|---|---|---|
| **JSON PMU turfinfo** | programmes, partants, performances passées, cotes, résultats, rapports | flux propre du PMU, non documenté | sans auth / gratuit | aucune licence publiée ; le PMU détient des droits de producteur de base de données | **Principale** |
| **Site France Galop** | résultats officiels, carrières, valeurs | oui | — | les CGU interdisent l'extraction automatisée et la réutilisation substantielle sans autorisation écrite | **Pas de scraping** ; demander l'autorisation si besoin |
| **IFCE — Fichier des équidés** | référence d'identité des chevaux | oui | sans auth / gratuit | Licence Ouverte | résolution d'identité |
| **Météo-France — API Données climatologiques** | météo observée par station | oui | compte requis / gratuit | Licence Ouverte 2.0 | météo observée, horizons tardifs, analyse |
| **Open-Meteo — Historical Forecast API** | *prévisions* archivées | non | sans auth / gratuit non commercial | CC BY 4.0 | features météo pour les horizons précoces |
| API turf.bzh | historique de cotes, résultats (dérivés du PMU) | non | payant | conditions commerciales | contre-vérification optionnelle |
| Aspiturf, Kaggle « Historical PMU » | tables historiques | non | variable | [non vérifié] | on ne s'appuie pas dessus |
| LeTROT | trot | oui | — | non évalué | seulement si trot plus tard |

### F.2 PMU turfinfo — détail

- Fournisseur : PMU (Pari Mutuel Urbain). Base : `https://online.turfinfo.api.pmu.fr/rest/client/{n}/programme/{JJMMAAAA}`.
- Vérifié aujourd'hui via WebFetch **[vérifié 2026-09-28]** :
  - `…/1/programme/{date}` → réunions et courses. Les champs de course incluent
    `heureDepart`, `distance`, `corde` (ex. `CORDE_DROITE` → sens de la piste),
    `discipline` (PLAT, ATTELE, MONTE, OBSTACLE…), `specialite`,
    `categorieParticularite` (ex. HANDICAP), `conditionAge`, `conditionSexe`,
    `conditions` (texte), `nombreDeclaresPartants`, `montantPrix`, `penetrometre`
    (valeur, heure de mesure, libellé), `parcours`, `ordreArrivee`, `statut`,
    `incidents`, `hippodrome`. Les réunions portent `pays` et un objet `meteo`
    (température, vent, ciel).
  - `…/1/programme/{date}/R{r}/C{c}/participants` → par partant : `nom`, `numPmu`,
    `age`, `sexe`, `race`, `idCheval` (présent en 2026, **absent de l'échantillon
    2015**), `driver` (jockey), `entraineur`, `proprietaire`, `eleveur`, `placeCorde`
    (numéro de corde), `handicapPoids`, `handicapValeur`, `oeilleres`, `supplement`,
    `driverChange`, `musique`, compteurs de carrière, gains (`gainsParticipant.*`),
    `ordreArrivee`, `dernierRapportReference` et `dernierRapportDirect` (cotes, chacune
    avec son horodatage `dateRapport`, tendance, indicateur de favori).
  - `…/61/programme/{date}/R{r}/C{c}/performances-detaillees/pretty` → par cheval,
    courses passées : date, hippodrome, discipline, allocation, distance, nombre de
    partants, temps du vainqueur, état du terrain, et pour chaque participant place,
    jockey, poids, corde, écart, œillères.
  - `…/1/programme/{date}/R{r}/C{c}/rapports-definitifs` → rapports officiels par type
    de pari.
- Profondeur historique : des programmes avec résultats ont été renvoyés pour le
  2013-05-05 et le 2015-06-07. Date la plus ancienne disponible et complétude des champs
  par année **[non vérifié]** — mesurées en Phase 1.
- Historique des cotes : seulement deux instantanés par partant dans l'archive
  (référence + dernier direct), et le direct manque parfois (vu dans l'échantillon
  2015). Tout ce qui est plus fin doit être capturé en direct.
- Juridique : aucune condition publique pour ce flux, aucune limite de débit
  documentée. Les droits du PMU sur sa base ont déjà été défendus : TGI de Paris,
  20 juin 2007, Eturf condamnée (120 000 €) pour avoir extrait et republié
  systématiquement les données de pmu.fr
  ([Legalis](https://www.legalis.net/actualite/eturf-condamnee-pour-extraction-illicite-de-la-base-de-donnees-du-pmu/)).
  **Règles d'usage proposées :** recherche personnelle et non commerciale ; faible
  débit de requêtes avec cache (ne jamais re-télécharger une journée close) ; données
  brutes jamais redistribuées ni commitées dans le dépôt public (même règle que pour
  les archives FDJ) ; si cela devient un produit, négocier une licence d'abord. Je ne
  suis pas juriste : c'est une position de risque, pas un avis juridique.
- Fragilité : non documenté, le segment numérique `client/{n}` varie selon
  l'endpoint. Les parsers doivent échouer bruyamment en cas de dérive du schéma, comme
  le fait le parser FDJ.

### F.3 Choix de la discipline — le plat, confirmé sous une condition

Le flux PMU expose ce dont une modélisation du plat a besoin : corde (`placeCorde`),
poids (`handicapPoids`), valeur de handicap (`handicapValeur`), terrain avec une valeur
mesurée et son heure (`penetrometre`), sens de la piste (`corde`), distance,
catégorie, et pour les courses passées poids, cordes et écarts. Cela justifie **PLAT,
hippodromes français (`pays = FRA`), pur-sang** comme premier modèle.

Le trot est l'alternative sérieuse : il est souvent présenté comme la discipline la
plus importante des programmes français, ce qui voudrait dire davantage de données
**[non vérifié — mesuré en Phase 1]**. Mais il ajoute les disqualifications pour
allure irrégulière, les handicaps de distance, deux modes de départ et les changements
de ferrure — davantage de modélisation métier avant la première baseline. France Galop
annonce « plus de 7 000 » courses de galop par an, plat et obstacle confondus
([France Galop, chiffres clés](https://www.france-galop.com/fr/chiffres-cles), chiffres
2020 pour l'essentiel) ; combien figurent dans le flux PMU avec des cotes
**[non vérifié]**.

**Condition :** la Phase 1 compte, par année, les courses de plat françaises avec des
cotes complètes dans le flux PMU. Si ce nombre rend l'objectif de puissance de E.3
inatteignable sur l'historique disponible, je reviens vers toi avec le trot comme
alternative documentée avant d'aller plus loin.

---

## G. Plan du front-end

**Stack :** React + TypeScript + **Vite** (une SPA locale : pas de SEO, pas de rendu
serveur ; Next.js ajouterait un serveur pour rien), React Router, TanStack Query pour
l'état des données d'API, **CSS Modules + design tokens en propriétés CSS
personnalisées** (pas de Tailwind, pas de framework de composants), primitives Radix
uniquement là où l'accessibilité est difficile (infobulle, dialogue, onglets).
Graphiques : Observable Plot pour les graphiques statistiques standards, SVG natif pour
les deux graphiques signature (barres de probabilité avec repère du marché, diagramme
de fiabilité). Types d'API générés depuis le schéma OpenAPI de FastAPI
(`openapi-typescript`), pour que l'interface ne puisse pas diverger du contrat.
L'interface ne lit jamais de fichiers de données.

**API backend :** FastAPI (pydantic est déjà la couche de modèles du projet ; OpenAPI
vient gratuitement), REST en lecture seule, servie localement par uvicorn.

```
GET /races?date=AAAA-MM-JJ        GET /races/today
GET /races/{race_id}              GET /races/{race_id}/predictions?horizon=
GET /races/{race_id}/odds         GET /races/{race_id}/result
GET /horses/{horse_id}            GET /persons/{person_id}   (jockey / entraîneur)
GET /models                       GET /models/{model_id}/performance
GET /experiments                  GET /hypotheses
GET /data/status
```

**Vues**

1. **Aujourd'hui** — tableau des courses de plat françaises du jour : heure,
   hippodrome, distance, terrain, partants, statut (à venir / figée / partie /
   résultat officiel), disponibilité des prédictions par horizon, indicateur de
   confiance. Aucune cote sur cette page.
2. **Détail d'une course** — tableau des partants trié par probabilité du modèle :
   barre de p_win avec le repère du marché sur le même axe, modèle − marché avec son
   intervalle, p_top3, 2 ou 3 facteurs clés ; évolution des cotes (quand des
   instantanés existent) ; après la course, le résultat et le score de la prédiction.
   L'en-tête affiche `prédiction figée à`, `données arrêtées à`, `cotes du`.
3. **Fiche cheval** — tableau de carrière ; performances par tranche de distance,
   terrain, hippodrome, sens de piste ; forme récente ; historique avec jockeys et
   entraîneurs. Taille d'échantillon sur chaque agrégat.
4. **Performance des modèles** — champion contre baselines contre marché : log loss,
   Brier, calibration (diagramme de fiabilité par tranche), performance dans le temps,
   par type de course / hippodrome / distance, avec intervalles bootstrap et n.
5. **Recherche** — champion, challengers, hypothèses (proposées / soutenues / rejetées
   / non concluantes), historique des expériences — lus dans les registres existants.

**Taxonomie visuelle** — cinq étiquettes, chacune avec son style de badge, utilisées
partout : `FAIT OBSERVÉ` · `FEATURE DU MODÈLE` · `ASSOCIATION STATISTIQUE` ·
`PRÉVISION` · `INFORMATION DE MARCHÉ`. Les explications de facteurs disent « associé
à », jamais « parce que ».

Ton : mode clair d'abord, palette neutre, tableaux denses, pas de codes vert/rouge
d'argent, pas de « tuyaux », aucune incitation à parier.

---

## H. Phases de mise en œuvre

Chaque phase se termine sur un critère de sortie, pas sur une date.

| Phase | Contenu | Critère de sortie |
|---|---|---|
| **0 — Décisions** | Tes réponses sur D.2, D.3, et la validation de ce plan | Feu vert écrit |
| **1 — Migration + socle de données** | Tag `lottery-m1-final`, archivage du code loterie, commit puis archivage de l'expérience Loto ; renommage des concepts ; schéma du domaine hippique ; stockage brut + manifeste ; client PMU avec limitation de débit + cache ; **audit des données** : un programme par jour sur l'historique pour compter les courses par discipline/pays/année et mesurer la complétude des champs. **Démarrer maintenant le collecteur d'instantanés en direct** (programmes + cotes toutes les N minutes les jours de course, `launchd` local). | Rapport d'audit ; position juridique rédigée ; condition sur la discipline levée ; collecteur en marche |
| **2 — Ingestion historique** | Partants, performances, résultats, rapports pour le plat français ; DuckDB normalisé ; validateurs stricts ; résolution d'identité v1 (identifiant PMU quand il existe, sinon nom + année de naissance + sexe + race, fichier IFCE pour départager) ; détection des révisions | Stockage reconstruit à l'identique à partir du brut ; rapport de complétude et de collisions d'identité |
| **3 — Baselines + backtest** | PointInTimeView, moteur générique sur événements, 6 baselines, métriques de course, bootstrap par grappes, analyse de puissance, tests du banc sur courses synthétiques (avantage planté trouvé, faux avantage refusé), rapport | On sait, avec des intervalles, à quelle distance chaque baseline se situe du marché calibré |
| **4 — Courses à venir** | Ingestion quotidienne des programmes, gestion des non-partants, instantanés par horizon | Chaque course de plat française d'une journée a un jeu d'entrées figé par horizon |
| **5 — API de prédiction** | Registre de prédictions forward par horizon, notation après résultat, endpoints FastAPI | Prédictions enregistrées avant le départ, notées automatiquement, servies par l'API |
| **6 — Front-end** | Les cinq vues | Tu peux ouvrir l'application et voir les courses du jour, les prédictions, la comparaison au marché, les résultats, la performance |
| **7 — Pipeline quotidien** | Jobs idempotents (planifier → instantané → figer → résultats → noter), journal d'exécution, alerte en cas d'échec ; `launchd` | 30 jours sans intervention manuelle |
| **8 — Modèles & agents** | Logit conditionnel, modèle combiné au marché, gradient boosting avec objectif de classement, Plackett–Luce pour le top-3 ; registre champion/challenger avec règle de promotion (pré-enregistrée, n minimal, test apparié, pas de promotion sur une série courte) ; puis agents : qualité des données et sceptique en premier | Un challenger promu — ou non — par la règle, pas par une série chanceuse |

Changement délibéré par rapport à l'ordre de ton brief : le **collecteur d'instantanés
de cotes démarre en Phase 1**, pas en Phase 4. Chaque jour sans lui est une journée
d'historique de cotes à T-1h / T-10min perdue pour de bon — la même leçon que le
collecteur France Travail a déjà apprise à ce projet.

---

## I. Risques

| Risque | Pourquoi c'est important | Parade |
|---|---|---|
| Fiabilité des sources | Flux non documenté ; peut changer ou disparaître | Capture brute de chaque réponse ; parsers stricts ; alertes de dérive de schéma ; une deuxième source identifiée pour les résultats |
| Licence des données | Le PMU et France Galop revendiquent des droits sur leurs bases ; dépôt public | Usage de recherche personnel, pas de redistribution, données brutes ignorées par git, pas de scraping de France Galop, licence avant tout produit |
| Fuite — résultats | Résultats du jour même, notations post-course, données révisées | `known_at` sur chaque fait ; règle du lendemain en v1 ; portage du test du modèle tricheur |
| Fuite — horodatage des cotes | Dernières cotes directes utilisées par un modèle d'horizon plus précoce | Instantanés joints seulement si `dateRapport ≤ prediction_time` ; horizon sur chaque prédiction |
| Fuite — météo | Météo observée utilisée à T-24h | Prévisions archivées pour les horizons précoces |
| Fuite — agrégats | Taux jockey/entraîneur calculés sur tout l'historique | Features uniquement via PointInTimeView ; tests sur des coupures tirées au hasard |
| Historique manquant | Seulement 2 instantanés de cotes historiquement ; champs absents les années anciennes (ex. `idCheval`) | Mesurer la complétude par année ; restreindre la fenêtre de backtest aux années où les features existent |
| Identifiants incohérents | Noms réutilisés, suffixes étrangers, graphies de jockeys (« G.MACAIRE (S) ») | Module d'identité avec tables d'alias et rapport de collisions ; fichier de référence IFCE |
| Fragilité du scraping | Chemins d'endpoints et charges utiles qui changent | Parsers versionnés ; échec bruyant ; jamais d'absorption silencieuse |
| Déséquilibre de classes | Un gagnant parmi ~8 à 16 partants | Softmax par course / logit conditionnel, pas de classifieurs binaires indépendants ; règles de score propres |
| Calibration | Biais favori–outsider du pari mutuel ; modèles trop confiants sur petits échantillons | Baseline marché calibrée ; diagrammes de fiabilité ; rétrécissement |
| Non-stationnarité | Changements de prélèvement, de règlement, carrières des jockeys | Évaluation stratifiée dans le temps ; frontières de régime consignées |
| Tests multiples | Nombreuses features × sous-groupes | Pré-enregistrement dans le registre d'hypothèses ; FDR BY comme aujourd'hui |
| Environnement d'exécution | Shells Cowork bloqués vers le PMU | `launchd` local, ou domaine ajouté à la liste blanche |
| Dérive vers le jeu | La comparaison au marché appelle des fonctions de « value bet » | Pas de mise, de gestion de bankroll, de prise de pari ni de compte PMU — jamais. L'interface présente modèle − marché comme une grandeur de recherche |

---

## J. Ce que je recommande de faire en premier

1. **Répondre à trois questions :** méthode d'archivage (D.2, je recommande tag +
   retrait), le volet emploi cadre (D.3, je recommande de le garder intact), et si tu
   acceptes les règles d'usage du PMU de F.2.
2. **Audit des données de la Phase 1** (petit, non destructif, réversible) : compter
   les courses de plat françaises par année avec cotes et mesurer la complétude des
   champs dans le flux PMU. C'est la condition du choix de discipline et de l'objectif
   de puissance.
3. **Démarrer le collecteur d'instantanés de cotes** sur ton Mac dès que le client
   existe — c'est la seule horloge irréversible de ce projet.
4. Seulement ensuite, la partie destructive de la migration (tag, archivage,
   renommages).

Rien ne sera supprimé, déplacé ni renommé avant ta validation.

---

## Sources consultées aujourd'hui

- Endpoints PMU turfinfo (programme, participants, performances-detaillees,
  rapports-definitifs ; dates 2013-05-05, 2015-06-07, 2026-09-26, 2026-09-27), lus via
  WebFetch le 2026-09-28.
- [Legalis — Eturf condamnée pour extraction illicite de la base de données du PMU](https://www.legalis.net/actualite/eturf-condamnee-pour-extraction-illicite-de-la-base-de-donnees-du-pmu/)
- [France Galop — Conditions générales d'utilisation du site](https://www.france-galop.com/en/terms-and-conditions-use-france-galop-website)
- [France Galop — Chiffres clés](https://www.france-galop.com/fr/chiffres-cles)
- [data.gouv.fr — Fichier des équidés (IFCE)](https://www.data.gouv.fr/datasets/fichier-des-equides)
- [data.gouv.fr — API Données climatologiques (Météo-France)](https://www.data.gouv.fr/dataservices/api-donnees-climatologiques)
- [Open-Meteo — Conditions](https://open-meteo.com/en/terms) · [Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api)
- [turf.bzh — Documentation de l'API](https://www.turf.bzh/api-docs.php)
- [LeTROT — Le PMU augmente le taux de retour joueurs sur le simple (2025-10-03)](https://www.letrot.com/actualites/le-pmu-augmente-le-taux-de-retour-joueurs-sur-le-simple-25329) — titre seulement ; chiffres illisibles
- [data.gouv.fr — L'institution des courses (Cour des comptes, 2018)](https://www.data.gouv.fr/datasets/linstitution-des-courses) — données financières, pas au niveau des courses : inutile ici

Non vérifiables : Aspiturf (site injoignable), jeu Kaggle « Historical PMU Horse
Racing Dataset » (description illisible), conditions d'utilisation de pmu.fr
applicables au flux.
