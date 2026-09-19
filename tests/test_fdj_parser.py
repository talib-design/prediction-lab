from __future__ import annotations

import pytest

from predlab.core.gamespec import GameSpec
from predlab.data.sources.fdj_loto import (
    EXPECTED_HEADER,
    DrawIntegrityError,
    SourceFormatError,
    parse_csv_bytes,
)

from .fdj_fixture import (
    DRAW_2019_11_06,
    DRAW_2026_09_14_PADDED,
    DRAW_2026_09_16,
    build_csv,
)


def test_header_has_the_verified_shape() -> None:
    assert len(EXPECTED_HEADER) == 50
    assert EXPECTED_HEADER[-1] == "", "the real file ends every line with a trailing ';'"


def test_parses_real_rows(loto: GameSpec) -> None:
    raw = build_csv([DRAW_2026_09_16, DRAW_2026_09_14_PADDED, DRAW_2019_11_06])
    draws = parse_csv_bytes(raw, loto)
    assert len(draws) == 3
    first = draws[0]
    assert first.draw_date.isoformat() == "2019-11-06"
    assert first.main_numbers == (23, 27, 42, 43, 44)
    assert first.chance_numbers == (10,)
    assert first.draw_key == "loto/2019-11/2019-11-06"
    assert first.source_draw_id == "20199133"


def test_output_is_sorted_ascending_though_the_source_is_descending(loto: GameSpec) -> None:
    raw = build_csv([DRAW_2026_09_16, DRAW_2026_09_14_PADDED, DRAW_2019_11_06])
    dates = [d.draw_date for d in parse_csv_bytes(raw, loto)]
    assert dates == sorted(dates)


def test_padded_weekday_is_normalised(loto: GameSpec) -> None:
    raw = build_csv([DRAW_2026_09_14_PADDED])
    (draw,) = parse_csv_bytes(raw, loto)
    assert draw.weekday == 1  # LUNDI, despite "LUNDI   " in the file


def test_header_drift_stops_ingestion(loto: GameSpec) -> None:
    drifted = ("un_nouveau_champ", *EXPECTED_HEADER)
    raw = build_csv([DRAW_2026_09_16], header=drifted)
    with pytest.raises(SourceFormatError, match="no longer matches"):
        parse_csv_bytes(raw, loto)


def test_renamed_column_is_reported_by_name(loto: GameSpec) -> None:
    renamed = tuple("numero_chance_v2" if c == "numero_chance" else c for c in EXPECTED_HEADER)
    raw = build_csv([DRAW_2026_09_16], header=renamed)
    with pytest.raises(SourceFormatError, match="numero_chance"):
        parse_csv_bytes(raw, loto)


def test_source_contradicting_itself_is_an_error(loto: GameSpec) -> None:
    """If the balls and the stated sorted combination disagree, refuse the file."""
    row = dict(DRAW_2026_09_16, combinaison_gagnante_en_ordre_croissant="1-5-13-31-48+10")
    with pytest.raises(DrawIntegrityError, match="contradicts itself"):
        parse_csv_bytes(build_csv([row]), loto)


def test_weekday_inconsistent_with_the_calendar_is_an_error(loto: GameSpec) -> None:
    row = dict(DRAW_2026_09_16, jour_de_tirage="LUNDI")
    with pytest.raises(DrawIntegrityError, match="ISO weekday"):
        parse_csv_bytes(build_csv([row]), loto)


def test_draw_on_a_non_draw_day_is_an_error(loto: GameSpec) -> None:
    # 2026-09-15 is a Tuesday: a legal calendar date, but not a Loto draw day.
    row = dict(
        DRAW_2026_09_16,
        jour_de_tirage="MARDI",
        date_de_tirage="15/09/2026",
    )
    with pytest.raises(DrawIntegrityError, match="not a draw day"):
        parse_csv_bytes(build_csv([row]), loto)


def test_out_of_range_ball_is_rejected(loto: GameSpec) -> None:
    row = dict(
        DRAW_2026_09_16, boule_2="50", combinaison_gagnante_en_ordre_croissant="1-5-13-31-50+10"
    )
    with pytest.raises(ValueError, match=r"outside \[1, 49\]"):
        parse_csv_bytes(build_csv([row]), loto)


def test_duplicate_date_is_not_silently_deduplicated(loto: GameSpec) -> None:
    raw = build_csv([DRAW_2026_09_16, dict(DRAW_2026_09_16, annee_numero_de_tirage="26111bis")])
    with pytest.raises(DrawIntegrityError, match="more than one draw"):
        parse_csv_bytes(raw, loto)


def test_draw_before_the_era_is_rejected(loto: GameSpec) -> None:
    row = dict(
        DRAW_2019_11_06,
        date_de_tirage="30/10/2019",
        jour_de_tirage="MERCREDI",
    )
    with pytest.raises(DrawIntegrityError, match="outside era"):
        parse_csv_bytes(build_csv([row]), loto)


def test_blank_trailing_lines_are_tolerated(loto: GameSpec) -> None:
    raw = build_csv([DRAW_2026_09_16]) + b";;;;\r\n\r\n"
    assert len(parse_csv_bytes(raw, loto)) == 1
