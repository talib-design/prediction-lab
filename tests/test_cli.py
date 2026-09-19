"""End-to-end exercise of the CLI, through a real ZIP and a real store.

These tests go through the same code path an operator does: an official-shaped archive
goes in, a report comes out. Nothing is stubbed except the network.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import date, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from predlab.cli import app

from .fdj_fixture import build_archive, synthetic_archive_rows

runner = CliRunner()


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    monkeypatch.setenv("PREDLAB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.chdir(tmp_path)
    yield tmp_path


@pytest.fixture
def archive(workspace: Path) -> Path:
    return build_archive(workspace / "loto.zip", synthetic_archive_rows(420, seed=0))


def run(*args: str):
    result = runner.invoke(app, list(args))
    if result.exit_code != 0 and result.exception:
        raise AssertionError(f"{args} failed: {result.output}") from result.exception
    return result


def test_version_lists_only_verified_specs(workspace: Path) -> None:
    out = run("version").output
    assert "loto/2019-11" in out
    assert "1976" not in out


def test_fetch_ingests_a_local_archive(workspace: Path, archive: Path) -> None:
    out = run("data", "fetch", "--archive", str(archive)).output
    assert "parsed 420 draws" in out
    assert "420 draws" in out
    assert (Path(workspace / "data" / "raw" / "fdj" / "MANIFEST.json")).exists()


def test_manifest_records_provenance(workspace: Path, archive: Path) -> None:
    run("data", "fetch", "--archive", str(archive))
    entries = json.loads((workspace / "data" / "raw" / "fdj" / "MANIFEST.json").read_text())
    assert entries[0]["sha256"] and entries[0]["era"] == "2019-11"


def test_re_fetching_adds_nothing(workspace: Path, archive: Path) -> None:
    run("data", "fetch", "--archive", str(archive))
    out = run("data", "fetch", "--archive", str(archive)).output
    assert "added 0, unchanged 420" in out


def test_a_retroactively_edited_archive_is_refused(workspace: Path, archive: Path) -> None:
    """The alert that matters: the official source rewrote a draw we already recorded."""
    run("data", "fetch", "--archive", str(archive))
    rows = synthetic_archive_rows(420, seed=0)
    tampered = dict(rows[-1])
    main = sorted({1, 2, 3, 4, 5})
    for i, n in enumerate(main, start=1):
        tampered[f"boule_{i}"] = str(n)
    tampered["combinaison_gagnante_en_ordre_croissant"] = (
        "-".join(map(str, main)) + "+" + tampered["numero_chance"]
    )
    rows[-1] = tampered
    bad = build_archive(workspace / "bad.zip", rows)

    result = runner.invoke(app, ["data", "fetch", "--archive", str(bad)])
    assert result.exit_code == 1
    assert "differ in the official source" in result.output


def test_status_and_verify(workspace: Path, archive: Path) -> None:
    run("data", "fetch", "--archive", str(archive))
    assert "420 draws" in run("data", "status").output
    assert "all checks passed" in run("data", "verify").output


def test_power_reports_the_detection_floor(workspace: Path, archive: Path) -> None:
    run("data", "fetch", "--archive", str(archive))
    out = run("power").output
    assert "must differ from" in out
    assert "Bonferroni" in out


def test_power_works_without_data(workspace: Path) -> None:
    out = run("power", "--draws", "1075").output
    assert "1075 draws" in out


def test_backtest_produces_a_report_with_a_verdict(workspace: Path, archive: Path) -> None:
    run("data", "fetch", "--archive", str(archive))
    out = run(
        "backtest", "--resamples", "150", "--permutations", "150", "--simulations", "80"
    ).output
    assert "What could have been detected" in out
    assert "No statistically meaningful predictive signal was detected." in out

    run_dir = next((workspace / "data" / "runs").glob("loto_2019-11_*"))
    report = json.loads((run_dir / "report.json").read_text())
    assert report["schema"] == "predlab.report.v1"
    assert report["provenance"]["dataset_fingerprint"]
    assert (run_dir / "report.md").exists()


def test_report_replays_the_latest_run(workspace: Path, archive: Path) -> None:
    run("data", "fetch", "--archive", str(archive))
    run("backtest", "--resamples", "150", "--permutations", "150", "--simulations", "80")
    assert "Prediction Lab evaluation report" in run("report").output


def test_backtest_without_data_explains_what_to_do(workspace: Path) -> None:
    result = runner.invoke(app, ["backtest"])
    assert result.exit_code == 1
    assert "predlab data fetch" in result.output


def test_predict_records_a_future_draw(workspace: Path, archive: Path) -> None:
    run("data", "fetch", "--archive", str(archive))
    target = _next_draw_day(date.today() + timedelta(days=1))
    out = run("predict", "--target", target.isoformat()).output
    assert "recorded" in out and target.isoformat() in out

    listing = run("predictions", "list").output
    assert target.isoformat() in listing and "pending" in listing
    assert "intact" in run("predictions", "verify").output


def test_predicting_the_past_is_refused_by_the_cli(workspace: Path, archive: Path) -> None:
    run("data", "fetch", "--archive", str(archive))
    past = _next_draw_day(date.today() - timedelta(days=8))
    result = runner.invoke(app, ["predict", "--target", past.isoformat()])
    assert result.exit_code == 1
    assert "not in the future" in result.output


def test_hypothesis_lifecycle(workspace: Path) -> None:
    out = run("hypothesis", "add", "Hot numbers repeat within 20 draws.").output
    hypothesis_id = out.split()[0]
    assert "PROPOSED" in out

    run(
        "hypothesis",
        "update",
        hypothesis_id,
        "--status",
        "INCONCLUSIVE",
        "--conclusion",
        "Underpowered at this sample size.",
    )
    listing = run("hypothesis", "list").output
    assert "INCONCLUSIVE" in listing
    assert "Underpowered" in listing
    assert listing.count("Hot numbers repeat") == 1, "only the latest revision is listed"


def _next_draw_day(start: date) -> date:
    day = start
    while day.isoweekday() not in (1, 3, 6):
        day += timedelta(days=1)
    return day
