from builtins import isinstance as is_instance
from typing import Any, Callable, Tuple, Type, TypeVar

from typing_extensions import TypeGuard

__all__ = ("AnyType", "DynamicTuple", "Nullary", "Unary", "Binary", "is_int", "is_instance")

AnyType = Type[Any]

T = TypeVar("T")
U = TypeVar("U")

R = TypeVar("R")

Nullary = Callable[[], R]
Unary = Callable[[T], R]
Binary = Callable[[T, U], R]

DynamicTuple = Tuple[T, ...]


def is_int(item: Any) -> TypeGuard[int]:
    return is_instance(item, int)


def is_same_type(item: Any, other: T) -> TypeGuard[T]:
    return is_instance(item, type(other))
