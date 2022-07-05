import pytest

from versions.functions import parse_version
from versions.version import Version


@pytest.mark.parametrize(
    ("string", "version"),
    (
        ("1", Version.from_parts(1)),
        ("1.0", Version.from_parts(1, 0)),
        ("1.0.0", Version.from_parts(1, 0, 0)),
        ("1.0.0.0", Version.from_parts(1, 0, 0, 0)),
    ),
)
def test_parse_version(string: str, version: Version) -> None:
    assert parse_version(string) == version
