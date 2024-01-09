from __future__ import annotations

from typing import ClassVar, Optional, final

from attrs import Attribute, evolve, field, frozen
from funcs.primitives import increment
from named import get_type_name
from typing_aliases import AnySet
from typing_extensions import Self

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
from versions.segments.constants import DEFAULT_VALUE
from versions.string import String, concat_dot_args, concat_empty_args

__all__ = ("Tag", "PreTag", "PostTag", "DevTag")

PHASE_NOT_ALLOWED = "phase `{}` is not allowed in `{}`"
CAN_NOT_PARSE = "can not parse `{}` to `{}`"


def convert_phase(phase: str) -> str:
    return SHORT_TO_PHASE.get(phase, phase)


@frozen(repr=False, eq=True, order=True)
class Tag(Representation, String):
    """Represents various version *tags* (`tag.n`)."""

    DEFAULT_PHASE: ClassVar[str] = PHASE_ALL_DEFAULT
    PHASE_SET: ClassVar[AnySet[str]] = PHASE_ALL_SET

    phase: str = field(converter=convert_phase)
    """The phase of the release tag."""

    value: int = field(default=DEFAULT_VALUE)
    """The value of the release tag."""

    @phase.default
    def default_phase(self) -> str:
        return self.DEFAULT_PHASE

    @phase.validator
    def check_phase(self, attribute: Attribute[str], value: str) -> None:
        if value not in self.PHASE_SET:
            raise ValueError(PHASE_NOT_ALLOWED.format(value, get_type_name(self)))

    @classmethod
    def create(cls, phase: Optional[str] = None, value: int = DEFAULT_VALUE) -> Self:
        """Creates a [`Tag`][versions.segments.tags.Tag] from `phase` and `value`.

        Arguments:
            phase: The phase of the tag.
            value: The value of the tag.

        Returns:
            The newly created [`Tag`][versions.segments.tags.Tag].
        """
        if phase is None:
            phase = cls.DEFAULT_PHASE

        return cls(phase, value)

    @classmethod
    def default_phase_with_value(cls, value: int) -> Self:
        """Creates a [`Tag`][versions.segments.tags.Tag] from `value` with the default phase.

        Arguments:
            value: The value of the tag.

        Returns:
            The newly created [`Tag`][versions.segments.tags.Tag].
        """
        return cls(cls.DEFAULT_PHASE, value)

    @property
    def short(self) -> str:
        """The *short* phase of the tag."""
        phase = self.phase

        return PHASE_TO_SHORT.get(phase, phase)

    @property
    def normal(self) -> str:
        """The *normalized* phase of the tag."""
        phase = self.phase

        return PHASE_TO_NORMAL.get(phase, phase)

    def normalize(self) -> Self:
        """Normalizes the version tag.

        Returns:
            The normalized tag.
        """
        return self.set_phase(self.normal)

    def set_phase(self, phase: str) -> Self:
        """Sets the phase of the version tag.

        Arguments:
            phase: The phase to set.

        Returns:
            The version tag with the new phase.
        """
        return evolve(self, phase=phase)

    def set_value(self, value: int) -> Self:
        """Sets the value of the version tag.

        Arguments:
            value: The value to set.

        Returns:
            The version tag with the new value.
        """
        return evolve(self, value=value)

    def next(self) -> Self:
        """Bumps the version tag value.

        Returns:
            The next version tag.
        """
        return self.set_value(increment(self.value))

    def next_phase(self, value: int = DEFAULT_VALUE) -> Optional[Self]:
        """Bumps the version tag phase, if possible.

        Returns:
            The next version tag, if present.
        """
        phase = PHASE_TO_NEXT.get(self.phase)

        return None if phase is None else self.set_phase(phase).set_value(value)

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Parses a [`Tag`][versions.segments.tags.Tag] from `string`.

        Arguments:
            string: The string to parse.

        Returns:
            The parsed tag.
        """
        return TagParser(cls).parse(string)

    def to_string(self) -> str:
        """Converts a [`Tag`][versions.segments.tags.Tag] to its string representation.

        Returns:
            The tag string.
        """
        return concat_dot_args(self.phase, str(self.value))

    def to_short_string(self) -> str:
        """Converts a [`Tag`][versions.segments.tags.Tag] to its *short* string representation.

        Returns:
            The *short* tag string.
        """
        return concat_empty_args(self.short, str(self.value))


@final
@frozen(repr=False, eq=True, order=True)
class PreTag(Tag):
    """Represents the *pre-release* tag of the version (`pre.n`)."""

    DEFAULT_PHASE = PHASE_PRE_DEFAULT
    PHASE_SET = PHASE_PRE_SET


@final
@frozen(repr=False, eq=True, order=True)
class PostTag(Tag):
    """Represents the *post-release* tag of the version (`post.n`)."""

    DEFAULT_PHASE = PHASE_POST_DEFAULT
    PHASE_SET = PHASE_POST_SET


@final
@frozen(repr=False, eq=True, order=True)
class DevTag(Tag):
    """Represents the *dev-release* tag of the version (`dev.n`)."""

    DEFAULT_PHASE = PHASE_DEV_DEFAULT
    PHASE_SET = PHASE_DEV_SET
