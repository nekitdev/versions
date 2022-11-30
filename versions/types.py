from __future__ import annotations

from typing import Any, Union

from solus import Singleton
from typing_extensions import TypeGuard

__all__ = (
    # infinities
    "Infinity",
    "NegativeInfinity",
    # instances
    "infinity",
    "negative_infinity",
    # positive or negative infinity
    "AnyInfinity",
    # checks
    "is_infinity",
    "is_negative_infinity",
    "is_any_infinity",
)


INFINITY = "infinity"
NEGATIVE = "-"
NEGATIVE_INFINITY = NEGATIVE + INFINITY


class Infinity(Singleton):
    """Represents the positive infinity."""

    def __repr__(self) -> str:
        return INFINITY

    def __eq__(self, other: Any) -> bool:
        return self is other

    def __ne__(self, other: Any) -> bool:
        return self is not other

    def __lt__(self, other: Any) -> bool:
        return False

    def __le__(self, other: Any) -> bool:
        return self is other

    def __gt__(self, other: Any) -> bool:
        return self is not other

    def __ge__(self, other: Any) -> bool:
        return True

    def __neg__(self: Infinity) -> NegativeInfinity:
        return negative_infinity


infinity = Infinity()
"""The singleton instance of [`Infinity`][versions.types.Infinity]."""


def is_infinity(item: Any) -> TypeGuard[Infinity]:
    """Checks if an `item` is an instance of [`Infinity`][versions.types.Infinity].

    Returns:
        Whether the `item` is an instance of [`Infinity`][versions.types.Infinity].
    """
    return item is infinity


class NegativeInfinity(Singleton):
    """Represents the negative infinity."""

    def __repr__(self) -> str:
        return NEGATIVE_INFINITY

    def __eq__(self, other: Any) -> bool:
        return self is other

    def __ne__(self, other: Any) -> bool:
        return self is not other

    def __lt__(self, other: Any) -> bool:
        return self is not other

    def __le__(self, other: Any) -> bool:
        return True

    def __gt__(self, other: Any) -> bool:
        return False

    def __ge__(self, other: Any) -> bool:
        return self is other

    def __neg__(self: NegativeInfinity) -> Infinity:
        return infinity


negative_infinity = NegativeInfinity()
"""The singleton instance of [`NegativeInfinity`][versions.types.NegativeInfinity]."""


def is_negative_infinity(item: Any) -> TypeGuard[NegativeInfinity]:
    """Checks if an `item` is an instance of [`NegativeInfinity`][versions.types.NegativeInfinity].

    Returns:
        Whether the `item` is an instance of [`NegativeInfinity`][versions.types.NegativeInfinity].
    """
    return item is negative_infinity


AnyInfinity = Union[Infinity, NegativeInfinity]
"""The union of [`Infinity`][versions.types.Infinity] and
[`NegativeInfinity`][versions.types.NegativeInfinity].
"""


def is_any_infinity(item: Any) -> TypeGuard[AnyInfinity]:
    """Checks if an `item` is an instance of [`AnyInfinity`][versions.types.AnyInfinity].

    Returns:
        Whether the `item` is an instance of [`AnyInfinity`][versions.types.AnyInfinity].
    """
    return item is infinity or item is negative_infinity
