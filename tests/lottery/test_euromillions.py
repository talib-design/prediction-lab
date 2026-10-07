"""Strict EuroMillions reader and store."""

from __future__ import annotations

import zipfile
from datetime import date
from pathlib import Path

import pytest

from predlab.lottery.euromillions import (
    EuroMillionsFormatError,
    EuroMillionsStore,
    parse_archives,
    parse_csv,
    record_manifest,
    verify_era_pools,
)
from predlab.lottery.gamespec import EM_2004_02, EM_2016_09, EM_MAIN_2004
from predlab.lottery.store import SourceMutationError
from tests.lottery.em_fixture import Row, build_csv

TUE_2020 = date(2020, 2, 4)  # Tuesday
FRI_2020 = date(2020, 2, 7)  # Friday
FRI_2005 = date(2005, 1, 7)  # Friday
FRI_2013 = date(2013, 1, 4)  # Friday


def _row(day: date = TUE_2020, **kw: object) -> Row:
    base: dict[str, object] = {"balls": (35, 21, 33, 23, 47), "stars": (6, 7)}
    base.update(kw)
    return Row(day=day, **base)  # type: ignore[arg-type]


def test_modern_layout_keeps_extraction_order_and_sorts_separately() -> None:
    draws, summary, warnings = parse_csv(build_csv([_row()], "modern"), "x.csv")
    d = draws[0]
    assert d.main_order == (35, 21, 33, 23, 47)
    assert d.main_sorted == (21, 23, 33, 35, 47)
    assert d.stars_order == (6, 7)
    assert d.era == "2016-09"
    assert d.weekday == 2
    assert summary["ranks"] == 13
    assert warnings == []


def test_latin1_file_with_mangled_accent_in_header_still_parses() -> None:
    raw = build_csv([_row()], "modern", encoding="latin-1")
    draws, summary, _ = parse_csv(raw, "x.csv")
    assert summary["encoding"] == "latin-1"
    assert len(draws) == 1


def test_two_digit_year_layout() -> None:
    draws, _, _ = parse_csv(build_csv([_row(FRI_2013, stars=(3, 11))], "mid"), "x.csv")
    assert draws[0].draw_date == FRI_2013
    assert draws[0].era == "2011-05"


def test_old_layout_has_twelve_ranks_and_compact_dates() -> None:
    draws, summary, _ = parse_csv(build_csv([_row(FRI_2005, stars=(3, 9))], "old"), "x.csv")
    assert draws[0].era == EM_2004_02.era
    assert summary["ranks"] == 12
    assert draws[0].winners_eu[12 - 1] == 0
    assert draws[0].winners_eu[13 - 1] is None  # rank 13 does not exist in that era


def test_payouts_use_decimal_comma_and_missing_when_nobody_won() -> None:
    row = _row(winners_eu=(0, 1, 0), rapports=("0", "447431,40", "0"))
    draws, _, warnings = parse_csv(build_csv([row], "modern"), "x.csv")
    d = draws[0]
    assert d.rapports[0] is None
    assert d.rapports[1] == pytest.approx(447431.40)
    assert warnings == []


def test_winners_without_payout_is_a_warning_not_an_error() -> None:
    row = _row(winners_eu=(0, 3), rapports=("0", "0"))
    draws, _, warnings = parse_csv(build_csv([row], "modern"), "x.csv")
    assert len(draws) == 1
    assert draws[0].rapports[1] is None
    assert any("rank 2" in w for w in warnings)


@pytest.mark.parametrize(
    ("row", "layout", "fragment"),
    [
        (_row(label="VENDREDI"), "modern", "disagrees with the date"),
        (_row(label="LUNDI"), "modern", "disagrees with the date"),
        (_row(stars=(6, 13)), "modern", "outside"),
        (_row(FRI_2013, stars=(3, 12)), "mid", "outside"),
        (_row(FRI_2005, stars=(3, 10)), "old", "outside"),
        (_row(balls=(1, 1, 2, 3, 4)), "modern", "distinct"),
        (_row(balls=(1, 2, 3, 4, 51)), "modern", "outside"),
        (_row(sorted_balls=(1, 2, 3, 4, 5)), "modern", "sorted-balls"),
        (_row(date(2020, 2, 5)), "modern", "does not draw"),
    ],
)
def test_illegal_rows_are_refused_with_their_line_number(
    row: Row, layout: str, fragment: str
) -> None:
    raw = build_csv([_row(), row], layout)  # type: ignore[arg-type]
    with pytest.raises(EuroMillionsFormatError, match=r"x\.csv:3") as exc:
        parse_csv(raw, "x.csv")
    assert fragment in str(exc.value)


def test_era_rank_count_mismatch_is_refused() -> None:
    # a 2005 draw written in the 13-rank layout cannot be an old-era file
    with pytest.raises(EuroMillionsFormatError, match="prize ranks"):
        parse_csv(build_csv([_row(FRI_2005, stars=(3, 9))], "mid"), "x.csv")


def test_missing_column_is_refused() -> None:
    raw = build_csv([_row()], "modern").replace(b"etoile_2", b"etoile_x")
    with pytest.raises(EuroMillionsFormatError, match="missing column"):
        parse_csv(raw, "x.csv")


def _zip(path: Path, name: str, content: bytes) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(name, content)
    return path


def test_archives_merge_in_date_order_and_report_missing_dates(tmp_path: Path) -> None:
    a = _zip(tmp_path / "b.zip", "b.csv", build_csv([_row(date(2020, 2, 11))], "modern"))
    b = _zip(tmp_path / "a.zip", "a.csv", build_csv([_row(TUE_2020)], "modern"))
    draws, report = parse_archives([a, b])
    assert [d.draw_date for d in draws] == [TUE_2020, date(2020, 2, 11)]
    assert report.missing_dates == [FRI_2020]  # the Friday in between has no row


def test_same_date_in_two_archives_is_refused(tmp_path: Path) -> None:
    a = _zip(tmp_path / "a.zip", "a.csv", build_csv([_row()], "modern"))
    b = _zip(tmp_path / "b.zip", "b.csv", build_csv([_row()], "modern"))
    with pytest.raises(EuroMillionsFormatError, match="appears in"):
        parse_archives([a, b])


def test_verify_era_pools_reports_highest_star() -> None:
    draws, _, _ = parse_csv(build_csv([_row(stars=(6, 12))], "modern"), "x.csv")
    out = verify_era_pools(draws)
    assert out["2016-09"]["max_star"] == 12 == out["2016-09"]["expected_max_star"]


def test_manifest_is_idempotent(tmp_path: Path) -> None:
    z = _zip(tmp_path / "part1.zip", "a.csv", build_csv([_row()], "modern"))
    _, report = parse_archives([z])
    manifest = tmp_path / "m.json"
    assert record_manifest(manifest, report, retrieved_at="t") == 1
    assert record_manifest(manifest, report, retrieved_at="t") == 0
    assert "documentations/" in manifest.read_text()


# -- store -----------------------------------------------------------------------------


def _store(tmp_path: Path) -> EuroMillionsStore:
    return EuroMillionsStore(tmp_path / "em.parquet")


PROV = {"retrieved_at": "2026-10-06T00:00:00+00:00"}


def _draws(*rows: Row) -> list:
    return parse_csv(build_csv(list(rows), "modern"), "x.csv")[0]


def test_store_ingest_is_idempotent(tmp_path: Path) -> None:
    store = _store(tmp_path)
    draws = _draws(_row(), _row(FRI_2020, balls=(1, 2, 3, 4, 5)))
    first = store.ingest(draws, PROV)
    again = store.ingest(draws, PROV)
    assert (first.added, again.added, again.unchanged) == (2, 0, 2)
    assert again.total_after == 2


def test_store_refuses_to_rewrite_a_recorded_draw(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.ingest(_draws(_row()), PROV)
    with pytest.raises(SourceMutationError):
        store.ingest(_draws(_row(balls=(1, 2, 3, 4, 5))), PROV)
    assert store.read()["main_order"][0].to_list() == [35, 21, 33, 23, 47]


def test_store_completes_late_payouts_and_says_so(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.ingest(_draws(_row()), PROV)
    late = _row(winners_eu=(0, 2), rapports=("0", "300000,50"))
    report = store.ingest(_draws(late), PROV)
    assert (report.added, report.payouts_revised) == (0, 1)
    assert store.read()["rapports"][0].to_list()[1] == pytest.approx(300000.5)


def test_arrays_for_an_era_and_for_the_pooled_balls(tmp_path: Path) -> None:
    store = _store(tmp_path)
    rows_old = parse_csv(build_csv([_row(FRI_2005, stars=(3, 9))], "old"), "o.csv")[0]
    store.ingest(rows_old + _draws(_row()), PROV)
    dates, pools = store.arrays(EM_2016_09)
    assert len(dates) == 1
    assert pools["main"].shape == (1, 5)
    assert pools["stars"].shape == (1, 2)
    dates_all, pools_all = store.arrays(EM_MAIN_2004, era_only=False)
    assert len(dates_all) == 2
    assert set(pools_all) == {"main"}
