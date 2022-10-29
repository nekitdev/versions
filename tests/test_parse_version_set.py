import pytest

from versions.errors import ParseSpecificationError
from versions.functions import parse_version_set
from versions.version import Version
from versions.version_sets import VersionEmpty, VersionPoint, VersionRange, VersionSet, VersionUnion


@pytest.mark.parametrize(
    ("string", "version_set"),
    (
        (
            "~= 3.2",
            VersionRange(
                min=Version.from_parts(3, 2),
                max=Version.from_parts(4, 0),
                include_min=True,
                include_max=False,
            ),
        ),
        ("== 4.2", VersionPoint(Version.from_parts(4, 2))),
        (
            "!= 2.5",
            VersionUnion.of(
                VersionRange(max=Version.from_parts(2, 5), include_max=False),
                VersionRange(min=Version.from_parts(2, 5), include_min=False),
            ),
        ),
        ("<= 6.9", VersionRange(max=Version.from_parts(6, 9), include_max=True)),
        (">= 1.3", VersionRange(min=Version.from_parts(1, 3), include_min=True)),
        ("< 6.4", VersionRange(max=Version.from_parts(6, 4), include_max=False)),
        ("> 0.7", VersionRange(min=Version.from_parts(0, 7), include_min=False)),
        (
            "^3.4",
            VersionRange(
                min=Version.from_parts(3, 4),
                max=Version.from_parts(4, 0),
                include_min=True,
                include_max=False,
            ),
        ),
        (
            "~1.8",
            VersionRange(
                min=Version.from_parts(1, 8),
                max=Version.from_parts(1, 9),
                include_min=True,
                include_max=False,
            ),
        ),
        (
            "~7",
            VersionRange(
                min=Version.from_parts(7),
                max=Version.from_parts(8),
                include_min=True,
                include_max=False,
            ),
        ),
        ("= 8.8", VersionPoint(Version.from_parts(8, 8))),
        ("1.0", VersionPoint(Version.from_parts(1, 0))),
        (
            "= 1.3.*",
            VersionRange(
                min=Version.from_parts(1, 3, 0),
                max=Version.from_parts(1, 4, 0),
                include_min=True,
                include_max=False,
            ),
        ),
        (
            "== 7.7.*",
            VersionRange(
                min=Version.from_parts(7, 7),
                max=Version.from_parts(7, 8),
                include_min=True,
                include_max=False,
            ),
        ),
        (
            "!= 4.2.*",
            VersionUnion.of(
                VersionRange(max=Version.from_parts(4, 2), include_max=False),
                VersionRange(min=Version.from_parts(4, 3), include_min=True),
            ),
        ),
        ("*", VersionRange()),
        ("!= *", VersionEmpty()),
        (
            ">= 3.7, < 4.0",
            VersionRange(
                min=Version.from_parts(3, 7),
                max=Version.from_parts(4, 0),
                include_min=True,
                include_max=False,
            ),
        ),
        (
            "^2.7 || ^3.7",
            VersionUnion.of(
                VersionRange(
                    min=Version.from_parts(2, 7),
                    max=Version.from_parts(3, 0),
                    include_min=True,
                    include_max=False,
                ),
                VersionRange(
                    min=Version.from_parts(3, 7),
                    max=Version.from_parts(4, 0),
                    include_min=True,
                    include_max=False,
                ),
            ),
        ),
    ),
)
def test_parse_version_set(string: str, version_set: VersionSet) -> None:
    assert parse_version_set(string) == version_set


@pytest.mark.parametrize("string", ("1.0.0.", "1.0.0-", "1.0.0+", "broken"))
def test_parse_invalid_version_set(string: str) -> None:
    with pytest.raises(ParseSpecificationError):
        parse_version_set(string)
