"""Live collection of cadre job-posting volumes from the France Travail API.

Verified against the official OpenAPI specification on 2026-09-20:

    token    https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire
    base     https://api.francetravail.io/partenaire/offresdemploi
    search   GET /v2/offres/search
    scopes   api_offresdemploiv2 + o2dsoffre   (both mandatory)
    counting range=0-0, then read the Content-Range header -- no need to page

The parameter that makes this source worth having, quoted from the spec:

    qualification : Qualification du poste : 0 - non-cadre, 9 - cadre.

Combined with ``minCreationDate`` / ``maxCreationDate``, ``secteurActivite`` and
``region``, that yields a monthly count of cadre postings by sector and region -- the
leading indicator the DPAE series cannot provide, because the public DPAE datasets
stopped being updated in October 2025.

=====================================================================================
THE CAVEAT THAT GOVERNS EVERY USE OF THIS DATA
=====================================================================================

The API returns offers that are **active right now**. Expired offers are gone. So a
count of "offers created in August", taken in September, is smaller than the same
count taken in August -- not because fewer were created, but because some have since
expired.

Two consequences, and ignoring either would poison the series:

1. **A count is only meaningful together with when it was taken.** Every record here
   carries ``captured_at`` and the window it describes, and the pair is what gets
   stored -- never the count alone.

2. **Only counts taken at the same lag are comparable.** Comparing "August measured
   at 30 days" with "September measured at 3 days" measures the expiry curve, not the
   labour market. The analysis layer must select a constant lag; this module records
   what it needs to make that possible and refuses to pretend otherwise.

3. **A window that has not closed yet is incomplete, not merely early.** Counting the
   current month on the 20th asks the API for offers created up to the 30th; the ones
   created on the 21st do not exist yet. The count is a partial sum over the elapsed
   part of the window, and putting it on the same axis as a completed month is not a
   lag artefact but an arithmetic error. Such a record carries ``window_complete =
   False`` and ``observed_days`` (how much of the window had elapsed at capture), so
   the analysis layer can either drop it or scale it deliberately. ``lag_days`` is
   signed and stays the literal ``captured_at - window_end``: negative means the
   window was still open.

This is also why the collector must start running now: the history cannot be rebuilt
afterwards, at any lag.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta

TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
API_BASE = "https://api.francetravail.io/partenaire/offresdemploi"
SEARCH_PATH = "/v2/offres/search"
DEFAULT_SCOPE = "api_offresdemploiv2 o2dsoffre"
COLLECTOR_VERSION = "ft-offres-2"

QUALIFICATION_CADRE = "9"
QUALIFICATION_NON_CADRE = "0"

TIMEOUT_S = 30
TOKEN_MARGIN_S = 60
USER_AGENT = "prediction-lab/0.1 (research)"

_CONTENT_RANGE = re.compile(r"^\s*\S+\s+(\d+)-(\d+)/(\d+)\s*$")


class MissingCredentialsError(RuntimeError):
    """The France Travail credentials are not present in the environment."""


class ApiError(RuntimeError):
    """The API answered with something this collector will not interpret."""


@dataclass(frozen=True, slots=True)
class Credentials:
    """Client credentials, read from the environment and never written anywhere.

    They are not logged, not stored, and not included in any record this module
    produces. ``__repr__`` is overridden so that an accidental print or a traceback
    cannot leak the secret.
    """

    client_id: str
    client_secret: str = field(repr=False)
    scope: str = DEFAULT_SCOPE

    def __repr__(self) -> str:
        return f"Credentials(client_id={self.client_id[:6]}…, secret=<hidden>)"

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Credentials:
        source = env if env is not None else dict(os.environ)
        client_id = (source.get("FRANCETRAVAIL_CLIENT_ID") or "").strip()
        secret = (source.get("FRANCETRAVAIL_CLIENT_SECRET") or "").strip()
        missing = [
            name
            for name, value in (
                ("FRANCETRAVAIL_CLIENT_ID", client_id),
                ("FRANCETRAVAIL_CLIENT_SECRET", secret),
            )
            if not value
        ]
        if missing:
            raise MissingCredentialsError(
                f"missing {', '.join(missing)}. Copy .env.example to .env and fill it in; "
                ".env is git-ignored and must stay that way."
            )
        return cls(
            client_id=client_id,
            client_secret=secret,
            scope=(source.get("FRANCETRAVAIL_SCOPE") or DEFAULT_SCOPE).strip(),
        )


def parse_content_range(header: str) -> int:
    """Total number of matching offers, from a ``Content-Range: offres 0-0/1234`` header.

    Counting this way costs one request regardless of how many offers match, which is
    what makes a sector-by-region sweep affordable.
    """
    match = _CONTENT_RANGE.match(header or "")
    if not match:
        raise ApiError(f"unparseable Content-Range header: {header!r}")
    return int(match.group(3))


def month_window(year: int, month: int) -> tuple[date, date]:
    """First and last day of a calendar month."""
    first = date(year, month, 1)
    following = date(year + (month == 12), (month % 12) + 1, 1)
    return first, following - timedelta(days=1)


def day_window(day: date) -> tuple[date, date]:
    """A single calendar day as a window.

    This is the window shape that makes a usable series. Measuring the day ``L`` days
    ago puts the lag at exactly ``L``, every single time, with no arithmetic and no
    correction -- which is the one property calendar months cannot have, since a month
    measured today is measured at whatever lag the calendar happens to give it.
    """
    return day, day


def _as_api_datetime(day: date, end_of_day: bool) -> str:
    suffix = "T23:59:59Z" if end_of_day else "T00:00:00Z"
    return day.isoformat() + suffix


@dataclass(frozen=True, slots=True)
class OfferCount:
    """One measurement: how many offers matched, for which window, taken when."""

    captured_at: str
    window_start: str
    window_end: str
    qualification: str
    secteur_activite: str | None
    region: str | None
    count: int
    lag_days: int
    observed_days: int
    window_days: int
    collector_version: str = COLLECTOR_VERSION

    @property
    def window_complete(self) -> bool:
        """Had the whole window elapsed when the count was taken?

        False means the count is a partial sum: offers that will be created later in
        the window are missing from it by construction, not by expiry.
        """
        return self.observed_days >= self.window_days

    def payload(self) -> dict[str, object]:
        return {
            "captured_at": self.captured_at,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "qualification": self.qualification,
            "secteur_activite": self.secteur_activite,
            "region": self.region,
            "count": self.count,
            "lag_days": self.lag_days,
            "observed_days": self.observed_days,
            "window_days": self.window_days,
            "window_complete": self.window_complete,
            "collector_version": self.collector_version,
        }


class TokenProvider:
    """Fetches and caches an OAuth access token.

    The token is held in memory only, refreshed shortly before it expires, and never
    written to disk or to a record.
    """

    def __init__(self, credentials: Credentials) -> None:
        self._credentials = credentials
        self._token: str | None = None
        self._expires_at: datetime | None = None

    def __repr__(self) -> str:
        return f"TokenProvider({self._credentials!r}, token=<hidden>)"

    def token(self, now: datetime | None = None) -> str:
        moment = now or datetime.now(UTC)
        if self._token and self._expires_at and moment < self._expires_at:
            return self._token
        self._token, self._expires_at = self._fetch(moment)
        return self._token

    def _fetch(self, moment: datetime) -> tuple[str, datetime]:
        body = urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": self._credentials.client_id,
                "client_secret": self._credentials.client_secret,
                "scope": self._credentials.scope,
            }
        ).encode()
        request = urllib.request.Request(
            TOKEN_URL,
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
                payload = json.loads(response.read())
        except urllib.error.HTTPError as exc:
            raise ApiError(
                f"token request refused ({exc.code}). Check the credentials in .env and "
                "that the application is linked to the Offres d'emploi API on "
                "francetravail.io."
            ) from None
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ApiError(
                f"could not reach {TOKEN_URL.split('?')[0]} ({exc}). "
                "Check the network, a proxy, or a firewall."
            ) from None
        token = payload.get("access_token")
        if not token:
            raise ApiError("token response contained no access_token")
        lifetime = int(payload.get("expires_in", 1200))
        return token, moment + timedelta(seconds=max(1, lifetime - TOKEN_MARGIN_S))


class OffersClient:
    """Counts matching offers. Deliberately does not download the offers themselves.

    The licence governs redistribution of the offers; counting them does not touch
    that, and a count is all the indicator needs. Keeping the raw offers out of this
    project is a design decision, not an omission.
    """

    def __init__(self, tokens: TokenProvider) -> None:
        self._tokens = tokens

    def count(
        self,
        window_start: date,
        window_end: date,
        *,
        qualification: str = QUALIFICATION_CADRE,
        secteur_activite: str | None = None,
        region: str | None = None,
        now: datetime | None = None,
    ) -> OfferCount:
        params: dict[str, str] = {
            "range": "0-0",
            "minCreationDate": _as_api_datetime(window_start, end_of_day=False),
            "maxCreationDate": _as_api_datetime(window_end, end_of_day=True),
            "qualification": qualification,
        }
        if secteur_activite:
            params["secteurActivite"] = secteur_activite
        if region:
            params["region"] = region

        url = f"{API_BASE}{SEARCH_PATH}?{urllib.parse.urlencode(params)}"
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self._tokens.token(now)}",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
                status = response.status
                header = response.headers.get("Content-Range", "")
        except urllib.error.HTTPError as exc:
            if exc.code == 204:  # no matching offer
                status, header = 204, exc.headers.get("Content-Range", "")
            else:
                raise ApiError(
                    f"search refused ({exc.code}) for {window_start}..{window_end}"
                ) from None

        total = 0 if (status == 204 and not header) else parse_content_range(header)
        moment = now or datetime.now(UTC)
        window_days = (window_end - window_start).days + 1
        # Days of the window already over at capture time. The capture day itself does
        # not count: offers can still be created during it.
        observed = (moment.date() - window_start).days
        observed_days = max(0, min(window_days, observed))
        return OfferCount(
            captured_at=moment.isoformat(timespec="seconds"),
            window_start=window_start.isoformat(),
            window_end=window_end.isoformat(),
            qualification=qualification,
            secteur_activite=secteur_activite,
            region=region,
            count=total,
            lag_days=(moment.date() - window_end).days,
            observed_days=observed_days,
            window_days=window_days,
        )
