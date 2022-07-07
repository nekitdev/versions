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
DEFAULT_VALUE = 0
DEFAULT_PADDING = 0

MAJOR = 0
MINOR = 1
MICRO = 2
TOTAL = 3

PATCH = MICRO  # alias

E = TypeVar("E", bound="Epoch")


@frozen(repr=False, eq=True, order=True)
class Epoch(Representation, FromString, ToString):
    """Represents the epoch part of the version (`e!`)."""
    value: int = field(default=DEFAULT_VALUE)

    def __bool__(self) -> bool:
        return bool(self.value)

    @classmethod
    def create(cls: Type[E], value: int = DEFAULT_VALUE) -> E:
        return cls(value)

    @classmethod
    def from_string(cls: Type[E], string: str) -> E:
        return cls(int(string))

    def to_string(self) -> str:
        return str(self.value)


EMPTY_RELEASE = "release can not be empty"

R = TypeVar("R", bound="Release")


@frozen(repr=False, eq=True, order=True)
class Release(Representation, FromString, ToString):
    """Represents the release part of the version (`x.y.z`)."""

    parts: Parts = field(default=DEFAULT_PARTS, eq=False, order=False)

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
        return cls(parts)

    @classmethod
    def from_iterable(cls: Type[R], iterable: Iterable[int]) -> R:
        return cls(tuple(iterable))

    @classmethod
    def from_parts(cls: Type[R], *parts: int) -> R:
        return cls(parts)

    def into_parts(self) -> Parts:
        return self.parts

    @property
    def precision(self) -> int:
        return len(self.parts)

    @property
    def last_index(self) -> int:
        return self.precision - 1

    def get_major(self) -> int:
        return self.get_at(MAJOR)

    def get_minor(self) -> int:
        return self.get_at(MINOR)

    def get_micro(self) -> int:
        return self.get_at(MICRO)

    def get_patch(self) -> int:
        return self.get_at(PATCH)

    def get_extra(self) -> Extra:
        return self.parts[TOTAL:]

    @property
    def extra(self) -> Extra:
        ...

    extra = property(get_extra)  # type: ignore

    def get_at(self, index: int, default: int = DEFAULT_VALUE) -> int:
        return self.get_at_unchecked(index) if self.has_at(index) else default

    def get_at_unchecked(self, index: int) -> int:
        return self.parts[index]

    def is_semantic(self) -> bool:
        return self.precision == TOTAL

    def to_semantic(self: R) -> R:
        if self.has_extra():
            return self.next_patch().slice(TOTAL)

        return self if self.is_semantic() else self.pad_to(TOTAL)

    def set_major(self: R, value: int) -> R:
        return self.set_at(MAJOR, value)

    def set_minor(self: R, value: int) -> R:
        return self.set_at(MINOR, value)

    def set_micro(self: R, value: int) -> R:
        return self.set_at(MICRO, value)

    def set_patch(self: R, value: int) -> R:
        return self.set_at(PATCH, value)

    @property
    def major(self) -> int:
        ...

    @property
    def minor(self) -> int:
        ...

    @property
    def micro(self) -> int:
        ...

    @property
    def patch(self) -> int:
        ...

    major = property(get_major, set_major)  # type: ignore
    minor = property(get_minor, set_minor)  # type: ignore
    micro = property(get_micro, set_micro)  # type: ignore
    patch = property(get_patch, set_patch)  # type: ignore

    def set_at(self: R, index: int, value: int) -> R:
        return self.pad_to_index(index).set_at_unchecked(index, value)

    def set_at_unchecked(self: R, index: int, value: int) -> R:
        mutable = list(self.parts)
        mutable[index] = value

        return self.from_iterable(mutable)

    def next_major(self: R) -> R:
        return self.next_at(MAJOR)

    def next_minor(self: R) -> R:
        return self.next_at(MINOR)

    def next_micro(self: R) -> R:
        return self.next_at(MICRO)

    def next_patch(self: R) -> R:
        return self.next_at(PATCH)

    def next_at(self: R, index: int) -> R:
        updated = self.set_at(index, self.get_at(index) + 1)

        return updated.slice(index + 1).pad_to(updated.precision)

    def has_major(self) -> bool:
        return self.has_at(MAJOR)

    def has_minor(self) -> bool:
        return self.has_at(MINOR)

    def has_micro(self) -> bool:
        return self.has_at(MICRO)

    def has_patch(self) -> bool:
        return self.has_at(PATCH)

    def has_extra(self) -> bool:
        return self.has_at(TOTAL)

    def has_at(self, index: int) -> bool:
        return self.precision > index

    def pad_to(self: R, length: int, padding: int = DEFAULT_PADDING) -> R:
        if self.precision < length:
            return self.from_iterable(pad_to_length(length, padding, self.parts))

        return self

    def pad_to_index(self: R, index: int, padding: int = DEFAULT_PADDING) -> R:
        return self.pad_to(index + 1, padding)

    def pad_to_next(self: R, padding: int = DEFAULT_PADDING) -> R:
        return self.pad_to(self.precision + 1, padding)

    def slice(self: R, stop: int) -> R:
        return self.create(self.slice_parts(stop))

    def slice_parts(self, stop: int) -> Parts:
        return self.parts[:stop]

    @classmethod
    def from_string(cls: Type[R], string: str) -> R:
        return cls.from_iterable(map(int, split_dot(string)))

    def to_string(self) -> str:
        return concat_dot(map(str, self.parts))


PHASE_NOT_ALLOWED = "phase `{}` is not allowed in `{}`"
CAN_NOT_PARSE = "can not parse `{}` to `{}`"

T = TypeVar("T", bound="Tag")


@frozen(repr=False, eq=True, order=True)
class Tag(Representation, FromString, ToString):
    """Represents various tag parts of the version (`tag.n`)."""

    DEFAULT_PHASE: ClassVar[str] = PHASE_ALL_DEFAULT
    PHASE_SET: ClassVar[Set[str]] = PHASE_ALL_SET

    phase: str = field(converter=case_fold)  # type: ignore
    value: int = field(default=DEFAULT_VALUE)

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
        if phase is None:
            phase = cls.DEFAULT_PHASE

        return cls(phase, value)

    @classmethod
    def default_with_value(cls: Type[T], value: int) -> T:  # TODO: change the name?
        return cls(value=value)

    @property
    def short(self) -> str:
        return self.reduce(self.phase)

    @property
    def normal(self) -> str:
        return self.normalize_phase(self.phase)

    def normalize(self: T) -> T:
        return evolve(self, phase=self.normal)

    def next(self: T) -> T:
        return evolve(self, value=self.value + 1)

    def next_phase(self: T) -> Optional[T]:
        phase = PHASE_TO_NEXT.get(self.phase)

        return None if phase is None else self.create(phase)

    @classmethod
    def from_string(cls: Type[T], string: str) -> T:
        return TagParser(cls).parse(string)

    def to_string(self) -> str:
        return concat_dot_args(self.phase, str(self.value))

    def to_short_string(self) -> str:
        return concat_empty_args(self.short, str(self.value))


@frozen(repr=False, eq=True, order=True)
class PreTag(Tag):
    """Represents the pre-release part of the version (`pre.n`)."""

    DEFAULT_PHASE = PHASE_PRE_DEFAULT
    PHASE_SET = PHASE_PRE_SET


@frozen(repr=False, eq=True, order=True)
class PostTag(Tag):
    """Represents the post-release part of the version (`pre.n`)."""

    DEFAULT_PHASE = PHASE_POST_DEFAULT
    PHASE_SET = PHASE_POST_SET


@frozen(repr=False, eq=True, order=True)
class DevTag(Tag):
    """Represents the dev-release part of the version (`dev.n`)."""

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
    """Represents the local part of the version (`+abcdefg.n`)"""

    parts: LocalParts = field(eq=False, order=False)

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
        return cls(parts)

    @classmethod
    def from_iterable(cls: Type[L], iterable: Iterable[LocalPart]) -> L:
        return cls(tuple(iterable))

    @classmethod
    def from_parts(cls: Type[L], *local_parts: LocalPart) -> L:
        return cls(local_parts)

    def into_parts(self) -> LocalParts:
        return self.parts

    @classmethod
    def from_string(cls: Type[L], string: str) -> L:
        return cls.from_iterable(map(local_part, split_separators(string)))

    def to_string(self) -> str:
        return concat_dot(map(str, self.parts))
