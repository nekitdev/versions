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
    "is_not_infinity",
    "is_negative_infinity",
    "is_not_negative_infinity",
    "is_any_infinity",
    "is_not_any_infinity",
)

T = TypeVar("T")


class Ordering(Enum):
    LESS = -1
    EQUAL = 0
    GREATER = 1

    def is_less(self) -> bool:
        return self is type(self).LESS

    def is_equal(self) -> bool:
        return self is type(self).EQUAL

    def is_greater(self) -> bool:
        return self is type(self).GREATER

    def is_less_or_equal(self) -> bool:
        return self.is_less() or self.is_equal()

    def is_greater_or_equal(self) -> bool:
        return self.is_greater() or self.is_equal()

    def is_not_equal(self) -> bool:
        return not self.is_equal()


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


def is_infinity(item: Union[Infinity, Any]) -> TypeGuard[Infinity]:
    return item is infinity


def is_not_infinity(item: Union[Infinity, T]) -> TypeGuard[T]:
    return not is_infinity(item)


class NegativeInfinity(Singleton):
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


def is_negative_infinity(item: Union[NegativeInfinity, Any]) -> TypeGuard[NegativeInfinity]:
    return item is negative_infinity


def is_not_negative_infinity(item: Union[NegativeInfinity, T]) -> TypeGuard[T]:
    return not is_negative_infinity(item)


AnyInfinity = Union[Infinity, NegativeInfinity]

A = TypeVar("A", bound=AnyInfinity)


def is_any_infinity(item: Union[A, Any]) -> TypeGuard[A]:
    return item is infinity or item is negative_infinity


def is_not_any_infinity(item: Union[Any, T]) -> TypeGuard[T]:
    return not is_any_infinity(item)  # type: ignore
