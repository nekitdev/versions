from typing import Any, Iterator, Optional, Tuple, Type, TypeVar, Union

from attrs import evolve, field, frozen

from versions.constants import DASH, DOT, EXCLAMATION, PLUS
from versions.parsers import VersionParser
from versions.representation import Representation
from versions.segments import (
    DEFAULT_PADDING,
    DEFAULT_VALUE,
    DevTag,
    Epoch,
    Extra,
    Local,
    PostTag,
    PreTag,
    Release,
)
from versions.specification import Specification
from versions.string import FromString, ToString, concat_empty
from versions.types import AnyInfinity, Infinity, NegativeInfinity, infinity, negative_infinity
from versions.utils import evolve_in_place

__all__ = ("CompareKey", "Version")

CompareEpoch = Epoch
CompareRelease = Release
ComparePreTag = Union[PreTag, AnyInfinity]
ComparePostTag = Union[PostTag, NegativeInfinity]
CompareDevTag = Union[DevTag, Infinity]
CompareLocal = Union[Local, NegativeInfinity]

CompareKey = Tuple[
    CompareEpoch,
    CompareRelease,
    ComparePreTag,
    ComparePostTag,
    CompareDevTag,
    CompareLocal,
]

V = TypeVar("V", bound="Version")
W = TypeVar("W", bound="Version")


@frozen(repr=False, eq=True, order=True)
class Version(Representation, FromString, ToString):
    """Represents versions."""

    epoch: Epoch = field(factory=Epoch, eq=False, order=False)
    release: Release = field(factory=Release, eq=False, order=False)
    pre: Optional[PreTag] = field(default=None, eq=False, order=False)
    post: Optional[PostTag] = field(default=None, eq=False, order=False)
    dev: Optional[DevTag] = field(default=None, eq=False, order=False)
    local: Optional[Local] = field(default=None, eq=False, order=False)

    compare_key: CompareKey = field(repr=False, init=False, eq=True, order=True)

    def __attrs_post_init__(self) -> None:
        evolve_in_place(self, compare_key=self.compute_compare_key())

    @staticmethod
    def compute_compare_tags(
        pre: Optional[PreTag], post: Optional[PostTag], dev: Optional[DevTag]
    ) -> Tuple[ComparePreTag, ComparePostTag, CompareDevTag]:
        compare_pre: ComparePreTag
        compare_post: ComparePostTag
        compare_dev: CompareDevTag

        if pre is None:
            if post is None and dev is not None:
                compare_pre = negative_infinity

            else:
                compare_pre = infinity

        else:
            compare_pre = pre

        compare_post = negative_infinity if post is None else post
        compare_dev = infinity if dev is None else dev

        return (compare_pre, compare_post, compare_dev)

    @staticmethod
    def compute_compare_local(local: Optional[Local]) -> CompareLocal:
        return negative_infinity if local is None else local

    def compute_compare_key(self) -> CompareKey:
        compare_epoch = self.epoch
        compare_release = self.release

        compare_pre, compare_post, compare_dev = self.compute_compare_tags(
            self.pre, self.post, self.dev
        )

        compare_local = self.compute_compare_local(self.local)

        return (
            compare_epoch,
            compare_release,
            compare_pre,
            compare_post,
            compare_dev,
            compare_local,
        )

    def to_string_iterator(self) -> Iterator[str]:
        epoch = self.epoch

        if epoch:
            yield epoch.to_string()
            yield EXCLAMATION

        yield self.release.to_string()

        pre = self.pre

        if pre:
            yield DASH
            yield pre.to_string()

        post = self.post

        if post:
            yield DASH
            yield post.to_string()

        dev = self.dev

        if dev:
            yield DASH
            yield dev.to_string()

        local = self.local

        if local:
            yield PLUS
            yield local.to_string()

    def to_short_string_iterator(self) -> Iterator[str]:
        epoch = self.epoch

        if epoch:
            yield epoch.to_short_string()
            yield EXCLAMATION

        yield self.release.to_short_string()

        pre = self.pre

        if pre:
            yield pre.to_short_string()

        post = self.post

        if post:
            yield DOT
            yield post.to_short_string()

        dev = self.dev

        if dev:
            yield DOT
            yield dev.to_short_string()

        local = self.local

        if local:
            yield PLUS
            yield local.to_short_string()

    def to_string(self) -> str:
        return concat_empty(self.to_string_iterator())

    def to_short_string(self) -> str:
        return concat_empty(self.to_short_string_iterator())

    @classmethod
    def from_string(cls: Type[V], string: str) -> V:
        return VersionParser(cls).parse(string)

    @property
    def precision(self) -> int:
        return self.release.precision

    @property
    def last_index(self) -> int:
        return self.release.last_index

    @property
    def major(self) -> int:
        return self.release.major

    @property
    def minor(self) -> int:
        return self.release.minor

    @property
    def micro(self) -> int:
        return self.release.micro

    @property
    def patch(self) -> int:
        return self.release.patch

    @property
    def extra(self) -> Extra:
        return self.release.extra

    def get_major(self) -> int:
        return self.release.get_major()

    def get_minor(self) -> int:
        return self.release.get_minor()

    def get_micro(self) -> int:
        return self.release.get_micro()

    def get_patch(self) -> int:
        return self.release.get_patch()

    def get_extra(self) -> Extra:
        return self.release.get_extra()

    def get_at(self, index: int, default: int = DEFAULT_VALUE) -> int:
        return self.release.get_at(index, default)

    def get_at_unchecked(self, index: int) -> int:
        return self.release.get_at_unchecked(index)

    def is_semantic(self) -> bool:
        return self.release.is_semantic()

    def to_semantic(self: V) -> V:
        return self.update(release=self.release.to_semantic())

    def set_major(self: V, value: int) -> V:
        return self.update(release=self.release.set_major(value))

    def set_minor(self: V, value: int) -> V:
        return self.update(release=self.release.set_minor(value))

    def set_micro(self: V, value: int) -> V:
        return self.update(release=self.release.set_micro(value))

    def set_patch(self: V, value: int) -> V:
        return self.update(release=self.release.set_patch(value))

    def set_at(self: V, index: int, value: int) -> V:
        return self.update(release=self.release.set_at(index, value))

    def set_at_unchecked(self: V, index: int, value: int) -> V:
        return self.update(release=self.release.set_at_unchecked(index, value))

    def next_major(self: V) -> V:
        release = self.release

        if self.is_stable():
            release = release.next_major()

        return self.create(self.epoch, release)

    def next_minor(self: V) -> V:
        release = self.release

        if self.is_stable():
            release = release.next_minor()

        return self.create(self.epoch, release)

    def next_micro(self: V) -> V:
        release = self.release

        if self.is_stable():
            release = release.next_micro()

        return self.create(self.epoch, release)

    def next_patch(self: V) -> V:
        release = self.release

        if self.is_stable():
            release = release.next_patch()

        return self.create(self.epoch, release)

    def next_at(self: V, index: int) -> V:
        release = self.release

        if self.is_stable():
            release = release.next_at(index)

        return self.create(self.epoch, release)

    def has_major(self) -> bool:
        return self.release.has_major()

    def has_minor(self) -> bool:
        return self.release.has_minor()

    def has_micro(self) -> bool:
        return self.release.has_micro()

    def has_patch(self) -> bool:
        return self.release.has_patch()

    def has_extra(self) -> bool:
        return self.release.has_extra()

    def has_at(self, index: int) -> bool:
        return self.has_at(index)

    def pad_to(self: V, length: int, padding: int = DEFAULT_PADDING) -> V:
        return evolve(self, release=self.release.pad_to(length, padding))

    def pad_to_index(self: V, index: int, padding: int = DEFAULT_PADDING) -> V:
        return evolve(self, release=self.release.pad_to_index(index, padding))

    def pad_to_next(self: V, padding: int = DEFAULT_PADDING) -> V:
        return evolve(self, release=self.release.pad_to_next(padding))

    def is_pre_release(self) -> bool:
        return self.pre is not None

    def is_post_release(self) -> bool:
        return self.post is not None

    def is_dev_release(self) -> bool:
        return self.dev is not None

    def is_local(self) -> bool:
        return self.local is not None

    def is_not_pre_release(self) -> bool:
        return self.pre is None

    def is_not_post_release(self) -> bool:
        return self.post is None

    def is_not_dev_release(self) -> bool:
        return self.dev is None

    def is_not_local(self) -> bool:
        return self.local is None

    def is_unstable(self) -> bool:
        return self.is_pre_release() or self.is_dev_release()

    def is_stable(self) -> bool:
        return self.is_not_pre_release() and self.is_not_dev_release()

    def next_pre(self: V) -> V:
        pre = self.pre

        if pre is None:
            pre = PreTag()

        else:
            pre = pre.next()

        return self.create(self.epoch, self.release, pre)

    def next_pre_phase(self: V) -> Optional[V]:
        pre = self.pre

        if pre is None:
            pre = PreTag()

        else:
            pre = pre.next_phase()

            if pre is None:
                return None

        return self.create(self.epoch, self.release, pre)

    def next_post(self: V) -> V:
        post = self.post

        if post is None:
            post = PostTag()

        else:
            post = post.next()

        return self.create(self.epoch, self.release, self.pre, post, self.dev)

    def next_dev(self: V) -> V:
        dev = self.dev

        if dev is None:
            dev = DevTag()

        else:
            dev = dev.next()

        return self.create(self.epoch, self.release, self.pre, self.post, dev)

    def with_pre(self: V, pre: PreTag) -> V:
        return self.update(pre=pre)

    def with_post(self: V, post: PostTag) -> V:
        return self.update(post=post)

    def with_dev(self: V, dev: DevTag) -> V:
        return self.update(dev=dev)

    def with_local(self: V, local: Local) -> V:
        return self.update(local=local)

    def without_pre(self: V) -> V:
        return self.update(pre=None)

    def without_post(self: V) -> V:
        return self.update(post=None)

    def without_dev(self: V) -> V:
        return self.update(dev=None)

    def without_local(self: V) -> V:
        return self.update(local=None)

    def update(self: V, **changes: Any) -> V:
        return evolve(self, **changes)

    def weaken(self, other: W) -> W:
        if not self.is_local() and other.is_local():
            other = other.without_local()

        if not self.is_post_release() and other.is_post_release():
            other = other.without_post()

        return other

    def to_stable(self: V) -> V:
        return self if self.is_stable() else self.create(self.epoch, self.release)

    def next_breaking(self: V) -> V:
        """Returns the next breaking version.

        This function is slightly convoluted due to how `0.x.y` versions are handled:

        | version | next breaking |
        |---------|---------------|
        | `1.2.3` | `2.0.0`       |
        | `1.2.0` | `2.0.0`       |
        | `1.0.0` | `2.0.0`       |
        | `0.2.3` | `0.3.0`       |
        | `0.0.3` | `0.0.4`       |
        | `0.0.0` | `0.0.1`       |
        | `0.0`   | `0.1.0`       |
        | `0`     | `1.0.0`       |

        Returns:
            The next breaking [`Version`][versions.version.Version].
        """
        if not self.major:
            if self.minor:
                return self.next_minor()

            if self.has_micro():
                return self.next_micro()

            if self.has_minor():
                return self.next_minor()

            return self.next_major()

        return self.to_stable().next_major()

    def normalize(self: V) -> V:
        pre = self.pre

        if pre:
            pre = pre.normalize()

        post = self.post

        if post:
            post = post.normalize()

        dev = self.dev

        if dev:
            dev = dev.normalize()

        return self.update(pre=pre, post=post, dev=dev)

    @classmethod
    def create(
        cls: Type[V],
        epoch: Optional[Epoch] = None,
        release: Optional[Release] = None,
        pre: Optional[PreTag] = None,
        post: Optional[PostTag] = None,
        dev: Optional[DevTag] = None,
        local: Optional[Local] = None,
    ) -> V:
        if epoch is None:
            epoch = Epoch()

        if release is None:
            release = Release()

        return cls(epoch, release, pre, post, dev, local)

    @classmethod
    def from_parts(
        cls: Type[V],
        major: int = DEFAULT_VALUE,
        minor: int = DEFAULT_VALUE,
        micro: int = DEFAULT_VALUE,
        *extra: int,
        epoch: Optional[Epoch] = None,
        pre: Optional[PreTag] = None,
        post: Optional[PostTag] = None,
        dev: Optional[DevTag] = None,
        local: Optional[Local] = None,
    ) -> V:
        release = Release.from_parts(major, minor, micro, *extra)

        return cls.create(epoch, release, pre, post, dev, local)

    def matches(self, specification: Specification) -> bool:
        return specification.accepts(self)
