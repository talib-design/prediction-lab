# Statut — Phase 1 : migration et socle de données

Dernière mise à jour : 2026-09-28.

## Décisions actées (2026-09-28)

- Domaine unique : **courses hippiques, plat, hippodromes français.** Loterie et
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

Stockage normalisé et identité (Phase 2) ; PointInTimeView, baselines, backtest,
puissance (Phase 3) ; courses à venir et registre de prédictions (Phases 4-5) ;
API et front (Phase 6) ; pipeline quotidien complet (Phase 7) ; modèles avancés et
agents (Phase 8).

## Prochaine étape

Phase 1 terminée (collecte installée le 2026-09-28, audit fait). Phase 2 : ingestion
historique complète du plat français 2015 → aujourd'hui (tous les jours, partants,
performances, rapports), stockage normalisé DuckDB, identité par clé
`NOM-MÈRE-PÈRE`, tolérance par réunion dans le parser.

## Comment lancer

```bash
uv sync
uv run predlab racing collect --dry-run
uv run predlab racing collect
uv run predlab racing today
uv run predlab racing verify
uv run predlab racing parse-check
uv run predlab racing audit --start 2013-01-01
uv run predlab hypothesis list
```

Vérifications : `uv run ruff check . && uv run pyright && uv run pytest`.
