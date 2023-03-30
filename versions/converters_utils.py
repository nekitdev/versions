from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Optional

from versions.errors import InternalError
from versions.specifiers import Specifier, SpecifierAll, SpecifierFalse, SpecifierOne, SpecifierTrue
from versions.version_sets import VersionRange, VersionSet, VersionUnion

if TYPE_CHECKING:
    from versions.version import Version

__all__ = (
    "cache",
    "version_set_intersection",
    "version_set_union",
    "pin_version",
    "unpin_version",
    "try_exclude_version",
    "try_range_simple",
    "try_range_unwrap",
)

cache = lru_cache(None)


def version_set_intersection(left: VersionSet, right: VersionSet) -> VersionSet:
    return left.intersection(right)


def version_set_union(left: VersionSet, right: VersionSet) -> VersionSet:
    return left.union(right)


def pin_version(version: Version) -> SpecifierOne:
    return SpecifierOne.double_equal(version)


def unpin_version(version: Version) -> SpecifierOne:
    return SpecifierOne.not_equal(version)


def try_exclude_version(version_union: VersionUnion) -> Optional[SpecifierOne]:
    exclude_version = version_union.exclude_version

    return None if exclude_version is None else unpin_version(exclude_version)


def try_range_simple(version_range: VersionRange) -> Optional[Specifier]:
    if version_range.is_empty():
        return SpecifierFalse()

    if version_range.is_universal():
        return SpecifierTrue()

    if version_range.is_point():
        return pin_version(version_range.version)

    return None


EXPECTED_MIN_OR_MAX = "expected either `min` or `max` to be different from `None`"


def try_range_unwrap(
    min: Optional[Version], max: Optional[Version], include_min: bool, include_max: bool
) -> Specifier:
    min_specifier = None
    max_specifier = None

    if min is not None:
        min_specifier = (
            SpecifierOne.greater_or_equal(min) if include_min else SpecifierOne.greater(min)
        )

    if max is not None:
        max_specifier = SpecifierOne.less_or_equal(max) if include_max else SpecifierOne.less(max)

    if min_specifier is not None and max_specifier is not None:
        return SpecifierAll.of(min_specifier, max_specifier)

    specifier = min_specifier or max_specifier

    if specifier is None:
        raise InternalError(EXPECTED_MIN_OR_MAX)

    return specifier
