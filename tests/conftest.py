from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import pytest

from predlab.racing.sources.pmu.client import PmuClient

FIXTURES = Path(__file__).parent / "fixtures" / "pmu"


def fixture_bytes(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


class FakeTransport:
    """Serves canned bodies by URL suffix; records every URL requested."""

    def __init__(self, routes: dict[str, tuple[int, bytes]] | None = None) -> None:
        self.routes = routes or {}
        self.calls: list[str] = []

    def __call__(self, url: str, timeout: float) -> tuple[int, bytes]:
        self.calls.append(url)
        for suffix, answer in self.routes.items():
            if url.endswith(suffix):
                return answer
        return 404, b""


class Clock:
    def __init__(self, start: datetime) -> None:
        self.now = start

    def __call__(self) -> datetime:
        return self.now


def make_client(transport: Callable[[str, float], tuple[int, bytes]], now: datetime) -> PmuClient:
    return PmuClient(transport=transport, min_interval=0.0, clock=Clock(now), sleep=lambda _: None)


@pytest.fixture
def t0() -> datetime:
    """2026-09-28 08:00 UTC: 50 minutes before the R2C1 flat race in the fixture."""
    return datetime(2026, 9, 28, 8, 0, tzinfo=UTC)
