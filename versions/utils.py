from itertools import chain
from itertools import islice as iter_slice
from itertools import repeat
from typing import Iterable, Iterator, MutableSequence, Optional, Sequence, Sized, Tuple, TypeVar

__all__ = (
    "first",
    "last",
    "set_last",
    "next_or_none",
    "contains_only_item",
    "fix_to_length",
    "count_leading_zeros",
)

A = TypeVar("A")
T = TypeVar("T")


FIRST = 0
LAST = ~0


def first(sequence: Sequence[T]) -> T:
    return sequence[FIRST]


def last(sequence: Sequence[T]) -> T:
    return sequence[LAST]


def set_last(sequence: MutableSequence[T], item: T) -> None:
    sequence[LAST] = item


def next_or_none(iterator: Iterator[T]) -> Optional[T]:
    return next(iterator, None)


def contains_only_item(sized: Sized) -> bool:
    return len(sized) == 1


def fix_to_length(length: int, padding: T, iterable: Iterable[T]) -> Iterator[T]:
    return iter_slice(chain(iterable, repeat(padding)), length)


def count_leading_zeros(iterable: Iterable[int]) -> int:
    count = 0

    for item in iterable:
        if item:
            break

        count += 1

    return count


def unary_tuple(item: T) -> Tuple[T]:
    return (item,)
