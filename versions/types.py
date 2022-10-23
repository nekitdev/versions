from __future__ import annotations

from enum import Enum
from threading import Lock
from typing import Any, Type, TypeVar, Union

from typing_extensions import TypeGuard

from versions.typing import get_name

__all__ = (
    # ordering
    "Ordering",
    # singletons
    "Infinity",
    "NegativeInfinity",
    "Singleton",
    # instances
    "infinity",
    "negative_infinity",
    "singleton",
    # positive or negative infinity
    "AnyInfinity",
    # checks
    "is_infinity",
    "is_negative_infinity",
    "is_any_infinity",
)

T = TypeVar("T")


class Ordering(Enum):
    """Represents ordering."""

    LESS = -1
    """The left item is *less* than the right item."""
    EQUAL = 0
    """The left item is *equal* to the right item."""
    GREATER = 1
    """The left item is *greater* than the right item."""

    def is_less(self) -> bool:
        """Checks if the ordering is [`LESS`][versions.types.Ordering.LESS].

        Returns:
            Whether the ordering is [`LESS`][versions.types.Ordering.LESS].
        """
        return self is type(self).LESS

    def is_equal(self) -> bool:
        """Checks if the ordering is [`EQUAL`][versions.types.Ordering.EQUAL].

        Returns:
            Whether the ordering is [`EQUAL`][versions.types.Ordering.EQUAL].
        """
        return self is type(self).EQUAL

    def is_greater(self) -> bool:
        """Checks if the ordering is [`GREATER`][versions.types.Ordering.GREATER].

        Returns:
            Whether the ordering is [`GREATER`][versions.types.Ordering.GREATER].
        """
        return self is type(self).GREATER

    def is_less_or_equal(self) -> bool:
        """Checks if the ordering is [`LESS`][versions.types.Ordering.LESS] or
        [`EQUAL`][versions.types.Ordering.EQUAL].

        This is equivalent to:

        ```python
        ordering.is_less() or ordering.is_equal()
        ```

        Returns:
            Whether the ordering is [`LESS`][versions.types.Ordering.LESS]
                or [`EQUAL`][versions.types.Ordering.EQUAL].
        """
        return self.is_less() or self.is_equal()

    def is_not_equal(self) -> bool:
        """Checks if the ordering is not [`EQUAL`][versions.types.Ordering.EQUAL].

        This is equivalent to:

        ```python
        not ordering.is_equal()
        ```

        Returns:
            Whether the ordering is not [`EQUAL`][versions.types.Ordering.EQUAL].
        """
        return not self.is_equal()

    def is_greater_or_equal(self) -> bool:
        """Checks if the ordering is [`GREATER`][versions.types.Ordering.GREATER] or
        [`EQUAL`][versions.types.Ordering.EQUAL].

        This is equivalent to:

        ```python
        ordering.is_greater() or ordering.is_equal()
        ```

        Returns:
            Whether the ordering is [`GREATER`][versions.types.Ordering.GREATER]
                or [`EQUAL`][versions.types.Ordering.EQUAL].
        """
        return self.is_greater() or self.is_equal()


S = TypeVar("S")


class SingletonType(type):
    _INSTANCES = {}  # type: ignore
    _LOCK = Lock()  # single lock is enough here

    def __call__(cls: Type[S], *args: Any, **kwargs: Any) -> S:
        instances = cls._INSTANCES  # type: ignore
        lock = cls._LOCK  # type: ignore

        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = super().__call__(*args, **kwargs)  # type: ignore

        return instances[cls]  # type: ignore


class Singleton(metaclass=SingletonType):
    def __repr__(self) -> str:
        return get_name(type(self))


singleton = Singleton()


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
