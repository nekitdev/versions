import pytest
from versions.segments import Epoch, Local

from versions.version import Version


@pytest.fixture
def v100() -> Version:
    return Version.from_parts(1, 0, 0)


@pytest.fixture
def v120() -> Version:
    return Version.from_parts(1, 2, 0)


@pytest.fixture
def v123() -> Version:
    return Version.from_parts(1, 2, 3)


@pytest.fixture
def v200() -> Version:
    return Version.from_parts(2, 0, 0)


@pytest.fixture
def v100build1() -> Version:
    return Version.from_parts(1, 0, 0, local=Local.from_parts("build", 1))


@pytest.fixture
def v1e100() -> Version:
    return Version.from_parts(1, 0, 0, epoch=Epoch(1))


def test_epoch(v100: Version, v1e100: Version) -> None:
    assert not v100.epoch.value
    assert v1e100.epoch.value == 1


def test_next_major(v100: Version, v200: Version) -> None:
    assert v100.next_major() == v200


def test_set_major(v100: Version, v200: Version) -> None:
    assert v100.set_major(2) == v200
