"""Builder for CSV bytes that reproduce the real FDJ file's quirks.

Every quirk encoded here was observed in the official 2019-11 era archive on
2026-09-19: Windows-1252, ``;`` separator, a trailing ``;`` on every line (so the
header has an empty 50th column), CRLF line endings, rows in descending date order,
and a ``jour_de_tirage`` column that is sometimes right-padded with spaces.
"""

from __future__ import annotations

from predlab.data.sources.fdj_loto import EXPECTED_HEADER

# Two genuine draws from the official archive, used as realistic anchors.
DRAW_2026_09_16 = {
    "annee_numero_de_tirage": "26111",
    "jour_de_tirage": "MERCREDI",
    "date_de_tirage": "16/09/2026",
    "date_de_forclusion": "16/12/2026",
    "boule_1": "5",
    "boule_2": "49",
    "boule_3": "13",
    "boule_4": "31",
    "boule_5": "1",
    "numero_chance": "10",
    "combinaison_gagnante_en_ordre_croissant": "1-5-13-31-49+10",
}
DRAW_2019_11_06 = {
    "annee_numero_de_tirage": "20199133",
    "jour_de_tirage": "MERCREDI",
    "date_de_tirage": "06/11/2019",
    "date_de_forclusion": "06/01/2020",
    "boule_1": "43",
    "boule_2": "27",
    "boule_3": "23",
    "boule_4": "44",
    "boule_5": "42",
    "numero_chance": "10",
    "combinaison_gagnante_en_ordre_croissant": "23-27-42-43-44+10",
}
# Real row showing the padded-weekday quirk.
DRAW_2026_09_14_PADDED = {
    "annee_numero_de_tirage": "26110",
    "jour_de_tirage": "LUNDI   ",
    "date_de_tirage": "14/09/2026",
    "date_de_forclusion": "14/12/2026",
    "boule_1": "7",
    "boule_2": "12",
    "boule_3": "3",
    "boule_4": "40",
    "boule_5": "21",
    "numero_chance": "4",
    "combinaison_gagnante_en_ordre_croissant": "3-7-12-21-40+4",
}


def build_csv(
    rows: list[dict[str, str]],
    *,
    header: tuple[str, ...] = EXPECTED_HEADER,
    fill: str = "",
) -> bytes:
    """Assemble CSV bytes in the official file's exact shape.

    ``rows`` are given newest-first, as the real file is. Unspecified columns are
    filled with ``fill``, which is what the prize columns look like when unused.
    """
    lines = [";".join(header)]
    for row in rows:
        lines.append(";".join(row.get(col, fill) for col in header))
    return ("\r\n".join(lines) + "\r\n").encode("cp1252")
