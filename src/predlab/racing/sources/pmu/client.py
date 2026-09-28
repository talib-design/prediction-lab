"""HTTP access to the PMU turfinfo feed, and nothing else.

What was verified on 2026-09-28 (docs/DATA_SOURCES.md): these four endpoints answer
without authentication, in JSON. What was **not** verified, because it is not
published: terms of use, rate limits, stability. The client is therefore built to be
a polite, low-volume reader:

* one request at a time, at least ``min_interval`` seconds apart;
* a small number of retries, with backoff, only on errors that retrying can fix
  (network failures, 429, 5xx) -- never on 404 or other 4xx;
* failures come back as a :class:`FetchResult` with an error sentence, not as an
  exception, so a collector run that loses one request still records the others.

The transport is injectable: tests never touch the network.
"""

from __future__ import annotations

import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum

from predlab import __version__
from predlab.core.clock import utcnow

BASE_URL = "https://online.turfinfo.api.pmu.fr/rest/client"
USER_AGENT = f"prediction-lab/{__version__} (personal non-commercial research; low volume)"

Transport = Callable[[str, float], tuple[int, bytes]]


class Endpoint(StrEnum):
    PROGRAMME = "programme"
    PARTICIPANTS = "participants"
    PERFORMANCES = "performances"
    RAPPORTS = "rapports"


def _ddmmyyyy(day: date) -> str:
    return day.strftime("%d%m%Y")


def url_for(
    endpoint: Endpoint, day: date, meeting: int | None = None, race: int | None = None
) -> str:
    """The exact URLs read on 2026-09-28. Note the ``client/{n}`` segment differs."""
    if endpoint is Endpoint.PROGRAMME:
        return f"{BASE_URL}/1/programme/{_ddmmyyyy(day)}"
    if meeting is None or race is None:
        raise ValueError(f"{endpoint} needs a meeting and a race number")
    stem = f"programme/{_ddmmyyyy(day)}/R{meeting}/C{race}"
    if endpoint is Endpoint.PARTICIPANTS:
        return f"{BASE_URL}/1/{stem}/participants"
    if endpoint is Endpoint.PERFORMANCES:
        return f"{BASE_URL}/61/{stem}/performances-detaillees/pretty"
    return f"{BASE_URL}/1/{stem}/rapports-definitifs"


def capture_key(
    endpoint: Endpoint, day: date, meeting: int | None = None, race: int | None = None
) -> str:
    """Stable identity of *what* was captured, independent of *when*."""
    if endpoint is Endpoint.PROGRAMME:
        return f"{endpoint}/{day.isoformat()}"
    return f"{endpoint}/{day.isoformat()}/R{meeting}C{race}"


@dataclass(frozen=True, slots=True)
class FetchResult:
    url: str
    status: int  # 0 when no HTTP response was obtained at all
    body: bytes
    retrieved_at: datetime
    error: str | None = None
    attempts: int = 1

    @property
    def ok(self) -> bool:
        return self.error is None and 200 <= self.status < 300 and bool(self.body)


def urllib_transport(url: str, timeout: float) -> tuple[int, bytes]:
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status), response.read()
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read() if exc.fp else b""


@dataclass
class PmuClient:
    transport: Transport = urllib_transport
    min_interval: float = 1.0
    retries: int = 2
    backoff: float = 2.0
    timeout: float = 20.0
    clock: Callable[[], datetime] = utcnow
    sleep: Callable[[float], None] = time.sleep
    requests_made: int = field(default=0, init=False)
    _last_request: float | None = field(default=None, init=False, repr=False)

    def fetch(self, url: str) -> FetchResult:
        attempts = 0
        last_error = "no attempt made"
        status = 0
        for attempt in range(self.retries + 1):
            attempts = attempt + 1
            self._wait_politely()
            retrieved_at = self.clock()
            try:
                status, body = self.transport(url, self.timeout)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = f"network error: {exc}"
                status = 0
            else:
                if 200 <= status < 300 and body:
                    return FetchResult(url, status, body, retrieved_at, attempts=attempts)
                if status == 204 or (200 <= status < 300 and not body):
                    return FetchResult(
                        url, status, b"", retrieved_at, "empty response", attempts=attempts
                    )
                last_error = f"HTTP {status}"
                if status != 429 and not 500 <= status < 600:
                    break  # 404 and other client errors do not improve with retrying
            if attempt < self.retries:
                self.sleep(self.backoff * (2**attempt))
        return FetchResult(url, status, b"", self.clock(), last_error, attempts=attempts)

    def _wait_politely(self) -> None:
        now = time.monotonic()
        if self._last_request is not None:
            wait = self.min_interval - (now - self._last_request)
            if wait > 0:
                self.sleep(wait)
        self._last_request = time.monotonic()
        self.requests_made += 1
