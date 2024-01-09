from attrs import evolve, frozen
from typing_extensions import Self

from funcs.primitives import increment

from versions.representation import Representation
from versions.segments.constants import DEFAULT_VALUE
from versions.string import String

__all__ = ("Epoch",)


@frozen(repr=False, eq=True, order=True)
class Epoch(Representation, String):
    """Represents the *epoch* segment of the version (`e!`)."""

    value: int = DEFAULT_VALUE

    def __bool__(self) -> bool:
        return bool(self.value)

    @classmethod
    def create(cls, value: int = DEFAULT_VALUE) -> Self:
        """Creates an [`Epoch`][versions.segments.epoch.Epoch] from `value`.

        Arguments:
            value: The value of the epoch.

        Returns:
            The newly created [`Epoch`][versions.segments.epoch.Epoch].
        """
        return cls(value)

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Parses an [`Epoch`][versions.segments.epoch.Epoch] from `string`.

        Arguments:
            string: The string to parse.

        Returns:
            The parsed epoch.
        """
        return cls(int(string))

    def to_string(self) -> str:
        """Converts an [`Epoch`][versions.segments.epoch.Epoch] to its string representation.

        Returns:
            The epoch string.
        """
        return str(self.value)

    def set_value(self, value: int) -> Self:
        """Sets the value of the epoch.

        Arguments:
            value: The value to set.

        Returns:
            The updated epoch.
        """
        return evolve(self, value=value)

    def next_value(self) -> Self:
        """Increments the value of the epoch.

        Returns:
            The next epoch.
        """
        return self.set_value(increment(self.value))
