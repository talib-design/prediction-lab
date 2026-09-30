"""A small racing database whose truth is known, built with the real table schemas.

Horses have a latent ability and, for some, a liking for heavy ground that the market
does not see. The market quotes a blurred version of ability only. Each finishing
order is drawn from the true strengths (Plackett-Luce).
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import numpy as np
import polars as pl

from predlab.racing.store.normalized import ODDS_SCHEMA, RACE_SCHEMA, RUNNER_SCHEMA

GOINGS = [("Bon", 3.1), ("Souple", 3.6), ("Lourd", 4.8), ("PSF STANDARD", None)]


def make_db(
    path: Path,
    *,
    days: int = 120,
    races_per_day: int = 6,
    field: int = 10,
    horses: int = 300,
    mudder_boost: float = 1.2,
    start: date = date(2024, 1, 2),
    seed: int = 7,
) -> Path:
    import duckdb

    rng = np.random.default_rng(seed)
    ability = rng.normal(0, 1, horses)
    mudder = rng.random(horses) < 0.3
    races, runners, odds = [], [], []
    for d in range(days):
        day = start + timedelta(days=d)
        for k in range(races_per_day):
            race_id = f"{day.isoformat()}/R1C{k + 1}"
            off = datetime(day.year, day.month, day.day, 12 + k, 0, tzinfo=UTC)
            label, value = GOINGS[rng.integers(len(GOINGS))]
            heavy = label == "Lourd"
            ids = rng.choice(horses, field, replace=False)
            strength = ability[ids] + (mudder_boost * mudder[ids] if heavy else 0.0)
            # Plackett-Luce finishing order from the true strengths.
            w = np.exp(strength)
            order: list[int] = []
            alive = list(range(field))
            while alive:
                p = w[alive] / w[alive].sum()
                pick = alive[int(rng.choice(len(alive), p=p))]
                order.append(pick)
                alive.remove(pick)
            market = np.exp(ability[ids] + rng.normal(0, 0.3, field))
            market /= market.sum()
            quoted = np.round(1.0 / (market * 1.19), 1).clip(1.1, None)
            races.append(
                {
                    "race_id": race_id,
                    "day": day,
                    "meeting_number": 1,
                    "race_number": k + 1,
                    "off_time": off,
                    "country_code": "FRA",
                    "venue_code": "XXX",
                    "venue_name": "Nulle-Part",
                    "discipline": "PLAT",
                    "distance_m": [1200, 1600, 2000, 2400][k % 4],
                    "going_label": label,
                    "going_value": value,
                    "temperature_c": float(rng.integers(0, 30)),
                    "wind_force": float(rng.integers(0, 40)),
                    "sky": ["Soleil", "Couvert", "Pluie faible"][k % 3],
                    "is_final": True,
                    "has_quinte": False,
                    "declared_runners": field,
                }
            )
            for i, h in enumerate(ids):
                number = i + 1
                runners.append(
                    {
                        "race_id": race_id,
                        "number": number,
                        "name": f"H{h}",
                        "horse_id": f"H{h}",
                        "status": "PARTANT",
                        "age": int(2 + h % 6),
                        "sex": ["MALES", "FEMELLES", "HONGRES"][h % 3],
                        "draw": int(rng.permutation(field)[i] + 1),
                        "weight_raw": int(540 + rng.integers(0, 40)),
                        "jockey": f"J{h % 25}",
                        "trainer": f"T{h % 40}",
                        "finish_position": order.index(i) + 1,
                    }
                )
                odds.append(
                    {
                        "race_id": race_id,
                        "number": number,
                        "kind": "REFERENCE",
                        "odds": float(quoted[i]),
                        "reported_at": off - timedelta(minutes=30),
                    }
                )
    con = duckdb.connect(str(path))
    for name, rows, schema in (
        ("races", races, RACE_SCHEMA),
        ("runners", runners, RUNNER_SCHEMA),
        ("odds", odds, ODDS_SCHEMA),
    ):
        frame = pl.DataFrame([{c: r.get(c) for c in schema} for r in rows], schema=schema)
        parquet = path.with_suffix(f".{name}.parquet")
        frame.write_parquet(parquet)
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM read_parquet('{parquet}')")
        parquet.unlink()
    con.close()
    return path
