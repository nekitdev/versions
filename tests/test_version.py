import pytest

from versions.segments import DevTag, Epoch, Local, PostTag, PreTag
from versions.version import Version


@pytest.fixture()
def v100() -> Version:
    return Version.from_parts(1, 0, 0)


DEV = "dev"


@pytest.fixture()
def v100dev0() -> Version:
    return Version.from_parts(1, 0, 0, dev=DevTag(DEV, 0))


@pytest.fixture()
def v100dev1() -> Version:
    return Version.from_parts(1, 0, 0, dev=DevTag(DEV, 1))


ALPHA = "alpha"


@pytest.fixture()
def v100alpha0() -> Version:
    return Version.from_parts(1, 0, 0, pre=PreTag(ALPHA, 0))


BETA = "beta"


@pytest.fixture()
def v100beta1() -> Version:
    return Version.from_parts(1, 0, 0, pre=PreTag(BETA, 1))


RC = "rc"


@pytest.fixture()
def v100rc0() -> Version:
    return Version.from_parts(1, 0, 0, pre=PreTag(RC, 0))


@pytest.fixture()
def v100rc1() -> Version:
    return Version.from_parts(1, 0, 0, pre=PreTag(RC, 1))


BUILD = "build"


@pytest.fixture()
def v100build1() -> Version:
    return Version.from_parts(1, 0, 0, local=Local.from_parts(BUILD, 1))


POST = "post"


@pytest.fixture()
def v100post0() -> Version:
    return Version.from_parts(1, 0, 0, post=PostTag(POST, 0))


@pytest.fixture()
def v100post1() -> Version:
    return Version.from_parts(1, 0, 0, post=PostTag(POST, 1))


# weird ones


@pytest.fixture()
def v1e100alpha1post1dev1build1() -> Version:
    return Version.from_parts(
        1,
        0,
        0,
        epoch=Epoch(1),
        pre=PreTag(ALPHA, 1),
        post=PostTag(POST, 1),
        dev=DevTag(DEV, 1),
        local=Local.from_parts(BUILD, 1),
    )


CANDIDATE = "candidate"
REV = "rev"


@pytest.fixture()
def v100candidate0rev0dev0() -> Version:
    return Version.from_parts(
        1, 0, 0, pre=PreTag(CANDIDATE, 0), post=PostTag(REV, 0), dev=DevTag(DEV, 0)
    )


@pytest.fixture()
def v100rc0post0dev0() -> Version:
    return Version.from_parts(1, 0, 0, pre=PreTag(RC, 0), post=PostTag(POST, 0), dev=DevTag(DEV, 0))


@pytest.fixture()
def v120() -> Version:
    return Version.from_parts(1, 2, 0)


@pytest.fixture()
def v130() -> Version:
    return Version.from_parts(1, 3, 0)


@pytest.fixture()
def v123() -> Version:
    return Version.from_parts(1, 2, 3)


@pytest.fixture()
def v1234() -> Version:
    return Version.from_parts(1, 2, 3, 4)


@pytest.fixture()
def v12345() -> Version:
    return Version.from_parts(1, 2, 3, 4, 5)


@pytest.fixture()
def v124() -> Version:
    return Version.from_parts(1, 2, 4)


@pytest.fixture()
def v200() -> Version:
    return Version.from_parts(2, 0, 0)


@pytest.fixture()
def v1e100() -> Version:
    return Version.from_parts(1, 0, 0, epoch=Epoch(1))


@pytest.fixture()
def dev1() -> DevTag:
    return DevTag(DEV, 1)


@pytest.fixture()
def rc1() -> PreTag:
    return PreTag(RC, 1)


@pytest.fixture()
def post1() -> PostTag:
    return PostTag(POST, 1)


@pytest.fixture()
def build1() -> Local:
    return Local.from_parts(BUILD, 1)


def test_epoch(v100: Version, v1e100: Version) -> None:
    assert not v100.epoch
    assert v1e100.epoch


def test_precision(v100: Version) -> None:
    assert v100.precision == 3


def test_last_index(v200: Version) -> None:
    assert v200.last_index == 2


def test_major_minor_micro(v123: Version) -> None:
    assert v123.major == 1
    assert v123.minor == 2
    assert v123.micro == 3


def test_patch_is_micro(v120: Version) -> None:
    assert v120.patch == v120.micro


def test_extra(v100: Version, v12345: Version) -> None:
    assert not v100.extra
    assert v12345.extra == (4, 5)


def test_get_at(v100: Version) -> None:
    assert v100.get_at(0)
    assert not v100.get_at(1)
    assert not v100.get_at(2)
    assert not v100.get_at(3)  # defaults


def test_get_at_unchecked(v100: Version) -> None:
    with pytest.raises(IndexError):
        v100.get_at_unchecked(3)


def test_is_semantic(v123: Version, v12345: Version) -> None:
    assert v123.is_semantic()
    assert not v12345.is_semantic()


def test_to_semantic(v12345: Version, v124: Version, v130: Version) -> None:
    assert v130.to_semantic() == v130
    assert v12345.to_semantic() == v124


def test_set_major(v100: Version, v200: Version) -> None:
    assert v100.set_major(2) == v200


def test_set_minor(v120: Version, v130: Version) -> None:
    assert v120.set_minor(3) == v130


def test_set_micro(v123: Version, v124: Version) -> None:
    assert v123.set_micro(4) == v124


def test_set_patch_is_set_micro(v200: Version) -> None:
    assert v200.set_patch(1) == v200.set_micro(1)


def test_set_at(
    v100: Version,
    v120: Version,
    v123: Version,
    v1234: Version,
    v124: Version,
    v130: Version,
    v200: Version,
) -> None:
    assert v100.set_at(0, 2) == v200
    assert v120.set_at(1, 3) == v130
    assert v123.set_at(2, 4) == v124

    assert v123.set_at(3, 4) == v1234


def test_set_at_unchecked(v100: Version) -> None:
    with pytest.raises(IndexError):
        v100.set_at_unchecked(3, 0)


def test_next_major(v100: Version, v200: Version) -> None:
    assert v100.next_major() == v200


def test_next_minor(v120: Version, v130: Version) -> None:
    assert v120.next_minor() == v130


def test_next_micro(v123: Version, v124: Version) -> None:
    assert v123.next_micro() == v124


def test_next_patch_is_next_micro(v200: Version) -> None:
    assert v200.next_patch() == v200.next_micro()


def test_next_at(v123: Version, v124: Version, v130: Version, v200: Version) -> None:
    assert v123.next_at(0) == v200
    assert v123.next_at(1) == v130
    assert v123.next_at(2) == v124


def test_has_major_minor_micro_extra(v1234: Version) -> None:
    assert v1234.has_major()
    assert v1234.has_minor()
    assert v1234.has_micro()
    assert v1234.has_extra()


def test_has_at(v100: Version) -> None:
    assert v100.has_at(0)
    assert not v100.has_at(3)


def test_has_patch_is_has_micro(v200: Version) -> None:
    assert v200.has_patch() == v200.has_micro()


def test_pad_to(v100: Version) -> None:
    assert v100.pad_to(3) == v100

    assert v100.pad_to(5).release.parts == (1, 0, 0, 0, 0)


def test_pad_to_index(v200: Version) -> None:
    assert v200.pad_to_index(2) == v200

    assert v200.pad_to_index(4).release.parts == (2, 0, 0, 0, 0)


def test_pad_to_next(v130: Version) -> None:
    assert v130.pad_to_next().release.parts == (1, 3, 0, 0)


def test_is_pre_release(v100rc1: Version, v100: Version) -> None:
    assert not v100.is_pre_release()
    assert v100rc1.is_pre_release()


def test_is_post_release(v100: Version, v100post1: Version) -> None:
    assert not v100.is_post_release()
    assert v100post1.is_post_release()


def test_is_dev_release(v100dev1: Version, v100: Version) -> None:
    assert not v100.is_dev_release()
    assert v100dev1.is_dev_release()


def test_is_local(v100: Version, v100build1: Version) -> None:
    assert not v100.is_local()
    assert v100build1.is_local()


def test_is_unstable(
    v100dev1: Version, v100rc1: Version, v100: Version, v100build1: Version
) -> None:
    assert v100dev1.is_unstable()
    assert v100rc1.is_unstable()
    assert not v100.is_unstable()
    assert not v100build1.is_unstable()


def test_is_stable(v100dev1: Version, v100rc1: Version, v100: Version, v100build1: Version) -> None:
    assert not v100dev1.is_stable()
    assert not v100rc1.is_stable()
    assert v100.is_stable()
    assert v100build1.is_stable()


def test_next_pre(v100alpha0: Version, v100rc0: Version, v100rc1: Version, v100: Version) -> None:
    assert v100.next_pre() == v100alpha0
    assert v100rc0.next_pre() == v100rc1


def test_next_pre_phase(
    v100alpha0: Version, v100beta1: Version, v100rc0: Version, v100rc1: Version, v100: Version
) -> None:
    assert v100.next_pre_phase() == v100alpha0
    assert v100beta1.next_pre_phase() == v100rc0
    assert v100rc1.next_pre_phase() is None


def test_next_post(v100: Version, v100post0: Version, v100post1: Version) -> None:
    assert v100.next_post() == v100post0
    assert v100post0.next_post() == v100post1


def test_next_dev(v100dev0: Version, v100dev1: Version, v100: Version) -> None:
    assert v100.next_dev() == v100dev0
    assert v100dev0.next_dev() == v100dev1


def test_with_pre(v100rc1: Version, v100: Version, rc1: PreTag) -> None:
    assert v100.with_pre(rc1) == v100rc1


def test_with_post(v100: Version, v100post1: Version, post1: PostTag) -> None:
    assert v100.with_post(post1) == v100post1


def test_with_dev(v100dev1: Version, v100: Version, dev1: DevTag) -> None:
    assert v100.with_dev(dev1) == v100dev1


def test_with_local(v100: Version, v100build1: Version, build1: Local) -> None:
    assert v100.with_local(build1) == v100build1


def test_without_pre(v100rc1: Version, v100: Version) -> None:
    assert v100rc1.without_pre() == v100


def test_without_post(v100: Version, v100post1: Version) -> None:
    assert v100post1.without_post() == v100


def test_without_dev(v100dev1: Version, v100: Version) -> None:
    assert v100dev1.without_dev() == v100


def test_without_local(v100: Version, v100build1: Version) -> None:
    assert v100build1.without_local() == v100


def test_to_stable(
    v100dev1: Version, v100rc1: Version, v100: Version, v100build1: Version, v100post1: Version
) -> None:
    assert v100.to_stable() == v100
    assert v100rc1.to_stable() == v100
    assert v100dev1.to_stable() == v100

    assert v100build1.to_stable() == v100build1
    assert v100post1.to_stable() == v100post1


@pytest.mark.parametrize(
    ("version", "next_breaking"),
    (  # taken from the `next_breaking` table
        (Version.from_parts(1, 2, 3), Version.from_parts(2, 0, 0)),
        (Version.from_parts(1, 2, 0), Version.from_parts(2, 0, 0)),
        (Version.from_parts(1, 0, 0), Version.from_parts(2, 0, 0)),
        (Version.from_parts(0, 2, 3), Version.from_parts(0, 3, 0)),
        (Version.from_parts(0, 0, 3), Version.from_parts(0, 0, 4)),
        (Version.from_parts(0, 0, 0), Version.from_parts(0, 0, 1)),
        (Version.from_parts(0, 0), Version.from_parts(0, 1, 0)),
        (Version.from_parts(0), Version.from_parts(1, 0, 0)),
    ),
)
def test_next_breaking(version: Version, next_breaking: Version) -> None:
    assert version.next_breaking() == next_breaking


def test_normalize(v100candidate0rev0dev0: Version, v100rc0post0dev0: Version) -> None:
    assert v100candidate0rev0dev0.normalize() == v100rc0post0dev0


V1E100A1POST1DEV1BUILD1 = "1!1.0.0-alpha.1-post.1-dev.1+build.1"
V1E100A1POST1DEV1BUILD1_SHORT = "1!1.0.0a1.post1.dev1+build.1"


def test_to_string(v1e100alpha1post1dev1build1: Version) -> None:
    assert v1e100alpha1post1dev1build1.to_string() == V1E100A1POST1DEV1BUILD1


def test_to_short_string(v1e100alpha1post1dev1build1: Version) -> None:
    assert v1e100alpha1post1dev1build1.to_short_string() == V1E100A1POST1DEV1BUILD1_SHORT
