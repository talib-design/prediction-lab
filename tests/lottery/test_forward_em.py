"""Forward carnet: timing rules, freezing, settlement, refresh."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

from predlab.core.clock import PARIS
from predlab.core.hashing import AppendOnlyLedger
from predlab.lottery.euromillions import EuroMillionsStore, parse_csv
from predlab.lottery.forward_em import (
    WITNESS,
    Carnet,
    can_freeze,
    fetch_current_archive,
    freeze_next,
    latest_due_draw,
    next_draw_date,
    settle,
    summarise,
)
from tests.lottery.em_fixture import Row, build_csv

PROV = {"retrieved_at": "2026-10-06T00:00:00+00:00"}


def paris(y: int, m: int, d: int, hh: int, mm: int = 0) -> datetime:
    return datetime(y, m, d, hh, mm, tzinfo=PARIS)


def draw_days(start: date, n: int) -> list[date]:
    out, day = [], start
    while len(out) < n:
        if day.isoweekday() in (2, 5):
            out.append(day)
        day += timedelta(days=1)
    return out


def make_store(tmp_path: Path, days: list[date], seed: int = 0) -> EuroMillionsStore:
    rng = np.random.default_rng(seed)
    rows = []
    for d in days:
        balls = tuple(int(v) + 1 for v in rng.choice(50, 5, replace=False))
        s1, s2 = (int(v) + 1 for v in rng.choice(12, 2, replace=False))
        rows.append(
            Row(
                day=d,
                balls=balls,
                stars=(s1, s2),
                winners_eu=(0,) + (5,) * 12,
                rapports=("0",) + ("10,5",) * 12,
            )
        )
    store = EuroMillionsStore(tmp_path / "em.parquet")
    store.ingest(parse_csv(build_csv(rows, "modern"), "x.csv")[0], PROV)
    return store


def test_calendar_rules() -> None:
    assert next_draw_date(date(2026, 10, 6)) == date(2026, 10, 9)  # Tue -> Fri
    assert next_draw_date(date(2026, 10, 9)) == date(2026, 10, 13)  # Fri -> Tue
    assert latest_due_draw(paris(2026, 10, 9, 22, 0)) == date(2026, 10, 6)
    assert latest_due_draw(paris(2026, 10, 9, 23, 45)) == date(2026, 10, 9)
    assert latest_due_draw(paris(2026, 10, 11, 9, 0)) == date(2026, 10, 9)
    assert can_freeze(date(2026, 10, 9), paris(2026, 10, 9, 19, 59))
    assert not can_freeze(date(2026, 10, 9), paris(2026, 10, 9, 20, 0))


def test_freeze_is_once_per_draw_and_includes_the_witness(tmp_path: Path) -> None:
    days = draw_days(date(2024, 1, 2), 260)
    store = make_store(tmp_path, days)
    carnet = Carnet(AppendOnlyLedger(tmp_path / "c.jsonl"))
    now = datetime.combine(days[-1] + timedelta(days=1), datetime.min.time(), PARIS).replace(hour=9)
    first = freeze_next(carnet, store, now)
    again = freeze_next(carnet, store, now + timedelta(hours=1))
    assert len(first) == 9 and again == []
    assert {r["logic"] for r in first} >= {WITNESS, "hot50", "cold50", "repeat", "gap"}
    target = next_draw_date(days[-1])
    assert all(r["draw_date"] == target.isoformat() for r in first)
    assert all(r["history_last_draw"] == days[-1].isoformat() for r in first)
    assert not first[0]["history_stale"]
    carnet.ledger.verify()


def test_too_late_on_draw_day_plays_nothing(tmp_path: Path) -> None:
    days = draw_days(date(2024, 1, 2), 250)
    store = make_store(tmp_path, days)
    carnet = Carnet(AppendOnlyLedger(tmp_path / "c.jsonl"))
    target = next_draw_date(days[-1])
    late = datetime.combine(target, datetime.min.time(), PARIS).replace(hour=20)
    assert freeze_next(carnet, store, late) == []


def test_settle_after_the_result_arrives(tmp_path: Path) -> None:
    days = draw_days(date(2024, 1, 2), 251)
    store = make_store(tmp_path, days[:-1])
    carnet = Carnet(AppendOnlyLedger(tmp_path / "c.jsonl"))
    now = datetime.combine(days[-2] + timedelta(days=1), datetime.min.time(), PARIS).replace(hour=9)
    frozen = freeze_next(carnet, store, now)
    assert settle(carnet, store, now) == []  # result not in the store yet
    full = make_store(tmp_path / "b", days)  # same seed: same history + the new draw
    results = settle(carnet, full, now + timedelta(days=3))
    assert len(results) == len(frozen)
    assert settle(carnet, full, now + timedelta(days=4)) == []
    summary = summarise(carnet)
    assert summary[WITNESS]["draws"] == 1
    assert summary[WITNESS]["staked_eur"] == pytest.approx(2.5)
    carnet.ledger.verify()


def test_fetch_current_archive_keeps_one_file_per_content(tmp_path: Path) -> None:
    payload = b"PK\x03\x04fake"
    first = fetch_current_archive(tmp_path, opener=lambda url: payload)
    second = fetch_current_archive(tmp_path, opener=lambda url: payload)
    assert first is not None and first.name.startswith("current_")
    assert second is None
    with pytest.raises(ValueError):
        fetch_current_archive(tmp_path, opener=lambda url: b"<html>")


def test_timestamps_are_utc(tmp_path: Path) -> None:
    days = draw_days(date(2024, 1, 2), 250)
    store = make_store(tmp_path, days)
    carnet = Carnet(AppendOnlyLedger(tmp_path / "c.jsonl"))
    now = datetime(2030, 1, 1, 8, tzinfo=UTC)
    recs = freeze_next(carnet, store, now)
    assert recs and recs[0]["frozen_at"].endswith("+00:00")
