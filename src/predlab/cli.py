"""Command line interface.

Deliberately small. Every command either produces a reproducible artefact under the
data directory or prints something a person has to read and judge.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Annotated

import numpy as np
import typer

from predlab import __version__
from predlab.backtest.engine import BacktestConfig, dataset_fingerprint, run_backtest
from predlab.backtest.splits import proportional_split
from predlab.core.dotenv import load_dotenv
from predlab.core.gamespec import REGISTRY, get_spec
from predlab.core.hashing import AppendOnlyLedger, LedgerCorruptionError, sha256_file
from predlab.core.historyview import build_view
from predlab.core.paths import default_paths
from predlab.data.sources import fdj_loto, francetravail
from predlab.data.store import ArchiveManifest, DrawStore, SourceMutationError
from predlab.eval.power import power_report
from predlab.eval.report import build_report, render_markdown
from predlab.models.baselines import FrequencyPredictor, default_baselines
from predlab.models.selection import TopKPolicy
from predlab.registry.hypotheses import Hypothesis, HypothesisRegistry, Origin, Status
from predlab.registry.predictions import HindsightError, PredictionLedger

app = typer.Typer(
    help="Prediction Lab — build and honestly evaluate predictive systems.",
    no_args_is_help=True,
    add_completion=False,
)
data_app = typer.Typer(help="Fetch, inspect and verify draw data.", no_args_is_help=True)
predictions_app = typer.Typer(help="Forward predictions.", no_args_is_help=True)
hypothesis_app = typer.Typer(help="Hypothesis registry.", no_args_is_help=True)
app.add_typer(data_app, name="data")
app.add_typer(predictions_app, name="predictions")
collect_app = typer.Typer(help="Live collection from external APIs.", no_args_is_help=True)
app.add_typer(hypothesis_app, name="hypothesis")
app.add_typer(collect_app, name="collect")

GameOpt = Annotated[str, typer.Option("--game", help="Game name, e.g. loto.")]
EraOpt = Annotated[str | None, typer.Option("--era", help="Rule era; default is the current one.")]


def _fail(message: str) -> None:
    typer.secho(message, fg=typer.colors.RED, err=True)
    raise typer.Exit(code=1)


# --------------------------------------------------------------------------------- data


@data_app.command("fetch")
def data_fetch(
    game: GameOpt = "loto",
    era: EraOpt = None,
    archive: Annotated[
        Path | None,
        typer.Option("--archive", help="Ingest this local ZIP instead of downloading."),
    ] = None,
    allow_mutation: Annotated[
        bool,
        typer.Option("--allow-mutation", help="Accept upstream edits to recorded draws."),
    ] = False,
) -> None:
    """Download (or read) the official archive and merge it into the local store."""
    spec = get_spec(game, era)
    paths = default_paths().ensure()

    if archive is None:
        target = paths.raw / f"{spec.game}_era_{spec.era}.zip"
        typer.echo(f"downloading {fdj_loto.SOURCE_URLS[spec.era]}")
        try:
            archive = fdj_loto.download_archive(spec.era, target)
        except Exception as exc:
            _fail(
                f"download failed: {exc}\n"
                "If this machine has no outbound access to sto.api.fdj.fr, download the "
                "archive elsewhere and pass it with --archive."
            )
            return
    if not archive.exists():
        _fail(f"no such archive: {archive}")
        return

    digest = sha256_file(archive)
    member, raw = fdj_loto.read_archive(archive)
    draws = fdj_loto.parse_csv_bytes(raw, spec)

    provenance = {
        "official_source": fdj_loto.SOURCE_URLS.get(spec.era, str(archive)),
        "source_hash": digest,
        "retrieved_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "parser_version": fdj_loto.PARSER_VERSION,
    }
    store = DrawStore(paths.processed)
    try:
        report = store.ingest(spec, draws, provenance, allow_mutation=allow_mutation)
    except SourceMutationError as exc:
        _fail(str(exc))
        return

    ArchiveManifest(paths.manifest).record(
        url=provenance["official_source"],
        filename=archive.name,
        sha256=digest,
        n_bytes=archive.stat().st_size,
        era=spec.era,
    )
    typer.echo(f"parsed {len(draws)} draws from {member} (sha256 {digest[:16]}…)")
    typer.echo(report.summary())


@data_app.command("status")
def data_status(game: GameOpt = "loto", era: EraOpt = None) -> None:
    """What is in the local store, and how far it reaches."""
    spec = get_spec(game, era)
    store = DrawStore(default_paths().processed)
    if not store.exists(spec):
        typer.echo(f"{spec.key}: no dataset. Run `predlab data fetch --game {spec.game}`.")
        raise typer.Exit(code=1)
    df = store.read(spec)
    dates = df["draw_date"].to_list()
    typer.echo(f"{spec.key}: {len(df)} draws, {dates[0]} → {dates[-1]}")
    typer.echo("  pools: " + ", ".join(f"{p.name} {p.k}/{p.size}" for p in spec.pools))
    typer.echo(f"  parser versions: {sorted(set(df['parser_version'].to_list()))}")
    typer.echo(f"  last retrieved: {max(df['retrieved_at'].to_list())}")


@data_app.command("verify")
def data_verify(game: GameOpt = "loto", era: EraOpt = None) -> None:
    """Re-check the store's internal consistency and the ledgers' hash chains."""
    spec = get_spec(game, era)
    paths = default_paths()
    store = DrawStore(paths.processed)
    problems: list[str] = []

    if store.exists(spec):
        df = store.read(spec)
        dates = df["draw_date"].to_list()
        if len(set(dates)) != len(dates):
            problems.append("duplicate draw dates in the store")
        if dates != sorted(dates):
            problems.append("store is not chronologically ordered")
        bad_days = [d for d in dates if d.isoweekday() not in spec.draw_weekdays]
        if bad_days:
            problems.append(f"{len(bad_days)} draw(s) on non-draw weekdays, e.g. {bad_days[:3]}")
        typer.echo(f"{spec.key}: {len(df)} draws checked")
    else:
        typer.echo(f"{spec.key}: no dataset to check")

    for label, path in (("predictions", paths.predictions), ("hypotheses", paths.hypotheses)):
        if not path.exists():
            typer.echo(f"{label}: empty")
            continue
        try:
            AppendOnlyLedger(path).verify()
            typer.echo(f"{label}: hash chain intact")
        except LedgerCorruptionError as exc:
            problems.append(str(exc))

    if problems:
        for p in problems:
            typer.secho(f"  !! {p}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    typer.secho("all checks passed", fg=typer.colors.GREEN)


# -------------------------------------------------------------------------------- power


@app.command("power")
def power(
    game: GameOpt = "loto",
    era: EraOpt = None,
    draws: Annotated[
        int | None, typer.Option("--draws", help="Override the number of draws.")
    ] = None,
) -> None:
    """How large a bias would have to be before this dataset could reveal it.

    Run this before drawing any conclusion from a backtest.
    """
    spec = get_spec(game, era)
    n = draws
    if n is None:
        store = DrawStore(default_paths().processed)
        if not store.exists(spec):
            _fail(f"no dataset for {spec.key}; pass --draws N to compute a hypothetical.")
            return
        n = len(store.read(spec))
    for floor in power_report(spec, n):
        typer.echo(floor.describe())


# ----------------------------------------------------------------------------- backtest


@app.command("backtest")
def backtest(
    game: GameOpt = "loto",
    era: EraOpt = None,
    min_train: Annotated[int, typer.Option("--min-train")] = 200,
    phase: Annotated[
        str | None, typer.Option("--phase", help="train | validation | test; default all.")
    ] = None,
    resamples: Annotated[int, typer.Option("--resamples")] = 2000,
    permutations: Annotated[int, typer.Option("--permutations")] = 5000,
    simulations: Annotated[int, typer.Option("--simulations")] = 2000,
    seed: Annotated[int, typer.Option("--seed")] = 0,
) -> None:
    """Run every baseline chronologically and write a report."""
    spec = get_spec(game, era)
    paths = default_paths().ensure()
    store = DrawStore(paths.processed)
    if not store.exists(spec):
        _fail(f"no dataset for {spec.key}; run `predlab data fetch --game {spec.game}` first.")
        return

    dates, pools = store.arrays(spec)
    split = proportional_split(dates)
    try:
        result = run_backtest(
            spec,
            dates,
            pools,
            default_baselines(spec, seed=seed),
            TopKPolicy(),
            BacktestConfig(min_train_draws=min_train, seed=seed),
            split=split,
        )
    except ValueError as exc:
        _fail(str(exc))
        return

    report = build_report(
        result,
        pools,
        phase=phase,
        seed=seed,
        n_resamples=resamples,
        n_permutations=permutations,
        n_simulations=simulations,
    )
    run_id = f"{spec.game}_{spec.era}_{datetime.now(UTC):%Y%m%dT%H%M%SZ}"
    run_dir = paths.runs / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown = render_markdown(report)
    (run_dir / "report.md").write_text(markdown, encoding="utf-8")
    (paths.runs / "LATEST").write_text(run_id, encoding="utf-8")

    typer.echo(markdown)
    typer.echo(f"\nwritten to {run_dir}")


@app.command("report")
def report(
    run_id: Annotated[
        str | None, typer.Option("--run-id", help="Defaults to the most recent run.")
    ] = None,
) -> None:
    """Print a stored report."""
    paths = default_paths()
    if run_id is None:
        latest = paths.runs / "LATEST"
        if not latest.exists():
            _fail("no runs yet; run `predlab backtest` first.")
            return
        run_id = latest.read_text(encoding="utf-8").strip()
    path = paths.runs / run_id / "report.md"
    if not path.exists():
        _fail(f"no report at {path}")
        return
    typer.echo(path.read_text(encoding="utf-8"))


# ------------------------------------------------------------------------- predictions


@app.command("predict")
def predict(
    target: Annotated[str, typer.Option("--target", help="Target draw date, YYYY-MM-DD.")],
    game: GameOpt = "loto",
    era: EraOpt = None,
    window: Annotated[
        int | None, typer.Option("--window", help="Rolling window; omit for all history.")
    ] = None,
    seed: Annotated[int, typer.Option("--seed")] = 0,
) -> None:
    """Record an immutable forward prediction for a draw that has not happened yet."""
    spec = get_spec(game, era)
    paths = default_paths().ensure()
    store = DrawStore(paths.processed)
    if not store.exists(spec):
        _fail(f"no dataset for {spec.key}; run `predlab data fetch --game {spec.game}` first.")
        return

    target_date = date.fromisoformat(target)
    dates, pools = store.arrays(spec)
    history = build_view(spec, dates, pools, as_of=target_date)
    model = FrequencyPredictor(spec=spec, window=window)
    forecast = model.forecast(history, target_date)
    policy = TopKPolicy()

    known = frozenset(d.astype("datetime64[D]").astype(date) for d in dates)
    ledger = PredictionLedger(AppendOnlyLedger(paths.predictions))
    try:
        prediction = ledger.record(
            spec,
            forecast,
            policy.ticket(forecast),
            selection_policy=policy.name,
            model_name=model.name,
            model_version=model.version,
            config=model.config(),
            training_cutoff=history.dates.max().astype("datetime64[D]").astype(date)
            if len(history)
            else target_date,
            dataset_fingerprint=dataset_fingerprint(dates, pools),
            seed=seed,
            known_draw_dates=known,
        )
    except (HindsightError, ValueError) as exc:
        _fail(str(exc))
        return

    typer.echo(f"recorded {prediction.prediction_id} for {prediction.target_date}")
    typer.echo(f"  model: {prediction.model_name} v{prediction.model_version}")
    typer.echo(f"  ticket: {prediction.ticket}")
    typer.secho(
        "  commit data/predictions.jsonl now — an external timestamp is what makes "
        "this credible later.",
        fg=typer.colors.YELLOW,
    )


@predictions_app.command("list")
def predictions_list() -> None:
    """Show every recorded forward prediction."""
    ledger = PredictionLedger(AppendOnlyLedger(default_paths().predictions))
    entries = ledger.all()
    if not entries:
        typer.echo("no predictions recorded")
        return
    for p in entries:
        state = "pending" if p.target_date > datetime.now(UTC).date() else "matured"
        typer.echo(
            f"{p.prediction_id[:8]}  {p.target_date}  {p.model_name:<22} {state:<8} {p.ticket}"
        )


@predictions_app.command("score")
def predictions_score(game: GameOpt = "loto", era: EraOpt = None) -> None:
    """Score predictions whose draw has since happened, against the real result."""
    spec = get_spec(game, era)
    paths = default_paths()
    store = DrawStore(paths.processed)
    ledger = PredictionLedger(AppendOnlyLedger(paths.predictions))
    matured = [p for p in ledger.matured() if p.game == spec.game and p.era == spec.era]
    if not matured:
        typer.echo("no matured predictions to score")
        return
    if not store.exists(spec):
        _fail("no dataset to score against")
        return

    df = store.read(spec)
    actual = {
        row[0]: (row[1], row[2])
        for row in zip(
            df["draw_date"].to_list(),
            df["main_numbers"].to_list(),
            df["chance_numbers"].to_list(),
            strict=True,
        )
    }
    for p in matured:
        if p.target_date not in actual:
            typer.echo(f"{p.prediction_id[:8]}  {p.target_date}  draw not in store yet")
            continue
        main, chance = actual[p.target_date]
        hits = len(set(p.ticket["main"]) & set(main))
        probs = np.array(p.inclusion_probabilities["main"])
        mass = float(probs[np.array(main) - spec.pool("main").low].sum())
        baseline = spec.pool("main").k * spec.pool("main").marginal_probability
        typer.echo(
            f"{p.prediction_id[:8]}  {p.target_date}  {p.model_name:<22} "
            f"matches {hits}/5  mass {mass:.4f} (lift {mass / baseline:.3f})  "
            f"chance {'hit' if p.ticket['chance'][0] in chance else 'miss'}"
        )
    typer.secho(
        "One matured prediction is an anecdote. These figures mean nothing until there "
        "are enough of them to test, and the detection floor from `predlab power` says "
        "how many that is.",
        fg=typer.colors.YELLOW,
    )


@predictions_app.command("verify")
def predictions_verify() -> None:
    """Check the prediction ledger's hash chain."""
    try:
        PredictionLedger(AppendOnlyLedger(default_paths().predictions)).verify()
    except LedgerCorruptionError as exc:
        _fail(str(exc))
        return
    typer.secho("prediction ledger intact", fg=typer.colors.GREEN)


# -------------------------------------------------------------------------- hypotheses


@hypothesis_app.command("add")
def hypothesis_add(
    description: Annotated[str, typer.Argument(help="What is being claimed, in one sentence.")],
    origin: Annotated[Origin, typer.Option("--origin")] = Origin.HUMAN,
) -> None:
    registry = HypothesisRegistry(AppendOnlyLedger(default_paths().hypotheses))
    h = registry.add(Hypothesis(description=description, origin=origin))
    typer.echo(f"{h.hypothesis_id}  {h.status}  {h.description}")


@hypothesis_app.command("list")
def hypothesis_list() -> None:
    registry = HypothesisRegistry(AppendOnlyLedger(default_paths().hypotheses))
    entries = registry.current()
    if not entries:
        typer.echo("no hypotheses recorded")
        return
    for h in entries:
        typer.echo(f"{h.hypothesis_id}  {h.status:<13} {h.description}")
        if h.conclusion:
            typer.echo(f"                 -> {h.conclusion}")


@hypothesis_app.command("update")
def hypothesis_update(
    hypothesis_id: str,
    status: Annotated[Status | None, typer.Option("--status")] = None,
    conclusion: Annotated[str | None, typer.Option("--conclusion")] = None,
) -> None:
    registry = HypothesisRegistry(AppendOnlyLedger(default_paths().hypotheses))
    changes = {k: v for k, v in {"status": status, "conclusion": conclusion}.items() if v}
    if not changes:
        _fail("nothing to update")
        return
    h = registry.update(hypothesis_id, **changes)
    typer.echo(f"{h.hypothesis_id}  {h.status}  {h.description}")


# ------------------------------------------------------------------------- collect


@collect_app.command("offers")
def collect_offers(
    months: Annotated[
        int, typer.Option("--months", help="How many closed months back to capture.")
    ] = 6,
    skip_current: Annotated[
        bool,
        typer.Option(
            "--skip-current",
            help="Do not capture the month in progress (its count is partial).",
        ),
    ] = False,
    qualification: Annotated[
        str, typer.Option("--qualification", help="cadre | non-cadre")
    ] = "cadre",
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Check credentials with one call, store nothing."),
    ] = False,
) -> None:
    """Capture how many job offers were created per month, from France Travail.

    Run this on a schedule. The API only exposes offers that are still active, so the
    history cannot be rebuilt later: a month not captured now is captured at a longer
    lag forever after, and lags are not comparable.

    The month in progress is captured too, and marked ``window_complete: false``: its
    count covers only the days already elapsed, so it belongs to a nowcast series, not
    to the monthly one. ``--skip-current`` leaves it out entirely.
    """
    paths = default_paths().ensure()
    # Read .env before looking for credentials. Anything already exported wins.
    load_dotenv()
    try:
        credentials = francetravail.Credentials.from_env()
    except francetravail.MissingCredentialsError as exc:
        _fail(str(exc))
        return

    code = {
        "cadre": francetravail.QUALIFICATION_CADRE,
        "non-cadre": francetravail.QUALIFICATION_NON_CADRE,
    }.get(qualification)
    if code is None:
        _fail("--qualification must be 'cadre' or 'non-cadre'")
        return

    client = francetravail.OffersClient(francetravail.TokenProvider(credentials))
    today = datetime.now(UTC).date()
    windows = []
    year, month = today.year, today.month
    if skip_current:
        year, month = (year - 1, 12) if month == 1 else (year, month - 1)
    for _ in range(1 if dry_run else months + 1):
        windows.append(francetravail.month_window(year, month))
        year, month = (year - 1, 12) if month == 1 else (year, month - 1)

    ledger = AppendOnlyLedger(paths.offers)
    written = 0
    failure: str | None = None
    # A window that fails mid-sweep does not invalidate the ones already captured:
    # each record stands alone. So the loop records what it can, and the failure is
    # reported afterwards -- exit code included -- rather than discarding the rest.
    for start, end in reversed(windows):
        try:
            record = client.count(start, end, qualification=code)
        except francetravail.ApiError as exc:
            failure = str(exc)
            break
        typer.echo(
            f"{record.window_start[:7]}  {record.count:>8,} offres {qualification}"
            f"  ({_describe_window(record)})"
        )
        if not dry_run:
            ledger.append(record.payload())
            written += 1

    if dry_run:
        if failure:
            _fail(failure)
        typer.secho("identifiants valides — rien n'a été enregistré", fg=typer.colors.GREEN)
        return

    if written:
        # The chain is what makes the series tamper-evident. A ledger that no longer
        # verifies must stop the job rather than be published.
        ledger.verify()
        typer.echo(f"\nenregistré dans {paths.offers} ({len(ledger)} mesures au total)")

    if failure:
        _fail(f"{failure}\n{written} mesure(s) tout de même enregistrée(s).")

    # Run unattended, a collector that captures nothing and exits 0 leaves a hole
    # nobody notices until the series is analysed months later. Fail loudly.
    if written == 0:
        _fail("aucune mesure enregistrée — la collecte n'a rien capturé")

    typer.secho(
        "Relancez cette commande régulièrement : la fenêtre d'un mois non capturé "
        "aujourd'hui ne sera plus jamais mesurable au même délai.",
        fg=typer.colors.YELLOW,
    )


@collect_app.command("daily")
def collect_daily(
    lags: Annotated[
        str,
        typer.Option(
            "--lags",
            help="Ages, in days, at which to measure a single past day. E.g. 1,7,30.",
        ),
    ] = "1,7,30",
    qualification: Annotated[
        str, typer.Option("--qualification", help="cadre | non-cadre")
    ] = "cadre",
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Check credentials with one call, store nothing."),
    ] = False,
) -> None:
    """Measure single past days, each at a fixed age. This is the usable series.

    A calendar month measured today is measured at whatever lag the calendar gives it,
    and counts at different lags are not comparable -- the first collection showed six
    months spanning a factor of 86 purely from expiry. Measuring instead *the day that
    is L days old* pins the lag to L by construction, every run, forever.

    Several lags per run are not redundancy. The same calendar day is measured again at
    each larger lag, which traces its own survival curve: the lag-1 series is usable
    immediately, and the later measurements are what will later let a longer-lag series
    be corrected onto the same scale.

    Days, not weeks: a daily series can be aggregated into weeks afterwards, while a
    weekly one can never be taken apart.
    """
    paths = default_paths().ensure()
    load_dotenv()
    try:
        credentials = francetravail.Credentials.from_env()
    except francetravail.MissingCredentialsError as exc:
        _fail(str(exc))
        return

    code = {
        "cadre": francetravail.QUALIFICATION_CADRE,
        "non-cadre": francetravail.QUALIFICATION_NON_CADRE,
    }.get(qualification)
    if code is None:
        _fail("--qualification must be 'cadre' or 'non-cadre'")
        return

    try:
        wanted = sorted({int(part) for part in lags.split(",") if part.strip()})
    except ValueError:
        _fail(f"--lags must be a comma-separated list of whole numbers, got {lags!r}")
        return
    # A lag of 0 would measure today, which is still running: a partial sum, and the
    # one thing this command exists to avoid.
    if not wanted or wanted[0] < 1:
        _fail("--lags must contain only values >= 1 (0 would measure the day in progress)")
        return

    client = francetravail.OffersClient(francetravail.TokenProvider(credentials))
    today = datetime.now(UTC).date()
    ledger = AppendOnlyLedger(paths.offers)
    written = 0
    failure: str | None = None

    for lag in wanted[:1] if dry_run else wanted:
        day = today - timedelta(days=lag)
        start, end = francetravail.day_window(day)
        try:
            record = client.count(start, end, qualification=code)
        except francetravail.ApiError as exc:
            failure = str(exc)
            break
        typer.echo(
            f"{record.window_start}  {record.count:>7,} offres {qualification}"
            f"  (J+{record.lag_days})"
        )
        if not dry_run:
            ledger.append(record.payload())
            written += 1

    if dry_run:
        if failure:
            _fail(failure)
        typer.secho("identifiants valides — rien n'a été enregistré", fg=typer.colors.GREEN)
        return

    if written:
        ledger.verify()
        typer.echo(f"\nenregistré dans {paths.offers} ({len(ledger)} mesures au total)")
    if failure:
        _fail(f"{failure}\n{written} mesure(s) tout de même enregistrée(s).")
    if written == 0:
        _fail("aucune mesure enregistrée — la collecte n'a rien capturé")


@collect_app.command("verify")
def collect_verify() -> None:
    """Check that the offers ledger's hash chain is intact.

    Run before appending, not only after: writing onto a ledger whose chain is
    already broken buries the breakage under a valid-looking tail. An absent ledger
    is not a failure -- it is the state before the first collection.
    """
    paths = default_paths()
    if not paths.offers.exists():
        typer.echo("aucun relevé pour l'instant — rien à vérifier")
        return
    ledger = AppendOnlyLedger(paths.offers)
    try:
        ledger.verify()
    except LedgerCorruptionError as exc:
        _fail(str(exc))
        return
    typer.secho(
        f"chaîne intacte — {len(ledger)} mesures, head {ledger.head_hash()[:12]}",
        fg=typer.colors.GREEN,
    )


def _describe_window(record: francetravail.OfferCount) -> str:
    """How the measurement should be read, in one phrase.

    A closed window is described by its lag, which is what makes two months
    comparable. An open one is described by how much of it has elapsed, because its
    count is a partial sum and no lag makes it comparable to anything.
    """
    if record.window_complete:
        return f"mesuré à J+{record.lag_days}"
    return f"PARTIEL — {record.observed_days}/{record.window_days} j écoulés, mois en cours"


@app.command("version")
def version() -> None:
    typer.echo(f"prediction-lab {__version__}")
    typer.echo("verified game specs: " + ", ".join(sorted(REGISTRY)))


if __name__ == "__main__":
    app()
