from versions.types import infinity, negative_infinity


def test_negation() -> None:
    assert -infinity is negative_infinity
    assert -negative_infinity is infinity


def test_infinity() -> None:
    ...


def test_negative_infinity() -> None:
    ...
