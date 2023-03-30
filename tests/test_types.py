from hypothesis import given, strategies

from versions.types import (
    infinity,
    is_any_infinity,
    is_infinity,
    is_negative_infinity,
    negative_infinity,
)


def test_negation() -> None:
    assert -infinity is negative_infinity
    assert -negative_infinity is infinity


@given(strategies.integers())
def test_infinity(value: int) -> None:  # type: ignore
    assert infinity != value
    assert infinity > value
    assert infinity >= value
    assert not infinity == value
    assert not infinity < value
    assert not infinity <= value


def test_infinity_with_infinity() -> None:
    assert infinity == infinity
    assert infinity >= infinity
    assert infinity <= infinity
    assert not infinity != infinity
    assert not infinity > infinity
    assert not infinity < infinity


@given(strategies.integers())
def test_negative_infinity(value: int) -> None:  # type: ignore
    assert negative_infinity != value
    assert negative_infinity < value
    assert negative_infinity <= value
    assert not negative_infinity == value
    assert not negative_infinity > value
    assert not negative_infinity >= value


def test_negative_infinity_with_negative_infinity() -> None:
    assert negative_infinity == negative_infinity
    assert negative_infinity >= negative_infinity
    assert negative_infinity <= negative_infinity
    assert not negative_infinity != negative_infinity
    assert not negative_infinity > negative_infinity
    assert not negative_infinity < negative_infinity


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
