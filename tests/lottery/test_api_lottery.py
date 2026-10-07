"""Dashboard endpoints for EuroMillions: read-only views over the CLI outputs."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from predlab.api.app import create_app
from predlab.core.clock import PARIS
from predlab.core.hashing import AppendOnlyLedger
from predlab.core.paths import Paths
from predlab.lottery.euromillions import EuroMillionsStore
from predlab.lottery.forward_em import Carnet, freeze_next
from tests.lottery.test_forward_em import draw_days, make_store


def _paths(tmp_path: Path) -> Paths:
    paths = Paths(tmp_path)
    days = draw_days(date(2024, 1, 2), 250)
    store = make_store(tmp_path / "build", days)
    target = paths.euromillions_store
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(store.path.read_bytes())
    carnet = Carnet(AppendOnlyLedger(paths.lottery / "euromillions_carnet.jsonl"))
    now = datetime.combine(days[-1] + timedelta(days=1), datetime.min.time(), PARIS).replace(hour=9)
    freeze_next(carnet, EuroMillionsStore(target), now)
    return paths


def test_carnet_endpoint_lists_pending_grids(tmp_path: Path) -> None:
    client = TestClient(create_app(_paths(tmp_path)))
    body = client.get("/api/euromillions/carnet").json()
    assert body["chain_ok"] is True
    assert len(body["pending"]) == 9
    assert body["next_draw"] == body["pending"][0]["draw_date"]
    assert body["draws"] == [] and body["summary"] == {}


def test_other_endpoints_answer_without_results_yet(tmp_path: Path) -> None:
    client = TestClient(create_app(_paths(tmp_path)))
    assert client.get("/api/euromillions/analysis").json()["analysis"] is None
    assert client.get("/api/euromillions/backtest").json()["backtest"] is None
    data = client.get("/api/euromillions/data").json()
    assert data["store"]["draws"] == 250
    assert len(data["recent"]) == 12


def test_empty_lab_does_not_crash(tmp_path: Path) -> None:
    client = TestClient(create_app(Paths(tmp_path)))
    assert client.get("/api/euromillions/carnet").json()["next_draw"] is None
    assert client.get("/api/euromillions/data").json()["store"] is None
