"""Command line: ``predlab racing …`` and ``predlab hypothesis …``.

Errors are answered with a sentence, not a stack trace: the collector runs unattended
and its log must be readable by a person.
"""

from __future__ import annotations

import json
import socket
from datetime import date, timedelta
from typing import Annotated

import typer

from predlab import __version__
from predlab.core.clock import PARIS, paris_day, utcnow
from predlab.core.dotenv import load_dotenv
from predlab.core.hashing import AppendOnlyLedger, LedgerCorruptionError
from predlab.core.paths import default_paths
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
from predlab.racing.collect import PROGRAMME, SNAPSHOT, CollectConfig, run_collect
from predlab.racing.events import load_events
from predlab.racing.models import CalibratedMarketModel, MarketModel, default_models
from predlab.racing.report import build_report, compare
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
    if report.failed and report.failed == report.fetched:
        raise typer.Exit(code=1)


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
        typer.Option(help="Disciplines et premier jour, par priorité : PLAT:2015-01-01,ATTELE:…"),
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
    paths = default_paths().ensure()
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
        progress=typer.echo,
    )
    for discipline, report in reports:
        line = f"{discipline} — {report.summary()}"
        typer.echo(line)
        _log_line(f"{started.isoformat(timespec='seconds')} | {line}")
    if then_build:
        build_db()


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
    settled = sum(1 for e in result.scored_events if e.card.race_id in dividends)
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
        sock = bind_loopback(port)
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
