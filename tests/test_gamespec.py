from __future__ import annotations

import pytest

from predlab.core.gamespec import LOTO_2019_11, GameSpec, NumberPool, get_spec


def test_loto_mechanics_match_the_verified_archive(loto: GameSpec) -> None:
    main = loto.pool("main")
    chance = loto.pool("chance")
    assert (main.low, main.high, main.k) == (1, 49, 5)
    assert (chance.low, chance.high, chance.k) == (1, 10, 1)
    assert loto.draw_weekdays == frozenset({1, 3, 6})
    assert loto.source_verified


def test_marginal_probability_is_k_over_size() -> None:
    pool = NumberPool("main", 1, 49, 5)
    assert pool.marginal_probability == pytest.approx(5 / 49)


def test_expected_matches_is_identical_for_every_legal_ticket() -> None:
    """The reason match-count is a diagnostic, not a decision criterion.

    Under a fair mechanism every number has probability k/size of being drawn, so
    the expected number of matches of ANY 5-number ticket is the same constant.
    """
    pool = NumberPool("main", 1, 49, 5)
    expected = pool.k * pool.marginal_probability
    for ticket in [(1, 2, 3, 4, 5), (7, 13, 22, 38, 49), (10, 20, 30, 40, 45)]:
        assert sum(pool.marginal_probability for _ in ticket) == pytest.approx(expected)


@pytest.mark.parametrize(
    "numbers, reason",
    [
        ((1, 2, 3, 4), "too few"),
        ((1, 2, 3, 4, 5, 6), "too many"),
        ((1, 1, 2, 3, 4), "duplicate"),
        ((0, 1, 2, 3, 4), "below range"),
        ((1, 2, 3, 4, 50), "above range"),
    ],
)
def test_illegal_combinations_are_rejected(numbers: tuple[int, ...], reason: str) -> None:
    with pytest.raises(ValueError):
        NumberPool("main", 1, 49, 5).validate_combination(numbers)


def test_unverified_era_is_not_silently_available() -> None:
    """Older FDJ archives exist but their mechanics are unverified: refuse them."""
    with pytest.raises(KeyError):
        get_spec("loto", "1976-05")
    with pytest.raises(KeyError):
        get_spec("euromillions")


def test_default_era_resolves(loto: GameSpec) -> None:
    assert get_spec("loto") is LOTO_2019_11
