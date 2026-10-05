"""Command line: ``predlab racing …`` and ``predlab hypothesis …``.

Errors are answered with a sentence, not a stack trace: the collector runs unattended
and its log must be readable by a person.
"""

from __future__ import annotations

import json
import os
import socket
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from predlab import __version__
from predlab.core.clock import PARIS, paris_day, utcnow
from predlab.core.dotenv import load_dotenv
from predlab.core.hashing import AppendOnlyLedger, LedgerCorruptionError
from predlab.core.paths import default_paths
from predlab.racing import strategies as banc_lib
from predlab.racing.audit import run_audit, write_report
from predlab.racing.backfill import DEFAULT_PLAN, parse_plan, run_backfill_plan
from predlab.racing.backtest import DEFAULT_HORIZON_MINUTES, PREREGISTERED_SPLIT, run_backtest
from predlab.racing.betting import (
    build_simulation_report,
    exotic_strategies,
    load_dividends,
    render_simulation_markdown,
    simple_strategies,
    simulate,
)
from predlab.racing.carnet import CarnetReport, entries, run_carnet, summarise_entries
from predlab.racing.collect import PROGRAMME, SNAPSHOT, CollectConfig, run_collect
from predlab.racing.events import load_events
from predlab.racing.features import load_finished
from predlab.racing.marketplus import load_dividends as load_simple_dividends
from predlab.racing.marketplus import model_for_paths, write_model
from predlab.racing.marketplus import run as run_marketplus
from predlab.racing.models import CalibratedMarketModel, MarketModel, default_models
from predlab.racing.profile import build_profile, write_profile
from predlab.racing.report import build_report, compare, latest_alpha
from predlab.racing.report import write_report as write_backtest_report
from predlab.racing.sources.pmu.client import Endpoint, PmuClient, capture_key
from predlab.racing.sources.pmu.parser import (
    PmuFormatError,
    parse_participants,
    parse_programme_detailed,
)
from predlab.racing.store.normalized import build
from predlab.racing.store.raw import RawStore
from predlab.racing.synthetic import JitteredMarketModel, OracleModel, make_world
from predlab.registry.hypotheses import Hypothesis, HypothesisRegistry, Origin, Status

app = typer.Typer(
    help="Prediction Lab — prédiction de courses hippiques, évaluée honnêtement.",
    no_args_is_help=True,
)
racing_app = typer.Typer(help="Collecte et audit des données de courses.", no_args_is_help=True)
hypothesis_app = typer.Typer(help="Registre d'hypothèses.", no_args_is_help=True)
app.add_typer(racing_app, name="racing")
app.add_typer(hypothesis_app, name="hypothesis")


@app.callback()
def _main() -> None:
    load_dotenv()


def _store() -> RawStore:
    return RawStore(default_paths().ensure().raw_pmu)


def _log_line(text: str) -> None:
    log = default_paths().ensure().logs / "collect.log"
    with log.open("a", encoding="utf-8") as fh:
        fh.write(text + "\n")


# ---------------------------------------------------------------------------- racing


@racing_app.command("collect")
def collect(
    dry_run: Annotated[
        bool, typer.Option(help="Show what would be fetched, fetch nothing.")
    ] = False,
    max_requests: Annotated[int, typer.Option(help="Cap on requests for this run.")] = 60,
) -> None:
    """One collection pass: programmes, odds snapshots, results. Meant to run every 5 min."""
    report = run_collect(
        PmuClient(),
        _store(),
        now=utcnow(),
        config=CollectConfig(max_requests=max_requests),
        dry_run=dry_run,
        log=None if dry_run else _log_line,
    )
    typer.echo(report.summary())
    for day, state in report.programmes.items():
        typer.echo(f"  programme {day}: {state}")
    if not dry_run:
        # The carnet rides on the collector: same schedule, freshest captures. A failure
        # here must never stop the collection itself.
        try:
            _run_carnet_pass()
        except Exception as exc:
            _log_line(f"{utcnow().isoformat(timespec='seconds')} | carnet ERREUR {exc!r}")
        try:
            _run_banc_pass()
        except Exception as exc:
            _log_line(f"{utcnow().isoformat(timespec='seconds')} | banc ERREUR {exc!r}")
        try:
            _daytime_backfill_slice()
        except Exception as exc:
            _log_line(
                f"{utcnow().isoformat(timespec='seconds')} | rattrapage de jour ERREUR {exc!r}"
            )
    if report.failed and report.failed == report.fetched:
        raise typer.Exit(code=1)


def _run_carnet_pass() -> CarnetReport:
    paths = default_paths().ensure()
    rep = run_carnet(
        RawStore(paths.raw_pmu),
        AppendOnlyLedger(paths.carnet),
        now=utcnow(),
        alpha_for=lambda d: latest_alpha(paths.runs, d),
        model_for=model_for_paths(paths.runs, paths.database),
    )
    if rep.frozen or rep.settled or rep.errors:
        _log_line(f"{utcnow().isoformat(timespec='seconds')} | {rep.summary()}")
    return rep


def _run_banc_pass() -> banc_lib.BancReport | None:
    paths = default_paths().ensure()
    panel = banc_lib.Panel.load(paths.banc / "panel.json")
    if not panel.strategies:
        return None
    rep = banc_lib.run_banc(
        RawStore(paths.raw_pmu),
        AppendOnlyLedger(paths.banc / "ledger.jsonl"),
        panel,
        now=utcnow(),
        frame_for=banc_lib.frame_for_paths(paths.runs, paths.database),
    )
    if rep.frozen or rep.settled or rep.errors:
        _log_line(f"{utcnow().isoformat(timespec='seconds')} | {rep.summary()}")
    return rep


@racing_app.command("banc")
def banc(
    discipline: Annotated[str, typer.Option(help="PLAT, ATTELE ou MONTE.")] = "PLAT",
) -> None:
    """Strategy bench: explore combinations on 2024, confirm the newcomers once on
    2025-2026, add them to the bench that plays every coming race (fictitious, 1 EUR)."""
    paths = default_paths().ensure()
    if not paths.database.exists():
        typer.echo("Base absente : lancez d'abord `predlab racing build`.")
        raise typer.Exit(code=1)
    from predlab.racing.champion import EXTENDED, Champion, history_ready

    champ = Champion.load(paths.lab, discipline)
    frame = banc_lib.build_frame(
        paths.database, paths.runs, discipline, features=champ.features, tau=champ.tau
    )
    if history_ready(paths.database, discipline):
        # The historical curve covers the extended history; the bench keeps its 2024 window.
        _write_replay(
            banc_lib.build_frame(
                paths.database,
                paths.runs,
                discipline,
                since=EXTENDED.since,
                features=champ.features,
                tau=champ.tau,
            ),
            discipline,
            paths.runs,
        )
    else:
        _write_replay(frame, discipline, paths.runs)
    explored = frame.filter(pl.col("day") <= banc_lib.EXPLORATION_END)
    if explored["race_id"].n_unique() < NIGHTLY_MIN_RACES:
        typer.echo(f"Trop peu de courses d'exploration ({discipline}) : banc non mis à jour.")
        return
    panel = banc_lib.Panel.load(paths.banc / "panel.json")
    now = utcnow()
    added = banc_lib.update_panel(panel, frame, discipline, now)
    live, _ = banc_lib.live_stats(AppendOnlyLedger(paths.banc / "ledger.jsonl"))
    gone = banc_lib.apply_eliminations(panel, live, now)
    panel.save()
    gauge = panel.gauge.get(discipline, {})
    typer.echo(
        f"Banc {discipline} : {len(added)} nouvelle(s) stratégie(s) ; "
        f"découvertes 2024 confirmées sur 2025-2026 : {gauge.get('confirmed', 0)}"
        f"/{gauge.get('tested', 0)} ; {len(gone)} éliminée(s) ; "
        f"{len(panel.active(discipline))} en jeu."
    )


@racing_app.command("lab")
def lab(
    discipline: Annotated[str, typer.Option(help="PLAT, ATTELE ou MONTE.")] = "PLAT",
    max_tests: Annotated[int, typer.Option(help="Tests lancés au plus par passage.")] = 3,
) -> None:
    """The lab: pre-register the catalogue's new criteria, run the tests whose data is
    ready (each once, by the rule fixed beforehand), refresh the favourites study."""
    from predlab.racing import lab as lab_lib

    paths = default_paths().ensure()
    if not paths.database.exists():
        typer.echo("Base absente : lancez d'abord `predlab racing build`.")
        raise typer.Exit(code=1)
    reg = HypothesisRegistry(AppendOnlyLedger(paths.hypotheses))
    frame = load_finished(paths.database, discipline)
    added = lab_lib.register(reg, discipline)
    if added:
        typer.echo(
            f"Labo {discipline} : {len(added)} critère(s) pré-enregistré(s) : {', '.join(added)}"
        )
    rep = lab_lib.study_favourites(
        reg,
        banc_lib.with_returns(frame, banc_lib.load_simple_dividends(paths.database)),
        paths.lab,
        discipline,
    )
    top = rep["bands"][0]
    if top["races"]:
        typer.echo(
            f"Labo {discipline} : favoris < 1,5 → {top['races']} courses, gagnent "
            f"{top['win_rate']:.0%}, retour gagnant {top['roi_sg']:+.1%}."
        )
    lines = lab_lib.run_pending(
        reg, frame, paths.database, paths.lab, discipline, max_tests=max_tests
    )
    lines += _arena_pass(reg, paths, discipline, max_tests)
    for line in lines:
        typer.echo(f"Labo {line}")
        _log_line(f"{utcnow().isoformat(timespec='seconds')} | labo {line}")


def _arena_pass(reg: HypothesisRegistry, paths: Any, discipline: str, max_tests: int) -> list[str]:
    """Objective "beat the favourite": register, test against the champion, try the vault,
    promote (then refit the model at once, the replaced version's parameters frozen)."""
    from predlab.racing import arena
    from predlab.racing import lab as lab_lib
    from predlab.racing.champion import EXTENDED, Champion, history_ready
    from predlab.racing.marketplus import latest_params

    added = arena.register(reg, discipline, paths.lab)
    lines = (
        [f"{len(added)} candidat(s) pré-enregistré(s) pour l'objectif : {', '.join(added)}"]
        if added
        else []
    )
    ready = history_ready(paths.database, discipline)
    frame = None
    if ready:
        frame = banc_lib.with_returns(
            lab_lib.add_candidates(
                load_finished(paths.database, discipline, since=EXTENDED.since), discipline
            ),
            banc_lib.load_simple_dividends(paths.database),
        )
    out, promotion = arena.run(
        reg, frame, paths.lab, discipline, EXTENDED, ready=ready, max_tests=max_tests
    )
    lines += out
    if promotion is not None:
        champ = Champion.load(paths.lab, discipline)
        new = champ.promote(
            features=tuple(promotion["features"]),
            tau=float(promotion["tau"]),
            origin=promotion["origin"],
            evidence=promotion["evidence"],
            now=utcnow(),
            params_before=latest_params(paths.runs, discipline),
        )
        champ.save()
        lines.append(f"Marché+ v{new['version']} en service : {promotion['origin']}")
        model(discipline=discipline)
    return lines


def _write_replay(frame: pl.DataFrame, discipline: str, runs: Path) -> None:
    """Historical curve, favourite vs model, from the frame the bench already built."""
    from predlab.racing import replay as replay_lib

    rep = replay_lib.build_report(frame, discipline)
    s = rep["summary"]
    if not s.get("races"):
        typer.echo(f"Courbe historique {discipline} : pas encore de modèle walk-forward.")
        return
    replay_lib.write_report(rep, runs)
    typer.echo(
        f"Courbe historique {discipline} : {s['races']} courses depuis le {s['first_day']}, "
        f"le modèle quitte le favori sur {s['differ_share']:.0%} d'entre elles."
    )


@racing_app.command("replay")
def replay(
    discipline: Annotated[str, typer.Option(help="PLAT, ATTELE ou MONTE.")] = "PLAT",
) -> None:
    """Historical curve: favourite vs Marché+ pick on every past race (reconstruction)."""
    paths = default_paths().ensure()
    if not paths.database.exists():
        typer.echo("Base absente : lancez d'abord `predlab racing build`.")
        raise typer.Exit(code=1)
    from predlab.racing.champion import EXTENDED, Champion, history_ready

    champ = Champion.load(paths.lab, discipline)
    since = EXTENDED.since if history_ready(paths.database, discipline) else None
    _write_replay(
        banc_lib.build_frame(
            paths.database,
            paths.runs,
            discipline,
            since=since,
            features=champ.features,
            tau=champ.tau,
        ),
        discipline,
        paths.runs,
    )


@racing_app.command("carnet")
def carnet(
    verify: Annotated[
        bool, typer.Option(help="Vérifier la chaîne de hash, sans rien écrire.")
    ] = False,
) -> None:
    """Carnet de paris fictifs en direct : fige les tickets avant le départ, règle au rapport.

    Tourne déjà tout seul avec le collecteur ; cette commande fait une passe à la main
    et affiche le bilan.
    """
    paths = default_paths().ensure()
    ledger = AppendOnlyLedger(paths.carnet)
    try:
        ledger.verify()
    except LedgerCorruptionError as exc:
        typer.echo(f"CARNET ALTÉRÉ : {exc}")
        raise typer.Exit(code=1) from exc
    if not verify:
        typer.echo(_run_carnet_pass().summary())
    items = entries(ledger)
    typer.echo(
        f"{len(items)} courses au carnet, {sum(e['settled'] for e in items)} réglées ; "
        f"chaîne intacte ({len(ledger)} enregistrements)."
    )
    for row in summarise_entries(items):
        if row.get("races"):
            typer.echo(
                f"  {row['label']:<28} {row['races']:>4} courses  ROI {row['roi'] * 100:+6.1f} %"
                f"  ({row['pending']} en attente)"
            )


@racing_app.command("audit")
def audit(
    start: Annotated[str, typer.Option(help="Premier jour, AAAA-MM-JJ.")] = "2013-01-01",
    end: Annotated[str | None, typer.Option(help="Dernier jour (défaut : hier).")] = None,
    step: Annotated[int, typer.Option(help="Un jour sur N (pas un multiple de 7).")] = 5,
    runners_per_day: Annotated[
        int, typer.Option(help="Courses dont on lit les partants, par jour.")
    ] = 1,
) -> None:
    """Measure volume, field completeness and odds timing for French flat racing."""
    first = date.fromisoformat(start)
    last = date.fromisoformat(end) if end else paris_day(utcnow()) - timedelta(days=1)
    paths = default_paths().ensure()
    result = run_audit(
        PmuClient(),
        RawStore(paths.raw_pmu),
        start=first,
        end=last,
        step=step,
        runners_per_day=runners_per_day,
        progress=typer.echo,
    )
    md, _ = write_report(result, paths.audit, utcnow())
    typer.echo(f"{result.requests} requêtes, {len(result.failures)} échecs. Rapport : {md}")


@racing_app.command("backfill")
def backfill(
    plan: Annotated[
        str,
        typer.Option(help="Disciplines et premier jour, par priorité : PLAT:2024-01-01,ATTELE:…"),
    ] = DEFAULT_PLAN,
    end: Annotated[
        str | None, typer.Option(help="Jour le plus récent (défaut : avant-hier).")
    ] = None,
    hours: Annotated[float, typer.Option(help="Durée maximale de ce passage.")] = 5.0,
    max_requests: Annotated[
        int, typer.Option(help="Plafond de requêtes pour ce passage.")
    ] = 20_000,
    then_build: Annotated[
        bool, typer.Option("--build", help="Reconstruire la base après.")
    ] = False,
) -> None:
    """Fetch past French races, discipline by discipline, newest first, resumable."""
    reports = _backfill_locked(plan, end, hours, max_requests, blocking=True)
    for discipline, report in reports or []:
        typer.echo(f"{discipline} — {report.summary()}")
    if then_build:
        build_db()


def _backfill_locked(
    plan: str, end: str | None, hours: float, max_requests: int, *, blocking: bool, log: bool = True
) -> list[tuple[str, Any]] | None:
    """One backfill pass under a lock shared by the nightly run and the daytime slices,
    so two passes never fetch the same days. None when ``blocking`` is False and another
    pass holds the lock."""
    import fcntl

    paths = default_paths().ensure()
    lock = (paths.logs / "backfill.lock").open("a")
    try:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
        except BlockingIOError:
            return None
        started = utcnow()
        last = date.fromisoformat(end) if end else paris_day(started) - timedelta(days=2)
        reports = run_backfill_plan(
            PmuClient(),
            RawStore(paths.raw_pmu),
            plan=parse_plan(plan),
            end=last,
            now=utcnow,
            max_requests=max_requests,
            deadline=started + timedelta(hours=hours),
            progress=typer.echo if log else None,
        )
        if log:
            for discipline, report in reports:
                _log_line(
                    f"{started.isoformat(timespec='seconds')} | {discipline} — {report.summary()}"
                )
        return reports
    finally:
        lock.close()


SLICE_SECONDS = 90
SLICE_REQUESTS = 120
SLICE_QUIET_MINUTES = (5, 35)  # no slice from 35 min before an off to 5 min after it


def _daytime_backfill_slice() -> None:
    """While the Mac is awake, a short backfill slice after each collection pass -- the
    nightly run alone loses its hours whenever the Mac sleeps at night. Skipped near a
    race's freeze window, so the T-25 snapshots are never delayed; logged only when it
    completes days."""
    from predlab.racing.carnet import _is_target, _programme

    paths = default_paths().ensure()
    store = RawStore(paths.raw_pmu)
    now = utcnow()
    before, after = SLICE_QUIET_MINUTES
    for race in _programme(store, store.index(), paris_day(now)):
        if _is_target(race) and (
            race.off_time - timedelta(minutes=after)
            <= now
            <= race.off_time + timedelta(minutes=before)
        ):
            return
    reports = _backfill_locked(
        DEFAULT_PLAN, None, SLICE_SECONDS / 3600, SLICE_REQUESTS, blocking=False, log=False
    )
    done = [(d, r) for d, r in reports or [] if r.days_completed]
    if done:
        stamp = now.isoformat(timespec="seconds")
        _log_line(
            f"{stamp} | rattrapage de jour : "
            + ", ".join(
                f"{d} {r.days_completed} j. (jusqu'au {r.oldest_day_reached})" for d, r in done
            )
        )


NIGHTLY_MIN_RACES = 300  # below this, a backtest says nothing: skip the discipline


@racing_app.command("nightly")
def nightly(
    hours: Annotated[float, typer.Option(help="Durée maximale du rattrapage.")] = 5.0,
    publish: Annotated[
        bool, typer.Option("--publish/--no-publish", help="Commiter et pousser carnet et rapports.")
    ] = True,
) -> None:
    """La passe de nuit, sans personne : rattrapage, base, puis par discipline profil des
    vainqueurs, modèle Marché+, backtests et paris fictifs ; enfin carnet et rapports
    datés dans git. Lancée chaque nuit par launchd."""
    started = utcnow()
    stamp = started.isoformat(timespec="seconds")
    backfill(plan=DEFAULT_PLAN, end=None, hours=hours, max_requests=20_000, then_build=True)
    paths = default_paths().ensure()
    for discipline in ("PLAT", "ATTELE", "MONTE"):
        events = load_events(
            paths.database, horizon_minutes=DEFAULT_HORIZON_MINUTES, discipline=discipline
        )
        usable = sum(1 for e in events if e.card.market_complete)
        if usable < NIGHTLY_MIN_RACES:
            _log_line(
                f"{stamp} | nuit {discipline} : {usable} courses exploitables, analyse reportée"
            )
            continue
        # Profile and Marché+ first: minutes, and the morning's carnet uses the model.
        try:
            profile(discipline=discipline)
            model(discipline=discipline)
            banc(discipline=discipline)
            _log_line(f"{stamp} | nuit {discipline} : profil, Marché+ et banc d'essai mis à jour")
        except Exception as exc:
            _log_line(f"{stamp} | nuit {discipline} profil/modèle ERREUR {exc!r}")
        try:
            lab(discipline=discipline)
        except Exception as exc:
            _log_line(f"{stamp} | nuit {discipline} labo ERREUR {exc!r}")
        try:
            backtest(horizon=DEFAULT_HORIZON_MINUTES, discipline=discipline)
            simulate_bets(horizon=DEFAULT_HORIZON_MINUTES, discipline=discipline)
            _log_line(
                f"{stamp} | nuit {discipline} : backtest et paris fictifs sur {usable} courses"
            )
        except Exception as exc:
            _log_line(f"{stamp} | nuit {discipline} ERREUR {exc!r}")
    if publish:
        _log_line(f"{stamp} | nuit git : {_publish(paths.root, started)}")


def _publish(data_dir: Path, when: datetime) -> str:
    """Commit the carnet and the reports (our own outputs, never PMU data) and push.

    The commit's date on GitHub is the outside anchor that makes "written before the
    race" checkable. Best effort: a failure is logged, never raised.
    """
    import subprocess

    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}

    def git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args], cwd=data_dir, env=env, capture_output=True, text=True, timeout=120
        )

    top = git("rev-parse", "--show-toplevel")
    if top.returncode != 0:
        return "pas un dépôt git"
    targets = [
        str(p)
        for p in (
            data_dir / "carnet.jsonl",
            data_dir / "runs",
            data_dir / "banc",
            data_dir / "lab",
            data_dir / "hypotheses.jsonl",
        )
        if p.exists()
    ]
    if not targets:
        return "rien à publier"
    git("add", "--", *targets)
    if git("diff", "--cached", "--quiet", "--", *targets).returncode == 0:
        return "rien de nouveau"
    msg = f"Nuit du {paris_day(when).isoformat()} : carnet et rapports"
    commit = git("commit", "-m", msg, "--", *targets)
    if commit.returncode != 0:
        return f"commit refusé : {commit.stderr.strip()[:200]}"
    push = git("push")
    return (
        "commité et poussé"
        if push.returncode == 0
        else f"commité, push refusé : {push.stderr.strip()[:200]}"
    )


@racing_app.command("build")
def build_db() -> None:
    """Rebuild the normalized tables and the DuckDB database from the raw store."""
    paths = default_paths().ensure()
    report = build(RawStore(paths.raw_pmu), paths.normalized, paths.database)
    typer.echo(f"Base reconstruite ({paths.database}) : {report.summary()}")
    for error in report.errors[:10]:
        typer.echo(f"  {error}")


@racing_app.command("backtest")
def backtest(
    horizon: Annotated[
        float, typer.Option(help="Minutes avant le départ.")
    ] = DEFAULT_HORIZON_MINUTES,
    discipline: Annotated[str, typer.Option(help="PLAT, ATTELE ou MONTE.")] = "PLAT",
) -> None:
    """Walk-forward backtest of the baselines on the normalized database."""
    paths = default_paths().ensure()
    if not paths.database.exists():
        typer.echo("Base absente : lancez d'abord `predlab racing build`.")
        raise typer.Exit(code=1)
    events = load_events(paths.database, horizon_minutes=horizon, discipline=discipline)
    typer.echo(f"{len(events)} courses chargées ({discipline}), évaluation en cours…")
    models = default_models()
    result = run_backtest(events, models, horizon_minutes=horizon, split=PREREGISTERED_SPLIT)
    calibrated = next(m for m in models if isinstance(m, CalibratedMarketModel))
    report = build_report(
        result,
        {
            "alpha": calibrated.alpha,
            "alpha_refits": len(calibrated.history),
            "discipline": discipline,
        },
    )
    md, _ = write_backtest_report(report, paths.runs)
    typer.echo(f"{result.n_eligible} courses évaluées. Rapport : {md}")


@racing_app.command("simulate")
def simulate_bets(
    horizon: Annotated[
        float, typer.Option(help="Minutes avant le départ.")
    ] = DEFAULT_HORIZON_MINUTES,
    discipline: Annotated[str, typer.Option(help="PLAT, ATTELE ou MONTE.")] = "PLAT",
) -> None:
    """Fictitious bets (simple, tiercé, quinté) settled against official dividends."""
    paths = default_paths().ensure()
    if not paths.database.exists():
        typer.echo("Base absente : lancez d'abord `predlab racing build`.")
        raise typer.Exit(code=1)
    events = load_events(paths.database, horizon_minutes=horizon, discipline=discipline)
    dividends = load_dividends(paths.database)
    result = run_backtest(
        events,
        default_models(),
        horizon_minutes=horizon,
        split=PREREGISTERED_SPLIT,
        keep_forecasts=True,
    )
    chosen = ["market_calibrated", "horse_win_rate", "form"]
    strategies = {**simple_strategies(chosen), **exotic_strategies(chosen)}
    ledgers = simulate(result, dividends, strategies)
    settled = sum(
        1 for e in result.scored_events if e.card.race_id in dividends and e.card.market_coherent
    )
    stamp = utcnow().isoformat(timespec="seconds")
    report = build_simulation_report(
        result, ledgers, n_races_with_dividends=settled, generated_at=stamp, discipline=discipline
    )
    out = (
        paths.runs
        / f"simulation_{discipline}_T{horizon:g}_{stamp.replace(':', '').replace('-', '')[:15]}Z"
    )
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_text(render_simulation_markdown(report), encoding="utf-8")
    (out / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    typer.echo(
        f"{settled} courses réglées avec les rapports officiels. Rapport : {out / 'report.md'}"
    )


PROFILE_MIN_RACES = 100  # below this, every level is "too little data"


@racing_app.command("profile")
def profile(
    discipline: Annotated[str, typer.Option(help="PLAT, ATTELE ou MONTE.")] = "PLAT",
) -> None:
    """Winners' profile: how each condition bears on the odds and on the result."""
    paths = default_paths().ensure()
    if not paths.database.exists():
        typer.echo("Base absente : lancez d'abord `predlab racing build`.")
        raise typer.Exit(code=1)
    frame = load_finished(paths.database, discipline)
    races = frame["race_id"].n_unique() if frame.height else 0
    if races < PROFILE_MIN_RACES:
        typer.echo(f"{races} courses exploitables ({discipline}) : trop peu pour un profil.")
        return
    out = write_profile(build_profile(frame, discipline), paths.runs)
    typer.echo(f"Profil sur {frame['race_id'].n_unique()} courses. Rapport : {out / 'report.md'}")


@racing_app.command("model")
def model(
    discipline: Annotated[str, typer.Option(help="PLAT, ATTELE ou MONTE.")] = "PLAT",
) -> None:
    """Fit Marché+ by the pre-registered procedure (train, validation, test) and save
    the parameters the carnet uses."""
    paths = default_paths().ensure()
    if not paths.database.exists():
        typer.echo("Base absente : lancez d'abord `predlab racing build`.")
        raise typer.Exit(code=1)
    from predlab.backtest.splits import TimeSplit
    from predlab.racing import lab as lab_lib
    from predlab.racing.champion import EXTENDED, Champion, history_ready

    champ = Champion.load(paths.lab, discipline)
    if history_ready(paths.database, discipline):
        # Extended history in place (decision of 2026-10-05): train 2020-2023, λ on 2024.
        since = EXTENDED.since
        split = TimeSplit(
            train_end=EXTENDED.train_end,
            validation_end=EXTENDED.validation_end,
            test_end=PREREGISTERED_SPLIT.test_end,
        )
    else:
        since, split = None, PREREGISTERED_SPLIT
    frame = lab_lib.add_candidates(
        load_finished(paths.database, discipline, **({"since": since} if since else {})),
        discipline,
    )
    rep = run_marketplus(
        frame,
        discipline,
        split,
        load_simple_dividends(paths.database),
        features=champ.features,
        tau=champ.tau,
        champion_version=champ.current["version"],
    )
    if rep is None:
        typer.echo(f"Pas assez de courses d'apprentissage ({discipline}) : modèle non ajusté.")
        return
    out = write_model(rep, paths.runs)
    t = rep["test"]
    verdict = t.get("verdict", "test vide")
    typer.echo(
        f"Marché+ {discipline} : test sur {t['races']} courses → {verdict}. Rapport : {out / 'report.md'}"
    )


@racing_app.command("synthetic-check")
def synthetic_check(races: int = 10_000, seed: int = 0) -> None:
    """Level 1: does the bench find a real edge, fix a planted bias, refuse a fake edge?"""
    world = make_world(races, seed=seed)
    models = [
        MarketModel(),
        CalibratedMarketModel(),
        OracleModel(world.truth),
        JitteredMarketModel(),
    ]
    result = run_backtest(world.events, models, horizon_minutes=DEFAULT_HORIZON_MINUTES)
    rows = {r["model"]: r for r in compare(result, "all")}
    checks = [
        (
            "un vrai avantage est trouvé (oracle)",
            rows["oracle"]["verdict"] == "meilleur que la référence",
        ),
        (
            "un biais planté est corrigé (marché brut)",
            rows["market"]["verdict"] == "moins bon que la référence",
        ),
        (
            "un faux avantage est refusé (marché bruité)",
            rows["market_jittered"]["verdict"] != "meilleur que la référence",
        ),
    ]
    for label, ok in checks:
        typer.echo(f"  {'OK ' if ok else 'ÉCHEC'}  {label}")
    if not all(ok for _, ok in checks):
        raise typer.Exit(code=1)


@racing_app.command("today")
def today() -> None:
    """Today's target races from the latest stored programme, with snapshot counts."""
    store = _store()
    now = utcnow()
    day = paris_day(now)
    index = store.index([day - timedelta(days=1), day, day + timedelta(days=1)])
    caps = [
        c
        for c in index.get(capture_key(Endpoint.PROGRAMME, day), [])
        if c.ok and c.purpose == PROGRAMME
    ]
    if not caps:
        typer.echo("Aucun programme stocké pour aujourd'hui. Lancez `predlab racing collect`.")
        raise typer.Exit(code=1)
    config = CollectConfig()
    races = [r for r in parse_programme_detailed(store.read(caps[-1])).races if config.is_target(r)]
    typer.echo(f"{day} — {len(races)} course(s) cible(s)")
    for r in sorted(races, key=lambda r: r.off_time):
        key = capture_key(Endpoint.PARTICIPANTS, r.day, r.meeting_number, r.race_number)
        n = sum(1 for c in index.get(key, []) if c.ok and c.purpose == SNAPSHOT)
        off = r.off_time.astimezone(PARIS).strftime("%H:%M")
        typer.echo(
            f"  {off}  R{r.meeting_number}C{r.race_number:<2} {r.venue_name:<14} "
            f"{r.distance_m or '?':>5} m  {r.status or '?':<28} instantanés: {n}"
        )


@racing_app.command("verify")
def verify() -> None:
    """Check every manifest hash chain."""
    try:
        n = _store().verify()
    except LedgerCorruptionError as exc:
        typer.echo(f"Manifeste corrompu : {exc}")
        raise typer.Exit(code=1) from exc
    typer.echo(f"{n} enregistrements vérifiés, chaînes intactes.")


@racing_app.command("parse-check")
def parse_check() -> None:
    """Re-parse every stored programme and runners capture with the current parser."""
    store = _store()
    ok = bad = partial = 0
    for cap in store.captures():
        if not cap.ok or cap.endpoint not in (Endpoint.PROGRAMME, Endpoint.PARTICIPANTS):
            continue
        try:
            body = store.read(cap)
            if cap.endpoint == Endpoint.PROGRAMME:
                errors = parse_programme_detailed(body).errors
                if errors:
                    partial += 1
                    typer.echo(f"  PARTIEL {cap.key}: {errors[0]}")
            else:
                parse_participants(body, cap.key)
            ok += 1
        except (PmuFormatError, ValueError) as exc:
            bad += 1
            typer.echo(
                f"  ÉCHEC {cap.key} @ {cap.retrieved_at.isoformat(timespec='seconds')}: {exc}"
            )
    typer.echo(f"{ok} captures parsées (dont {partial} partielles), {bad} en échec.")
    if bad:
        raise typer.Exit(code=1)


# ------------------------------------------------------------------------ hypotheses


def _registry() -> HypothesisRegistry:
    return HypothesisRegistry(AppendOnlyLedger(default_paths().ensure().hypotheses))


@hypothesis_app.command("add")
def hypothesis_add(
    description: str,
    origin: Annotated[Origin, typer.Option()] = Origin.HUMAN,
) -> None:
    h = _registry().add(Hypothesis(description=description, origin=origin))
    typer.echo(h.hypothesis_id)


@hypothesis_app.command("list")
def hypothesis_list() -> None:
    for h in _registry().current():
        typer.echo(f"{h.hypothesis_id}  r{h.revision}  {h.status:<12}  {h.description}")


@hypothesis_app.command("update")
def hypothesis_update(
    hypothesis_id: str,
    status: Annotated[Status | None, typer.Option()] = None,
    conclusion: Annotated[str | None, typer.Option()] = None,
) -> None:
    changes: dict[str, object] = {}
    if status is not None:
        changes["status"] = status
    if conclusion is not None:
        changes["conclusion"] = conclusion
    h = _registry().update(hypothesis_id, **changes)
    typer.echo(f"{h.hypothesis_id} -> r{h.revision} {h.status}")


@app.command("version")
def version() -> None:
    typer.echo(__version__)


def bind_loopback(first_port: int, tries: int = 20) -> socket.socket:
    """A socket bound on 127.0.0.1 at the first free port from ``first_port``.

    Binding before announcing the URL means the browser can only ever open *this*
    server -- never another local app that already holds the port.
    """
    for port in range(first_port, first_port + tries):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            sock.close()
            continue
        return sock
    raise OSError(f"aucun port libre entre {first_port} et {first_port + tries - 1}")


@app.command("dashboard")
def dashboard(
    port: int = typer.Option(8765, help="Premier port essayé (le suivant libre sinon)."),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Ouvrir le navigateur."),
    strict_port: bool = typer.Option(
        False, "--strict-port", help="Échouer si le port est pris (mode service : adresse fixe)."
    ),
) -> None:
    """Tableau de bord en lecture seule sur http://127.0.0.1:PORT (Ctrl+C pour arrêter)."""
    import threading
    import webbrowser

    import uvicorn

    from predlab.api.app import WEB_DIST, create_app

    if not WEB_DIST.exists():
        typer.echo(f"Interface absente ({WEB_DIST}) : seule l'API est servie, doc sur /api/docs.")
    # Loopback only: the dashboard is personal and must never be exposed on the network.
    try:
        sock = bind_loopback(port, tries=1 if strict_port else 20)
    except OSError as exc:
        typer.echo(f"Impossible de démarrer : {exc}. Essayez --port 9100.")
        raise typer.Exit(code=1) from exc
    actual = sock.getsockname()[1]
    if actual != port:
        typer.echo(f"Port {port} déjà pris par une autre application : j'utilise {actual}.")
    url = f"http://127.0.0.1:{actual}/"
    typer.echo(f"Tableau de bord Prediction Lab : {url}  (Ctrl+C pour arrêter)")
    if open_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    server = uvicorn.Server(uvicorn.Config(create_app(default_paths()), log_level="warning"))
    server.run(sockets=[sock])
