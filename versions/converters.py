from functools import reduce

from versions.errors import InternalError
from versions.operators import OperatorType
from versions.specifiers import (
    Specifier,
    SpecifierAll,
    SpecifierAny,
    SpecifierFalse,
    SpecifierSingle,
    SpecifierTrue,
    is_specifier_all,
    is_specifier_any,
    is_specifier_false,
    is_specifier_single,
    is_specifier_true,
)
from versions.version_sets import (
    VersionEmpty,
    VersionRange,
    VersionSet,
    is_version_empty,
    is_version_point,
    is_version_range,
    is_version_union,
)

__all__ = (
    "simplify",
    "specifier_from_version_set",
    "specifier_to_version_set",
    "version_set_from_specifier",
    "version_set_to_specifier",
)


def intersection(left: VersionSet, right: VersionSet) -> VersionSet:
    return left.intersection(right)


def union(left: VersionSet, right: VersionSet) -> VersionSet:
    return left.union(right)


def simplify(specifier: Specifier) -> Specifier:
    """Simplifies a [`Specifier`][versions.specifiers.Specifier].

    Simplification is accomplished through converting to the version set and back.

    Arguments:
        specifier: The version specifier to simplify.

    Returns:
        The simplified specifier.
    """
    return specifier_from_version_set(specifier_to_version_set(specifier))


def specifier_to_version_set(specifier: Specifier) -> VersionSet:
    """Converts a [`Specifier`][versions.specifiers.Specifier]
    to [`VersionSet`][versions.version_sets.VersionSet].

    Arguments:
        specifier: The version specifier to convert.

    Returns:
        The converted version set.
    """
    if is_specifier_single(specifier):
        return specifier.translate(specifier.version)

    if is_specifier_false(specifier):
        return VersionEmpty()

    if is_specifier_true(specifier):
        return VersionRange()

    if is_specifier_all(specifier):
        return reduce(intersection, map(specifier_to_version_set, specifier.specifiers))

    if is_specifier_any(specifier):
        return reduce(union, map(specifier_to_version_set, specifier.specifiers))

    raise TypeError  # TODO: message?


version_set_from_specifier = specifier_to_version_set
"""An alias of [`specifier_to_version_set`][versions.converters.specifier_to_version_set]."""


def version_set_to_specifier(version_set: VersionSet) -> Specifier:
    """Converts a [`VersionSet`][versions.version_sets.VersionSet]
    to [`Specifier`][versions.specifiers.Specifier].

    Arguments:
        version_set: The version set to convert.

    Returns:
        The converted version specifier.
    """
    if is_version_empty(version_set):
        return SpecifierFalse()

    if is_version_point(version_set):
        return SpecifierSingle(OperatorType.DOUBLE_EQUAL, version_set.version)

    if is_version_range(version_set):
        if version_set.is_empty():
            return SpecifierFalse()

        if version_set.is_universe():
            return SpecifierTrue()

        if version_set.is_point():
            return SpecifierSingle(OperatorType.DOUBLE_EQUAL, version_set.version)

        min = version_set.min
        max = version_set.max

        min_specifier = None
        max_specifier = None

        if min:
            min_type = (
                OperatorType.GREATER_OR_EQUAL if version_set.include_min else OperatorType.GREATER
            )
            min_specifier = SpecifierSingle(min_type, min)

        if max:
            max_type = OperatorType.LESS_OR_EQUAL if version_set.include_max else OperatorType.LESS
            max_specifier = SpecifierSingle(max_type, max)

        if min_specifier and max_specifier:
            return SpecifierAll.of(min_specifier, max_specifier)

        specifier = min_specifier or max_specifier

        if specifier is None:
            raise InternalError  # TODO: message?

        return specifier

    if is_version_union(version_set):
        exclude_version = version_set.exclude_version

        if exclude_version:
            return SpecifierSingle(OperatorType.NOT_EQUAL, exclude_version)

        return SpecifierAny.of_iterable(map(version_set_to_specifier, version_set.items))

    raise TypeError  # TODO: message?


specifier_from_version_set = version_set_to_specifier
"""An alias of [`version_set_to_specifier`][versions.converters.version_set_to_specifier]."""
