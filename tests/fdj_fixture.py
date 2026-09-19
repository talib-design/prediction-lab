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


ISO_TO_FRENCH = {
    1: "LUNDI",
    2: "MARDI",
    3: "MERCREDI",
    4: "JEUDI",
    5: "VENDREDI",
    6: "SAMEDI",
    7: "DIMANCHE",
}


def synthetic_archive_rows(
    n: int, seed: int = 0, start: str = "2019-11-06"
) -> list[dict[str, str]]:
    """``n`` internally consistent rows on real Loto draw days, newest first.

    Built to pass every integrity check the parser applies, so that tests exercise the
    real pipeline rather than a relaxed version of it.
    """
    import datetime as _dt
    import random as _random

    rng = _random.Random(seed)
    day = _dt.date.fromisoformat(start)
    rows: list[dict[str, str]] = []
    index = 0
    while len(rows) < n:
        if day.isoweekday() in (1, 3, 6):
            main = sorted(rng.sample(range(1, 50), 5))
            chance = rng.randint(1, 10)
            rows.append(
                {
                    "annee_numero_de_tirage": f"{day.year}{index:04d}",
                    "jour_de_tirage": ISO_TO_FRENCH[day.isoweekday()]
                    + ("   " if index % 3 == 0 else ""),
                    "date_de_tirage": day.strftime("%d/%m/%Y"),
                    "date_de_forclusion": (day + _dt.timedelta(days=60)).strftime("%d/%m/%Y"),
                    "boule_1": str(main[2]),
                    "boule_2": str(main[0]),
                    "boule_3": str(main[4]),
                    "boule_4": str(main[1]),
                    "boule_5": str(main[3]),
                    "numero_chance": str(chance),
                    "combinaison_gagnante_en_ordre_croissant": "-".join(map(str, main))
                    + f"+{chance}",
                    "devise": "eur",
                }
            )
            index += 1
        day += _dt.timedelta(days=1)
    return list(reversed(rows))


def build_archive(path, rows: list[dict[str, str]], member: str = "loto_201911.csv"):
    """Write ``rows`` into a ZIP shaped like the official archive."""
    import zipfile

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(member, build_csv(rows))
    return path
