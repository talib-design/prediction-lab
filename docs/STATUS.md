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

- **Aucune requête réelle vers le PMU n'a été faite par ce code** : les environnements
  Cowork sont bloqués par la politique réseau. Le parser a été écrit contre des
  extraits verbatim lus le 2026-09-28 (tests/fixtures/pmu/README.md). La première
  passe sur le Mac est le vrai test ; `predlab racing parse-check` le rejoue sur tout.
- Le script `launchd` n'a pas été exécuté sur macOS.
- Le PMU accepte-t-il un `User-Agent` non navigateur ? Inconnu jusqu'à la première
  passe.

## Ce qui manque (phases suivantes)

Stockage normalisé et identité (Phase 2) ; PointInTimeView, baselines, backtest,
puissance (Phase 3) ; courses à venir et registre de prédictions (Phases 4-5) ;
API et front (Phase 6) ; pipeline quotidien complet (Phase 7) ; modèles avancés et
agents (Phase 8).

## Prochaine étape — dans cet ordre

1. **Installer la collecte** (Terminal, dans le dossier du projet) :
   `bash ops/install_collector.sh`. Le script fait une passe de test avant d'installer.
2. **Lancer l'audit** : `uv run predlab racing audit` (2013 → hier, un jour sur 5,
   ≈ 2 000 requêtes, 35-45 min à 1 req/s). Rapport dans `data/audit/`.
3. Relire le rapport ensemble : il tranche la condition sur la discipline, fixe la
   fenêtre de backtest et dit si l'horizon T-30 min est rétro-testable.

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
