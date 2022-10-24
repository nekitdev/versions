from versions.types import (
    infinity,
    is_any_infinity,
    is_infinity,
    is_negative_infinity,
    negative_infinity,
)


def test_is_any_infinity() -> None:
    assert is_any_infinity(infinity)
    assert is_any_infinity(negative_infinity)
    assert not is_any_infinity(69)


def test_is_infinity() -> None:
    assert is_infinity(infinity)
    assert not is_infinity(negative_infinity)
    assert not is_infinity(13)


def test_is_negative_infinity() -> None:
    assert not is_negative_infinity(infinity)
    assert is_negative_infinity(negative_infinity)
    assert not is_negative_infinity(42)
