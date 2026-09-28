from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from predlab.cli import app
from predlab.racing.audit import render_markdown, run_audit, sample_days, write_report
from predlab.racing.store.raw import RawStore

from .conftest import FakeTransport, fixture_bytes, make_client

NOW = datetime(2026, 9, 28, 20, 0, tzinfo=UTC)


def test_sampling_rotates_weekdays() -> None:
    days = sample_days(date(2026, 1, 1), date(2026, 3, 1), 5)
    assert len({d.weekday() for d in days}) == 7
    with pytest.raises(ValueError, match="multiple of 7"):
        sample_days(date(2026, 1, 1), date(2026, 3, 1), 7)


def _transport() -> FakeTransport:
    return FakeTransport(
        {
            "/1/programme/28092026": (200, fixture_bytes("programme_2026-09-28_excerpt.json")),
            "/1/programme/27092026": (200, fixture_bytes("programme_2026-09-27_R1C1_partial.json")),
            "/R1/C1/participants": (
                200,
                fixture_bytes("participants_2026-09-27_R1C1_partial.json"),
            ),
        }
    )


def test_audit_counts_and_measures_odds_timing(tmp_path: Path) -> None:
    transport = _transport()
    store = RawStore(tmp_path)
    result = run_audit(
        make_client(transport, NOW),
        store,
        start=date(2026, 9, 27),
        end=date(2026, 9, 28),
        step=1,
        discipline="ATTELE",
    )
    y = result.to_dict()["years"]["2026"]
    assert y["sampled_days"] == 2
    assert y["estimated_races_by_group"]["FRA/ATTELE"] >= 2
    direct = y["direct_odds_minutes_from_off"]
    assert direct["share_after_off"] == 1.0, "every sampled final quote postdates the off"
    assert y["reference_odds_minutes_from_off"]["median"] < -30
    assert y["runner_field_presence"]["finish_position"] == pytest.approx(0.8)
    assert "Audit des données" in render_markdown(result, NOW)
    md, js = write_report(result, tmp_path / "audit", NOW)
    assert md.exists() and js.exists()


def test_rerunning_the_audit_uses_the_cache(tmp_path: Path) -> None:
    store = RawStore(tmp_path)
    run_audit(
        make_client(_transport(), NOW),
        store,
        start=date(2026, 9, 27),
        end=date(2026, 9, 28),
        step=1,
        discipline="ATTELE",
    )
    again = _transport()
    result = run_audit(
        make_client(again, NOW),
        store,
        start=date(2026, 9, 27),
        end=date(2026, 9, 28),
        step=1,
        discipline="ATTELE",
    )
    assert again.calls == []
    assert result.requests == 0


# ----------------------------------------------------------------------------- cli


@pytest.fixture
def cli_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("PREDLAB_DATA_DIR", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_cli_version_and_dry_run(cli_env: Path) -> None:
    runner = CliRunner()
    assert runner.invoke(app, ["version"]).exit_code == 0
    out = runner.invoke(app, ["racing", "collect", "--dry-run"])
    assert out.exit_code == 0, out.output
    assert "would fetch programme" in out.output


def test_cli_verify_and_today_on_an_empty_store(cli_env: Path) -> None:
    runner = CliRunner()
    assert runner.invoke(app, ["racing", "verify"]).exit_code == 0
    today = runner.invoke(app, ["racing", "today"])
    assert today.exit_code == 1
    assert "Aucun programme" in today.output


def test_cli_hypotheses(cli_env: Path) -> None:
    runner = CliRunner()
    added = runner.invoke(app, ["hypothesis", "add", "Le numéro de corde compte à Chantilly."])
    assert added.exit_code == 0
    listed = runner.invoke(app, ["hypothesis", "list"])
    assert "corde" in listed.output
