from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from predlab.core.gamespec import GameSpec
from predlab.core.historyview import build_view
from predlab.data.sources.fdj_loto import ParsedDraw
from predlab.data.store import DrawStore, SourceMutationError

PROVENANCE = {
    "official_source": "https://example.invalid/archive.zip",
    "source_hash": "deadbeef",
    "retrieved_at": "2026-09-19T00:00:00+00:00",
    "parser_version": "fdj-loto-1",
}


def draw(day: date, main: tuple[int, ...], chance: int) -> ParsedDraw:
    return ParsedDraw(
        draw_key=f"loto/2019-11/{day.isoformat()}",
        draw_date=day,
        weekday=day.isoweekday(),
        main_numbers=main,
        chance_numbers=(chance,),
        source_draw_id="x",
    )


A = draw(date(2020, 1, 4), (1, 2, 3, 4, 5), 1)
B = draw(date(2020, 1, 6), (6, 7, 8, 9, 10), 2)
C = draw(date(2020, 1, 8), (11, 12, 13, 14, 15), 3)


def test_first_ingest_writes_everything(tmp_path: Path, loto: GameSpec) -> None:
    store = DrawStore(tmp_path)
    report = store.ingest(loto, [A, B], PROVENANCE)
    assert (report.added, report.unchanged, report.total_after) == (2, 0, 2)
    assert report.first_date == "2020-01-04"
    assert report.last_date == "2020-01-06"


def test_re_ingesting_the_same_archive_adds_nothing(tmp_path: Path, loto: GameSpec) -> None:
    store = DrawStore(tmp_path)
    store.ingest(loto, [A, B], PROVENANCE)
    report = store.ingest(loto, [A, B], PROVENANCE)
    assert (report.added, report.unchanged, report.total_after) == (0, 2, 2)


def test_new_draws_are_appended(tmp_path: Path, loto: GameSpec) -> None:
    store = DrawStore(tmp_path)
    store.ingest(loto, [A, B], PROVENANCE)
    report = store.ingest(loto, [A, B, C], PROVENANCE)
    assert (report.added, report.unchanged, report.total_after) == (1, 2, 3)


def test_retroactive_change_to_a_recorded_draw_is_refused(tmp_path: Path, loto: GameSpec) -> None:
    """The scenario the store exists to catch: the source rewrote the past."""
    store = DrawStore(tmp_path)
    store.ingest(loto, [A, B], PROVENANCE)
    tampered = draw(date(2020, 1, 4), (1, 2, 3, 4, 49), 1)
    with pytest.raises(SourceMutationError, match="differ in the official source"):
        store.ingest(loto, [tampered, B], PROVENANCE)


def test_mutation_can_be_recorded_deliberately(tmp_path: Path, loto: GameSpec) -> None:
    store = DrawStore(tmp_path)
    store.ingest(loto, [A, B], PROVENANCE)
    tampered = draw(date(2020, 1, 4), (1, 2, 3, 4, 49), 1)
    report = store.ingest(loto, [tampered, B], PROVENANCE, allow_mutation=True)
    assert len(report.mutated) == 1


def test_arrays_round_trip_into_a_history_view(tmp_path: Path, loto: GameSpec) -> None:
    store = DrawStore(tmp_path)
    store.ingest(loto, [A, B, C], PROVENANCE)
    dates, pools = store.arrays(loto)
    view = build_view(loto, dates, pools, as_of=date(2020, 1, 8))
    assert len(view) == 2
    assert view.counts("main").sum() == 10
    assert view.counts("chance").sum() == 2


def test_reading_a_missing_dataset_explains_what_to_run(tmp_path: Path, loto: GameSpec) -> None:
    with pytest.raises(FileNotFoundError, match="predlab data fetch"):
        DrawStore(tmp_path).read(loto)
