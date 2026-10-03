from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path

from predlab.cli import _publish

WHEN = datetime(2026, 9, 29, 23, 30, tzinfo=UTC)


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


def _repo(tmp_path: Path) -> Path:
    remote, repo = tmp_path / "remote.git", tmp_path / "repo"
    subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    _git(repo, "config", "user.email", "t@example.org")
    _git(repo, "config", "user.name", "t")
    (repo / "README").write_text("x")
    _git(repo, "add", "README")
    _git(repo, "commit", "-qm", "init")
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "push", "-q", "-u", "origin", "main")
    return repo


def test_publish_commits_only_our_outputs_and_pushes(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    data = repo / "data"
    (data / "runs" / "r1").mkdir(parents=True)
    (data / "carnet.jsonl").write_text("{}\n")
    (data / "runs" / "r1" / "report.json").write_text("{}")
    (repo / "unrelated.txt").write_text("work in progress")
    _git(repo, "add", "unrelated.txt")  # staged by the user: must not be swept in

    assert _publish(data, WHEN) == "commité et poussé"
    files = _git(repo, "show", "--name-only", "--format=%s", "HEAD").split()
    assert "data/carnet.jsonl" in files and "unrelated.txt" not in files
    assert "Nuit" in _git(repo, "log", "-1", "--format=%s")
    assert _git(repo, "rev-parse", "HEAD") == _git(tmp_path / "remote.git", "rev-parse", "main")
    assert _publish(data, WHEN) == "rien de nouveau"


def test_publish_outside_a_repository_is_harmless(tmp_path: Path) -> None:
    assert _publish(tmp_path, WHEN) in {"pas un dépôt git", "rien à publier"}


def test_daytime_slice_waits_near_an_off_and_never_runs_twice(tmp_path, monkeypatch) -> None:
    import fcntl
    from datetime import timedelta

    from predlab import cli
    from predlab.core.paths import ENV_VAR
    from predlab.racing.sources.pmu.client import FetchResult
    from predlab.racing.store.raw import RawStore

    from .test_carnet import OFF, _programme

    monkeypatch.setenv(ENV_VAR, str(tmp_path / "data"))
    paths = cli.default_paths().ensure()
    store = RawStore(paths.raw_pmu)
    store.record(
        FetchResult("u", 200, _programme(), OFF - timedelta(hours=3)),
        key="programme/2026-09-28",
        endpoint="programme",
        purpose="t",
    )
    calls: list[bool] = []
    monkeypatch.setattr(cli, "_backfill_locked", lambda *a, **k: calls.append(k["blocking"]) or [])
    monkeypatch.setattr(cli, "utcnow", lambda: OFF - timedelta(minutes=20))
    cli._daytime_backfill_slice()
    assert calls == [], "20 min before an off: the T-25 snapshots come first"
    monkeypatch.setattr(cli, "utcnow", lambda: OFF - timedelta(hours=2))
    cli._daytime_backfill_slice()
    assert calls == [False], "far from any off: a non-blocking slice runs"

    monkeypatch.undo()
    monkeypatch.setenv(ENV_VAR, str(tmp_path / "data"))
    with (paths.logs / "backfill.lock").open("a") as held:
        fcntl.flock(held.fileno(), fcntl.LOCK_EX)
        assert cli._backfill_locked(cli.DEFAULT_PLAN, None, 0.01, 1, blocking=False) is None
