from __future__ import annotations

from pathlib import Path

from predlab.core.dotenv import load_dotenv, parse_dotenv


def test_parses_the_shapes_a_real_env_file_contains() -> None:
    parsed = parse_dotenv(
        "\n".join(
            [
                "# a comment",
                "",
                "PLAIN=value",
                "  SPACED = spaced value  ",
                "export EXPORTED=exported",
                'DOUBLE="double quoted"',
                "SINGLE='single quoted'",
                "EMPTY=",
                "no_equals_sign",
                "=novalue",
            ]
        )
    )
    assert parsed == {
        "PLAIN": "value",
        "SPACED": "spaced value",
        "EXPORTED": "exported",
        "DOUBLE": "double quoted",
        "SINGLE": "single quoted",
        "EMPTY": "",
    }


def test_a_value_containing_equals_is_kept_whole() -> None:
    """Secrets and tokens contain '=' padding more often than not."""
    assert parse_dotenv("TOKEN=abc=def==")["TOKEN"] == "abc=def=="


def test_the_real_environment_wins_over_the_file(tmp_path: Path) -> None:
    """A stale .env must never override what CI or a scheduled task exported."""
    path = tmp_path / ".env"
    path.write_text("A=from_file\nB=from_file\n", encoding="utf-8")
    environ = {"A": "from_environment"}
    applied = load_dotenv(path, environ=environ)
    assert environ["A"] == "from_environment"
    assert environ["B"] == "from_file"
    assert applied == ["B"]


def test_a_missing_file_is_not_an_error(tmp_path: Path) -> None:
    """Everything except the live collector runs with no credentials at all."""
    environ: dict[str, str] = {}
    assert load_dotenv(tmp_path / "absent.env", environ=environ) == []
    assert environ == {}


def test_comments_and_blank_lines_are_ignored() -> None:
    assert parse_dotenv("#x=1\n\n   \n# another\nY=2") == {"Y": "2"}
