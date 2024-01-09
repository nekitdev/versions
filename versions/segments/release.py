from __future__ import annotations
from typing import Iterable

from attrs import Attribute, evolve, field, frozen
from funcs.primitives import decrement, increment
from typing_extensions import Self

from versions.representation import Representation
from versions.segments.constants import (
    DEFAULT_PADDING,
    DEFAULT_PARTS,
    DEFAULT_VALUE,
    MAJOR,
    MICRO,
    MINOR,
    PATCH,
    TOTAL,
)
from versions.segments.typing import Extra, Parts
from versions.string import String, concat_dot, split_dot
from versions.utils import count_leading_zeros, fix_to_length

__all__ = ("Release",)

EMPTY_RELEASE = "releases can not be empty"


@frozen(repr=False, eq=True, order=True)
class Release(Representation, String):
    """Represents the *release* segment of the version (`x.y.z`)."""

    parts: Parts = field(default=DEFAULT_PARTS, eq=False, order=False)
    """The parts of the release."""

    compare_parts: Parts = field(repr=False, init=False, eq=True, order=True, hash=False)

    @parts.validator
    def check_parts(self, attribute: Attribute[Parts], value: Parts) -> None:
        if not value:
            raise ValueError(EMPTY_RELEASE)

    @compare_parts.default
    def default_compare_parts(self) -> Parts:
        parts = self.parts

        index = count_leading_zeros(reversed(parts))

        if index == self.precision:
            index -= 1  # preserve single zero if the version fully consists of zeros

        return self.slice_parts(-index) if index else parts

    @classmethod
    def create(cls, parts: Parts = DEFAULT_PARTS) -> Self:
        """Creates a [`Release`][versions.segments.release.Release] from `parts`.

        Arguments:
            parts: The parts of the release.

        Returns:
            The newly created [`Release`][versions.segments.release.Release].
        """
        return cls(parts)

    @classmethod
    def from_iterable(cls, iterable: Iterable[int]) -> Self:
        """Creates a [`Release`][versions.segments.release.Release] from `iterable`.

        Arguments:
            iterable: The parts of the release in an iterable.

        Returns:
            The newly created [`Release`][versions.segments.release.Release].
        """
        return cls(tuple(iterable))

    @classmethod
    def from_parts(cls, *parts: int) -> Self:
        """Creates a [`Release`][versions.segments.release.Release] from `parts`.

        Arguments:
            *parts: The parts of the release.

        Returns:
            The newly created [`Release`][versions.segments.release.Release].
        """
        return cls(parts)

    def into_parts(self) -> Parts:
        """Converts a [`Release`][versions.segments.release.Release] to its parts.

        Returns:
            The parts of the release.
        """
        return self.parts

    def set_parts(self, *parts: int) -> Self:
        """Sets the parts of the release to `parts`.

        Arguments:
            *parts: The parts of the release.

        Returns:
            The updated release.
        """
        return evolve(self, parts=parts)

    @property
    def precision(self) -> int:
        """The count of the release parts."""
        return len(self.parts)

    @property
    def last_index(self) -> int:
        """The index of the last release part."""
        # invariant: this is never negative since empty releases are not allowed
        return decrement(self.precision)

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
        """The *patch* part of the release.

        This is equivalent to [`micro`][versions.segments.release.Release.micro].
        """
        return self.get_at(PATCH)

    @property
    def extra(self) -> Extra:
        """The *extra* parts of the release."""
        return self.parts[TOTAL:]

    def get_at(self, index: int, default: int = DEFAULT_VALUE) -> int:
        """Gets the release part at the `index`, defaulting to `default`.

        Arguments:
            index: The index of the part to get.
            default: The default value to use.

        Returns:
            The release part at `index` or the `default` value.
        """
        return self.get_at_unchecked(index) if self.has_at(index) else default

    def get_at_unchecked(self, index: int) -> int:
        """Gets the release part at the `index`.

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

    def to_semantic(self) -> Self:
        """Converts the release to match the [`semver`](https://semver.org/) schema.

        Returns:
            The converted release.
        """
        if self.has_extra():
            return self.next_patch().slice(TOTAL)

        return self if self.is_semantic() else self.pad_to(TOTAL)

    def set_major(self, value: int) -> Self:
        """Sets the *major* part of the release to the `value`.

        Arguments:
            value: The value to set the *major* part to.

        Returns:
            The updated release.
        """
        return self.set_at(MAJOR, value)

    def set_minor(self, value: int) -> Self:
        """Sets the *minor* part of the release to the `value`.

        Arguments:
            value: The value to set the *minor* part to.

        Returns:
            The updated release.
        """
        return self.set_at(MINOR, value)

    def set_micro(self, value: int) -> Self:
        """Sets the *micro* part of the release to the `value`.

        Arguments:
            value: The value to set the *micro* part to.

        Returns:
            The updated release.
        """
        return self.set_at(MICRO, value)

    def set_patch(self, value: int) -> Self:
        """Sets the *patch* part of the release to the `value`.

        This is equivalent to [`set_micro`][versions.segments.release.Release.set_micro].

        Arguments:
            value: The value to set the *patch* part to.

        Returns:
            The updated release.
        """
        return self.set_at(PATCH, value)

    def set_at(self, index: int, value: int) -> Self:
        """Sets the release part at the `index` to the `value`.

        Arguments:
            index: The index to set the `value` at.
            value: The value to set the part to.

        Returns:
            The updated release.
        """
        return self.pad_to_index(index).set_at_unchecked(index, value)

    def set_at_unchecked(self, index: int, value: int) -> Self:
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

    def next_major(self) -> Self:
        """Bumps the *major* part of the release.

        Returns:
            The bumped release.
        """
        return self.next_at(MAJOR)

    def next_minor(self) -> Self:
        """Bumps the *minor* part of the release.

        Returns:
            The bumped release.
        """
        return self.next_at(MINOR)

    def next_micro(self) -> Self:
        """Bumps the *micro* part of the release.

        Returns:
            The bumped release.
        """
        return self.next_at(MICRO)

    def next_patch(self) -> Self:
        """Bumps the *patch* part of the release.

        This is equivalent to [`next_micro`][versions.segments.release.Release.next_micro].

        Returns:
            The bumped release.
        """
        return self.next_at(PATCH)

    def next_at(
        self, index: int, default: int = DEFAULT_VALUE, padding: int = DEFAULT_PADDING
    ) -> Self:
        """Bumps the part of the release at the `index`.

        Arguments:
            index: The index to bump the part at.
            default: The default value to use.
            padding: The padding to use.

        Returns:
            The bumped release.
        """
        updated = self.set_at(index, increment(self.get_at(index, default)))

        return updated.slice(increment(index)).pad_to(updated.precision, padding)

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

        This is equivalent to [`has_micro`][versions.segments.release.Release.has_micro].

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

    def pad_to(self, length: int, padding: int = DEFAULT_PADDING) -> Self:
        """Pads a [`Release`][versions.segments.release.Release] to the `length` with `padding`.

        Arguments:
            length: The length to pad the release to.
            padding: The padding to use.

        Returns:
            The padded release.
        """
        if self.precision < length:
            return self.from_iterable(fix_to_length(length, padding, self.parts))

        return self

    def pad_to_index(self, index: int, padding: int = DEFAULT_PADDING) -> Self:
        """Pads a [`Release`][versions.segments.release.Release] to the `index` with `padding`.

        Arguments:
            index: The index to pad the release to.
            padding: The padding to use.

        Returns:
            The padded release.
        """
        return self.pad_to(increment(index), padding)

    def pad_to_next(self, padding: int = DEFAULT_PADDING) -> Self:
        """Pads a [`Release`][versions.segments.release.Release] to the next index.

        Arguments:
            padding: The padding to use.

        Returns:
            The padded release.
        """
        return self.pad_to(increment(self.precision), padding)

    def slice(self, index: int) -> Self:
        return self.create(self.slice_parts(index))

    def slice_parts(self, index: int) -> Parts:
        return self.parts[:index]

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Parses a [`Release`][versions.segments.release.Release] from `string`.

        Arguments:
            string: The string to parse.

        Returns:
            The parsed release.
        """
        return cls.from_iterable(map(int, split_dot(string)))

    def to_string(self) -> str:
        """Converts a [`Release`][versions.segments.release.Release] to its string representation.

        Returns:
            The release string.
        """
        return concat_dot(map(str, self.parts))
