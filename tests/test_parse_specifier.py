import pytest

from versions.errors import ParseSpecificationError
from versions.functions import parse_specifier
from versions.operators import OperatorType
from versions.specifiers import Specifier, SpecifierAll, SpecifierAny, SpecifierOne
from versions.version import Version


@pytest.mark.parametrize(
    ("string", "specifier"),
    (
        ("~= 3.2", SpecifierOne(OperatorType.TILDE_EQUAL, Version.from_parts(3, 2))),
        ("== 4.2", SpecifierOne(OperatorType.DOUBLE_EQUAL, Version.from_parts(4, 2))),
        ("!= 2.5", SpecifierOne(OperatorType.NOT_EQUAL, Version.from_parts(2, 5))),
        ("<= 6.9", SpecifierOne(OperatorType.LESS_OR_EQUAL, Version.from_parts(6, 9))),
        (">= 1.3", SpecifierOne(OperatorType.GREATER_OR_EQUAL, Version.from_parts(1, 3))),
        ("< 6.4", SpecifierOne(OperatorType.LESS, Version.from_parts(6, 4))),
        ("> 0.7", SpecifierOne(OperatorType.GREATER, Version.from_parts(0, 7))),
        ("^3.4", SpecifierOne(OperatorType.CARET, Version.from_parts(3, 4))),
        ("~1.8", SpecifierOne(OperatorType.TILDE, Version.from_parts(1, 8))),
        ("~7", SpecifierOne(OperatorType.TILDE, Version.from_parts(7))),
        ("= 8.8", SpecifierOne(OperatorType.EQUAL, Version.from_parts(8, 8))),
        ("1.0", SpecifierOne(OperatorType.EQUAL, Version.from_parts(1, 0))),
        ("= 1.3.*", SpecifierOne(OperatorType.WILDCARD_EQUAL, Version.from_parts(1, 3))),
        ("== 7.7.*", SpecifierOne(OperatorType.WILDCARD_DOUBLE_EQUAL, Version.from_parts(7, 7))),
        ("!= 4.2.*", SpecifierOne(OperatorType.WILDCARD_NOT_EQUAL, Version.from_parts(4, 2))),
        ("*", SpecifierOne(OperatorType.WILDCARD_EQUAL, Version.from_parts(0))),
        ("!= *", SpecifierOne(OperatorType.WILDCARD_NOT_EQUAL, Version.from_parts(0))),
        (
            ">= 3.7, < 4.0",
            SpecifierAll.of(
                SpecifierOne(OperatorType.GREATER_OR_EQUAL, Version.from_parts(3, 7)),
                SpecifierOne(OperatorType.LESS, Version.from_parts(4, 0)),
            ),
        ),
        (
            "^2.7 || ^3.7",
            SpecifierAny.of(
                SpecifierOne(OperatorType.CARET, Version.from_parts(2, 7)),
                SpecifierOne(OperatorType.CARET, Version.from_parts(3, 7)),
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
