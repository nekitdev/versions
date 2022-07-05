from itertools import chain
from itertools import islice as iter_slice
from itertools import repeat
from typing import Any, Iterable, Iterator, MutableSequence, Optional, Sequence, Sized, TypeVar

__all__ = (
    "first",
    "last",
    "set_last",
    "next_or_none",
    "contains_only_item",
    "evolve_in_place",
    "pad_to_length",
    "count_leading_zeros",
)

A = TypeVar("A")
T = TypeVar("T")

set_attribute_directly = object.__setattr__


def first(sequence: Sequence[T]) -> T:
    return sequence[0]


def last(sequence: Sequence[T]) -> T:
    return sequence[~0]


def set_last(sequence: MutableSequence[T], item: T) -> None:
    sequence[~0] = item


def next_or_none(iterator: Iterator[T]) -> Optional[T]:
    return next(iterator, None)


def contains_only_item(sized: Sized) -> bool:
    return len(sized) == 1


def evolve_in_place(instance: A, **changes: Any) -> A:
    for name, value in changes.items():
        set_attribute_directly(instance, name, value)

    return instance


def pad_to_length(length: int, padding: T, iterable: Iterable[T]) -> Iterator[T]:
    return iter_slice(chain(iterable, repeat(padding)), length)


def count_leading_zeros(iterable: Iterable[int]) -> int:
    count = 0

    for item in iterable:
        if item:
            break

        count += 1

    return count
