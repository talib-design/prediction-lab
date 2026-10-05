from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from predlab.racing import probe
from predlab.racing.sources.pmu.client import PmuClient
from predlab.racing.store.raw import RawStore

NOW = datetime(2026, 10, 5, 9, tzinfo=UTC)


def _db(path: Path) -> Path:
    import duckdb

    con = duckdb.connect(str(path))
    con.execute(
        "CREATE TABLE races (race_id VARCHAR, day DATE, meeting_number INT, race_number INT, "
        "country_code VARCHAR, discipline VARCHAR, venue_name VARCHAR, "
        "off_time TIMESTAMPTZ, is_final BOOLEAN, status VARCHAR)"
    )
    rows = []
    day = date(2025, 3, 1)
    for i in range(30):
        d = day + timedelta(days=i)
        off = datetime(d.year, d.month, d.day, 14, tzinfo=UTC)
        for m, (cc, disc) in enumerate(
            [("GBR", "PLAT"), ("SWE", "ATTELE"), ("FRA", "PLAT"), ("USA", "HAIE")], 1
        ):
            if cc == "SWE" and i >= 3:
                continue  # a small group: it must still be drawn
            rows.append((f"{d}/R{m}C1", d, m, 1, cc, disc, cc, off, True, "FIN_COURSE"))
    rows.append(("2023-06-01/R9C1", date(2023, 6, 1), 9, 1, "GBR", "PLAT", "GBR",
                 datetime(2023, 6, 1, 14, tzinfo=UTC), True, ""))  # fmt: skip
    rows.append(("2025-03-02/R8C1", date(2025, 3, 2), 8, 1, "GBR", "PLAT", "GBR",
                 datetime(2025, 3, 2, 14, tzinfo=UTC), True, "COURSE_ANNULEE"))  # fmt: skip
    con.executemany("INSERT INTO races VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
    con.close()
    return path


def test_the_sample_spreads_over_countries_and_skips_france(tmp_path: Path) -> None:
    db = _db(tmp_path / "r.duckdb")
    first = probe.sample(db, 8)
    assert first == probe.sample(db, 8), "same seed, same races"
    assert {(t.country, t.discipline) for t in first} == {("GBR", "PLAT"), ("SWE", "ATTELE")}
    assert sum(t.country == "SWE" for t in first) == 3, "the small group is drawn in full"
    assert all(t.day >= date(2024, 1, 1) and t.race_id != "2025-03-02/R8C1" for t in first)
    assert probe.sample(db, 8, seed="autre") != first


def _participants(off: datetime) -> bytes:
    ref = int((off - timedelta(minutes=30)).timestamp() * 1000)
    runners = []
    for n, odds in ((1, 2.5), (2, 4.0), (3, 6.0)):
        runners.append(
            {
                "numPmu": n,
                "nom": f"HORSE {n}",
                "statut": "PARTANT",
                "musique": "1p2p" if n < 3 else None,
                "driver": "J. DOE",
                "handicapPoids": 580,
                "placeCorde": n,
                "ordreArrivee": n,
                "dernierRapportReference": {"rapport": odds, "dateRapport": ref},
            }
        )
    runners.append({"numPmu": 4, "nom": "NP", "statut": "NON_PARTANT"})
    return json.dumps({"participants": runners}).encode()


def test_fetch_once_then_report_what_the_feed_gives(tmp_path: Path) -> None:
    db = _db(tmp_path / "r.duckdb")
    targets = [t for t in probe.sample(db, 4) if t.country == "GBR"][:2]
    calls: list[str] = []

    def transport(url: str, timeout: float) -> tuple[int, bytes]:
        calls.append(url)
        if url.endswith("/participants"):
            (t,) = [t for t in targets if t.day.strftime("%d%m%Y") in url]
            return 200, _participants(t.off_time)
        if url.endswith("rapports-definitifs"):
            return 200, json.dumps(
                [
                    {
                        "typePari": "SIMPLE_GAGNANT",
                        "rapports": [{"dividendePourUnEuro": 250, "combinaison": "1"}],
                    }
                ]
            ).encode()
        return 200, json.dumps(
            {"participants": [{"numPmu": 1, "coursesCourues": [{}, {}]}]}
        ).encode()

    store = RawStore(tmp_path / "raw")
    client = PmuClient(transport=transport, sleep=lambda _: None)
    assert probe.fetch(client, store, targets) == 6
    assert probe.fetch(client, store, targets) == 0, "nothing fetched twice"
    rep = probe.report(store, targets, NOW)
    o = rep["overall"]
    assert o["runners"] == 6 and o["parser_ok"] == 1.0
    assert o["fields"]["musique"] == round(4 / 6, 3) and o["fields"]["handicapPoids"] == 1.0
    assert o["odds_reference"] == 1.0 and o["reference_minutes_before_off"] == 30.0
    assert o["overround"] == round(1 / 2.5 + 1 / 4 + 1 / 6, 3)
    assert o["simple_gagnant"] == 1.0 and o["simple_place"] == 0.0
    assert o["past_runs_median"] == 2
    assert set(rep["by_country"]) == {"GBR:PLAT"}
    path = probe.write_report(rep, tmp_path / "lab")
    assert json.loads(path.read_text())["overall"]["races"] == 2
