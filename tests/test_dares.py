"""The DARES monthly series: parsing, and the integrity rules that guard it.

The failures worth testing here are the silent ones. A mistyped filter modality
returns an empty set rather than an error; a missing month shifts every seasonal lag
by one without any exception being raised. Both are caught at parse time on purpose.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from predlab.data.sources.dares import (
    CADRE_FILTER,
    EXPECTED_HEADER,
    MonthlySeries,
    SeriesIntegrityError,
    SourceFormatError,
    export_url,
    is_rounded_to_hundred,
    month_index,
    next_period,
    parse_rows,
    period_of,
    publication_lag_months,
    quantisation_floor,
    read_csv,
    write_csv,
)

REAL = Path("data/raw/dares/offres_collectees_cadres_france_metro.csv")


def rows(*pairs: tuple[str, int]) -> list[dict[str, object]]:
    return [{"date": p, "nombre_d_offres_d_emploi": v} for p, v in pairs]


def test_month_index_round_trips() -> None:
    for period in ("1996-01", "2020-12", "2026-07"):
        assert period_of(month_index(period)) == period


def test_month_index_is_contiguous_across_a_year_boundary() -> None:
    assert month_index("2021-01") - month_index("2020-12") == 1
    assert next_period("2020-12") == "2021-01"


@pytest.mark.parametrize("bad", ["2020", "2020-13", "2020-00", "not-a-date", "2020-ab"])
def test_malformed_periods_are_refused(bad: str) -> None:
    with pytest.raises(SourceFormatError):
        month_index(bad)


def test_an_empty_result_is_an_error_not_an_empty_series() -> None:
    """The failure mode this guards: a mistyped modality returns [], not an error.

    Without this check the pipeline would carry on with nothing and report it as a
    series with no observations, which looks like missing data rather than a bug.
    """
    with pytest.raises(SourceFormatError, match="no row"):
        parse_rows([])


def test_a_missing_month_is_refused() -> None:
    """A gap shifts every seasonal lag by one, silently. It must not be filled."""
    with pytest.raises(SeriesIntegrityError, match="missing"):
        parse_rows(rows(("2020-01", 100), ("2020-02", 200), ("2020-04", 300)))


def test_a_duplicated_month_is_refused() -> None:
    with pytest.raises(SeriesIntegrityError, match="twice"):
        parse_rows(rows(("2020-01", 100), ("2020-01", 200)))


def test_a_null_value_is_refused() -> None:
    with pytest.raises(SeriesIntegrityError, match="no value"):
        parse_rows([{"date": "2020-01", "nombre_d_offres_d_emploi": None}])


def test_a_negative_count_is_refused() -> None:
    with pytest.raises(SeriesIntegrityError, match="negative"):
        parse_rows(rows(("2020-01", -5)))


def test_rows_are_sorted_regardless_of_input_order() -> None:
    series = parse_rows(rows(("2020-03", 3), ("2020-01", 1), ("2020-02", 2)))
    assert series.periods == ("2020-01", "2020-02", "2020-03")
    assert series.values == (1, 2, 3)


def test_the_export_url_carries_the_cadre_filter() -> None:
    url = export_url()
    assert "Cadres" in url and "exports/json" in url
    assert "order_by=date+asc" in url or "order_by=date%20asc" in url


def test_the_cadre_filter_names_every_dimension_it_must_pin() -> None:
    """Leaving one dimension free would silently sum incomparable slices."""
    for dimension in ("qualification", "type_d_emploi", "type_d_offre_d_emploi"):
        assert dimension in CADRE_FILTER


def test_csv_round_trips(tmp_path: Path) -> None:
    original = parse_rows(rows(("2020-01", 100), ("2020-02", 200)))
    path = write_csv(original, tmp_path / "s.csv")
    assert path.read_text(encoding="utf-8").startswith(",".join(EXPECTED_HEADER))
    assert read_csv(path) == original


def test_a_hand_edited_header_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "s.csv"
    path.write_text("periode,valeur\n2020-01,100\n", encoding="utf-8")
    with pytest.raises(SourceFormatError, match="header"):
        read_csv(path)


def test_mismatched_lengths_are_refused() -> None:
    with pytest.raises(SeriesIntegrityError):
        MonthlySeries(periods=("2020-01",), values=(1, 2))


def test_publication_lag_is_the_gap_a_nowcast_would_fill() -> None:
    series = parse_rows(rows(("2026-06", 1), ("2026-07", 2)))
    assert publication_lag_months(series, date(2026, 9, 20)) == 2


# --------------------------------------------------------------- the real series


@pytest.mark.skipif(not REAL.exists(), reason="stored series not present")
def test_the_stored_series_is_what_the_source_published() -> None:
    """Facts verified against the live API on 2026-09-20, pinned so drift is visible."""
    series = read_csv(REAL)
    assert len(series) == 367
    assert series.start == "1996-01"
    assert series.end == "2026-07"
    assert month_index(series.end) - month_index(series.start) + 1 == len(series)


@pytest.mark.skipif(not REAL.exists(), reason="stored series not present")
def test_the_published_values_are_rounded_to_a_hundred() -> None:
    """This is the accuracy floor, and it belongs in a test rather than a footnote.

    Every published value is a multiple of 100. On this series' own scale that is
    about 0.9% of the mean level, so a forecast error smaller than that is below the
    resolution of the data, not evidence of skill.
    """
    series = read_csv(REAL)
    assert is_rounded_to_hundred(series)
    floor = quantisation_floor(series)
    assert 0.005 < floor < 0.02, floor
