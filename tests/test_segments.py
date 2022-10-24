import pytest

from versions.segments import Epoch, Local, Release, Tag


class TestEpoch:
    def test_create(self) -> None:
        value = 1

        assert Epoch.create(value) == Epoch(value)


EMPTY_PARTS = ()


class TestRelease:
    def test_empty(self) -> None:
        with pytest.raises(ValueError):
            Release(EMPTY_PARTS)

    def test_create(self) -> None:
        parts = (1, 3, 0)

        assert Release.create(parts) == Release(parts)

    def test_from_parts(self) -> None:
        parts = (4, 2, 0)

        assert Release.from_parts(4, 2, 0) == Release(parts)

    def test_into_parts(self) -> None:
        parts = (6, 9, 0)

        release = Release(parts)

        assert release.into_parts() is parts


INVALID = "invalid"


class TestTag:
    def test_invalid(self) -> None:
        with pytest.raises(ValueError):
            Tag(INVALID)

    def test_create(self) -> None:
        assert Tag.create() == Tag()


EMPTY_LOCAL_PARTS = ()

BUILD = "build"


class TestLocal:
    def test_empty(self) -> None:
        with pytest.raises(ValueError):
            Local(EMPTY_LOCAL_PARTS)

    def test_create(self) -> None:
        local_parts = (BUILD, 1)

        assert Local.create(local_parts) == Local(local_parts)

    def test_into_parts(self) -> None:
        local_parts = (BUILD, 1)

        local = Local(local_parts)

        assert local.into_parts() == local_parts
