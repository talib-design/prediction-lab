# Prediction Lab

Laboratoire personnel de prédiction de **courses hippiques** (plat et trot, hippodromes
français), construit pour apprendre à coder des agents et à les faire évoluer — avec
une règle qui ne bouge pas : ne jamais se raconter d'histoires sur la performance.

> Peut-on estimer l'issue d'une course mieux que des baselines simples et que le
> marché, en n'utilisant que l'information réellement disponible avant le départ ?

Ce n'est pas un outil de pari : pas de mise, pas de gestion de bankroll, pas de compte
PMU. Le projet lit des données publiques et mesure des probabilités.

## Où en est-on

Phase 3 — banc de backtest, paris fictifs, tableau de bord v0. Voir [`docs/STATUS.md`](docs/STATUS.md).

## Démarrage

```bash
uv sync
uv run predlab racing collect --dry-run   # ce que le collecteur ferait maintenant
uv run predlab racing collect             # une passe réelle
uv run predlab racing today               # courses du jour et instantanés pris
bash ops/install_dashboard.sh             # tableau de bord permanent : http://127.0.0.1:8790
uv run predlab racing audit               # audit de l'historique (≈ 30-45 min)
bash ops/install_collector.sh             # collecte automatique toutes les 5 min (macOS)
bash ops/install_backfill.sh              # rattrapage de l'historique, une tranche par nuit
uv run predlab racing build               # reconstruit la base data/racing.duckdb
```

Vérifications : `uv run ruff check . && uv run pyright && uv run pytest`.

## Documentation

| Document | Contenu |
|---|---|
| [`docs/STATUS.md`](docs/STATUS.md) | Ce qui marche, ce qui manque, prochaine étape |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Structure, modèle temporel, choix techniques |
| [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) | Règles d'évaluation fixées à l'avance, critère de réussite |
| [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) | Sources vérifiées, règles d'usage, pièges connus |
| [`docs/MIGRATION_HORSE_RACING.md`](docs/MIGRATION_HORSE_RACING.md) | Analyse de migration (2026-09-28) |

L'ancien travail (loterie, emploi cadre) est archivé sous le tag git
`archive/loterie-emploi-2026-09-28`.
