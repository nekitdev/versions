import pytest

from versions.converters import simplify
from versions.operators import OperatorType
from versions.specifiers import (
    Specifier,
    SpecifierAll,
    SpecifierAny,
    SpecifierFalse,
    SpecifierOne,
    SpecifierTrue,
)
from versions.version import Version


@pytest.mark.parametrize(
    ("specifier", "simplified"),
    (
        (
            SpecifierAll.of(
                SpecifierAll.of(
                    SpecifierOne(OperatorType.GREATER_OR_EQUAL, Version.from_parts(1, 0, 0)),
                    SpecifierOne(OperatorType.LESS_OR_EQUAL, Version.from_parts(3, 0, 0)),
                ),
                SpecifierAll.of(
                    SpecifierOne(OperatorType.GREATER_OR_EQUAL, Version.from_parts(2, 0, 0)),
                    SpecifierOne(OperatorType.LESS_OR_EQUAL, Version.from_parts(4, 0, 0)),
                ),
            ),
            SpecifierAll.of(
                SpecifierOne(OperatorType.GREATER_OR_EQUAL, Version.from_parts(2, 0, 0)),
                SpecifierOne(OperatorType.LESS_OR_EQUAL, Version.from_parts(3, 0, 0)),
            ),
        ),
        (
            SpecifierAny.of(
                SpecifierAll.of(
                    SpecifierOne(OperatorType.GREATER_OR_EQUAL, Version.from_parts(1, 0, 0)),
                    SpecifierOne(OperatorType.LESS_OR_EQUAL, Version.from_parts(3, 0, 0)),
                ),
                SpecifierAll.of(
                    SpecifierOne(OperatorType.GREATER_OR_EQUAL, Version.from_parts(2, 0, 0)),
                    SpecifierOne(OperatorType.LESS_OR_EQUAL, Version.from_parts(4, 0, 0)),
                ),
            ),
            SpecifierAll.of(
                SpecifierOne(OperatorType.GREATER_OR_EQUAL, Version.from_parts(1, 0, 0)),
                SpecifierOne(OperatorType.LESS_OR_EQUAL, Version.from_parts(4, 0, 0)),
            ),
        ),
        (
            SpecifierOne(OperatorType.CARET, Version.from_parts(1, 0, 0)),
            SpecifierAll.of(
                SpecifierOne(OperatorType.GREATER_OR_EQUAL, Version.from_parts(1, 0, 0)),
                SpecifierOne(OperatorType.LESS, Version.from_parts(2, 0, 0)),
            ),
        ),
        (
            SpecifierOne(OperatorType.TILDE, Version.from_parts(1, 0, 0)),
            SpecifierAll.of(
                SpecifierOne(OperatorType.GREATER_OR_EQUAL, Version.from_parts(1, 0, 0)),
                SpecifierOne(OperatorType.LESS, Version.from_parts(1, 1, 0)),
            ),
        ),
        (SpecifierOne(OperatorType.WILDCARD_EQUAL, Version.from_parts(0)), SpecifierTrue()),
        (SpecifierOne(OperatorType.WILDCARD_NOT_EQUAL, Version.from_parts(0)), SpecifierFalse()),
        (
            SpecifierOne(OperatorType.TILDE_EQUAL, Version.from_parts(1, 0, 0)),
            SpecifierAll.of(
                SpecifierOne(OperatorType.GREATER_OR_EQUAL, Version.from_parts(1, 0, 0)),
                SpecifierOne(OperatorType.LESS, Version.from_parts(1, 1, 0)),
            ),
        ),
        # leaves things as is
        (
            SpecifierOne(OperatorType.EQUAL, Version.from_parts(1, 0, 0)),
            SpecifierOne(OperatorType.EQUAL, Version.from_parts(1, 0, 0)),
        ),
        (SpecifierTrue(), SpecifierTrue()),
        (SpecifierFalse(), SpecifierFalse()),
    ),
)
def test_simplify(specifier: Specifier, simplified: Specifier) -> None:
    assert simplify(specifier) == simplified
