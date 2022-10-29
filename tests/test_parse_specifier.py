import pytest

from versions.errors import ParseSpecificationError
from versions.functions import parse_specifier
from versions.operators import OperatorType
from versions.specifiers import (
    Specifier,
    SpecifierAll,
    SpecifierAny,
    SpecifierFalse,
    SpecifierSingle,
    SpecifierTrue,
)
from versions.version import Version


@pytest.mark.parametrize(
    ("string", "specifier"),
    (
        ("~= 3.2", SpecifierSingle(OperatorType.TILDE_EQUAL, Version.from_parts(3, 2))),
        ("== 4.2", SpecifierSingle(OperatorType.DOUBLE_EQUAL, Version.from_parts(4, 2))),
        ("!= 2.5", SpecifierSingle(OperatorType.NOT_EQUAL, Version.from_parts(2, 5))),
        ("<= 6.9", SpecifierSingle(OperatorType.LESS_OR_EQUAL, Version.from_parts(6, 9))),
        (">= 1.3", SpecifierSingle(OperatorType.GREATER_OR_EQUAL, Version.from_parts(1, 3))),
        ("< 6.4", SpecifierSingle(OperatorType.LESS, Version.from_parts(6, 4))),
        ("> 0.7", SpecifierSingle(OperatorType.GREATER, Version.from_parts(0, 7))),
        ("^3.4", SpecifierSingle(OperatorType.CARET, Version.from_parts(3, 4))),
        ("~1.8", SpecifierSingle(OperatorType.TILDE, Version.from_parts(1, 8))),
        ("~7", SpecifierSingle(OperatorType.TILDE, Version.from_parts(7))),
        ("= 8.8", SpecifierSingle(OperatorType.EQUAL, Version.from_parts(8, 8))),
        ("1.0", SpecifierSingle(OperatorType.EQUAL, Version.from_parts(1, 0))),
        ("= 1.3.*", SpecifierSingle(OperatorType.WILDCARD_EQUAL, Version.from_parts(1, 3))),
        ("== 7.7.*", SpecifierSingle(OperatorType.WILDCARD_DOUBLE_EQUAL, Version.from_parts(7, 7))),
        ("!= 4.2.*", SpecifierSingle(OperatorType.WILDCARD_NOT_EQUAL, Version.from_parts(4, 2))),
        ("*", SpecifierSingle(OperatorType.WILDCARD_EQUAL, Version.from_parts(0))),
        ("!= *", SpecifierSingle(OperatorType.WILDCARD_NOT_EQUAL, Version.from_parts(0))),
        (
            ">= 3.7, < 4.0",
            SpecifierAll.of(
                SpecifierSingle(OperatorType.GREATER_OR_EQUAL, Version.from_parts(3, 7)),
                SpecifierSingle(OperatorType.LESS, Version.from_parts(4, 0)),
            ),
        ),
        (
            "^2.7 || ^3.7",
            SpecifierAny.of(
                SpecifierSingle(OperatorType.CARET, Version.from_parts(2, 7)),
                SpecifierSingle(OperatorType.CARET, Version.from_parts(3, 7)),
            ),
        ),
    ),
)
def test_parse_specifier(string: str, specifier: Specifier) -> None:
    assert parse_specifier(string) == specifier


@pytest.mark.parametrize("string", ("1.0.0.", "1.0.0-", "1.0.0+", "broken"))
def test_parse_invalid_specifier(string: str) -> None:
    with pytest.raises(ParseSpecificationError):
        parse_specifier(string)
