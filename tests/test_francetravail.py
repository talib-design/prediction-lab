"""Collector tests that never touch the network.

Everything here is a pure function or an injected fake. The one part that cannot be
tested without credentials -- the real HTTP round trip -- is exercised by
`predlab collect offers --dry-run` against the live API, deliberately kept out of the
suite so that `pytest` stays runnable by anyone who clones this.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from predlab.data.sources.francetravail import (
    DEFAULT_SCOPE,
    QUALIFICATION_CADRE,
    ApiError,
    Credentials,
    MissingCredentialsError,
    OfferCount,
    TokenProvider,
    month_window,
    parse_content_range,
)

ENV = {
    "FRANCETRAVAIL_CLIENT_ID": "PAR_predictionlab_abc123",
    "FRANCETRAVAIL_CLIENT_SECRET": "s3cr3t-value-that-must-never-leak",
}


def test_credentials_are_read_from_the_environment() -> None:
    creds = Credentials.from_env(ENV)
    assert creds.client_id == ENV["FRANCETRAVAIL_CLIENT_ID"]
    assert creds.scope == DEFAULT_SCOPE


def test_scope_can_be_overridden() -> None:
    creds = Credentials.from_env({**ENV, "FRANCETRAVAIL_SCOPE": "other_scope"})
    assert creds.scope == "other_scope"


@pytest.mark.parametrize(
    "env",
    [
        {},
        {"FRANCETRAVAIL_CLIENT_ID": "x"},
        {"FRANCETRAVAIL_CLIENT_SECRET": "y"},
        {**ENV, "FRANCETRAVAIL_CLIENT_ID": "   "},
    ],
)
def test_missing_credentials_say_what_to_do(env: dict[str, str]) -> None:
    with pytest.raises(MissingCredentialsError, match=r"\.env"):
        Credentials.from_env(env)


def test_the_secret_never_appears_in_a_repr() -> None:
    """A traceback or a stray print must not leak the credential."""
    creds = Credentials.from_env(ENV)
    secret = ENV["FRANCETRAVAIL_CLIENT_SECRET"]
    assert secret not in repr(creds)
    assert secret not in repr(TokenProvider(creds))
    assert "<hidden>" in repr(creds)


def test_content_range_gives_the_total() -> None:
    assert parse_content_range("offres 0-0/1234") == 1234
    assert parse_content_range("offres 0-149/3987") == 3987
    assert parse_content_range("offres 0-0/0") == 0


@pytest.mark.parametrize("header", ["", "nonsense", "offres 0-0", "0-0/12"])
def test_unparseable_content_range_is_refused(header: str) -> None:
    with pytest.raises(ApiError, match="Content-Range"):
        parse_content_range(header)


@pytest.mark.parametrize(
    "year, month, expected",
    [
        (2026, 1, ("2026-01-01", "2026-01-31")),
        (2026, 2, ("2026-02-01", "2026-02-28")),
        (2024, 2, ("2024-02-01", "2024-02-29")),  # leap year
        (2026, 12, ("2026-12-01", "2026-12-31")),
    ],
)
def test_month_window(year: int, month: int, expected: tuple[str, str]) -> None:
    start, end = month_window(year, month)
    assert (start.isoformat(), end.isoformat()) == expected


def test_token_is_cached_until_shortly_before_expiry() -> None:
    creds = Credentials.from_env(ENV)
    provider = TokenProvider(creds)
    calls = {"n": 0}

    def fake_fetch(moment: datetime):
        calls["n"] += 1
        from datetime import timedelta

        return f"token-{calls['n']}", moment + timedelta(seconds=600)

    provider._fetch = fake_fetch  # type: ignore[method-assign]

    t0 = datetime(2026, 9, 20, 12, 0, tzinfo=UTC)
    from datetime import timedelta

    assert provider.token(t0) == "token-1"
    assert provider.token(t0 + timedelta(seconds=300)) == "token-1", "must reuse"
    assert calls["n"] == 1
    assert provider.token(t0 + timedelta(seconds=900)) == "token-2", "must refresh"
    assert calls["n"] == 2


def test_offer_count_records_when_it_was_taken() -> None:
    """The count alone is meaningless: the pair (window, captured_at) is the datum."""
    record = OfferCount(
        captured_at="2026-09-20T02:00:00+00:00",
        window_start="2026-08-01",
        window_end="2026-08-31",
        qualification=QUALIFICATION_CADRE,
        secteur_activite=None,
        region=None,
        count=18_432,
        lag_days=20,
    )
    payload = record.payload()
    assert payload["captured_at"] and payload["window_end"]
    assert payload["lag_days"] == 20
    assert payload["collector_version"]


def test_lag_is_what_makes_two_counts_comparable() -> None:
    """Two measurements of the same month at different lags are different quantities.

    Expired offers disappear from the API, so a window measured later returns fewer
    offers. Comparing across lags would measure the expiry curve rather than the
    labour market -- hence lag_days travels with every record.
    """
    early = OfferCount(
        "2026-09-02T00:00:00+00:00",
        "2026-08-01",
        "2026-08-31",
        QUALIFICATION_CADRE,
        None,
        None,
        18_432,
        lag_days=2,
    )
    late = OfferCount(
        "2026-10-15T00:00:00+00:00",
        "2026-08-01",
        "2026-08-31",
        QUALIFICATION_CADRE,
        None,
        None,
        11_907,
        lag_days=45,
    )
    assert early.window_start == late.window_start
    assert early.lag_days != late.lag_days
    assert early.count != late.count


def test_qualification_nine_is_cadre() -> None:
    """From the official spec: 0 - non-cadre, 9 - cadre."""
    assert QUALIFICATION_CADRE == "9"
