# Architecture

## Vue d'ensemble (cible)

```
PMU turfinfo ─► collecteur ─► STOCKAGE BRUT (blobs + manifestes chaînés)      ← Phase 1 ✔
                                   │ parser versionné, échec bruyant
                                   ▼
                         STOCKAGE NORMALISÉ (Parquet + DuckDB)                 ← Phase 2 ✔
                                   ▼
                  RaceCard (sans résultat) ─► baselines ─► backtest walk-forward   ← Phase 3 ✔
                                   ▼
                  rapports (data/runs) + paris fictifs réglés aux rapports PMU     ✔
                                   ▼
                        API FastAPI (lecture seule) ─► front React + TS + Vite    ← v0 ✔
                                   ▼
                  registre de prédictions ─► notation en conditions réelles        ← Phases 4-5
                                   ▼
                  agents LLM (analyste, sceptique, qualité des données…)      ← Phase 8
```

## Ce qui existe (Phases 1-3 + tableau de bord v0)

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
    events.py, knowledge.py, models.py, backtest.py, report.py   banc walk-forward
    orders.py, betting.py   modèle d'ordre (Harville), paris fictifs
    carnet.py        carnet en direct : tickets figés avant le départ, réglés au rapport
  api/app.py   API HTTP en lecture seule pour le tableau de bord (voir ci-dessous)
  cli.py       predlab racing {collect,backfill,build,backtest,simulate,…}, predlab dashboard, predlab hypothesis …
web/           front React + TypeScript + Vite ; web/dist (compilé) est commité
ops/           install_{collector,backfill}.sh / uninstall_… (launchd, macOS)
tests/         117 tests, fixtures PMU (voir tests/fixtures/pmu/README.md)
```

## Tableau de bord (v0, 2026-09-28)

`uv run predlab dashboard` sert, sur `127.0.0.1:8765` uniquement, l'API et le front
compilé. Le front ne lit aucun fichier : il appelle l'API, qui a trois sources, chacune
pour ce qu'elle fait bien :

| Endpoint | Source | Pourquoi |
|---|---|---|
| `GET /api/races?day=` | brut (dernier programme capturé) | toujours à jour, sans attendre la reconstruction nocturne |
| `GET /api/races/{jour}/{RxCy}` | brut (partants, toutes les cotes, rapports) + DuckDB (historique antérieur au jour) + dernier rapport de backtest (α) | la course telle qu'on la voit maintenant, et ce qu'on savait avant |
| `GET /api/horses/{id}` | DuckDB | carrière |
| `GET /api/reports`, `/api/reports/{id}` | `data/runs/*/report.json` | backtests et simulations |
| `GET /api/status` | manifestes, checkpoints, journaux, DuckDB | santé de la collecte |
| `GET /api/carnet` | `data/carnet.jsonl` (vérifié à chaque lecture) | carnet en direct |
| `GET /api/hypotheses` | registre | recherche |

Documentation interactive : `/api/docs`. Aucune route n'écrit.

Langage visuel : chaque chiffre porte son **statut épistémique** — fait observé,
feature, association, prévision, information de marché — et la couleur ne code jamais
« gagnant / perdant ». Pas de bibliothèque de graphiques : SVG écrits à la main
(évolution de la probabilité implicite, diagramme de fiabilité, intervalles). Pas de
Tailwind : jetons CSS dans `web/src/styles/app.css`, clair d'abord, sombre en miroir.

Développer le front : `cd web && npm install && npm run dev` (proxy vers l'API
lancée par `predlab dashboard`), puis `npm run build` pour régénérer `web/dist`.

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
| FastAPI + uvicorn | API typée, doc générée ; servie en local seulement |
| `web/dist` commité | Chris n'a pas besoin de Node pour ouvrir le tableau de bord |

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
