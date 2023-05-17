import pytest

import versions
from versions.functions import parse_version
from versions.version import Version
from versions.versioned import get_version, get_version_unchecked, has_version


@pytest.fixture()
def version() -> Version:
    return parse_version(versions.__version__)


def test_get_version(version: Version) -> None:
    assert get_version(versions) == version

    assert get_version(13) is None


def test_get_version_unchecked(version: Version) -> None:
    assert has_version(versions)  # for type checkers

    assert get_version_unchecked(versions) == version

    with pytest.raises(AttributeError):
        get_version_unchecked(42)  # type: ignore


def test_has_version() -> None:
    assert has_version(versions)
    assert not has_version(69)
