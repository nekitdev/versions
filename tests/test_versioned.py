import pytest

import versions
from versions.functions import parse_version
from versions.version import Version
from versions.versioned import get_version, has_version


@pytest.fixture()
def version() -> Version:
    return parse_version(versions.__version__)


def test_get_version_unchecked(version: Version) -> None:
    assert has_version(versions)  # for type checkers

    assert get_version(versions) == version

    with pytest.raises(AttributeError):
        get_version(42)  # type: ignore


def test_has_version() -> None:
    assert has_version(versions)
    assert not has_version(69)
