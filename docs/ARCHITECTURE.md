# Architecture

## Vue d'ensemble (cible)

```
PMU turfinfo ─► collecteur ─► STOCKAGE BRUT (blobs + manifestes chaînés)      ← Phase 1 ✔
                                   │ parser versionné, échec bruyant
                                   ▼
                         STOCKAGE NORMALISÉ (Parquet + DuckDB)                 ← Phase 2 ✔
                                   ▼
                  PointInTimeView ─► features ─► modèles (champion / challengers) ← Phase 3+
                                   ▼
                  registre de prédictions ─► notation ─► rapports
                                   ▼
                        API FastAPI ─► front React + TS + Vite                ← Phases 5-6
                                   ▼
                  agents LLM (analyste, sceptique, qualité des données…)      ← Phase 8
```

## Ce qui existe (Phases 1-2)

```
src/predlab/
  core/        hashing (registre append-only chaîné), clock (UTC/Paris), probability
               (normalisation, probabilités implicites), dotenv, paths
  registry/    hypotheses              ← repris tel quel de la phase loterie
  backtest/    splits                  ← repris tel quel
  eval/        uncertainty             ← repris tel quel (bootstrap par blocs, FDR)
  racing/
    domain.py        Race, Runner, OddsQuote, GoingMeasure, WeatherForecast
    sources/pmu/     client (HTTP poli, retries), parser (strict/lenient)
    store/raw.py     stockage brut adressé par contenu + manifestes par jour
    store/normalized.py  tables typées reconstruites depuis le brut (Parquet + DuckDB)
    collect.py       collecteur en direct + politique d'instantanés
    backfill.py      rattrapage historique borné et reprenable
    audit.py         audit volume / complétude / horodatage des cotes
  cli.py       predlab racing {collect,audit,today,verify,parse-check}, predlab hypothesis …
ops/           install_{collector,backfill}.sh / uninstall_… (launchd, macOS)
tests/         77+ tests, fixtures PMU (voir tests/fixtures/pmu/README.md)
```

## Quatre décisions structurantes

### 1. Le brut d'abord, le parsing ensuite

Le flux n'est pas documenté et le parser changera ; un instantané de cotes manqué ne se
rattrape jamais. Le collecteur stocke donc les octets exacts et un enregistrement de
manifeste (clé, URL, `retrieved_at`, statut HTTP, sha256, objectif), **y compris les
échecs**. Le parsing est une fonction pure rejouable sur tout l'historique
(`predlab racing parse-check`).

Manifestes : un fichier JSONL chaîné par hash et par jour UTC, pour que la
vérification reste rapide avec des centaines de captures par jour. Blobs : gzip,
adressés par sha256, stockés une fois.

### 2. Le temps est une donnée de premier rang

Tous les instants sont UTC et porteurs de fuseau (`core/clock.py`). `retrieved_at` d'une
capture est le `known_at` de tout ce qui en est tiré. C'est ce qui permettra, en
Phase 3, de reconstruire exactement ce qu'on savait à T-30 min, T-10 min, etc.

### 3. La politique de collecte est une fonction pure

`plan_race_tasks(now, races, index, config)` décide quoi récupérer ; elle ne fait pas
d'I/O et les tests fixent son comportement (fenêtres, intervalles, priorités, résultat
officiel, historique). Le collecteur ne fait qu'exécuter le plan, les tâches les plus
urgentes d'abord, dans une limite de requêtes par passe.

### 4. Le domaine ne connaît pas le PMU

`racing/domain.py` ne mentionne aucune source. Une seconde source = un second parser.

## Choix techniques

| Choix | Raison |
|---|---|
| `urllib` (stdlib) plutôt que `httpx` | quatre GET JSON ; zéro dépendance ajoutée |
| Parquet + DuckDB | ~50 000 courses, ~550 000 partants, jointures temporelles constantes : le seuil où une base analytique se justifie. Parquet écrit par polars (pas de pyarrow), DuckDB le lit |
| `launchd` plutôt que tâches planifiées Cowork | Cowork n'atteint pas le PMU ; `launchd` tourne toutes les 5 min sur le Mac |
| pydantic pour le domaine | déjà utilisé ; validation et sérialisation gratuites |

## Les agents, plus tard — et pourquoi l'ordre compte

Objectif du projet : apprendre à coder des agents et à les rendre évolutifs. Les agents
arrivent en Phase 8, sur un pipeline qui marche, et **ne remplacent jamais le calcul** :
ils lisent des rapports et des registres, proposent, critiquent. « Évolutif » veut dire
ici : la mémoire est le registre d'hypothèses, l'apprentissage est le cycle
champion / challengers, et chaque agent a un rôle étroit et testable (analyste de
course, sceptique, statisticien, qualité des données, mémoire de recherche).

## Frontières de sécurité

- Aucun identifiant n'est nécessaire ; `.env` reste ignoré par git.
- Aucune donnée brute ne quitte le Mac : ni commit, ni envoi à un LLM.
- Aucune fonction de pari, de mise ou de connexion à un compte.
