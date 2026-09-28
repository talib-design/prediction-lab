"""Command line: ``predlab racing …`` and ``predlab hypothesis …``.

Errors are answered with a sentence, not a stack trace: the collector runs unattended
and its log must be readable by a person.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Annotated

import typer

from predlab import __version__
from predlab.core.clock import PARIS, paris_day, utcnow
from predlab.core.dotenv import load_dotenv
from predlab.core.hashing import AppendOnlyLedger, LedgerCorruptionError
from predlab.core.paths import default_paths
from predlab.racing.audit import run_audit, write_report
from predlab.racing.collect import PROGRAMME, SNAPSHOT, CollectConfig, run_collect
from predlab.racing.sources.pmu.client import Endpoint, PmuClient, capture_key
from predlab.racing.sources.pmu.parser import PmuFormatError, parse_participants, parse_programme
from predlab.racing.store.raw import RawStore
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
    races = [r for r in parse_programme(store.read(caps[-1])) if config.is_target(r)]
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
    ok = bad = 0
    for cap in store.captures():
        if not cap.ok or cap.endpoint not in (Endpoint.PROGRAMME, Endpoint.PARTICIPANTS):
            continue
        try:
            body = store.read(cap)
            if cap.endpoint == Endpoint.PROGRAMME:
                parse_programme(body)
            else:
                parse_participants(body, cap.key)
            ok += 1
        except (PmuFormatError, ValueError) as exc:
            bad += 1
            typer.echo(
                f"  ÉCHEC {cap.key} @ {cap.retrieved_at.isoformat(timespec='seconds')}: {exc}"
            )
    typer.echo(f"{ok} captures parsées, {bad} en échec.")
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
