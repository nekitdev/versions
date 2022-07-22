from __future__ import annotations

from typing import ClassVar, Iterable, Optional, Set, Tuple, Type, TypeVar, Union

from attrs import Attribute, evolve, field, frozen

from versions.constants import EMPTY
from versions.parsers import TagParser
from versions.phases import (
    PHASE_ALL_DEFAULT,
    PHASE_ALL_SET,
    PHASE_DEV_DEFAULT,
    PHASE_DEV_SET,
    PHASE_POST_DEFAULT,
    PHASE_POST_SET,
    PHASE_PRE_DEFAULT,
    PHASE_PRE_SET,
    PHASE_TO_NEXT,
    PHASE_TO_NORMAL,
    PHASE_TO_SHORT,
    SHORT_TO_PHASE,
)
from versions.representation import Representation
from versions.string import (
    FromString,
    ToString,
    case_fold,
    check_int,
    concat_dot,
    concat_dot_args,
    concat_empty_args,
    split_dot,
    split_separators,
)
from versions.types import NegativeInfinity, negative_infinity
from versions.typing import DynamicTuple, get_name, is_int
from versions.utils import count_leading_zeros, evolve_in_place, pad_to_length

__all__ = (
    # default values
    "DEFAULT_PARTS",
    "DEFAULT_VALUE",
    # useful release indexes
    "MAJOR",
    "MINOR",
    "MICRO",
    "PATCH",
    "TOTAL",
    # segments that compose versions
    "Epoch",
    "Release",
    "Tag",
    "PreTag",
    "PostTag",
    "DevTag",
    "Local",
    # various segment parts
    "Extra",
    "Parts",
    "LocalPart",
    "LocalParts",
    "local_part",
)

Parts = DynamicTuple[int]
Extra = DynamicTuple[int]

DEFAULT_PARTS = (0, 0, 0)  # makes sense as the default for semantic versions
"""The default parts of the [`Release`][versions.segments.Release]."""

DEFAULT_VALUE = 0
"""The default value to use."""

DEFAULT_PADDING = 0
"""The default padding to use."""

MAJOR = 0
MINOR = 1
MICRO = 2
TOTAL = 3

PATCH = MICRO  # alias

E = TypeVar("E", bound="Epoch")


@frozen(repr=False, eq=True, order=True)
class Epoch(Representation, FromString, ToString):
    """Represents the *epoch* segment of the version (`e!`)."""

    value: int = field(default=DEFAULT_VALUE)
    """The value of the epoch."""

    def __bool__(self) -> bool:
        return bool(self.value)

    @classmethod
    def create(cls: Type[E], value: int = DEFAULT_VALUE) -> E:
        """Creates an [`Epoch`][versions.segments.Epoch] from `value`.

        Arguments:
            value: The value of the epoch.

        Returns:
            The newly created [`Epoch`][versions.segments.Epoch].
        """
        return cls(value)

    @classmethod
    def from_string(cls: Type[E], string: str) -> E:
        """Parses an [`Epoch`][versions.segments.Epoch] from `string`.

        Arguments:
            string: The string to parse.

        Returns:
            The parsed epoch.
        """
        return cls(int(string))

    def to_string(self) -> str:
        """Converts an [`Epoch`][versions.segments.Epoch] to its string representation.

        Returns:
            The epoch string.
        """
        return str(self.value)


EMPTY_RELEASE = "release can not be empty"

R = TypeVar("R", bound="Release")


@frozen(repr=False, eq=True, order=True)
class Release(Representation, FromString, ToString):
    """Represents the *release* segment of the version (`x.y.z`)."""

    parts: Parts = field(default=DEFAULT_PARTS, eq=False, order=False)
    """The parts of the release."""

    compare_parts: Parts = field(repr=False, init=False, eq=True, order=True)

    @parts.validator
    def check_parts(self, attribute: Attribute[Parts], value: Parts) -> None:
        if not value:
            raise ValueError(EMPTY_RELEASE)

    def __attrs_post_init__(self) -> None:
        evolve_in_place(self, compare_parts=self.compute_compare_parts())

    def compute_compare_parts(self) -> Parts:
        parts = self.parts

        index = count_leading_zeros(reversed(parts))

        if index == self.precision:
            index -= 1

        return self.slice_parts(-index) if index else parts

    @classmethod
    def create(cls: Type[R], parts: Parts = DEFAULT_PARTS) -> R:
        """Creates a [`Release`][versions.segments.Release] from `parts`.

        Arguments:
            parts: The parts of the release.

        Returns:
            The newly created [`Release`][versions.segments.Release].
        """
        return cls(parts)

    @classmethod
    def from_iterable(cls: Type[R], iterable: Iterable[int]) -> R:
        """Creates a [`Release`][versions.segments.Release] from `iterable`.

        Arguments:
            iterable: The parts of the release in an iterable.

        Returns:
            The newly created [`Release`][versions.segments.Release].
        """
        return cls(tuple(iterable))

    @classmethod
    def from_parts(cls: Type[R], *parts: int) -> R:
        """Creates a [`Release`][versions.segments.Release] from `parts`.

        Arguments:
            *parts: The parts of the release.

        Returns:
            The newly created [`Release`][versions.segments.Release].
        """
        return cls(parts)

    def into_parts(self) -> Parts:
        """Converts [`Release`][versions.segments.Release] to its parts.

        Returns:
            The parts of the release.
        """
        return self.parts

    @property
    def precision(self) -> int:
        """The count of the release parts."""
        return len(self.parts)

    @property
    def last_index(self) -> int:
        """The index of the last release part."""
        return self.precision - 1

    @property
    def major(self) -> int:
        """The *major* part of the release."""
        return self.get_at(MAJOR)

    @property
    def minor(self) -> int:
        """The *minor* part of the release."""
        return self.get_at(MINOR)

    @property
    def micro(self) -> int:
        """The *micro* part of the release."""
        return self.get_at(MICRO)

    @property
    def patch(self) -> int:
        """The *patch* part of the release. This is equivalent to
        [`micro`][versions.segments.Release.micro].
        """
        return self.get_at(PATCH)

    @property
    def extra(self) -> Extra:
        """The *extra* parts of the release."""
        return self.parts[TOTAL:]

    def get_at(self, index: int, default: int = DEFAULT_VALUE) -> int:
        """Gets the release part at `index`, defaulting to `default`.

        Arguments:
            index: The index of the part to get.
            default: The default value to use.

        Returns:
            The release part at `index` or the `default` value.
        """
        return self.get_at_unchecked(index) if self.has_at(index) else default

    def get_at_unchecked(self, index: int) -> int:
        """Gets the release part at `index`.

        Arguments:
            index: The index of the part to get.

        Raises:
            IndexError: The index is *out-of-bounds*.

        Returns:
            The release part at `index`.
        """
        return self.parts[index]

    def is_semantic(self) -> bool:
        """Checks if the release matches the *semantic versioning* schema.

        Returns:
            Whether the release matches the [`semver`](https://semver.org/) schema.
        """
        return self.precision == TOTAL

    def to_semantic(self: R) -> R:
        """Converts the release to match the [`semver`](https://semver.org/) schema.

        Returns:
            The converted release.
        """
        if self.has_extra():
            return self.next_patch().slice(TOTAL)

        return self if self.is_semantic() else self.pad_to(TOTAL)

    def set_major(self: R, value: int) -> R:
        """Sets the *major* part of the release to the `value`.

        Arguments:
            value: The value to set the *major* part to.

        Returns:
            The updated release.
        """
        return self.set_at(MAJOR, value)

    def set_minor(self: R, value: int) -> R:
        """Sets the *minor* part of the release to the `value`.

        Arguments:
            value: The value to set the *minor* part to.

        Returns:
            The updated release.
        """
        return self.set_at(MINOR, value)

    def set_micro(self: R, value: int) -> R:
        """Sets the *micro* part of the release to the `value`.

        Arguments:
            value: The value to set the *micro* part to.

        Returns:
            The updated release.
        """
        return self.set_at(MICRO, value)

    def set_patch(self: R, value: int) -> R:
        """Sets the *patch* part of the release to the `value`.

        This is equivalent to [`set_micro`][versions.segments.Release.set_micro].

        Arguments:
            value: The value to set the *patch* part to.

        Returns:
            The updated release.
        """
        return self.set_at(PATCH, value)

    def set_at(self: R, index: int, value: int) -> R:
        """Sets the release part at the `index` to the `value`.

        Arguments:
            index: The index to set the `value` at.
            value: The value to set the part to.

        Returns:
            The updated release.
        """
        return self.pad_to_index(index).set_at_unchecked(index, value)

    def set_at_unchecked(self: R, index: int, value: int) -> R:
        """Sets the release part at the `index` to the `value`.

        Arguments:
            index: The index to set the `value` at.
            value: The value to set the part to.

        Raises:
            IndexError: The index is *out-of-bounds*.

        Returns:
            The updated release.
        """
        mutable = list(self.parts)
        mutable[index] = value

        return self.from_iterable(mutable)

    def next_major(self: R) -> R:
        """Bumps the *major* part of the release.

        Returns:
            The bumped release.
        """
        return self.next_at(MAJOR)

    def next_minor(self: R) -> R:
        """Bumps the *minor* part of the release.

        Returns:
            The bumped release.
        """
        return self.next_at(MINOR)

    def next_micro(self: R) -> R:
        """Bumps the *micro* part of the release.

        Returns:
            The bumped release.
        """
        return self.next_at(MICRO)

    def next_patch(self: R) -> R:
        """Bumps the *patch* part of the release.

        This is equivalent to [`next_micro`][versions.segments.Release.next_micro].

        Returns:
            The bumped release.
        """
        return self.next_at(PATCH)

    def next_at(self: R, index: int) -> R:
        """Bumps the part of the release at the `index`.

        Arguments:
            index: The index to bump the part at.

        Returns:
            The bumped release.
        """
        updated = self.set_at(index, self.get_at(index) + 1)

        return updated.slice(index + 1).pad_to(updated.precision)

    def has_major(self) -> bool:
        """Checks if the release has the *major* part.

        Returns:
            Whether the *major* part is present.
        """
        return self.has_at(MAJOR)

    def has_minor(self) -> bool:
        """Checks if the release has the *minor* part.

        Returns:
            Whether the *minor* part is present.
        """
        return self.has_at(MINOR)

    def has_micro(self) -> bool:
        """Checks if the release has the *micro* part.

        Returns:
            Whether the *micro* part is present.
        """
        return self.has_at(MICRO)

    def has_patch(self) -> bool:
        """Checks if the release has the *patch* part.

        This is equivalent to [`has_micro`][versions.segments.Release.has_micro].

        Returns:
            Whether the *patch* part is present.
        """
        return self.has_at(PATCH)

    def has_extra(self) -> bool:
        """Checks if the release has any *extra* parts.

        Returns:
            Whether the *extra* parts are present.
        """
        return self.has_at(TOTAL)

    def has_at(self, index: int) -> bool:
        """Checks if the release has a part at the `index`.

        Returns:
            Whether the part at the `index` is present.
        """
        return self.precision > index

    def pad_to(self: R, length: int, padding: int = DEFAULT_PADDING) -> R:
        """Pads a [`Release`][versions.segments.Release] to the `length` with `padding`.

        Arguments:
            length: The length to pad the release to.
            padding: The padding to use.

        Returns:
            The padded release.
        """
        if self.precision < length:
            return self.from_iterable(pad_to_length(length, padding, self.parts))

        return self

    def pad_to_index(self: R, index: int, padding: int = DEFAULT_PADDING) -> R:
        """Pads a [`Release`][versions.segments.Release] to the `index` with `padding`.

        Arguments:
            index: The index to pad the release to.
            padding: The padding to use.

        Returns:
            The padded release.
        """
        return self.pad_to(index + 1, padding)

    def pad_to_next(self: R, padding: int = DEFAULT_PADDING) -> R:
        """Pads a [`Release`][versions.segments.Release] to the next index.

        Arguments:
            padding: The padding to use.

        Returns:
            The padded release.
        """
        return self.pad_to(self.precision + 1, padding)

    def slice(self: R, stop: int) -> R:
        return self.create(self.slice_parts(stop))

    def slice_parts(self, stop: int) -> Parts:
        return self.parts[:stop]

    @classmethod
    def from_string(cls: Type[R], string: str) -> R:
        """Parses a [`Release`][versions.segments.Release] from `string`.

        Arguments:
            string: The string to parse.

        Returns:
            The parsed release.
        """
        return cls.from_iterable(map(int, split_dot(string)))

    def to_string(self) -> str:
        """Converts a [`Release`][versions.segments.Release] to its string representation.

        Returns:
            The release string.
        """
        return concat_dot(map(str, self.parts))


PHASE_NOT_ALLOWED = "phase `{}` is not allowed in `{}`"
CAN_NOT_PARSE = "can not parse `{}` to `{}`"

T = TypeVar("T", bound="Tag")


@frozen(repr=False, eq=True, order=True)
class Tag(Representation, FromString, ToString):
    """Represents various version *tags* (`tag.n`)."""

    DEFAULT_PHASE: ClassVar[str] = PHASE_ALL_DEFAULT
    PHASE_SET: ClassVar[Set[str]] = PHASE_ALL_SET

    phase: str = field(converter=case_fold)  # type: ignore
    """The phase of the release tag."""

    value: int = field(default=DEFAULT_VALUE)
    """The value of the release tag."""

    @phase.default
    def default_phase(self) -> str:
        return self.DEFAULT_PHASE

    @phase.validator
    def check_phase(self, attribute: Attribute[str], value: str) -> None:
        if value not in self.PHASE_SET:
            raise ValueError(PHASE_NOT_ALLOWED.format(value, get_name(type(self))))

    def __attrs_post_init__(self) -> None:
        evolve_in_place(self, phase=self.expand(self.phase))

    @staticmethod
    def expand(phase: str) -> str:
        return SHORT_TO_PHASE.get(phase, phase)

    @staticmethod
    def reduce(phase: str) -> str:
        return PHASE_TO_SHORT.get(phase, phase)

    @staticmethod
    def normalize_phase(phase: str) -> str:
        return PHASE_TO_NORMAL.get(phase, phase)

    @classmethod
    def create(cls: Type[T], phase: Optional[str] = None, value: int = DEFAULT_VALUE) -> T:
        """Creates a [`Tag`][versions.segments.Tag] from `phase` and `value`.

        Arguments:
            phase: The phase of the tag.
            value: The value of the tag.

        Returns:
            The newly created [`Tag`][versions.segments.Tag].
        """
        if phase is None:
            phase = cls.DEFAULT_PHASE

        return cls(phase, value)

    @classmethod
    def default_phase_with_value(cls: Type[T], value: int) -> T:
        """Creates a [`Tag`][versions.segments.Tag] from `value` with the default phase.

        Arguments:
            value: The value of the tag.

        Returns:
            The newly created [`Tag`][versions.segments.Tag].
        """
        return cls(cls.DEFAULT_PHASE, value)

    @property
    def short(self) -> str:
        """The *short* phase of the release."""
        return self.reduce(self.phase)

    @property
    def normal(self) -> str:
        """The *normalized* phase of the release."""
        return self.normalize_phase(self.phase)

    def normalize(self: T) -> T:
        """Normalizes the version tag.

        Returns:
            The normalized tag.
        """
        return evolve(self, phase=self.normal)

    def next(self: T) -> T:
        """Bumps the version tag.

        Returns:
            The next version tag.
        """
        return evolve(self, value=self.value + 1)

    def next_phase(self: T) -> Optional[T]:
        """Bumps the version tag phase, if possible.

        Returns:
            The next version tag, if present.
        """
        phase = PHASE_TO_NEXT.get(self.phase)

        return None if phase is None else self.create(phase)

    @classmethod
    def from_string(cls: Type[T], string: str) -> T:
        """Parses a [`Tag`][versions.segments.Tag] from `string`.

        Arguments:
            string: The string to parse.

        Returns:
            The parsed tag.
        """
        return TagParser(cls).parse(string)

    def to_string(self) -> str:
        """Converts a [`Tag`][versions.segments.Tag] to its string representation.

        Returns:
            The tag string.
        """
        return concat_dot_args(self.phase, str(self.value))

    def to_short_string(self) -> str:
        """Converts a [`Tag`][versions.segments.Tag] to its *short* string representation.

        Returns:
            The *short* tag string.
        """
        return concat_empty_args(self.short, str(self.value))


@frozen(repr=False, eq=True, order=True)
class PreTag(Tag):
    """Represents the *pre-release* tag of the version (`pre.n`)."""

    DEFAULT_PHASE = PHASE_PRE_DEFAULT
    PHASE_SET = PHASE_PRE_SET


@frozen(repr=False, eq=True, order=True)
class PostTag(Tag):
    """Represents the *post-release* tag of the version (`post.n`)."""

    DEFAULT_PHASE = PHASE_POST_DEFAULT
    PHASE_SET = PHASE_POST_SET


@frozen(repr=False, eq=True, order=True)
class DevTag(Tag):
    """Represents the *dev-release* tag of the version (`dev.n`)."""

    DEFAULT_PHASE = PHASE_DEV_DEFAULT
    PHASE_SET = PHASE_DEV_SET


LocalPart = Union[int, str]
LocalParts = DynamicTuple[LocalPart]

CompareLocalIntPart = Tuple[int, str]
CompareLocalStringPart = Tuple[NegativeInfinity, str]

CompareLocalPart = Union[CompareLocalIntPart, CompareLocalStringPart]
CompareLocalParts = DynamicTuple[CompareLocalPart]

EMPTY_LOCAL = "local can not be empty"

L = TypeVar("L", bound="Local")


def local_part(string: str) -> LocalPart:
    return int(string) if check_int(string) else string


@frozen(repr=False, eq=True, order=True)
class Local(Representation, FromString, ToString):
    """Represents the *local* segment of the version (`+abcdefg.n`)"""

    parts: LocalParts = field(eq=False, order=False)
    """The local segment parts."""

    compare_parts: CompareLocalParts = field(repr=False, init=False, eq=True, order=True)

    @parts.validator
    def check_parts(self, attribute: Attribute[LocalParts], value: LocalParts) -> None:
        if not value:
            raise ValueError(EMPTY_LOCAL)

    def __attrs_post_init__(self) -> None:
        evolve_in_place(self, compare_parts=self.compute_compare_parts())

    def compute_compare_parts(self) -> CompareLocalParts:
        empty = EMPTY

        return tuple(
            (part, empty) if is_int(part) else (negative_infinity, part)  # type: ignore
            for part in self.parts
        )

    @classmethod
    def create(cls: Type[L], parts: LocalParts) -> L:
        """Creates a [`Local`][versions.segments.Local] from local `parts`.

        Arguments:
            parts: The local parts.

        Returns:
            The newly created [`Local`][versions.segments.Local].
        """
        return cls(parts)

    @classmethod
    def from_iterable(cls: Type[L], iterable: Iterable[LocalPart]) -> L:
        """Creates a [`Local`][versions.segments.Local] from `iterable`.

        Arguments:
            iterable: The local parts in an iterable.

        Returns:
            The newly created [`Local`][versions.segments.Local].
        """
        return cls(tuple(iterable))

    @classmethod
    def from_parts(cls: Type[L], *parts: LocalPart) -> L:
        """Creates a [`Local`][versions.segments.Local] from local `parts`.

        Arguments:
            *parts: The local parts.

        Returns:
            The newly created [`Local`][versions.segments.Local].
        """
        return cls(parts)

    def into_parts(self) -> LocalParts:
        """Converts a [`Local`][versions.segments.Local] to its parts.

        Returns:
            The parts of the local segment.
        """
        return self.parts

    @classmethod
    def from_string(cls: Type[L], string: str) -> L:
        """Parses a [`Local`][versions.segments.Local] from `string`.

        Arguments:
            string: The string to parse.

        Returns:
            The parsed local segment.
        """
        return cls.from_iterable(map(local_part, split_separators(string)))

    def to_string(self) -> str:
        """Converts a [`Local`][versions.segments.Local] to its string representation.

        Returns:
            The local string.
        """
        return concat_dot(map(str, self.parts))
