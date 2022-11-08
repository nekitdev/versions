from string import digits

import pytest

from versions.operators import OperatorType
from versions.specifiers import (
    SpecifierAll, SpecifierAny, SpecifierFalse, SpecifierSingle, SpecifierTrue
)
from versions.string import concat_empty_args, concat_space_args
from versions.version import Version


EMPTY = "∅"
UNIVERSE = "*"


@pytest.fixture()
def v0() -> Version:
    return Version.from_parts(0)


@pytest.fixture()
def v1() -> Version:
    return Version.from_parts(1)


@pytest.fixture()
def v100() -> Version:
    return Version.from_parts(1, 0, 0)


@pytest.fixture()
def v110() -> Version:
    return Version.from_parts(1, 1, 0)


@pytest.fixture()
def v200() -> Version:
    return Version.from_parts(2, 0, 0)


class TestSpecifierFalse:
    def test_accepts(self, v100: Version, v200: Version) -> None:
        specifier = SpecifierFalse()

        assert not specifier.accepts(v100)
        assert not specifier.accepts(v200)

    def test_to_string(self) -> None:
        specifier = SpecifierFalse()

        assert specifier.to_string() == EMPTY


class TestSpecifierTrue:
    def test_accepts(self, v100: Version, v200: Version) -> None:
        specifier = SpecifierTrue()

        assert specifier.accepts(v100)
        assert specifier.accepts(v200)

    def test_to_string(self) -> None:
        specifier = SpecifierTrue()

        assert specifier.to_string() == UNIVERSE


CARET = "^"
TILDE = "~"

TILDE_EQUAL = "~="
EQUAL = "="

STAR = "*"


def wildcard_string(string: str, wildcard: str = STAR) -> str:
    return concat_empty_args(string.rstrip(digits), wildcard)


class TestSpecifierSingle:
    def test_caret_accepts(self, v100: Version, v200: Version) -> None:
        caret_specifier = SpecifierSingle(OperatorType.CARET, v100)

        assert caret_specifier.accepts(v100)
        assert not caret_specifier.accepts(v200)

    def test_caret_to_string(self, v100: Version) -> None:
        caret_specifier = SpecifierSingle(OperatorType.CARET, v100)

        assert caret_specifier.to_string() == concat_empty_args(CARET, v100.to_string())

    def test_caret_to_short_string(self, v100: Version) -> None:
        caret_specifier = SpecifierSingle(OperatorType.CARET, v100)

        assert caret_specifier.to_short_string() == concat_empty_args(CARET, v100.to_string())

    def test_tilde_accepts(self, v100: Version, v110: Version) -> None:
        tilde_specifier = SpecifierSingle(OperatorType.TILDE, v100)

        assert tilde_specifier.accepts(v100)
        assert not tilde_specifier.accepts(v110)

    def test_tilde_to_string(self, v100: Version) -> None:
        tilde_specifier = SpecifierSingle(OperatorType.TILDE, v100)

        assert tilde_specifier.to_string() == concat_empty_args(TILDE, v100.to_string())

    def test_tilde_to_short_string(self, v100: Version) -> None:
        tilde_specifier = SpecifierSingle(OperatorType.TILDE, v100)

        assert tilde_specifier.to_short_string() == concat_empty_args(TILDE, v100.to_string())

    def test_tilde_equal_accepts(self, v100: Version, v110: Version) -> None:
        tilde_equal_specifier = SpecifierSingle(OperatorType.TILDE_EQUAL, v100)

        assert tilde_equal_specifier.accepts(v100)
        assert not tilde_equal_specifier.accepts(v110)

    def test_tilde_equal_to_string(self, v100: Version) -> None:
        tilde_equal_specifier = SpecifierSingle(OperatorType.TILDE_EQUAL, v100)

        assert tilde_equal_specifier.to_string() == concat_space_args(TILDE_EQUAL, v100.to_string())

    def test_tilde_equal_to_short_string(self, v100: Version) -> None:
        tilde_equal_specifier = SpecifierSingle(OperatorType.TILDE_EQUAL, v100)

        assert tilde_equal_specifier.to_short_string() == concat_empty_args(TILDE_EQUAL, v100.to_string())

    def test_wildcard_equal_accepts(self, v100: Version, v110: Version) -> None:
        wildcard_equal_specifier = SpecifierSingle(OperatorType.WILDCARD_EQUAL, v100)

        assert wildcard_equal_specifier.accepts(v100)
        assert not wildcard_equal_specifier.accepts(v110)

    def test_wildcard_equal_to_string(self, v100: Version) -> None:
        wildcard_equal_specifier = SpecifierSingle(OperatorType.WILDCARD_EQUAL, v100)

        assert wildcard_equal_specifier.to_string() == concat_space_args(
            EQUAL, wildcard_string(v100.to_string())
        )

    def test_wildcard_equal_to_short_string(self, v100: Version) -> None:
        wildcard_equal_specifier = SpecifierSingle(OperatorType.WILDCARD_EQUAL, v100)

        assert wildcard_equal_specifier.to_short_string() == concat_empty_args(
            EQUAL, wildcard_string(v100.to_short_string())
        )

    def test_wildcard_universe_accepts(self, v0: Version, v100: Version, v200: Version) -> None:
        wildcard_universe_specifier = SpecifierSingle(OperatorType.WILDCARD_EQUAL, v0)

        assert wildcard_universe_specifier.accepts(v100)
        assert wildcard_universe_specifier.accepts(v200)

    def test_can_not_use_tilde_equal(self, v1: Version) -> None:
        with pytest.raises(ValueError):
            SpecifierSingle(OperatorType.TILDE_EQUAL, v1)
