import pytest

from versions.functions import parse_version
from versions.segments import Epoch, PostTag, PreTag
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
        ("1.0.0a", Version.from_parts(1, 0, 0, pre=PreTag("alpha", 0))),
        ("1.0.0b1", Version.from_parts(1, 0, 0, pre=PreTag("beta", 1))),
        ("1.0.0-rc.1", Version.from_parts(1, 0, 0, pre=PreTag("rc", 1))),
        ("1.0.0-1", Version.from_parts(1, 0, 0, post=PostTag("post", 1))),
        ("1.0.0-post", Version.from_parts(1, 0, 0, post=PostTag("post", 0))),
        ("1.0.0-post.1", Version.from_parts(1, 0, 0, post=PostTag("post", 1))),
        ("1!1.0.0", Version.from_parts(1, 0, 0, epoch=Epoch(1))),
    ),
)
def test_parse_version(string: str, version: Version) -> None:
    assert parse_version(string) == version
