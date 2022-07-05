from builtins import hasattr as has_attribute
from builtins import isinstance as is_instance
from typing import Any, Callable, Tuple, Type, TypeVar

from typing_extensions import Protocol, TypeGuard, runtime_checkable

__all__ = (
    "AnyType",
    "DynamicTuple",
    "Nullary",
    "Unary",
    "Binary",
    "Named",
    "get_name",
    "is_named",
    "is_int",
)

AnyType = Type[Any]

T = TypeVar("T")
U = TypeVar("U")

R = TypeVar("R")

Nullary = Callable[[], R]
Unary = Callable[[T], R]
Binary = Callable[[T, U], R]

DynamicTuple = Tuple[T, ...]

NAME = "__name__"


@runtime_checkable
class Named(Protocol):
    __name__: str


def get_name(item: Named) -> str:
    return item.__name__


def is_named(item: Any) -> TypeGuard[Named]:
    return has_attribute(item, NAME)


def is_int(item: Any) -> TypeGuard[int]:
    return is_instance(item, int)
