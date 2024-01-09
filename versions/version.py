from typing import Iterator, Optional, Tuple, Union

from attrs import evolve, field, frozen
from typing_extensions import Self

from versions.constants import DASH, DOT, EXCLAMATION, PLUS
from versions.parsers import VersionParser
from versions.representation import Representation
from versions.segments.constants import DEFAULT_PADDING, DEFAULT_VALUE
from versions.segments.epoch import Epoch
from versions.segments.local import Local
from versions.segments.release import Release
from versions.segments.tags import DevTag, PostTag, PreTag
from versions.segments.typing import Extra, LocalPart

from versions.specification import Specification
from versions.string import String, concat_empty
from versions.types import AnyInfinity, Infinity, NegativeInfinity, infinity, negative_infinity

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


@frozen(repr=False, eq=True, order=True)
class Version(Representation, String):
    """Represents versions."""

    epoch: Epoch = field(factory=Epoch, eq=False, order=False)
    """The *epoch* segment of the version."""

    release: Release = field(factory=Release, eq=False, order=False)
    """The *release* segment of the version."""

    pre: Optional[PreTag] = field(default=None, eq=False, order=False)
    """The *pre-release* tag of the version."""

    post: Optional[PostTag] = field(default=None, eq=False, order=False)
    """The *post-release* tag of the version."""

    dev: Optional[DevTag] = field(default=None, eq=False, order=False)
    """The *dev-release* tag of the version."""

    local: Optional[Local] = field(default=None, eq=False, order=False)
    """The *local* segment of the version."""

    compare_key: CompareKey = field(repr=False, init=False, eq=True, order=True, hash=False)

    @compare_key.default
    def default_compare_key(self) -> CompareKey:
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

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Parses a [`Version`][versions.version.Version] from `string`.

        Arguments:
            string: The string to parse.

        Returns:
            The parsed version.
        """
        return VersionParser(cls).parse(string)

    def to_string_iterator(self) -> Iterator[str]:
        epoch = self.epoch

        if epoch:
            yield epoch.to_string()
            yield EXCLAMATION

        yield self.release.to_string()

        pre = self.pre

        if pre is not None:
            yield DASH
            yield pre.to_string()

        post = self.post

        if post is not None:
            yield DASH
            yield post.to_string()

        dev = self.dev

        if dev is not None:
            yield DASH
            yield dev.to_string()

        local = self.local

        if local is not None:
            yield PLUS
            yield local.to_string()

    def to_short_string_iterator(self) -> Iterator[str]:
        epoch = self.epoch

        if epoch:
            yield epoch.to_short_string()
            yield EXCLAMATION

        yield self.release.to_short_string()

        pre = self.pre

        if pre is not None:
            yield pre.to_short_string()

        post = self.post

        if post is not None:
            yield DOT
            yield post.to_short_string()

        dev = self.dev

        if dev is not None:
            yield DOT
            yield dev.to_short_string()

        local = self.local

        if local is not None:
            yield PLUS
            yield local.to_short_string()

    def to_string(self) -> str:
        """Converts a [`Version`][versions.version.Version] to its string representation.

        Returns:
            The version string.
        """
        return concat_empty(self.to_string_iterator())

    def to_short_string(self) -> str:
        """Converts a [`Version`][versions.version.Version] to its *short* string representation.

        Returns:
            The *short* version string.
        """
        return concat_empty(self.to_short_string_iterator())

    def to_pep440_string(self) -> str:
        """Converts a [`Version`][versions.version.Version] to its
        [*PEP 440*](https://peps.python.org/pep-0440) representation.

        ```python
        version.to_pep440_string()
        ```

        Is equivalent to the following:

        ```python
        version.normalize().to_short_string()
        ```

        Returns:
            The [*PEP 440*](https://peps.python.org/pep-0440) version string.
        """
        return self.normalize().to_short_string()

    @property
    def precision(self) -> int:
        """The precision of the [`Release`][versions.segments.release.Release]."""
        return self.release.precision

    @property
    def last_index(self) -> int:
        """The last index of the [`Release`][versions.segments.release.Release]."""
        return self.release.last_index

    @property
    def major(self) -> int:
        """The *major* part of the [`Release`][versions.segments.release.Release]."""
        return self.release.major

    @property
    def minor(self) -> int:
        """The *minor* part of the [`Release`][versions.segments.release.Release]."""
        return self.release.minor

    @property
    def micro(self) -> int:
        """The *micro* part of the [`Release`][versions.segments.release.Release]."""
        return self.release.micro

    @property
    def patch(self) -> int:
        """The *patch* part of the [`Release`][versions.segments.release.Release].

        This is equivalent to [`micro`][versions.version.Version.micro].
        """
        return self.release.patch

    @property
    def extra(self) -> Extra:
        """The *extra* parts of the [`Release`][versions.segments.release.Release]."""
        return self.release.extra

    def get_at(self, index: int, default: int = DEFAULT_VALUE) -> int:
        """Gets the [`Release`][versions.segments.release.Release] part at the `index`,
        defaulting to `default`.

        Arguments:
            index: The index of the part to get.
            default: The default value to use.

        Returns:
            The release part at `index` or the `default` value.
        """
        return self.release.get_at(index, default)

    def get_at_unchecked(self, index: int) -> int:
        """Gets the [`Release`][versions.segments.Release] part at the `index`.

        Arguments:
            index: The index of the part to get.

        Raises:
            IndexError: The index is *out-of-bounds*.

        Returns:
            The release part at the `index`.
        """
        return self.release.get_at_unchecked(index)

    def is_semantic(self) -> bool:
        """Checks if the [`Release`][versions.segments.Release]
        matches the *semantic versioning* schema.

        Returns:
            Whether the release matches the [`SemVer`](https://semver.org/) schema.
        """
        return self.release.is_semantic()

    def to_semantic(self) -> Self:
        """Converts the [`Release`][versions.segments.Release]
        to match the [`SemVer`](https://semver.org/) schema.

        Returns:
            The converted version.
        """
        return evolve(self, release=self.release.to_semantic())

    def set_epoch(self, epoch: Epoch) -> Self:
        return evolve(self, epoch=epoch)

    def set_epoch_value(self, value: int) -> Self:
        return self.set_epoch(self.epoch.set_value(value))

    def set_release(self, release: Release) -> Self:
        return evolve(self, release=release)

    def set_release_parts(self, *parts: int) -> Self:
        return self.set_release(self.release.set_parts(*parts))

    def slice(self, index: int) -> Self:
        return self.set_release(self.release.slice(index))

    def set_major(self, value: int) -> Self:
        """Sets the *major* part of the [`Release`][versions.segments.Release] to the `value`.

        Arguments:
            value: The value to set the *major* part to.

        Returns:
            The updated version.
        """
        return self.set_release(self.release.set_major(value))

    def set_minor(self, value: int) -> Self:
        """Sets the *minor* part of the [`Release`][versions.segments.Release] to the `value`.

        Arguments:
            value: The value to set the *minor* part to.

        Returns:
            The updated version.
        """
        return self.set_release(self.release.set_minor(value))

    def set_micro(self, value: int) -> Self:
        """Sets the *micro* part of the [`Release`][versions.segments.Release] to the `value`.

        Arguments:
            value: The value to set the *micro* part to.

        Returns:
            The updated version.
        """
        return self.set_release(self.release.set_micro(value))

    def set_patch(self, value: int) -> Self:
        """Sets the *patch* part of the [`Release`][versions.segments.Release] to the `value`.

        This is equivalent to [`set_micro`][versions.version.Version.set_micro].

        Arguments:
            value: The value to set the *patch* part to.

        Returns:
            The updated version.
        """
        return self.set_release(self.release.set_patch(value))

    def set_at(self, index: int, value: int) -> Self:
        """Sets the [`Release`][versions.segments.Release] part at the `index` to the `value`.

        Arguments:
            index: The index to set the `value` at.
            value: The value to set the part to.

        Returns:
            The updated version.
        """
        return self.set_release(self.release.set_at(index, value))

    def set_at_unchecked(self, index: int, value: int) -> Self:
        """Sets the [`Release`][versions.segments.Release] part at the `index` to the `value`.

        Arguments:
            index: The index to set the `value` at.
            value: The value to set the part to.

        Raises:
            IndexError: The index is *out-of-bounds*.

        Returns:
            The updated version.
        """
        return self.set_release(self.release.set_at_unchecked(index, value))

    def next_epoch(self) -> Self:
        return self.set_epoch(self.epoch.next_value())

    def next_major(self) -> Self:
        """Bumps the *major* part of the [`Release`][versions.segments.Release]
        if the version is stable, otherwise converts the version to be stable.

        Returns:
            The bumped version.
        """
        release = self.release

        if self.is_stable():
            release = release.next_major()

        return self.without_tags_and_local().set_release(release)

    def next_minor(self) -> Self:
        """Bumps the *minor* part of the [`Release`][versions.segments.Release]
        if the version is stable, otherwise converts the version to be stable.

        Returns:
            The bumped version.
        """
        release = self.release

        if self.is_stable():
            release = release.next_minor()

        return self.without_tags_and_local().set_release(release)

    def next_micro(self) -> Self:
        """Bumps the *micro* part of the [`Release`][versions.segments.Release]
        if the version is stable, otherwise converts the version to be stable.

        Returns:
            The bumped version.
        """
        release = self.release

        if self.is_stable():
            release = release.next_micro()

        return self.without_tags_and_local().set_release(release)

    def next_patch(self) -> Self:
        """Bumps the *patch* part of the [`Release`][versions.segments.Release]
        if the version is stable, otherwise converts the version to be stable.

        This is equivalent to [`next_micro`][versions.version.Version.next_micro].

        Returns:
            The bumped version.
        """
        release = self.release

        if self.is_stable():
            release = release.next_patch()

        return self.without_tags_and_local().set_release(release)

    def next_at(self, index: int) -> Self:
        """Bumps the part of the [`Release`][versions.segments.Release] at the `index`
        if the version is stable, otherwise converts the version to be stable.

        Arguments:
            index: The index to bump the part at.

        Returns:
            The bumped version.
        """
        release = self.release

        if self.is_stable():
            release = release.next_at(index)

        return self.without_tags_and_local().set_release(release)

    def has_major(self) -> bool:
        """Checks if the [`Release`][versions.segments.Release] has the *major* part.

        Returns:
            Whether the *major* part is present.
        """
        return self.release.has_major()

    def has_minor(self) -> bool:
        """Checks if the [`Release`][versions.segments.Release] has the *minor* part.

        Returns:
            Whether the *minor* part is present.
        """
        return self.release.has_minor()

    def has_micro(self) -> bool:
        """Checks if the [`Release`][versions.segments.Release] has the *micro* part.

        Returns:
            Whether the *micro* part is present.
        """
        return self.release.has_micro()

    def has_patch(self) -> bool:
        """Checks if the [`Release`][versions.segments.Release] has the *patch* part.

        This is equivalent to [`has_micro`][versions.version.Version.has_micro].

        Returns:
            Whether the *patch* part is present.
        """
        return self.release.has_patch()

    def has_extra(self) -> bool:
        """Checks if the [`Release`][versions.segments.Release] has any *extra* parts.

        Returns:
            Whether the *extra* parts are present.
        """
        return self.release.has_extra()

    def has_at(self, index: int) -> bool:
        """Checks if the [`Release`][versions.segments.Release] has a part at the `index`.

        Returns:
            Whether the part at the `index` is present.
        """
        return self.release.has_at(index)

    def pad_to(self, length: int, padding: int = DEFAULT_PADDING) -> Self:
        """Pads the [`Release`][versions.segments.Release] to the `length` with `padding`.

        Arguments:
            length: The length to pad the release to.
            padding: The padding to use.

        Returns:
            The padded version.
        """
        return self.set_release(self.release.pad_to(length, padding))

    def pad_to_index(self, index: int, padding: int = DEFAULT_PADDING) -> Self:
        """Pads the [`Release`][versions.segments.Release] to the `index` with `padding`.

        Arguments:
            index: The index to pad the release to.
            padding: The padding to use.

        Returns:
            The padded version.
        """
        return self.set_release(self.release.pad_to_index(index, padding))

    def pad_to_next(self, padding: int = DEFAULT_PADDING) -> Self:
        """Pads the [`Release`][versions.segments.Release] to the next index.

        Arguments:
            padding: The padding to use.

        Returns:
            The padded version.
        """
        return self.set_release(self.release.pad_to_next(padding))

    def is_pre_release(self) -> bool:
        """Checks if the version is *pre-release*.

        Returns:
            Whether the version is *pre-release*.
        """
        return self.pre is not None

    def is_post_release(self) -> bool:
        """Checks if the version is *post-release*.

        Returns:
            Whether the version is *post-release*.
        """
        return self.post is not None

    def is_dev_release(self) -> bool:
        """Checks if the version is *dev-release*.

        Returns:
            Whether the version is *dev-release*.
        """
        return self.dev is not None

    def is_local(self) -> bool:
        """Checks if the version is *local*.

        Returns:
            Whether the version is *local*.
        """
        return self.local is not None

    def is_unstable(self) -> bool:
        """Checks if the version is *unstable*.

        Returns:
            Whether the version is *unstable*.
        """
        return self.is_pre_release() or self.is_dev_release()

    def is_stable(self) -> bool:
        """Checks if the version is *stable*.

        Returns:
            Whether the version is *stable*.
        """
        return not self.is_unstable()

    def next_pre(self) -> Self:
        """Bumps the [`PreTag`][versions.segments.PreTag] if it is present,
        otherwise adds one to the version.

        Returns:
            The bumped version.
        """
        pre = self.pre

        if pre is None:
            pre = PreTag()

        else:
            pre = pre.next()

        return self.without_tags_and_local().with_pre(pre)

    def next_pre_phase(self) -> Optional[Self]:
        """Bumps the [`PreTag`][versions.segments.PreTag] phase if it is present (and if possible),
        otherwise adds one to the version.

        Returns:
            The bumped version (if the next [`PreTag`][versions.segments.PreTag] is present).
        """
        pre = self.pre

        if pre is None:
            pre = PreTag()

        else:
            pre = pre.next_phase()

            if pre is None:
                return None

        return self.without_tags_and_local().with_pre(pre)

    def next_post(self) -> Self:
        """Bumps the [`PostTag`][versions.segments.PostTag] if it is present,
        otherwise adds one to the version.

        Returns:
            The bumped version.
        """
        post = self.post

        if post is None:
            post = PostTag()

        else:
            post = post.next()

        return self.with_post(post).without_dev_and_local()

    def next_dev(self) -> Self:
        """Bumps the [`DevTag`][versions.segments.DevTag] if it is present,
        otherwise adds one to the version.

        Returns:
            The bumped version.
        """
        dev = self.dev

        if dev is None:
            dev = DevTag()

        else:
            dev = dev.next()

        return self.with_dev(dev).without_local()

    def set_pre(self, pre: Optional[PreTag]) -> Self:
        return evolve(self, pre=pre)

    def set_post(self, post: Optional[PostTag]) -> Self:
        return evolve(self, post=post)

    def set_dev(self, dev: Optional[DevTag]) -> Self:
        return evolve(self, dev=dev)

    def set_tags(
        self, pre: Optional[PreTag], post: Optional[PostTag], dev: Optional[DevTag]
    ) -> Self:
        return evolve(self, pre=pre, post=post, dev=dev)

    def set_local(self, local: Optional[Local]) -> Self:
        return evolve(self, local=local)

    def set_local_parts(self, *parts: LocalPart) -> Self:
        local = self.local

        local = Local.from_parts(*parts) if local is None else local.set_parts(*parts)

        return self.set_local(local)

    def set_dev_and_local(self, dev: Optional[DevTag], local: Optional[Local]) -> Self:
        return evolve(self, dev=dev, local=local)

    def set_tags_and_local(
        self,
        pre: Optional[PreTag],
        post: Optional[PostTag],
        dev: Optional[DevTag],
        local: Optional[Local],
    ) -> Self:
        return evolve(self, pre=pre, post=post, dev=dev, local=local)

    def with_pre(self, pre: PreTag) -> Self:
        """Updates a version to include [`PreTag`][versions.segments.PreTag].

        Arguments:
            pre: The *pre-release* tag to include.

        Returns:
            The updated version.
        """
        return self.set_pre(pre)

    def with_post(self, post: PostTag) -> Self:
        """Updates a version to include [`PostTag`][versions.segments.PostTag].

        Arguments:
            post: The *post-release* tag to include.

        Returns:
            The updated version.
        """
        return self.set_post(post)

    def with_dev(self, dev: DevTag) -> Self:
        """Updates a version to include [`DevTag`][versions.segments.DevTag].

        Arguments:
            dev: The *dev-release* tag to include.

        Returns:
            The updated version.
        """
        return self.set_dev(dev)

    def with_tags(self, pre: PreTag, post: PostTag, dev: DevTag) -> Self:
        return self.set_tags(pre, post, dev)

    def with_local(self, local: Local) -> Self:
        """Updates a version to include [`Local`][versions.segments.Local].

        Arguments:
            local: The *local* segment to include.

        Returns:
            The updated version.
        """
        return self.set_local(local)

    def with_dev_and_local(self, dev: DevTag, local: Local) -> Self:
        return self.set_dev_and_local(dev, local)

    def with_tags_and_local(self, pre: PreTag, post: PostTag, dev: DevTag, local: Local) -> Self:
        return self.set_tags_and_local(pre, post, dev, local)

    def without_pre(self) -> Self:
        """Updates a version, removing any [`PreTag`][versions.segments.PreTag] from it.

        Returns:
            The updated version.
        """
        return self.set_pre(None)

    def without_post(self) -> Self:
        """Updates a version, removing any [`PostTag`][versions.segments.PostTag] from it.

        Returns:
            The updated version.
        """
        return self.set_post(None)

    def without_dev(self) -> Self:
        """Updates a version, removing any [`DevTag`][versions.segments.DevTag] from it.

        Returns:
            The updated version.
        """
        return self.set_dev(None)

    def without_tags(self) -> Self:
        return self.set_tags(None, None, None)

    def without_local(self) -> Self:
        """Updates a version, removing any [`Local`][versions.segments.Local] segment from it.

        Returns:
            The updated version.
        """
        return self.set_local(None)

    def without_dev_and_local(self) -> Self:
        return self.set_dev_and_local(None, None)

    def without_tags_and_local(self) -> Self:
        return self.set_tags_and_local(None, None, None, None)

    def weaken(self, other: Self) -> Self:
        """Weakens the `other` version for further comparison.

        Arguments:
            other: The version to weaken.

        Returns:
            The weakened version.
        """
        if not self.is_local() and other.is_local():
            other = other.without_local()

        if not self.is_post_release() and other.is_post_release():
            other = other.without_post()

        return other

    def to_stable(self) -> Self:
        """Forces a version to be stable.

        Returns:
            The stable version.
        """
        return self if self.is_stable() else self.to_stable_unchecked()

    def to_stable_unchecked(self) -> Self:
        """Forces a version to be stable, without checking whether it is already stable.

        Returns:
            The stable version.
        """
        return self.without_tags_and_local()

    def next_breaking(self) -> Self:
        """Returns the next breaking version.

        This function is slightly convoluted due to how `0.x.y` and `0.0.z` versions are handled:

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

    def normalize(self) -> Self:
        """Normalizes all version tags.

        Returns:
            The normalized version.
        """
        pre = self.pre

        if pre is not None:
            pre = pre.normalize()

        post = self.post

        if post is not None:
            post = post.normalize()

        dev = self.dev

        if dev is not None:
            dev = dev.normalize()

        return self.set_tags(pre, post, dev)

    @classmethod
    def create(
        cls,
        epoch: Optional[Epoch] = None,
        release: Optional[Release] = None,
        pre: Optional[PreTag] = None,
        post: Optional[PostTag] = None,
        dev: Optional[DevTag] = None,
        local: Optional[Local] = None,
    ) -> Self:
        """Creates a [`Version`][versions.version.Version] from `epoch`, `release`,
        `pre`, `post`, `dev` and `local`.

        Arguments:
            epoch: The *epoch* to use.
            release: The *release* to use.
            pre: The *pre-release* tag to use.
            post: The *post-release* tag to use.
            dev: The *dev-release* tag to use.
            local: The *local* segment to use.

        Returns:
            The newly created [`Version`][versions.version.Version].
        """

        if epoch is None:
            epoch = Epoch()

        if release is None:
            release = Release()

        return cls(epoch, release, pre, post, dev, local)

    @classmethod
    def from_parts(
        cls,
        *parts: int,
        epoch: Optional[Epoch] = None,
        pre: Optional[PreTag] = None,
        post: Optional[PostTag] = None,
        dev: Optional[DevTag] = None,
        local: Optional[Local] = None,
    ) -> Self:
        """Creates a [`Version`][versions.version.Version] from `parts`,
        `epoch`, `pre`, `post`, `dev` and `local`.

        Arguments:
            *parts: The parts of the *release* to use.
            epoch: The *epoch* to use.
            pre: The *pre-release* tag to use.
            post: The *post-release* tag to use.
            dev: The *dev-release* tag to use.
            local: The *local* segment to use.

        Returns:
            The newly created [`Version`][versions.version.Version].
        """
        release = Release(parts)

        return cls.create(epoch, release, pre, post, dev, local)

    def matches(self, specification: Specification) -> bool:
        """Checks if a version matches the `specification`.

        Arguments:
            specification: The specification to check the version against.

        Returns:
            Whether the version matches the specification.
        """
        return specification.accepts(self)
