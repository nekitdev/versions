from hypothesis import given, strategies

from versions.types import infinity, negative_infinity


def test_negation() -> None:
    assert -infinity is negative_infinity
    assert -negative_infinity is infinity


@given(strategies.integers())
def test_infinity(value: int) -> None:
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
def test_negative_infinity(value: int) -> None:
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
