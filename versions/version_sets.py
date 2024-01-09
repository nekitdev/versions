from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)

from attrs import Attribute, define, evolve, field, frozen
from orderings import Ordering
from typing_aliases import DynamicTuple, is_instance, required
from typing_extensions import Self, TypeGuard

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
from versions.types import Infinity, NegativeInfinity, infinity, negative_infinity
from versions.utils import contains_only_item, first, flatten, last, next_or_none, set_last

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


@runtime_checkable
class VersionSetProtocol(Specification, Protocol):
    @required
    def is_empty(self) -> bool:
        """Checks if the set is *empty*.

        Returns:
            Whether the set is *empty*.
        """
        raise NotImplementedError

    @required
    def is_universal(self) -> bool:
        """Checks if the set is the *universal*.

        Returns:
            Whether the set is *universal*.
        """
        raise NotImplementedError

    @required
    def includes(self, version_set: VersionSet) -> bool:
        """Checks if the set includes `version_set`.

        Returns:
            Whether the set includes `version_set`.
        """
        raise NotImplementedError

    @required
    def intersects(self, version_set: VersionSet) -> bool:
        """Checks if the set intersects `version_set`.

        Returns:
            Whether the set intersects `version_set`.
        """
        raise NotImplementedError

    @required
    def contains(self, version: Version) -> bool:
        """Checks if the set contains some `version`.

        Returns:
            Whether the `version` is contained within the set.
        """
        raise NotImplementedError

    def accepts(self, version: Version) -> bool:
        """Checks if the set contains some `version`.

        This is an implementation of the [`accepts`][versions.specification.Specification.accepts]
        method of [`Specification`][versions.specification.Specification] protocol, equivalent to
        [`self.contains(version)`][versions.version_sets.VersionSetProtocol.contains].

        Returns:
            Whether the `version` is accepted by the set.
        """
        return self.contains(version)

    @required
    def intersection(self, version_set: VersionSet) -> VersionSet:
        """Computes the *intersection* of `self` and `version_set`.

        Returns:
            The set representing the *intersection* of `self` and `version_set`.
        """
        raise NotImplementedError

    @required
    def union(self, version_set: VersionSet) -> VersionSet:
        """Computes the *union* of `self` and `version_set`.

        Returns:
            The set representing the *union* of `self` and `version_set`.
        """
        raise NotImplementedError

    @required
    def difference(self, version_set: VersionSet) -> VersionSet:
        """Computes the *difference* of `self` and `version_set`.

        Returns:
            The set representing the *difference* of `self` and `version_set`.
        """
        raise NotImplementedError

    @required
    def complement(self) -> VersionSet:
        """Computes the *complement* of `self`.

        Returns:
            The set representing the *complement* of `self`.
        """
        raise NotImplementedError

    def symmetric_difference(self, version_set: VersionSet) -> VersionSet:
        """Computes the *symmetric difference* of `self` and `version_set`.

        Equivalent to [`self.union(version_set).difference(self.intersection(version_set))`]
        [versions.version_sets.VersionSetProtocol.difference].

        Returns:
            The set representing the *symmetric difference* of `self` and `version_set`.
        """
        return self.union(version_set).difference(self.intersection(version_set))

    def __contains__(self, version: Version) -> bool:
        """Checks if the set contains some `version` via the *contains* (`in`) operation.

        Returns:
            Whether the `version` is contained within the set.
        """
        return self.contains(version)

    def __and__(self, version_set: VersionSet) -> VersionSet:
        """Computes the *intersection* of `self` and `version_set` via the *and* (`&`) operation.

        This is equivalent to [`self.intersection(version_set)`]
        [versions.version_sets.VersionSetProtocol.intersection].

        Returns:
            The set representing the *intersection* of `self` and `version_set`.
        """
        return self.intersection(version_set)

    def __iand__(self, version_set: VersionSet) -> VersionSet:
        """Computes the *intersection* of `self` and `version_set` via the *and-assign*
        (`&=`) operation.

        This is equivalent to [`self.intersection(version_set)`]
        [versions.version_sets.VersionSetProtocol.intersection].

        Returns:
            The set representing the *intersection* of `self` and `version_set`.
        """
        return self.intersection(version_set)

    def __or__(self, version_set: VersionSet) -> VersionSet:
        """Computes the *union* of `self` and `version_set` via the *or* (`|`) operation.

        This is equivalent to [`self.union(version_set)`]
        [versions.version_sets.VersionSetProtocol.union].

        Returns:
            The set representing the *union* of `self` and `version_set`.
        """
        return self.union(version_set)

    def __ior__(self, version_set: VersionSet) -> VersionSet:
        """Computes the *union* of `self` and `version_set` via the *or-assign* (`|=`) operation.

        This is equivalent to [`self.union(version_set)`]
        [versions.version_sets.VersionSetProtocol.union].

        Returns:
            The set representing the *union* of `self` and `version_set`.
        """
        return self.union(version_set)

    def __sub__(self, version_set: VersionSet) -> VersionSet:
        """Computes the *difference* of `self` and `version_set` via the *sub* (`-`) operation.

        This is equivalent to [`self.difference(version_set)`]
        [versions.version_sets.VersionSetProtocol.difference].

        Returns:
            The set representing the *difference* of `self` and `version_set`.
        """
        return self.difference(version_set)

    def __isub__(self, version_set: VersionSet) -> VersionSet:
        """Computes the *difference* of `self` and `version_set` via the *sub-assign*
        (`-=`) operation.

        This is equivalent to [`self.difference(version_set)`]
        [versions.version_sets.VersionSetProtocol.difference].

        Returns:
            The set representing the *difference* of `self` and `version_set`.
        """
        return self.difference(version_set)

    def __xor__(self, version_set: VersionSet) -> VersionSet:
        """Computes the *symmetric difference* of `self` and `version_set` via the *xor*
        (`^`) operation.

        This is equivalent to [`self.symmetric_difference(version_set)`]
        [versions.version_sets.VersionSetProtocol.symmetric_difference].

        Returns:
            The set representing the *symmetric difference* of `self` and `version_set`.
        """
        return self.symmetric_difference(version_set)

    def __ixor__(self, version_set: VersionSet) -> VersionSet:
        """Computes the *symmetric difference* of `self` and `version_set` via the *xor-assign*
        (`^=`) operation.

        This is equivalent to [`self.symmetric_difference(version_set)`]
        [versions.version_sets.VersionSetProtocol.symmetric_difference].

        Returns:
            The set representing the *symmetric difference* of `self` and `version_set`.
        """
        return self.symmetric_difference(version_set)

    def __negate__(self) -> VersionSet:
        """Computes the *complement* of `self` via the *negate* (`~`) operation.

        This is equivalent to [`self.complement()`]
        [versions.version_sets.VersionSetProtocol.complement].

        Returns:
            The set representing the *complement* of `self`.
        """
        return self.complement()


def is_version_empty(item: Any) -> TypeGuard[VersionEmpty]:
    """Checks if an `item` is an instance of [`VersionEmpty`][versions.version_sets.VersionEmpty].

    Returns:
        Whether the `item` provided is an instance
            of [`VersionEmpty`][versions.version_sets.VersionEmpty].
    """
    return is_instance(item, VersionEmpty)


def is_version_point(item: Any) -> TypeGuard[VersionPoint]:
    """Checks if an `item` is an instance of [`VersionPoint`][versions.version_sets.VersionPoint].

    Returns:
        Whether the `item` provided is an instance
            of [`VersionPoint`][versions.version_sets.VersionPoint].
    """
    return is_instance(item, VersionPoint)


def is_version_range(item: Any) -> TypeGuard[VersionRange]:
    """Checks if an `item` is an instance of [`VersionRange`][versions.version_sets.VersionRange].

    Returns:
        Whether the `item` provided is an instance
            of [`VersionRange`][versions.version_sets.VersionRange].
    """
    return is_instance(item, VersionRange)


def is_version_union(item: Any) -> TypeGuard[VersionUnion]:
    """Checks if an `item` is an instance of [`VersionUnion`][versions.version_sets.VersionUnion].

    Returns:
        Whether the `item` provided is an instance
            of [`VersionUnion`][versions.version_sets.VersionUnion].
    """
    return is_instance(item, VersionUnion)


def is_version_item(item: Any) -> TypeGuard[VersionItem]:
    """Checks if an `item` is an instance of [`VersionItem`][versions.version_sets.VersionItem].

    Returns:
        Whether the `item` provided is an instance
            of [`VersionItem`][versions.version_sets.VersionItem].
    """
    return is_instance(item, VersionItemTypes)


def is_version_set(item: Any) -> TypeGuard[VersionSet]:
    """Checks if an `item` is an instance of [`VersionSet`][versions.version_sets.VersionSet].

    Returns:
        Whether the `item` provided is an instance
            of [`VersionSet`][versions.version_sets.VersionSet].
    """
    return is_instance(item, VersionSetTypes)


E = TypeVar("E", bound="VersionEmpty")
S = TypeVar("S", bound="VersionSet")


@frozen(repr=False, order=False)
class VersionEmpty(Representation, ToString, VersionSetProtocol):
    """Represents empty version sets (`0`)."""

    def is_empty(self) -> Literal[True]:
        return True

    def is_universal(self) -> Literal[False]:
        return False

    def includes(self, version_set: VersionSet) -> bool:
        return version_set.is_empty()

    def intersects(self, version_set: VersionSet) -> Literal[False]:
        return False

    def contains(self, version: Version) -> Literal[False]:
        return False

    def intersection(self, version_set: VersionSet) -> Self:
        return self

    def union(self, version_set: S) -> S:
        return version_set

    def difference(self, version_set: VersionSet) -> Self:
        return self

    def symmetric_difference(self, version_set: S) -> S:
        return version_set

    def complement(self) -> VersionRange:
        return UNIVERSAL_SET

    def to_string(self) -> str:
        return EMPTY_VERSION


EMPTY_SET = VersionEmpty()

MIN_MAX_CONSTRAINT = "version ranges expect `min <= max`, got `min > max`"
RANGE_NOT_POINT = "version range is not a point"
UNEXPECTED_VERSION_SET = "unexpected version set provided: {}"
CAN_NOT_INCLUDE_INFINITY = "ranges can not contain infinities"


def unexpected_version_set(item: Any) -> TypeError:
    return TypeError(UNEXPECTED_VERSION_SET.format(item))


@frozen(repr=False, eq=False, order=False)
class VersionRange(Representation, ToString, VersionSetProtocol):
    """Represents version ranges (`(v, w)`, `(v, w]`, `[v, w)` and `[v, w]`)."""

    min: Optional[Version] = None
    max: Optional[Version] = None
    include_min: bool = False
    include_max: bool = False

    def __attrs_post_init__(self) -> None:
        if self.min is None and self.include_min:
            raise ValueError(CAN_NOT_INCLUDE_INFINITY)

        if self.max is None and self.include_max:
            raise ValueError(CAN_NOT_INCLUDE_INFINITY)

        if self.comparable_min > self.comparable_max:
            raise ValueError(MIN_MAX_CONSTRAINT)

    # range stuff

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

    def is_lower(self, other: VersionRange) -> bool:
        self_comparable_min = self.comparable_min
        other_comparable_min = other.comparable_min

        if self_comparable_min < other_comparable_min:
            return True

        if self_comparable_min > other_comparable_min:
            return False

        return self.include_min and other.exclude_min

    def is_higher(self, other: VersionRange) -> bool:
        self_comparable_max = self.comparable_max
        other_comparable_max = other.comparable_max

        if self_comparable_max < other_comparable_max:
            return False

        if self_comparable_max > other_comparable_max:
            return True

        return self.include_max and other.exclude_max

    def is_strictly_lower(self, other: VersionRange) -> bool:
        self_comparable_max = self.comparable_max
        other_comparable_min = other.comparable_min

        if self_comparable_max < other_comparable_min:
            return True

        if self_comparable_max > other_comparable_min:
            return False

        return self.exclude_max or other.exclude_min

    def is_strictly_higher(self, other: VersionRange) -> bool:
        self_comparable_min = self.comparable_min
        other_comparable_max = other.comparable_max

        if self_comparable_min > other_comparable_max:
            return True

        if self_comparable_min < other_comparable_max:
            return False

        return self.exclude_min or other.exclude_max

    def is_left_adjacent(self, other: VersionRange) -> bool:
        return (self.max == other.min) and (self.include_max is other.exclude_min)

    def is_right_adjacent(self, other: VersionRange) -> bool:
        return (self.min == other.max) and (self.include_min is other.exclude_max)

    def is_adjacent(self, other: VersionRange) -> bool:
        return self.is_left_adjacent(other) or self.is_right_adjacent(other)

    def __hash__(self) -> int:
        return hash(self.parameters)

    def __eq__(self, other: Any) -> bool:
        return is_version_range(other) and self.parameters == other.parameters

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: VersionRange) -> bool:
        return self.compare(other).is_less()

    def __le__(self, other: VersionRange) -> bool:
        return self.compare(other).is_less_or_equal()

    def __gt__(self, other: VersionRange) -> bool:
        return self.compare(other).is_greater()

    def __ge__(self, other: VersionRange) -> bool:
        return self.compare(other).is_greater_or_equal()

    def compare(self, other: VersionRange) -> Ordering:
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

    # protocol implementation

    def is_empty(self) -> bool:
        return self.is_empty_or_point() and not self.is_closed()

    def is_point(self) -> bool:
        return self.is_empty_or_point() and self.is_closed()

    def is_universal(self) -> bool:
        return self.is_unbounded()

    @property
    def version(self) -> Version:
        if self.is_point():
            return self.version_unchecked

        raise ValueError(RANGE_NOT_POINT)

    @property
    def version_unchecked(self) -> Version:
        version = self.min or self.max

        if version is None:  # we can not violate the type system
            raise ValueError(RANGE_NOT_POINT)

        return version

    def contains(self, version: Version) -> bool:
        comparable_min = self.comparable_min
        comparable_max = self.comparable_max

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

        raise unexpected_version_set(version_set)

    def intersects(self, version_set: VersionSet) -> bool:
        if is_version_empty(version_set):
            return False

        if is_version_point(version_set):
            return self.contains(version_set.version)

        if is_version_range(version_set):
            return self.intersects_range(version_set)

        if is_version_union(version_set):
            return any(self.intersects(item) for item in version_set.items)

        raise unexpected_version_set(version_set)

    def intersects_range(self, range: VersionRange) -> bool:
        return not range.is_strictly_lower(self) and not range.is_strictly_higher(self)

    def intersection(self, version_set: VersionSet) -> VersionSet:
        if is_version_empty(version_set):
            return EMPTY_SET

        if is_version_point(version_set):
            return version_set.intersection(self)

        if is_version_range(version_set):
            if self.is_lower(version_set):
                if self.is_strictly_lower(version_set):
                    return EMPTY_SET

                intersection_min = version_set.min
                intersection_include_min = version_set.include_min

            else:
                if self.is_strictly_higher(version_set):
                    return EMPTY_SET

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

        raise unexpected_version_set(version_set)

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

        raise unexpected_version_set(version_set)

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
                before = VersionPoint(self.min)  # type: ignore

            else:
                before = evolve(self, max=version_set.min, include_max=version_set.exclude_min)

            after: Optional[VersionItem]

            if not self.is_higher(version_set):
                after = None

            elif self.max == version_set.max:
                after = VersionPoint(self.max)  # type: ignore

            else:
                after = evolve(self, min=version_set.max, include_min=version_set.exclude_max)

            if before is None:
                if after is None:
                    return EMPTY_SET

                return after

            if after is None:
                if before is None:
                    return EMPTY_SET

                return before

            return VersionUnion.of(before, after)

        if is_version_union(version_set):
            return VersionUnion.of_iterable(self.difference_iterator(version_set))

        raise unexpected_version_set(version_set)

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
        return UNIVERSAL_SET.difference(self)

    def to_string_iterator(self) -> Iterator[str]:
        if self.is_empty():
            yield EMPTY_VERSION
            return

        if self.is_point():
            yield self.version.to_string()
            return

        if self.is_universal():
            yield UNIVERSE_VERSION
            return

        min = self.min

        if min is not None:
            min_operator = (
                Operator.greater_or_equal(min) if self.include_min else Operator.greater(min)
            )

            yield min_operator.to_string()

        max = self.max

        if max is not None:
            max_operator = Operator.less_or_equal(max) if self.include_max else Operator.less(max)

            yield max_operator.to_string()

    def to_short_string_iterator(self) -> Iterator[str]:
        if self.is_empty():
            yield EMPTY_VERSION
            return

        if self.is_point():
            yield self.version.to_short_string()
            return

        if self.is_universal():
            yield UNIVERSE_VERSION
            return

        min = self.min

        if min is not None:
            min_operator = (
                Operator.greater_or_equal(min) if self.include_min else Operator.greater(min)
            )

            yield min_operator.to_short_string()

        max = self.max

        if max is not None:
            max_operator = Operator.less_or_equal(max) if self.include_max else Operator.less(max)

            yield max_operator.to_short_string()

    def to_string(self) -> str:
        return concat_comma_space(self.to_string_iterator())

    def to_short_string(self) -> str:
        return concat_comma(self.to_short_string_iterator())


UNIVERSAL_SET = VersionRange()


@frozen(repr=False, eq=False, order=False)
class VersionPoint(VersionRange):
    """Represents version points (`[v, v]` ranges, also known as singleton sets `{v}`)."""

    version: Version = field()

    # initialize range fields accordingly

    min: Version = field(init=False)
    max: Version = field(init=False)

    include_min: Literal[True] = field(default=True, init=False)
    include_max: Literal[True] = field(default=True, init=False)

    @min.default
    def default_min(self) -> Version:
        return self.version

    @max.default
    def default_max(self) -> Version:
        return self.version

    def is_empty(self) -> bool:
        return False

    def is_point(self) -> bool:
        return True

    def is_universal(self) -> bool:
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
        return self if version_set.contains(self.version) else EMPTY_SET

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

        raise unexpected_version_set(version_set)

    def difference(self, version_set: VersionSet) -> VersionSet:
        return EMPTY_SET if version_set.contains(self.version) else self

    def complement(self) -> VersionSet:
        return UNIVERSAL_SET.difference(self)

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


UNEXPECTED_UNION = "the union of adjacent or intersecting ranges must be a range"

U = TypeVar("U", bound="VersionUnion")


@frozen(repr=False, order=False)
class VersionUnion(Representation, ToString, Specification):
    """Represents version unions."""

    items: VersionItems = field()

    @items.validator
    def check_items(self, attribute: Attribute[VersionItems], items: VersionItems) -> None:
        check_items(items)

    @classmethod
    def of_unchecked(cls: Type[U], *items: VersionItem) -> U:
        return cls(items)

    @classmethod
    def of_iterable_unchecked(cls: Type[U], items: Iterable[VersionItem]) -> U:
        return cls(tuple(items))

    @staticmethod
    def extract(version_set: VersionSet) -> Iterator[VersionItem]:
        if is_version_union(version_set):
            yield from version_set.items

        if is_version_item(version_set):
            yield version_set

    @classmethod
    def merge(cls, iterable: Iterable[VersionSet]) -> VersionSet:
        extracted = list(flatten(map(cls.extract, iterable)))

        if not extracted:
            return EMPTY_SET

        if any(item.is_universal() for item in extracted):
            return UNIVERSAL_SET

        extracted.sort()  # since ranges and points are ordered

        merged: List[VersionItem] = []

        for item in extracted:
            if not merged:  # nothing to merge yet
                merged.append(item)

            else:
                last_item = last(merged)

                if last_item.intersects(item) or last_item.is_adjacent(item):
                    result = last_item.union(item)

                    if is_version_item(result):
                        set_last(merged, result)

                    else:
                        raise InternalError(UNEXPECTED_UNION)

                else:
                    merged.append(item)

        if contains_only_item(merged):
            return first(merged)

        return cls.of_iterable_unchecked(merged)

    @classmethod
    def of(cls, *version_sets: VersionSet) -> VersionSet:
        return cls.of_iterable(version_sets)

    @classmethod
    def of_iterable(cls, version_sets: Iterable[VersionSet]) -> VersionSet:
        return cls.merge(version_sets)

    @property
    def exclude_version(self) -> Optional[Version]:
        complement = self.complement()

        return complement.version if is_version_point(complement) else None

    def is_empty(self) -> bool:
        return False

    def is_universal(self) -> bool:
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
        return UNIVERSAL_SET.difference(self)

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

        raise TypeError(UNEXPECTED_VERSION_SET.format(repr(difference)))

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
"""The union of [`VersionPoint`][versions.version_sets.VersionPoint]
and [`VersionRange`][versions.version_sets.VersionRange].
"""

VersionItemTypes = (VersionPoint, VersionRange)

VersionItems = DynamicTuple[VersionItem]
