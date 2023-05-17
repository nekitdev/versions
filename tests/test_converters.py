import pytest

from versions.converters import specifier_to_version_set, version_set_to_specifier
from versions.operators import OperatorType
from versions.specifiers import (
    Specifier,
    SpecifierAll,
    SpecifierAlways,
    SpecifierAny,
    SpecifierNever,
    SpecifierOne,
)
from versions.version import Version
from versions.version_sets import VersionEmpty, VersionPoint, VersionRange, VersionSet, VersionUnion


@pytest.mark.parametrize(
    ("version_set", "specifier", "resulting_version_set"),
    (
        (VersionEmpty(), SpecifierNever(), VersionEmpty()),
        (VersionRange(), SpecifierAlways(), VersionRange()),
        (
            VersionRange(
                min=Version.from_parts(1, 0, 0),
                max=Version.from_parts(1, 0, 0),
                include_min=False,
                include_max=False,
            ),
            SpecifierNever(),
            VersionEmpty(),
        ),
        (
            VersionRange(
                min=Version.from_parts(2, 0, 0),
                max=Version.from_parts(2, 0, 0),
                include_min=True,
                include_max=True,
            ),
            SpecifierOne(OperatorType.DOUBLE_EQUAL, Version.from_parts(2, 0, 0)),
            VersionPoint(Version.from_parts(2, 0, 0)),
        ),
        (
            VersionPoint(Version.from_parts(3, 0, 0)),
            SpecifierOne(OperatorType.DOUBLE_EQUAL, Version.from_parts(3, 0, 0)),
            VersionPoint(Version.from_parts(3, 0, 0)),
        ),
        (
            VersionRange(min=Version.from_parts(4, 0, 0), include_min=True),
            SpecifierOne(OperatorType.GREATER_OR_EQUAL, Version.from_parts(4, 0, 0)),
            VersionRange(min=Version.from_parts(4, 0, 0), include_min=True),
        ),
        (
            VersionRange(max=Version.from_parts(5, 0, 0), include_max=True),
            SpecifierOne(OperatorType.LESS_OR_EQUAL, Version.from_parts(5, 0, 0)),
            VersionRange(max=Version.from_parts(5, 0, 0), include_max=True),
        ),
        (
            VersionUnion.of(
                VersionRange(max=Version.from_parts(7, 0, 0), include_max=False),
                VersionRange(min=Version.from_parts(7, 0, 0), include_min=False),
            ),
            SpecifierOne(OperatorType.NOT_EQUAL, Version.from_parts(7, 0, 0)),
            VersionUnion.of(
                VersionRange(max=Version.from_parts(7, 0, 0), include_max=False),
                VersionRange(min=Version.from_parts(7, 0, 0), include_min=False),
            ),
        ),
        (
            VersionUnion.of(
                VersionRange(
                    min=Version.from_parts(8, 0, 0),
                    max=Version.from_parts(9, 0, 0),
                    include_min=True,
                    include_max=False,
                ),
                VersionRange(
                    min=Version.from_parts(10, 0, 0),
                    include_min=True,
                ),
            ),
            SpecifierAny.of(
                SpecifierAll.of(
                    SpecifierOne(OperatorType.GREATER_OR_EQUAL, Version.from_parts(8, 0, 0)),
                    SpecifierOne(OperatorType.LESS, Version.from_parts(9, 0, 0)),
                ),
                SpecifierOne(OperatorType.GREATER_OR_EQUAL, Version.from_parts(10, 0, 0)),
            ),
            VersionUnion.of(
                VersionRange(
                    min=Version.from_parts(8, 0, 0),
                    max=Version.from_parts(9, 0, 0),
                    include_min=True,
                    include_max=False,
                ),
                VersionRange(
                    min=Version.from_parts(10, 0, 0),
                    include_min=True,
                ),
            ),
        ),
    ),
)
def test_conversion(
    version_set: VersionSet, specifier: Specifier, resulting_version_set: VersionSet
) -> None:
    converted_specifier = version_set_to_specifier(version_set)
    converted_version_set = specifier_to_version_set(specifier)

    assert converted_specifier == specifier
    assert converted_version_set == resulting_version_set


def test_invalid() -> None:
    with pytest.raises(TypeError):
        specifier_to_version_set(13)  # type: ignore

    with pytest.raises(TypeError):
        version_set_to_specifier(42)  # type: ignore
