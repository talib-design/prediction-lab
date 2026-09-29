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
