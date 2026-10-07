"""``predlab lottery …`` -- EuroMillions only (Loto's archived engine is reused as a library)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer

from predlab.core.hashing import AppendOnlyLedger
from predlab.core.paths import default_paths
from predlab.lottery.analysis import (
    EmData,
    apply_decisions,
    control_chunk,
    judge_control,
    multiplicity_summary,
    popularity_tests,
    run_battery,
)
from predlab.lottery.backtest_em import run_d1, run_d2
from predlab.lottery.euromillions import (
    EuroMillionsFormatError,
    EuroMillionsStore,
    parse_archives,
    provenance_now,
    record_manifest,
    verify_era_pools,
)
from predlab.lottery.forward_em import (
    Carnet,
    fetch_current_archive,
    freeze_next,
    latest_due_draw,
    settle,
    summarise,
)
from predlab.lottery.gamespec import EM_2016_09, EM_MAIN_2004
from predlab.lottery.hypotheses_em import register_all
from predlab.lottery.payouts import RANKS_2016_09, verify_rank_mapping
from predlab.lottery.report_em import render
from predlab.lottery.store import SourceMutationError
from predlab.registry.hypotheses import HypothesisRegistry

lottery_app = typer.Typer(help="EuroMillions : historique, analyses, tests.", no_args_is_help=True)


def _fail(message: str) -> typer.Exit:
    typer.echo(message, err=True)
    return typer.Exit(code=1)


@lottery_app.command("ingest")
def ingest(
    archives: Annotated[
        list[Path] | None,
        typer.Argument(help="ZIP/CSV FDJ ; par défaut tous les .zip de data/raw/euromillions_fdj."),
    ] = None,
) -> None:
    """Lit les archives officielles (lecture stricte) et met à jour le store local."""
    paths = default_paths()
    files = archives or sorted(paths.raw_euromillions.glob("*.zip"))
    if not files:
        raise _fail(f"aucune archive dans {paths.raw_euromillions}")
    try:
        draws, report = parse_archives(files)
    except EuroMillionsFormatError as exc:
        raise _fail(f"archive refusée : {exc}") from exc
    typer.echo(report.summary())
    for era, info in verify_era_pools(draws).items():
        ok = "ok" if info["max_star"] == info["expected_max_star"] else "ÉCART"
        typer.echo(
            f"  époque {era}: {info['draws']} tirages, étoile max {info['max_star']} "
            f"(attendue {info['expected_max_star']}) {ok}, {info['distinct_balls']} boules vues"
        )
    prov = provenance_now()
    try:
        result = EuroMillionsStore(paths.euromillions_store).ingest(draws, prov)
    except SourceMutationError as exc:
        raise _fail(str(exc)) from exc
    new = record_manifest(
        paths.manifests / "euromillions_fdj.json", report, retrieved_at=prov["retrieved_at"]
    )
    typer.echo(result.summary())
    typer.echo(f"manifeste : {new} archive(s) nouvelle(s) enregistrée(s)")


@lottery_app.command("status")
def status() -> None:
    """État du store local."""
    paths = default_paths()
    store = EuroMillionsStore(paths.euromillions_store)
    if not store.exists():
        raise _fail("store absent : lancer `predlab lottery ingest`")
    df = store.read()
    dates = df["draw_date"].to_list()
    typer.echo(f"{len(df)} tirages, {dates[0]} -> {dates[-1]}")
    for era, n in df.group_by("era").len().sort("era").iter_rows():
        typer.echo(f"  {era}: {n}")


@lottery_app.command("register")
def register() -> None:
    """Inscrit au registre (chaîné) les hypothèses EuroMillions, avant toute analyse."""
    registry = HypothesisRegistry(AppendOnlyLedger(default_paths().hypotheses))
    added = register_all(registry)
    registry.verify()
    typer.echo(f"{len(added)} hypothèse(s) ajoutée(s) : {', '.join(added) or '-'}")


def _load_data() -> EmData:
    store = EuroMillionsStore(default_paths().euromillions_store)
    if not store.exists():
        raise _fail("store absent : lancer `predlab lottery ingest`")
    return EmData.from_frame(store.read())


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


@lottery_app.command("control")
def control(
    start: Annotated[int, typer.Option(help="Premier historique (inclus).")] = 0,
    stop: Annotated[int, typer.Option(help="Dernier historique (exclu).")] = 200,
    combine: Annotated[bool, typer.Option(help="Fusionner les morceaux et juger.")] = False,
) -> None:
    """em-R2 : la batterie complète sur des historiques fabriqués 100 % au hasard.

    Se lance par morceaux (--start/--stop), puis --combine applique les critères inscrits.
    """
    # Raw chunks (p-values) are recomputable and bulky: kept in the ignored normalized/ dir.
    parts = default_paths().normalized / "lottery_control_r2_parts"
    if not combine:
        data = _load_data()
        chunk = control_chunk(data, range(start, stop))
        _write_json(parts / f"part_{start:04d}_{stop:04d}.json", chunk)
        typer.echo(f"historiques {start}-{stop - 1} faits")
        return
    chunks = [json.loads(f.read_text()) for f in sorted(parts.glob("part_*.json"))]
    if not chunks:
        raise _fail("aucun morceau : lancer d'abord --start/--stop")
    verdict = judge_control(chunks)
    out = default_paths().lottery / "control_r2.json"
    _write_json(
        out,
        {
            "hypothesis": "em-R2",
            "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
            **verdict.as_dict(),
        },
    )
    typer.echo(f"contrôle négatif : {'RÉUSSI' if verdict.passed else 'ÉCHEC'} -> {out}")
    typer.echo(f"  {verdict.histories} historiques x {verdict.tests_per_history} tests")
    typer.echo(f"  part de p < 0,05 : {verdict.nominal_rate:.3%}")
    for fam, frac in verdict.histories_with_survivor.items():
        typer.echo(f"  {fam}: {frac:.1%} des historiques avec un survivant BH")
    typer.echo(f"  KS famille B : p = {verdict.ks_p_family_b:.3f}")
    for reason in verdict.reasons:
        typer.echo(f"  ! {reason}")


@lottery_app.command("analyze")
def analyze() -> None:
    """Familles A, B, C sur les vrais tirages (hypothèses inscrites avant)."""
    data = _load_data()
    results = run_battery(data)
    d3 = apply_decisions(popularity_tests(data.subset(data.era_mask("2016-09"))))
    summary = multiplicity_summary(results)
    out = default_paths().lottery / "analysis_v1.json"
    _write_json(
        out,
        {
            "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "n_draws": len(data),
            "first_draw": str(data.dates[0]),
            "last_draw": str(data.dates[-1]),
            "summary": summary,
            "results": [r.as_dict() for r in results],
            "d3_popularity": [r.as_dict() for r in d3],
        },
    )
    for fam, info in summary.items():
        typer.echo(
            f"{fam}: {info['tests']} tests, {info['nominal_p_lt_0_05']} à p<0,05 "
            f"(hasard : {info['expected_by_chance']:.1f}), {info['bh_survivors']} après BH"
        )
    for r in d3:
        typer.echo(
            f"D3 {r.label}: {r.observed:+.1%} par boule, p={r.p_value:.2g}, q={r.q_value:.2g}"
        )
    typer.echo(f"-> {out}")


@lottery_app.command("backtest")
def backtest() -> None:
    """D1/D2/R1 : logiques contre hasard, en marche avant, sur l'historique."""
    paths = default_paths()
    store = EuroMillionsStore(paths.euromillions_store)
    if not store.exists():
        raise _fail("store absent : lancer `predlab lottery ingest`")
    data = EmData.from_frame(store.read())
    era = data.subset(data.era_mask("2016-09"))
    mapping_check = verify_rank_mapping(era.winners_eu, RANKS_2016_09, 12)

    dates, pools = store.arrays(EM_MAIN_2004, era_only=False)
    _, balls = run_d1(EM_MAIN_2004, dates, pools)
    typer.echo(f"boules 2004-2026 : {balls['n_targets']} tirages évalués")
    dates_e, pools_e = store.arrays(EM_2016_09)
    result_e, grid = run_d1(EM_2016_09, dates_e, pools_e)
    typer.echo(f"grille ère 2016-09 : {grid['n_targets']} tirages évalués")
    payouts = run_d2(result_e, era.rapports[len(era) - grid["n_targets"] :], "2016-09")

    out = paths.lottery / "backtest_v1.json"
    _write_json(
        out,
        {
            "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "rank_mapping_check": mapping_check,
            "balls_2004": balls,
            "grid_2016_09": grid,
            "payouts_2016_09": payouts,
        },
    )
    for label, block in (("boules 2004-2026", balls), ("grille 2016-09", grid)):
        for pool_name, info in block["pools"].items():
            typer.echo(f"{label} / {pool_name} (hasard : {info['expected_matches']:.3f} trouvés)")
            for lg in info["logics"]:
                typer.echo(
                    f"  {lg['logic']:<24} trouvés {lg['mean_matches']:.3f} (z {lg['matches_z']:+.2f})"
                    f"  log loss vs uniforme {lg['logloss_diff']:+.5f} q={lg['logloss_q']:.3f}"
                )
            w = info["witness_r1"]
            typer.echo(f"  {'témoin R1':<24} trouvés {w['mean_matches']:.3f} (z {w['z']:+.2f})")
    typer.echo(f"-> {out}")


def _carnet() -> Carnet:
    return Carnet(AppendOnlyLedger(default_paths().lottery / "euromillions_carnet.jsonl"))


@lottery_app.command("forward")
def forward(
    network: Annotated[
        bool, typer.Option(help="Télécharger l'archive FDJ si un tirage manque.")
    ] = True,
) -> None:
    """F1/R1 : met à jour les tirages, note les grilles jouées, fige celles du prochain tirage."""
    paths = default_paths()
    now = datetime.now(UTC)
    stamp = now.isoformat(timespec="seconds")
    store = EuroMillionsStore(paths.euromillions_store)
    if not store.exists():
        raise _fail("store absent : lancer `predlab lottery ingest`")
    last = store.read()["draw_date"].to_list()[-1]
    due = latest_due_draw(now)
    if network and last < due:
        try:
            new = fetch_current_archive(paths.raw_euromillions)
        except Exception as exc:  # network or FDJ trouble: log, keep going offline
            typer.echo(f"{stamp} téléchargement FDJ impossible ({type(exc).__name__}: {exc})")
            new = None
        if new is not None:
            try:
                draws, report = parse_archives([new])
                result = store.ingest(draws, provenance_now())
                record_manifest(
                    paths.manifests / "euromillions_fdj.json", report, retrieved_at=stamp
                )
                typer.echo(f"{stamp} {result.summary()}")
            except (EuroMillionsFormatError, SourceMutationError) as exc:
                raise _fail(f"{stamp} archive FDJ refusée : {exc}") from exc
        else:
            typer.echo(
                f"{stamp} archive FDJ inchangée (dernier tirage connu {last}, attendu {due})"
            )
    carnet = _carnet()
    settled = settle(carnet, store, now)
    frozen = freeze_next(carnet, store, now)
    carnet.ledger.verify()
    if settled:
        day = settled[0]["draw_date"]
        typer.echo(f"{stamp} tirage {day} noté pour {len(settled)} grille(s)")
    if frozen:
        typer.echo(
            f"{stamp} {len(frozen)} grilles figées pour le tirage du {frozen[0]['draw_date']}"
        )
    _write_json(
        paths.lottery / "forward_summary.json",
        {"updated_at": stamp, "logics": summarise(carnet)},
    )
    if not settled and not frozen:
        typer.echo(f"{stamp} rien à faire (dernier tirage {last})")


@lottery_app.command("carnet")
def carnet_status() -> None:
    """Résumé du carnet à terme et grilles en attente."""
    carnet = _carnet()
    summary = summarise(carnet)
    if summary:
        typer.echo("logique                   tirages  boules  z      étoiles  gains   ROI")
        for logic, s in summary.items():
            typer.echo(
                f"{logic:<25} {s['draws']:>7}  {s['mean_balls']:.3f}  {s['z_balls']:+.2f}  "
                f"{s['mean_stars']:.3f}    {s['paid_eur']:>6.2f}  {s['roi']:+.0%}"
            )
    settled = carnet.settled()
    pending = [g for g in carnet.grids() if (g["draw_date"], g["logic"]) not in settled]
    for g in pending:
        balls = " ".join(f"{b:02d}" for b in g["balls"])
        stars = " ".join(f"{s:02d}" for s in g["stars"])
        typer.echo(f"en attente {g['draw_date']}  {g['logic']:<24} {balls}  * {stars}")


@lottery_app.command("report")
def report(
    out: Annotated[Path, typer.Option(help="Fichier Markdown à écrire.")] = Path(
        "docs/reports/euromillions.md"
    ),
) -> None:
    """Régénère le rapport EuroMillions depuis les résultats JSON."""
    lot = default_paths().lottery

    def load(name: str) -> dict[str, object] | None:
        path = lot / name
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    analysis = load("analysis_v1.json")
    if analysis is None:
        raise _fail("lancer d'abord `predlab lottery analyze`")
    carnet = _carnet()
    settled = carnet.settled()
    pending = [g for g in carnet.grids() if (g["draw_date"], g["logic"]) not in settled]
    text = render(
        analysis,  # type: ignore[arg-type]
        load("control_r2.json"),  # type: ignore[arg-type]
        load("backtest_v1.json"),  # type: ignore[arg-type]
        load("forward_summary.json"),  # type: ignore[arg-type]
        pending,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    typer.echo(f"rapport -> {out}")
