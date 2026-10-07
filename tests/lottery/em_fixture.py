"""Synthetic EuroMillions archives in the three layouts the FDJ actually publishes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

Layout = Literal["modern", "mid", "old"]
_DAY = {2: "MARDI   ", 5: "VENDREDI"}


@dataclass(frozen=True)
class Row:
    day: date
    balls: tuple[int, ...]
    stars: tuple[int, int]
    winners_eu: tuple[int, ...] = ()
    rapports: tuple[str, ...] = ()
    label: str | None = None
    sorted_balls: tuple[int, ...] | None = None


def _date(day: date, layout: Layout) -> str:
    if layout == "old":
        return day.strftime("%Y%m%d")
    if layout == "mid":
        return day.strftime("%d/%m/%y")
    return day.strftime("%d/%m/%Y")


def header(layout: Layout) -> list[str]:
    if layout == "modern":
        cols = ["annee_numero_de_tirage", "jour_de_tirage", "date_de_tirage"]
        cols += ["numéro_de_tirage_dans_le_cycle", "date_de_forclusion"]
        n_ranks, tag = 13, "_Euro_Millions"
    elif layout == "mid":
        cols = ["annee_numero_de_tirage", "jour_de_tirage", "date_de_tirage", "date_de_forclusion"]
        n_ranks, tag = 13, ""
    else:
        cols = ["annee_numero_de_tirage", "jour_de_tirage", "date_de_tirage", "date_de_forclusion"]
        n_ranks, tag = 12, ""
    cols += [f"boule_{i}" for i in range(1, 6)] + ["etoile_1", "etoile_2"]
    cols += ["boules_gagnantes_en_ordre_croissant", "etoiles_gagnantes_en_ordre_croissant"]
    for r in range(1, n_ranks + 1):
        cols += [
            f"nombre_de_gagnant_au_rang{r}{tag}_en_france",
            f"nombre_de_gagnant_au_rang{r}{tag}_en_europe",
            f"rapport_du_rang{r}{tag}",
        ]
    if layout == "modern":
        cols += ["nombre_de_gagnant_au_rang1_Etoile+", "rapport_du_rang1_Etoile+"]
    cols += ["numero_My_Million"]
    if layout != "modern":
        cols += ["devise"]
    return cols


def build_csv(rows: list[Row], layout: Layout, *, encoding: str = "utf-8") -> bytes:
    head = header(layout)
    n_ranks = {"modern": 13, "mid": 13, "old": 12}[layout]
    lines = [";".join(head) + ";"]
    for i, r in enumerate(rows):
        label = r.label or _DAY.get(r.day.isoweekday(), "MERCREDI")
        if layout == "old":
            label = label[:2]
        cells = [f"{r.day.year}{i:03d}", label, _date(r.day, layout)]
        if layout == "modern":
            cells += ["1", "01/01/2099"]
        else:
            cells += ["01/01/2099"]
        cells += [str(b) for b in r.balls] + [str(s) for s in r.stars]
        sb = r.sorted_balls if r.sorted_balls is not None else tuple(sorted(r.balls))
        cells += [
            "-" + "-".join(map(str, sb)) + "-",
            "-" + "-".join(map(str, sorted(r.stars))) + "-",
        ]
        for rank in range(1, n_ranks + 1):
            eu = r.winners_eu[rank - 1] if rank <= len(r.winners_eu) else 0
            rap = r.rapports[rank - 1] if rank <= len(r.rapports) else "0"
            cells += [str(eu), str(eu), rap]
        if layout == "modern":
            cells += ["0", "0"]
        cells += ["AB 123 4567"]
        if layout != "modern":
            cells += ["eur"]
        lines.append(";".join(cells) + ";")
    return ("\n".join(lines) + "\n").encode(encoding)
