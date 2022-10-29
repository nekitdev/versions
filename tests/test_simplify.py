import pytest

from versions.converters import simplify
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
    ("specifier", "simplified"),
    (
        (
            SpecifierAll.of(
                SpecifierAll.of(
                    SpecifierSingle(OperatorType.GREATER_OR_EQUAL, Version.from_parts(1, 0, 0)),
                    SpecifierSingle(OperatorType.LESS_OR_EQUAL, Version.from_parts(3, 0, 0)),
                ),
                SpecifierAll.of(
                    SpecifierSingle(OperatorType.GREATER_OR_EQUAL, Version.from_parts(2, 0, 0)),
                    SpecifierSingle(OperatorType.LESS_OR_EQUAL, Version.from_parts(4, 0, 0)),
                ),
            ),
            SpecifierAll.of(
                SpecifierSingle(OperatorType.GREATER_OR_EQUAL, Version.from_parts(2, 0, 0)),
                SpecifierSingle(OperatorType.LESS_OR_EQUAL, Version.from_parts(3, 0, 0)),
            ),
        ),
        (
            SpecifierAny.of(
                SpecifierAll.of(
                    SpecifierSingle(OperatorType.GREATER_OR_EQUAL, Version.from_parts(1, 0, 0)),
                    SpecifierSingle(OperatorType.LESS_OR_EQUAL, Version.from_parts(3, 0, 0)),
                ),
                SpecifierAll.of(
                    SpecifierSingle(OperatorType.GREATER_OR_EQUAL, Version.from_parts(2, 0, 0)),
                    SpecifierSingle(OperatorType.LESS_OR_EQUAL, Version.from_parts(4, 0, 0)),
                ),
            ),
            SpecifierAll.of(
                SpecifierSingle(OperatorType.GREATER_OR_EQUAL, Version.from_parts(1, 0, 0)),
                SpecifierSingle(OperatorType.LESS_OR_EQUAL, Version.from_parts(4, 0, 0)),
            ),
        ),
        (
            SpecifierSingle(OperatorType.CARET, Version.from_parts(1, 0, 0)),
            SpecifierAll.of(
                SpecifierSingle(OperatorType.GREATER_OR_EQUAL, Version.from_parts(1, 0, 0)),
                SpecifierSingle(OperatorType.LESS, Version.from_parts(2, 0, 0)),
            ),
        ),
        (
            SpecifierSingle(OperatorType.TILDE, Version.from_parts(1, 0, 0)),
            SpecifierAll.of(
                SpecifierSingle(OperatorType.GREATER_OR_EQUAL, Version.from_parts(1, 0, 0)),
                SpecifierSingle(OperatorType.LESS, Version.from_parts(1, 1, 0)),
            ),
        ),
        (SpecifierSingle(OperatorType.WILDCARD_EQUAL, Version.from_parts(0)), SpecifierTrue()),
        (SpecifierSingle(OperatorType.WILDCARD_NOT_EQUAL, Version.from_parts(0)), SpecifierFalse()),
        (
            SpecifierSingle(OperatorType.TILDE_EQUAL, Version.from_parts(1, 0, 0)),
            SpecifierAll.of(
                SpecifierSingle(OperatorType.GREATER_OR_EQUAL, Version.from_parts(1, 0, 0)),
                SpecifierSingle(OperatorType.LESS, Version.from_parts(1, 1, 0)),
            ),
        ),
        # leaves things as is
        (
            SpecifierSingle(OperatorType.EQUAL, Version.from_parts(1, 0, 0)),
            SpecifierSingle(OperatorType.EQUAL, Version.from_parts(1, 0, 0)),
        ),
        (SpecifierTrue(), SpecifierTrue()),
        (SpecifierFalse(), SpecifierFalse()),
    ),
)
def test_simplify(specifier: Specifier, simplified: Specifier) -> None:
    assert simplify(specifier) == simplified
