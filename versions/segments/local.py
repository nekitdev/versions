from __future__ import annotations
from typing import Iterable

from attrs import Attribute, evolve, field, frozen
from typing_aliases import is_int
from typing_extensions import Self

from versions.constants import EMPTY
from versions.representation import Representation
from versions.segments.typing import CompareLocalParts, LocalPart, LocalParts
from versions.string import String, check_int, concat_dot, split_separators
from versions.types import negative_infinity

__all__ = ("Local",)

EMPTY_LOCAL = "local can not be empty"


def local_part(string: str) -> LocalPart:
    return int(string) if check_int(string) else string


@frozen(repr=False, eq=True, order=True)
class Local(Representation, String):
    """Represents the *local* segment of the version (`+local.n`)"""

    parts: LocalParts = field(eq=False, order=False)
    """The local segment parts."""

    compare_parts: CompareLocalParts = field(
        repr=False, init=False, eq=True, order=True, hash=False
    )

    @parts.validator
    def check_parts(self, attribute: Attribute[LocalParts], value: LocalParts) -> None:
        if not value:
            raise ValueError(EMPTY_LOCAL)

    @compare_parts.default
    def default_compare_parts(self) -> CompareLocalParts:
        empty = EMPTY

        return tuple(
            (part, empty) if is_int(part) else (negative_infinity, part)  # type: ignore[misc]
            for part in self.parts
        )

    @classmethod
    def create(cls, parts: LocalParts) -> Local:
        """Creates a [`Local`][versions.segments.local.Local] segment from local `parts`.

        Arguments:
            parts: The local parts.

        Returns:
            The newly created [`Local`][versions.segments.local.Local] segment.
        """
        return cls(parts)

    @classmethod
    def from_iterable(cls, iterable: Iterable[LocalPart]) -> Self:
        """Creates a [`Local`][versions.segments.Local] segment from `iterable`.

        Arguments:
            iterable: The local parts in an iterable.

        Returns:
            The newly created [`Local`][versions.segments.Local] segment.
        """
        return cls(tuple(iterable))

    @classmethod
    def from_parts(cls, *parts: LocalPart) -> Self:
        """Creates a [`Local`][versions.segments.Local] segment from local `parts`.

        Arguments:
            *parts: The local parts.

        Returns:
            The newly created [`Local`][versions.segments.Local] segment.
        """
        return cls(parts)

    def into_parts(self) -> LocalParts:
        """Converts a [`Local`][versions.segments.Local] segment to its parts.

        Returns:
            The parts of the local segment.
        """
        return self.parts

    def set_parts(self, *parts: LocalPart) -> Self:
        """Sets the parts of a [`Local`][versions.segments.Local] segment.

        Arguments:
            *parts: The new parts.

        Returns:
            The updated local segment.
        """
        return evolve(self, parts=parts)

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Parses a [`Local`][versions.segments.Local] segment from `string`.

        Arguments:
            string: The string to parse.

        Returns:
            The parsed local segment.
        """
        return cls.from_iterable(map(local_part, split_separators(string)))

    def to_string(self) -> str:
        """Converts a [`Local`][versions.segments.Local] segment to its string representation.

        Returns:
            The local segment string.
        """
        return concat_dot(map(str, self.parts))
