from __future__ import annotations

from abc import abstractmethod
from builtins import isinstance as is_instance
from itertools import chain
from typing import TYPE_CHECKING, Any, Iterable, Iterator, List, Optional, Tuple, TypeVar, Union

from attrs import Attribute, define, evolve, field, frozen
from typing_extensions import Literal, Protocol, TypeGuard, runtime_checkable

from versions.constants import EMPTY_VERSION, UNIVERSE_VERSION
from versions.errors import InternalError
from versions.operators import Operator, OperatorType
from versions.representation import Representation
from versions.specification import Specification
from versions.string import (
    ToString,
    concat_comma,
    concat_comma_space,
    concat_pipes,
    concat_pipes_spaced,
)
from versions.types import Infinity, NegativeInfinity, Ordering, infinity, negative_infinity
from versions.typing import DynamicTuple
from versions.utils import contains_only_item, evolve_in_place, first, last, next_or_none, set_last

if TYPE_CHECKING:
    from versions.version import Version

__all__ = (
    "VersionEmpty",
    "VersionPoint",
    "VersionRange",
    "VersionUnion",
    "VersionItem",
    "VersionSet",
    "is_version_empty",
    "is_version_point",
    "is_version_range",
    "is_version_union",
    "is_version_item",
    "is_version_set",
)

flatten = chain.from_iterable

T = TypeVar("T")


@runtime_checkable
class VersionSetProtocol(Specification, Protocol):
    @abstractmethod
    def is_empty(self) -> bool:
        ...

    @abstractmethod
    def is_universe(self) -> bool:
        ...

    @abstractmethod
    def includes(self, version_set: VersionSet) -> bool:
        ...

    @abstractmethod
    def intersects(self, version_set: VersionSet) -> bool:
        ...

    @abstractmethod
    def contains(self, version: Version) -> bool:
        ...

    def accepts(self, version: Version) -> bool:
        return self.contains(version)

    @abstractmethod
    def intersection(self, version_set: VersionSet) -> VersionSet:
        ...

    @abstractmethod
    def union(self, version_set: VersionSet) -> VersionSet:
        ...

    @abstractmethod
    def difference(self, version_set: VersionSet) -> VersionSet:
        ...

    @abstractmethod
    def complement(self) -> VersionSet:
        ...

    def symmetric_difference(self, version_set: VersionSet) -> VersionSet:
        return self.union(version_set).difference(self.intersection(version_set))

    def __contains__(self, version: Version) -> bool:
        return self.contains(version)

    def __and__(self, version_set: VersionSet) -> VersionSet:
        return self.intersection(version_set)

    def __iand__(self, version_set: VersionSet) -> VersionSet:
        return self.intersection(version_set)

    def __or__(self, version_set: VersionSet) -> VersionSet:
        return self.union(version_set)

    def __ior__(self, version_set: VersionSet) -> VersionSet:
        return self.union(version_set)

    def __sub__(self, version_set: VersionSet) -> VersionSet:
        return self.difference(version_set)

    def __isub__(self, version_set: VersionSet) -> VersionSet:
        return self.difference(version_set)

    def __xor__(self, version_set: VersionSet) -> VersionSet:
        return self.symmetric_difference(version_set)

    def __ixor__(self, version_set: VersionSet) -> VersionSet:
        return self.symmetric_difference(version_set)

    def __negate__(self) -> VersionSet:
        return self.complement()


def is_version_empty(item: Any) -> TypeGuard[VersionEmpty]:
    return is_instance(item, VersionEmpty)


def is_version_point(item: Any) -> TypeGuard[VersionPoint]:
    return is_instance(item, VersionPoint)


def is_version_range(item: Any) -> TypeGuard[VersionRange]:
    return is_instance(item, VersionRange)


def is_version_union(item: Any) -> TypeGuard[VersionUnion]:
    return is_instance(item, VersionUnion)


def is_version_item(item: Any) -> TypeGuard[VersionItem]:
    return is_instance(item, VersionItemTypes)


def is_version_set(item: Any) -> TypeGuard[VersionSet]:
    return is_instance(item, VersionSetTypes)


E = TypeVar("E", bound="VersionEmpty")
S = TypeVar("S", bound="VersionSet")


@frozen(repr=False, order=False)
class VersionEmpty(Representation, ToString, VersionSetProtocol):
    """Represents version empty sets (`{}`)."""

    def is_empty(self) -> Literal[True]:
        return True

    def is_universe(self) -> Literal[False]:
        return False

    def includes(self, version_set: VersionSet) -> bool:
        return version_set.is_empty()

    def intersects(self, version_set: VersionSet) -> Literal[False]:
        return False

    def contains(self, version: Version) -> Literal[False]:
        return False

    def intersection(self: E, version_set: VersionSet) -> E:
        return self

    def union(self, version_set: S) -> S:
        return version_set

    def difference(self: E, version_set: VersionSet) -> E:
        return self

    def symmetric_difference(self, version_set: S) -> S:
        return version_set

    def complement(self) -> VersionRange:
        return VersionRange()

    def to_string(self) -> str:
        return EMPTY_VERSION


def is_version_range_protocol(item: Any) -> TypeGuard[VersionRangeProtocol]:
    return is_instance(item, VersionRangeProtocol)


@runtime_checkable
class VersionRangeProtocol(Protocol):
    min: Optional[Version]
    max: Optional[Version]
    include_min: bool
    include_max: bool

    @property
    def parameters(self) -> Tuple[Optional[Version], Optional[Version], bool, bool]:
        return (self.min, self.max, self.include_min, self.include_max)

    @property
    def exclude_min(self) -> bool:
        return not self.include_min

    @property
    def exclude_max(self) -> bool:
        return not self.include_max

    @property
    def checked_min(self) -> Version:
        min = self.min

        if min is None:
            raise ValueError  # TODO: message?

        return min

    @property
    def checked_max(self) -> Version:
        max = self.max

        if max is None:
            raise ValueError  # TODO: message?

        return max

    @property
    def comparable_min(self) -> Union[Version, NegativeInfinity]:
        min = self.min

        return negative_infinity if min is None else min

    @property
    def comparable_max(self) -> Union[Version, Infinity]:
        max = self.max

        return infinity if max is None else max

    def is_closed(self) -> bool:
        return self.is_left_closed() and self.is_right_closed()

    def is_left_closed(self) -> bool:
        return self.include_min

    def is_right_closed(self) -> bool:
        return self.include_max

    def is_open(self) -> bool:
        return self.is_left_open() and self.is_right_open()

    def is_left_open(self) -> bool:
        return self.exclude_min

    def is_right_open(self) -> bool:
        return self.exclude_max

    def is_unbounded(self) -> bool:
        return self.is_left_unbounded() and self.is_right_unbounded()

    def is_left_unbounded(self) -> bool:
        return self.min is None

    def is_right_unbounded(self) -> bool:
        return self.max is None

    def is_bounded(self) -> bool:
        return self.is_left_bounded() and self.is_right_bounded()

    def is_left_bounded(self) -> bool:
        return self.min is not None

    def is_right_bounded(self) -> bool:
        return self.max is not None

    def is_empty_or_point(self) -> bool:
        return self.comparable_min == self.comparable_max

    def is_lower(self, other: VersionRangeProtocol) -> bool:
        self_comparable_min = self.comparable_min
        other_comparable_min = other.comparable_min

        if self_comparable_min < other_comparable_min:
            return True

        if self_comparable_min > other_comparable_min:
            return False

        return self.include_min and other.exclude_min

    def is_higher(self, other: VersionRangeProtocol) -> bool:
        self_comparable_max = self.comparable_max
        other_comparable_max = other.comparable_max

        if self_comparable_max < other_comparable_max:
            return False

        if self_comparable_max > other_comparable_max:
            return True

        return self.include_max and other.exclude_max

    def is_strictly_lower(self, other: VersionRangeProtocol) -> bool:
        self_comparable_max = self.comparable_max
        other_comparable_min = other.comparable_min

        if self_comparable_max < other_comparable_min:
            return True

        if self_comparable_max > other_comparable_min:
            return False

        return self.exclude_max or other.exclude_min

    def is_strictly_higher(self, other: VersionRangeProtocol) -> bool:
        self_comparable_min = self.comparable_min
        other_comparable_max = other.comparable_max

        if self_comparable_min > other_comparable_max:
            return True

        if self_comparable_min < other_comparable_max:
            return False

        return self.exclude_min or other.exclude_max

    def is_left_adjacent(self, other: VersionRangeProtocol) -> bool:
        return (self.max == other.min) and (self.include_max != other.include_min)

    def is_right_adjacent(self, other: VersionRangeProtocol) -> bool:
        return (self.min == other.max) and (self.include_min != other.include_max)

    def is_adjacent(self, other: VersionRangeProtocol) -> bool:
        return self.is_left_adjacent(other) or self.is_right_adjacent(other)

    def __eq__(self, other: Any) -> bool:
        return is_version_range_protocol(other) and self.parameters == other.parameters

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: VersionRangeProtocol) -> bool:
        return self.compare(other).is_less()

    def __le__(self, other: VersionRangeProtocol) -> bool:
        return self.compare(other).is_less_or_equal()

    def __gt__(self, other: VersionRangeProtocol) -> bool:
        return self.compare(other).is_greater()

    def __ge__(self, other: VersionRangeProtocol) -> bool:
        return self.compare(other).is_greater_or_equal()

    def compare(self, other: VersionRangeProtocol) -> Ordering:
        self_comparable_min = self.comparable_min
        other_comparable_min = other.comparable_min

        if self_comparable_min > other_comparable_min:
            return Ordering.GREATER

        if self_comparable_min < other_comparable_min:
            return Ordering.LESS

        include_min = self.include_min

        if include_min == other.exclude_min:
            return Ordering.LESS if include_min else Ordering.GREATER

        self_comparable_max = self.comparable_max
        other_comparable_max = other.comparable_max

        if self_comparable_max > other_comparable_max:
            return Ordering.GREATER

        if self_comparable_max < other_comparable_max:
            return Ordering.LESS

        include_max = self.include_max

        if include_max == other.exclude_max:
            return Ordering.GREATER if include_max else Ordering.LESS

        return Ordering.EQUAL


@frozen(repr=False, eq=False, order=False)
class VersionRange(Representation, ToString, VersionRangeProtocol, VersionSetProtocol):
    """Represents version ranges (`(x, y)`, `(x, y]`, `[x, y)` and `[x, y]`)."""

    min: Optional[Version] = None
    max: Optional[Version] = None
    include_min: bool = False
    include_max: bool = False

    def __attrs_post_init__(self) -> None:
        if self.min is None:
            evolve_in_place(self, include_min=False)

        if self.max is None:
            evolve_in_place(self, include_max=False)

        if self.comparable_min > self.comparable_max:
            raise ValueError  # TODO: message?

    def is_empty(self) -> bool:
        return self.is_empty_or_point() and not self.is_closed()

    def is_point(self) -> bool:
        return self.is_empty_or_point() and self.is_closed()

    def is_universe(self) -> bool:
        return self.is_unbounded()

    @property
    def version(self) -> Version:
        version = self.min or self.max

        if version is None:
            raise ValueError  # TODO: message?

        if self.is_point():
            return version

        raise ValueError  # TODO: message?

    def contains(self, version: Version) -> bool:
        comparable_min = self.comparable_min
        comparable_max = self.comparable_max

        # if is_not_infinity(comparable_max):
        #     version = comparable_max.weaken(version)

        if version < comparable_min:
            return False

        if self.exclude_min and version == comparable_min:
            return False

        if version > comparable_max:
            return False

        if self.exclude_max and version == comparable_max:
            return False

        return True

    accepts = contains

    def includes(self, version_set: VersionSet) -> bool:
        if is_version_empty(version_set):
            return True

        if is_version_point(version_set):
            return self.contains(version_set.version)

        if is_version_range(version_set):
            return not version_set.is_lower(self) and not version_set.is_higher(self)

        if is_version_union(version_set):
            return all(self.includes(item) for item in version_set.items)

        raise TypeError  # TODO: message?

    def intersects(self, version_set: VersionSet) -> bool:
        if is_version_empty(version_set):
            return False

        if is_version_point(version_set):
            return self.contains(version_set.version)

        if is_version_range(version_set):
            return self.intersects_range(version_set)

        if is_version_union(version_set):
            return any(self.intersects(item) for item in version_set.items)

        raise TypeError  # TODO: message?

    def intersects_range(self, range: VersionRange) -> bool:
        return not range.is_strictly_lower(self) and not range.is_strictly_higher(self)

    def intersection(self, version_set: VersionSet) -> VersionSet:
        if is_version_empty(version_set):
            return VersionEmpty()

        if is_version_point(version_set):
            return version_set.intersection(self)

        if is_version_range(version_set):
            if self.is_lower(version_set):
                if self.is_strictly_lower(version_set):
                    return VersionEmpty()

                intersection_min = version_set.min
                intersection_include_min = version_set.include_min

            else:
                if self.is_strictly_higher(version_set):
                    return VersionEmpty()

                intersection_min = self.min
                intersection_include_min = self.include_min

            if self.is_higher(version_set):
                intersection_max = version_set.max
                intersection_include_max = version_set.include_max

            else:
                intersection_max = self.max
                intersection_include_max = self.include_max

            # if we reached here, there is an actual range
            intersection = VersionRange(
                intersection_min,
                intersection_max,
                intersection_include_min,
                intersection_include_max,
            )

            if intersection.is_point():
                return VersionPoint(intersection.version)

            return intersection

        if is_version_union(version_set):
            return version_set.intersection(self)

        raise TypeError  # TODO: message

    def union(self, version_set: VersionSet) -> VersionSet:
        if is_version_empty(version_set):
            return self

        if is_version_point(version_set):
            version = version_set.version

            if self.contains(version):
                return self

            if version == self.min:
                return evolve(self, include_min=True)

            if version == self.max:
                return evolve(self, include_max=True)

            return VersionUnion.of(self, version_set)

        if is_version_range(version_set):
            if not self.is_adjacent(version_set) and not self.intersects(version_set):
                return VersionUnion.of(self, version_set)

            if self.is_lower(version_set):
                union_min = self.min
                union_include_min = self.include_min

            else:
                union_min = version_set.min
                union_include_min = version_set.include_min

            if self.is_higher(version_set):
                union_max = self.max
                union_include_max = self.include_max

            else:
                union_max = version_set.max
                union_include_max = version_set.include_max

            return VersionRange(
                union_min,
                union_max,
                union_include_min,
                union_include_max,
            )

        if is_version_union(version_set):
            return version_set.union(self)

        raise TypeError  # TODO: message

    def difference(self, version_set: VersionSet) -> VersionSet:
        if is_version_empty(version_set):
            return self

        if is_version_point(version_set):
            version = version_set.version

            if not self.contains(version):
                return self

            if version == self.min:
                if self.exclude_min:
                    return self

                return evolve(self, include_min=False)

            if version == self.max:
                if self.exclude_max:
                    return self

                return evolve(self, include_max=False)

            return VersionUnion.of(
                evolve(self, max=version, include_max=False),
                evolve(self, min=version, include_min=False),
            )

        if is_version_range(version_set):
            if not self.intersects(version_set):
                return self

            before: Optional[VersionItem]

            if not self.is_lower(version_set):
                before = None

            elif self.min == version_set.min:
                before = VersionPoint(self.checked_min)

            else:
                before = evolve(self, max=version_set.min, include_max=version_set.exclude_min)

            after: Optional[VersionItem]

            if not self.is_higher(version_set):
                after = None

            elif self.max == version_set.max:
                after = VersionPoint(self.checked_max)

            else:
                after = evolve(self, min=version_set.max, include_min=version_set.exclude_max)

            if before is None and after is None:
                return VersionEmpty()

            if before is None:
                return after  # type: ignore

            if after is None:
                return before  # type: ignore

            return VersionUnion.of(before, after)

        if is_version_union(version_set):
            return VersionUnion.of_iterable(self.difference_iterator(version_set))

        raise TypeError  # TODO: message?

    def difference_iterator(self, version_union: VersionUnion) -> Iterator[VersionItem]:
        current: VersionItem = self

        for item in version_union.items:
            if item.is_strictly_lower(current):
                continue

            if item.is_strictly_higher(current):
                break

            difference = current.difference(item)

            if is_version_union(difference):
                item, current = difference.items

                yield item

            if is_version_item(difference):
                current = difference

        yield current

    def complement(self) -> VersionSet:
        return VersionRange().difference(self)

    def to_string_iterator(self) -> Iterator[str]:
        if self.is_empty():
            yield EMPTY_VERSION
            return

        if self.is_point():
            yield self.version.to_string()
            return

        if self.is_universe():
            yield UNIVERSE_VERSION
            return

        min = self.min

        if min:
            min_type = OperatorType.GREATER_OR_EQUAL if self.include_min else OperatorType.GREATER
            min_operator = Operator(min_type, min)

            yield min_operator.to_string()

        max = self.max

        if max:
            max_type = OperatorType.LESS_OR_EQUAL if self.include_max else OperatorType.LESS
            max_operator = Operator(max_type, max)

            yield max_operator.to_string()

    def to_short_string_iterator(self) -> Iterator[str]:
        if self.is_empty():
            yield EMPTY_VERSION
            return

        if self.is_point():
            yield self.version.to_short_string()
            return

        if self.is_universe():
            yield UNIVERSE_VERSION
            return

        min = self.min

        if min:
            min_type = OperatorType.GREATER_OR_EQUAL if self.include_min else OperatorType.GREATER
            min_operator = Operator(min_type, min)

            yield min_operator.to_short_string()

        max = self.max

        if max:
            max_type = OperatorType.LESS_OR_EQUAL if self.include_max else OperatorType.LESS
            max_operator = Operator(max_type, max)

            yield max_operator.to_short_string()

    def to_string(self) -> str:
        return concat_comma_space(self.to_string_iterator())

    def to_short_string(self) -> str:
        return concat_comma(self.to_short_string_iterator())


@frozen(repr=False, eq=False, order=False)
class VersionPoint(Representation, ToString, VersionRangeProtocol, VersionSetProtocol):
    """Represents version points (`[v, v]` aka `{v}`)."""

    version: Version

    @property
    def min(self) -> Optional[Version]:  # type: ignore
        return self.version

    @property
    def max(self) -> Optional[Version]:  # type: ignore
        return self.version

    @property
    def include_min(self) -> bool:  # type: ignore
        return True

    @property
    def include_max(self) -> bool:  # type: ignore
        return True

    def is_empty(self) -> bool:
        return False

    def is_point(self) -> bool:
        return True

    def is_universe(self) -> bool:
        return False

    def contains(self, version: Version) -> bool:
        # version = self.version.weaken(version)
        return self.version == version

    accepts = contains

    def includes(self, version_set: VersionSet) -> bool:
        return version_set.is_empty() or (
            is_version_point(version_set) and self.contains(version_set.version)
        )

    def intersects(self, version_set: VersionSet) -> bool:
        return version_set.contains(self.version)

    def intersection(self, version_set: VersionSet) -> VersionSet:
        return self if version_set.contains(self.version) else VersionEmpty()

    def union(self, version_set: VersionSet) -> VersionSet:
        if is_version_empty(version_set):
            return self

        if is_version_point(version_set):
            if self.contains(version_set.version):
                return self

            return VersionUnion.of(self, version_set)

        if version_set.contains(self.version):
            return version_set

        if is_version_range(version_set) or is_version_union(version_set):
            return VersionUnion.of(self, version_set)

        raise TypeError  # TODO: message?

    def difference(self, version_set: VersionSet) -> VersionSet:
        return VersionEmpty() if version_set.contains(self.version) else self

    def complement(self) -> VersionSet:
        return VersionRange().difference(self)

    def to_string(self) -> str:
        return self.version.to_string()

    def to_short_string(self) -> str:
        return self.version.to_short_string()


NO_ITEMS = "expected at least 2 items, 0 found"
ONE_ITEM = "expected at least 2 items, 1 found; consider using it directly"


def check_items(items: VersionItems) -> None:
    if not items:
        raise ValueError(NO_ITEMS)

    if contains_only_item(items):
        raise ValueError(ONE_ITEM)


@frozen(repr=False, order=False)
class VersionUnion(Representation, ToString, Specification):
    """Represents version unions."""

    items: VersionItems = field()

    @items.validator
    def check_items(self, attribute: Attribute[VersionItems], items: VersionItems) -> None:
        check_items(items)

    @classmethod
    def extract(cls, version_set: VersionSet) -> Iterator[VersionItem]:
        if is_version_union(version_set):
            yield from version_set.items

        elif is_version_item(version_set):
            yield version_set

        else:
            raise TypeError  # TODO: message?

    @classmethod
    def of(cls, *version_sets: VersionSet) -> VersionSet:
        return cls.of_iterable(version_sets)

    @classmethod
    def of_iterable(cls, iterable: Iterable[VersionSet]) -> VersionSet:
        extracted = list(flatten(map(cls.extract, iterable)))

        if not extracted:
            return VersionEmpty()

        if any(item.is_universe() for item in extracted):
            return VersionRange()

        extracted.sort()

        merged: List[VersionItem] = []

        for item in extracted:
            if not merged:
                merged.append(item)

            else:
                last_item = last(merged)

                if last_item.intersects(item) or last_item.is_adjacent(item):
                    result = last_item.union(item)

                    if is_version_item(result):
                        set_last(merged, result)

                    else:
                        raise InternalError  # TODO: message?

                else:
                    merged.append(item)

        if contains_only_item(merged):
            return first(merged)

        return cls(tuple(merged))

    @property
    def exclude_version(self) -> Optional[Version]:
        complement = self.complement()

        return complement.version if is_version_point(complement) else None

    def is_empty(self) -> bool:
        return False

    def is_universe(self) -> bool:
        return False

    def contains(self, version: Version) -> bool:
        return any(item.contains(version) for item in self.items)

    accepts = contains

    def includes(self, version_set: VersionSet) -> bool:
        self_items = iter(self.items)
        items = self.extract(version_set)

        self_item = next_or_none(self_items)
        item = next_or_none(items)

        while self_item and item:
            if self_item.includes(item):
                item = next_or_none(items)

            else:
                self_item = next_or_none(self_items)

        return item is None  # all items are covered

    def intersects(self, version_set: VersionSet) -> bool:
        self_items = iter(self.items)
        items = self.extract(version_set)

        self_item = next_or_none(self_items)
        item = next_or_none(items)

        while self_item and item:
            if self_item.intersects(item):
                return True

            if item.is_higher(self_item):
                self_item = next_or_none(self_items)

            else:
                item = next_or_none(items)

        return False  # none of the items are allowed

    def intersection_iterator(self, version_set: VersionSet) -> Iterator[VersionItem]:
        self_items = iter(self.items)
        items = self.extract(version_set)

        self_item = next_or_none(self_items)
        item = next_or_none(items)

        while self_item and item:
            intersection = self_item.intersection(item)

            if is_version_item(intersection):
                yield intersection

            if item.is_higher(self_item):
                self_item = next_or_none(self_items)

            else:
                item = next_or_none(items)

    def intersection(self, version_set: VersionSet) -> VersionSet:
        return self.of_iterable(self.intersection_iterator(version_set))

    def union(self, version_set: VersionSet) -> VersionSet:
        return self.of(self, version_set)

    def difference(self, version_set: VersionSet) -> VersionSet:
        items_difference = ItemsDifference(iter(self.items), self.extract(version_set))
        return self.of_iterable(items_difference.compute())

    def complement(self) -> VersionSet:
        return VersionRange().difference(self)

    def to_string(self) -> str:
        exclude_version = self.exclude_version

        if exclude_version:
            operator = Operator(OperatorType.NOT_EQUAL, exclude_version)

            return operator.to_string()

        return concat_pipes_spaced(item.to_string() for item in self.items)

    def to_short_string(self) -> str:
        exclude_version = self.exclude_version

        if exclude_version:
            operator = Operator(OperatorType.NOT_EQUAL, exclude_version)

            return operator.to_short_string()

        return concat_pipes(item.to_short_string() for item in self.items)


ALREADY_PREPARED = "`prepare` must be called exactly once"
NOT_PREPARED = "`prepare` must be called before computing"


@define()
class ItemsDifference:
    items: Iterator[VersionItem] = field(repr=False)
    other_items: Iterator[VersionItem] = field(repr=False)

    current: Optional[VersionItem] = field(default=None, init=False)
    other_current: Optional[VersionItem] = field(default=None, init=False)

    prepared: bool = field(default=False, init=False)

    result: List[VersionItem] = field(factory=list, init=False)

    def is_prepared(self) -> bool:
        return self.prepared

    def is_not_prepared(self) -> bool:
        return not self.prepared

    def check_prepared(self) -> None:
        if self.is_not_prepared():
            raise ValueError(NOT_PREPARED)

    def check_not_prepared(self) -> None:
        if self.is_prepared():
            raise ValueError(ALREADY_PREPARED)

    def next_other_current(self) -> bool:
        self.other_current = next_or_none(self.other_items)

        if self.other_current:  # if another item is available
            return True  # continue iteration

        # otherwise, append all remaining items to result

        result = self.result
        current = self.current

        if current:
            result.append(current)

        for item in self.items:
            result.append(item)

        return False  # stop iteration

    def next_current(self, include_current: bool = True) -> bool:
        current = self.current

        if include_current and current:  # add current if needed
            self.result.append(current)

        current = next_or_none(self.items)

        if not current:  # if items are exhausted
            return False  # stop iteration

        self.current = current

        return True  # continue iteration

    def prepare(self) -> None:
        self.check_not_prepared()

        self.current = next_or_none(self.items)
        self.other_current = next_or_none(self.other_items)

        self.prepared = True

    def step(self) -> bool:
        self.check_prepared()

        current = self.current
        other_current = self.other_current

        if not current or not other_current:
            return False

        if other_current.is_strictly_lower(current):
            return self.next_other_current()

        if other_current.is_strictly_higher(current):
            return self.next_current()

        # if we reach here, current items are guaranteed to be overlapping
        difference = current.difference(other_current)

        if is_version_union(difference):  # one item is contained within another
            left, right = difference.items

            self.result.append(left)

            self.current = right

            return self.next_other_current()

        if is_version_empty(difference):
            return self.next_current(include_current=False)

        if is_version_range(difference):
            self.current = difference

            if difference.is_higher(other_current):  # apply last check in the step
                return self.next_other_current()

            else:
                return self.next_current()

        raise TypeError  # TODO: message?

    def loop(self) -> None:
        # print("prepared", self)

        while self.step():
            # print("step", self)
            pass

        # print("finished", self)

    def compute(self) -> List[VersionItem]:
        self.prepare()

        self.loop()

        return self.result


VersionSet = Union[VersionEmpty, VersionPoint, VersionRange, VersionUnion]
"""The union of the following types:

- [`VersionEmpty`][versions.version_sets.VersionEmpty]
- [`VersionPoint`][versions.version_sets.VersionPoint]
- [`VersionRange`][versions.version_sets.VersionRange]
- [`VersionUnion`][versions.version_sets.VersionUnion]
"""
VersionSetTypes = (VersionEmpty, VersionPoint, VersionRange, VersionUnion)

VersionItem = Union[VersionPoint, VersionRange]
VersionItemTypes = (VersionPoint, VersionRange)

VersionItems = DynamicTuple[VersionItem]
