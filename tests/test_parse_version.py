import pytest

from versions.functions import parse_version
from versions.version import Version


@pytest.mark.parametrize(
    ("string", "version"),
    (
        ("0", Version.from_parts(0)),
        ("0.0", Version.from_parts(0, 0)),
        ("0.0.0", Version.from_parts(0, 0, 0)),
        ("0.0.0.0", Version.from_parts(0, 0, 0, 0)),
        ("1", Version.from_parts(1)),
        ("1.2", Version.from_parts(1, 2)),
        ("1.2.3", Version.from_parts(1, 2, 3)),
        ("1.2.3.4", Version.from_parts(1, 2, 3, 4)),
    ),
)
def test_parse_version(string: str, version: Version) -> None:
    assert parse_version(string) == version
