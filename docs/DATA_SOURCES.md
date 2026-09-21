# Data sources

Everything in this document was read from the live official source on the date stated.
Nothing here is recalled from training data or inferred. Where a fact has **not** been
verified, it says so.

## Loto — official FDJ archive

**Retrieved:** 2026-09-19
**Publisher:** La Française des Jeux (FDJ)
**Landing page:** <https://www.fdj.fr/jeux-de-tirage/loto/historique>

FDJ splits the Loto history into five archives. The split points are format and rule
changes, not arbitrary chunking. Only the current era is ingested; see *Era scope*.

| Period | URL suffix (under the base below) | Size | Ingested |
|---|---|---|---|
| Nov 2019 → Sep 2026 | `1a2b3c4d-9876-4562-b3fc-2c963f66afp6` | 180 kB | **yes** |
| Feb 2019 → Nov 2019 | `…afo6` | 14 kB | no |
| Mar 2017 → Feb 2019 | `…afn6` | 39 kB | no |
| Oct 2008 → Mar 2017 | `…afm6` | 69 kB | no |
| May 1976 → Oct 2008 | `…afl6` | 239 kB | no |

Base: `https://www.sto.api.fdj.fr/anonymous/service-draw-info/v3/documentations/`

The same page also publishes Grand Loto and Super Loto archives. These are different
games with different mechanics and are deliberately out of scope.

### Verified file format (2019-11 era)

| Property | Value |
|---|---|
| Container | ZIP, single member `loto_201911.csv` |
| SHA-256 of the ZIP as retrieved | `66a0f0a94c3f9ba45758f8cea886764be7ab9ef4f4e0e1931f3c7f6f5170e074` |
| ZIP size | 183 954 bytes |
| Encoding | Windows-1252 (`cp1252`) |
| Separator | `;` |
| Columns | 50, the 50th empty — every line ends with a trailing `;` |
| Line endings | CRLF |
| Row order | **descending** by draw date |
| Rows | 1 075 draws, 2019-11-06 → 2026-09-16 |
| Date format | `DD/MM/YYYY` |
| Ball range | 1–49, five per draw (all 5 375 values checked) |
| `numero_chance` range | 1–10, one per draw |
| Weekday counts | LUNDI 358, MERCREDI 359, SAMEDI 358 |
| Currency column | `eur` on every row |

### Quirks that would silently corrupt a naive parser

1. **`jour_de_tirage` is right-padded.** 277 of 1 075 rows carry trailing spaces
   (`"LUNDI   "`, `"SAMEDI  "`). Grouping on the raw string yields five weekday
   values instead of three. The parser strips before mapping.
2. **`annee_numero_de_tirage` changes format inside one file.** `20199133` in 2019
   versus `26111` in 2026. It is therefore kept verbatim for traceability only and
   never used as a key; the canonical key is derived from the draw date.
3. **`numero_7` is a Joker+ code, not a lottery number.** Three incompatible
   formats appear (`1003591`, `0 000 212`, and the literal string
   `Jokerplus indisponible`). Excluded from the predictive dataset.
4. **A "second tirage" block exists on every row.** Columns
   `boule_1_second_tirage` … are populated throughout the era. This is a second,
   separate draw, not part of the main one. It is **not** ingested in Milestone 1,
   and is noted in `docs/STATUS.md` as a candidate additional dataset.
5. **Prize and winner columns are read but discarded.** They describe how the public
   bet, not how the balls fell. Keeping them next to the numbers invites narrative
   fitting after the fact.

### Integrity checks applied at parse time

Each row must satisfy all of the following or ingestion stops:

- the five balls, sorted, plus the chance number must reproduce the source's own
  `combinaison_gagnante_en_ordre_croissant` string exactly;
- the stated weekday must match the calendar weekday of `date_de_tirage`;
- that weekday must be a draw day for the era (Mon/Wed/Sat);
- the date must fall inside the era's range;
- all numbers must lie in their declared pool;
- no two rows may share a draw date.

The header is compared against an exact expected tuple. If FDJ renames, adds or
reorders a column, ingestion fails with a message naming the difference. This is
intentional: a one-column shift would silently move `numero_chance` into `boule_5`
and poison every downstream result. The fix is to review the change and bump
`PARSER_VERSION`, never to relax the check.

### Era scope

Only `loto/2019-11` is defined as a `GameSpec`, because only its mechanics were
verified against data. The 1976, 2008, 2017 and 2019-02 archives exist and can be
downloaded, but their ball counts and rules have **not** been confirmed, so
`get_spec("loto", "1976-05")` deliberately raises rather than guessing.

Pooling draws across a format change is a methodological error, not an
approximation. Extending coverage means verifying each era's mechanics first.

### Known limitations

- The current-era file is **republished after every draw**, so its SHA-256 changes
  roughly three times a week. A different hash is expected, not alarming; a *changed
  historical row* is alarming, and `DrawStore` refuses it by default.
- The endpoint is undocumented. It is the download link the official history page
  actually uses, but FDJ publishes no contract for it and may change it without
  notice.
- No licence statement accompanies the archives. Usage here is non-commercial
  research. Redistribution of the raw files is not assumed to be permitted, which is
  why `data/raw/` is git-ignored while the provenance manifest is tracked.
- `data.gouv.fr` has not been evaluated as a cross-check source.

## Rules

Confirmed on <https://www.fdj.fr/jeux-de-tirage/loto> (2026-09-19): draws take place
Monday, Wednesday and Saturday.

FDJ announced a change of player return rate (TRJ 54.85% → 54.35%) effective
**2026-05-04**. Whether this touched the draw mechanics or only the prize structure
has **not** been verified. It is flagged as a candidate regime boundary and should be
checked before treating the era as homogeneous.

---

## Cadre job postings — France Travail API

Verified against the official OpenAPI specification on 2026-09-20.

| | |
|---|---|
| token | `https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire` |
| base | `https://api.francetravail.io/partenaire/offresdemploi` |
| search | `GET /v2/offres/search` |
| scopes | `api_offresdemploiv2 o2dsoffre` (both mandatory) |
| counting | `range=0-0`, then read the `Content-Range` header — one request per count |
| cadre filter | `qualification=9` (`0` = non-cadre), from the spec |

Credentials live in a git-ignored `.env` (`FRANCETRAVAIL_CLIENT_ID`,
`FRANCETRAVAIL_CLIENT_SECRET`). Anything already exported in the environment wins over
the file. They are never logged, never stored in a record, and `__repr__` hides the
secret.

**Offers are counted, never downloaded.** The licence governs redistribution of the
offers themselves; a count is all the indicator needs, and keeping the offers out is a
design decision rather than an omission.

### The two measurement rules that govern every use of this data

The API returns offers that are **active right now**. Expired offers are gone. So:

1. **A count means nothing without `captured_at`.** "Offers created in August" counted
   in September is smaller than the same count taken in August — not because fewer
   were created, but because some have expired. The datum is the triple
   `(window, captured_at, lag_days)`.

2. **Only counts taken at the same lag are comparable.** Comparing "August at J+30"
   with "September at J+3" measures the expiry curve, not the labour market. The
   analysis layer must select a constant lag.

### A window still open is incomplete, not merely early

Counting the current month on the 20th asks the API for offers created up to the 30th;
the ones created on the 21st do not exist yet. The result is a **partial sum over the
elapsed part of the window** — an arithmetic error if placed on the monthly axis, not a
lag artefact that a lag correction could absorb.

Every record therefore carries:

| field | meaning |
|---|---|
| `lag_days` | signed `captured_at − window_end`. **Negative ⇒ the window was still open.** |
| `observed_days` | days of the window already over at capture (the capture day itself excluded — offers can still be created during it) |
| `window_days` | length of the window |
| `window_complete` | `observed_days >= window_days` |

`predlab collect offers` captures the month in progress by default and labels it
`PARTIEL — n/N j écoulés`; re-measured daily it gives the intra-month accumulation
curve a nowcast needs. `--skip-current` leaves it out. **Records with
`window_complete: false` must never be mixed into the monthly series.**

`collector_version` is `ft-offres-2` (v1 recorded no completeness information).

### La forme de fenêtre : journée à lag fixe

C'est la décision qui conditionne tout le reste, et la mesure d'expiration ci-dessous
l'a imposée.

Mesurer un **mois calendaire** place le lag là où le calendrier le met : le 20
septembre, août est à J+20 et mars à J+173. Comme la survie d'une annonce est
exponentielle de demi-vie ~24 jours, deux mois mesurés le même jour ne sont pas sur la
même échelle — facteur 86 entre les deux extrêmes de la première collecte. Ramener ces
mesures sur une échelle commune suppose de connaître la courbe d'expiration, qu'on ne
connaît pas encore, et dont l'erreur d'estimation contaminerait chaque point.

Mesurer **la journée qui a exactement L jours** place le lag à L, par construction, à
chaque exécution, sans arithmétique et sans correction. Deux mesures consécutives sont
comparables parce qu'elles ont le même âge, pas parce qu'on les a corrigées.

| | mois calendaire | journée à lag fixe |
|---|---|---|
| lag | subi | choisi |
| comparabilité | après correction estimée | par construction |
| points par semaine | 0,23 | 7 |
| premier point exploitable | à la clôture du mois suivant | le lendemain |
| agrégation | indécomposable | jours → semaines → mois |

Le sens de l'agrégation est décisif : une série quotidienne se replie en semaines ou en
mois après coup, une série hebdomadaire ne se déplie jamais.

**Plusieurs lags par passage** (`--lags 1,7,30,90`) n'est pas de la redondance. Chaque
journée calendaire est remesurée à 1, 7, 30 puis 90 jours d'âge, ce qui trace **sa
propre** courbe de survie. La série à lag 1 est exploitable immédiatement ; les mesures
plus tardives sont ce qui permettra plus tard de ramener une série à lag long sur la
même échelle, avec une courbe estimée sur les données et non supposée.

Lag 0 est refusé : ce serait la journée en cours, donc une somme partielle — exactement
la mesure que cette commande existe pour éviter.

Les deux formes partagent le même ledger. Un enregistrement journalier se reconnaît à
`window_start == window_end`, sans champ redondant qui pourrait contredire les dates
qu'il duplique.

### Collecte automatique

`.github/workflows/collect-offers.yml` capture tous les jours à 04:10 UTC et commite
le ledger. Il tourne chez GitHub plutôt que sur une machine parce qu'un jour manqué
est un trou définitif : un Mac endormi produit exactement ça, un cron hébergé non.

- Secrets attendus : `FRANCETRAVAIL_CLIENT_ID`, `FRANCETRAVAIL_CLIENT_SECRET`
  (Settings → Secrets and variables → Actions). Le dépôt est public : les secrets ne
  sont pas exposés aux workflows déclenchés par une PR de fork, et ce workflow n'a
  aucun déclencheur `pull_request`.
- `concurrency` interdit deux exécutions simultanées : le ledger est chaîné, un append
  concurrent forkerait la chaîne.
- 04:10 UTC et non minuit : un retard d'ordonnancement GitHub (plusieurs dizaines de
  minutes en charge) ne doit pas faire basculer `captured_at` d'un jour et décaler
  silencieusement tous les lags.
- Les mois clos sont re-mesurés à chaque passage. Ce n'est pas de la redondance :
  mesurer la même fenêtre à des lags croissants trace la courbe d'expiration.
- Deux passes par jour d'exécution : `collect daily --lags 1,7,30,90` (la série qui
  sera modélisée) puis `collect offers --months 6` (la courbe d'expiration mensuelle,
  et le seul chiffre comparable à ce qu'un tiers citerait pour un mois). La seconde
  tourne en `if: always()` : elle ne doit pas être annulée par l'échec de la première.
- `predlab collect offers` sort en code non-zéro si aucune mesure n'a été enregistrée,
  et l'étape de commit tourne malgré l'échec : une passe interrompue à mi-parcours a
  quand même capturé des mesures qu'on ne pourra plus jamais reprendre à ce lag.
- `predlab collect verify` contrôle la chaîne avant l'append, pas seulement après :
  écrire sur un ledger déjà rompu enterrerait la rupture sous une queue valide.

### Mesure de la courbe d'expiration (2026-09-20)

Première collecte : 6 mois clos mesurés le même jour, donc chacun à un lag différent.

| fenêtre | lag | offres cadre |
|---|---:|---:|
| 2026-03 | J+173 | 54 |
| 2026-04 | J+143 | 113 |
| 2026-05 | J+112 | 339 |
| 2026-06 | J+82 | 771 |
| 2026-07 | J+51 | 1 388 |
| 2026-08 | J+20 | 4 625 |

Une régression log-linéaire du comptage sur le lag donne R² = 0,994 et une demi-vie
apparente de **24,3 jours** (survie 42 % à J+30, 7,6 % à J+90). Août mesuré à J+20
compte **86×** plus d'offres que mars mesuré à J+173.

Ceci n'est pas une série du marché de l'emploi : c'est la fonction de survie des
annonces, et rien d'autre. Un R² de 0,994 sur six points ne laisse pratiquement aucune
place à un signal de marché. **Conséquence : l'historique rétro-capturé est
inutilisable comme série de volumes.** Seules les mesures prises à lag constant, en
avant, le sont. La table ci-dessus garde une valeur propre — elle mesure la survie —
mais elle ne doit jamais servir de niveau de marché.

### Known limitations

- **History cannot be rebuilt.** Only active offers are exposed, so a month not
  captured today is captured at a longer lag forever after. The collector has to run
  on a schedule from now on.
- Counts are of France Travail postings, not of the whole cadre market. They are a
  leading indicator to be validated against an external series, not a census.
- The relationship between these counts and any Apec-internal volume is **unmeasured**
  and must be established before it is claimed.


---

## Offres cadre collectées — série DARES

Vérifiée sur l'API Opendatasoft le 2026-09-20.

| | |
|---|---|
| jeu | `dares_offres_collectees_satisfaites_france_travail_brutes_mens` |
| base | `https://data.dares.travail-emploi.gouv.fr/api/explore/v2.1/catalog/datasets` |
| catalogue | <https://www.data.gouv.fr/datasets/offres-collectees-et-satisfaites-par-france-travail-brutes-mensuelles> |
| licence | **Licence Ouverte v2.0** — redistribution autorisée avec attribution |
| filtre | `qualification="Cadres" and type_d_emploi="Total" and type_d_offre_d_emploi="Offres d'emploi collectées"` |
| couverture | 1996-01 → 2026-07, mensuel, **367 points, aucun trou** |
| champ | France métropolitaine, données **brutes** (non CVS) |

Attribution requise : *DARES, offres collectées et satisfaites par France Travail
(brutes, mensuelles)*.

### Pourquoi cette série change le projet

C'est **le même concept que le collecteur live** — offres collectées par France
Travail — publié par le service statistique du ministère et ventilé par qualification,
donc `Cadres` est disponible directement et non par proxy. Trois conséquences :

1. **Une cible qui existe aujourd'hui.** 367 observations mensuelles réelles, sur
   lesquelles un moteur de prévision se construit et se backteste maintenant, au lieu
   d'attendre que la série live mûrisse.
2. **Un contrôle externe du collecteur.** Si les comptages API, corrigés de
   l'expiration, ne suivent pas cette série, le collecteur mesure un artefact de
   plateforme et non le marché du travail. C'est une affirmation réfutable, et c'est
   cette série qui la rend réfutable.
3. **Un problème de prévision avec un usage réel.** La DARES publie avec ~2 mois de
   retard (2026-07 était le dernier chiffre au 2026-09-20). Prévoir le chiffre avant
   sa publication est un *nowcast d'une statistique officielle* — quelque chose de
   défendable, contrairement à « prédire le marché de l'emploi » dans l'abstrait.

### Ce qui borne toute affirmation d'exactitude

**Les valeurs sont arrondies à la centaine.** Toutes, sans exception. Sur cette série
la moyenne est de 8 461, donc le pas d'arrondi vaut **1,18 % du niveau moyen**. Une
erreur de prévision inférieure à ~1,2 % n'est pas de la compétence : elle est sous la
résolution de la donnée. Toute exactitude annoncée doit être lue contre ce plancher, et
un test le vérifie plutôt qu'une note de bas de page.

**La série est brute, non désaisonnalisée.** La saisonnalité est massive :

| mois | indice | | mois | indice |
|---|---:|---|---|---:|
| janvier | 1,066 | | juillet | 1,033 |
| février | 1,017 | | **août** | **0,765** |
| mars | 1,096 | | septembre | 1,093 |
| avril | 1,001 | | octobre | 1,079 |
| mai | 0,952 | | novembre | 0,963 |
| juin | 1,056 | | décembre | 0,879 |

Amplitude saisonnière **33,1 %** du niveau annuel, contre une variation annuelle
médiane de **11,8 %**.

> **Correction apportée par le backtest.** De ces deux chiffres, ce document concluait
> que la baseline de référence devait être le *naïf saisonnier*. La mesure dit le
> contraire : à tous les horizons testés, le naïf simple le bat (MASE 1,78 contre 2,52
> à un mois). Le raisonnement sautait une étape — une saisonnalité forte ne rend pas
> « le même mois l'an dernier » bon, parce qu'y accéder coûte douze mois de dérive de
> niveau, et ce niveau passe de 4 000 à 19 000 puis à 12 000. La forme saisonnière est
> réelle ; payer un an de dérive pour l'atteindre ne l'est pas.
>
> Ce qui gagne à un mois est `seasonal_naive_drift` — le même mois l'an dernier,
> corrigé de l'évolution récente du niveau. La conclusion survit donc sous une forme
> affaiblie : la saisonnalité aide, mais seulement une fois le niveau corrigé.
>
> Détail d'arithmétique utile à la lecture des tableaux : à l'horizon 12, le naïf
> saisonnier **est** le naïf (le même mois l'an dernier, douze mois à l'avance, c'est
> la dernière observation). Leurs scores y coïncident par construction.

**Rupture COVID.** 2020-03 → 2020-05 : 7 300 → 4 600 → 4 700, contre ~11 000 en début
d'année. C'est le point aberrant le plus violent de trente ans d'historique et il
dominera n'importe quelle métrique d'erreur moyenne. À traiter explicitement — jamais à
supprimer en silence.

### Limites connues

- Offres **collectées par France Travail**, pas le marché cadre entier. Beaucoup
  d'offres cadre ne passent jamais par France Travail. C'est un indicateur, pas un
  recensement.
- La série des offres *satisfaites* est suspendue depuis une rupture méthodologique en
  juillet 2013 ; seules les offres collectées sont utilisées ici.
- Le lien entre cette série et les volumes internes Apec est **non mesuré** et ne doit
  pas être affirmé.


---

## Climat des affaires — INSEE

Vérifié sur le service SDMX le 2026-09-21.

| | |
|---|---|
| endpoint | `https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/{idbank}` — **sans clé** |
| idbank | `001565530` |
| intitulé | Indicateur du climat des affaires — Tous secteurs — France métropolitaine |
| couverture | mensuel, 1977-01 → 2026-08 (retenu à partir de 1996-01) |
| licence | Licence Ouverte — attribution Insee |

### Pourquoi cette variable et pas une autre

**Les élections et la géopolitique ne sont pas modélisables ici, et l'arithmétique le
dit sans détour.** 367 mois de données cibles contiennent environ sept élections
nationales françaises : on ne peut pas estimer à partir de sept observations un effet
dont on ignore le signe, l'ampleur et le délai. C'est le même calcul de puissance qui
disait qu'il faudrait 385 ans pour détecter un biais de 5 % au Loto. « Tensions
géopolitiques » est pire encore : ce n'est pas une série, donc il n'y a rien à
confronter à la cible.

Le climat des affaires est le cas inverse. Série mensuelle depuis 1977, il mesure
l'appréciation que les entreprises portent sur leur propre situation — ce qui précède
une décision d'embauche — et surtout **il est publié en avance sur la cible** : la
lecture d'août 2026 est sortie le 21 août, quand la DARES n'avait publié que juin. Une
variable qui arrive après ce qu'elle doit prédire ne sert à rien, si bien corrélée
soit-elle.

### La règle de causalité, et la faute qu'elle a corrigée

La première version lisait le climat **du mois prévu**. À un mois d'échéance c'est
légitime ; à six mois c'est une fiction — prévoir janvier 2027 depuis une série
s'arrêtant en juillet 2026 aurait utilisé le climat de janvier, qui n'existe pas
encore. Le backtest aurait rapporté un modèle impossible à exécuter.

La règle qui tient à tous les horizons est opérationnelle : la DARES publie à +2 mois,
le climat à +0, donc au moment de prévoir, la lecture la plus fraîche disponible est
environ *dernier mois DARES publié + 2*. Chaque horizon utilise **cette** lecture.
Corriger cette faute a ramené le gain à un mois de 21,4 % à 18,2 % — l'écart était la
fuite.

### Résultat mesuré (2026-09-21)

139 prévisions, entraînement ≤ 2014-12, base `seasonal_naive_drift`.

| horizon | sans climat | avec climat | gain | p (permutation par blocs) |
|---|---:|---:|---:|---:|
| 1 mois | 1 543 | **1 261** | +18,2 % | 0,0146 |
| 3 mois | 1 858 | **1 451** | +21,9 % | 0,0104 |
| 6 mois | 2 341 | **1 872** | +20,0 % | 0,0128 |

MAPE à un mois : **11,4 %** contre 14,3 %. Couverture 85,6 % pour 80 % annoncés.

**Et pourtant : rien ne survit au contrôle des tests multiples.** Six tests (2 bases ×
3 horizons), Benjamini-Yekutieli à q = 0,05 donne un seuil de 0,0034 au rang 1 ; le
plus petit p vaut 0,0104. Tout est rejeté.

Les deux lectures méritent d'être posées côte à côte :

- **Contre.** Le protocole que ce projet s'est imposé rejette le résultat. Le point
  principal n'avait pas été pré-spécifié : avoir choisi `seasonal_naive_drift` à
  l'horizon 1 *après* avoir vu les chiffres est précisément ce que la correction
  sanctionne.
- **Pour.** Le gain est de même signe et de même ampleur aux trois horizons (18 à
  22 %), et la calibration s'améliore en même temps que l'erreur baisse. Du bruit pur
  produirait des signes dispersés.

La résolution n'est pas de choisir la lecture qui arrange. L'hypothèse est enregistrée
au registre (`d609a33dd501`, statut PROPOSED) et sera tranchée **en aveugle** sur les
prévisions forward déjà consignées. C'est exactement ce à quoi sert ce registre.
