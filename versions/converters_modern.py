from functools import reduce

from versions.errors import InternalError
from versions.operators import OperatorType
from versions.specifiers import (
    Specifier, SpecifierAll, SpecifierAny, SpecifierFalse, SpecifierOne, SpecifierTrue
)
from versions.version_sets import VersionEmpty, VersionPoint, VersionRange, VersionSet, VersionUnion

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

    The simplification is accomplished through converting to the version set and back.

    Arguments:
        specifier: The version specifier to simplify.

    Returns:
        The simplified specifier.
    """
    return specifier_from_version_set(specifier_to_version_set(specifier))


UNEXPECTED_SPECIFIER = "unexpected specifier provided: {}"


def specifier_to_version_set(specifier: Specifier) -> VersionSet:
    """Converts a [`Specifier`][versions.specifiers.Specifier]
    to [`VersionSet`][versions.version_sets.VersionSet].

    Arguments:
        specifier: The version specifier to convert.

    Returns:
        The converted version set.
    """
    match specifier:
        case SpecifierOne(_, version) as one:
            return one.translate(version)

        case SpecifierFalse():
            return VersionEmpty()

        case SpecifierTrue():
            return VersionRange()

        case SpecifierAll(specifiers):
            return reduce(intersection, map(specifier_to_version_set, specifiers))

        case SpecifierAny(specifiers):
            return reduce(union, map(specifier_to_version_set, specifiers))

        case _:
            raise TypeError(UNEXPECTED_SPECIFIER.format(repr(specifier)))


version_set_from_specifier = specifier_to_version_set
"""An alias of [`specifier_to_version_set`][versions.converters.specifier_to_version_set]."""


UNEXPECTED_VERSION_SET = "unexpected version set provided: {}"

EXPECTED_MIN_OR_MAX = "expected either `min` or `max` to be different from `None`"


def version_set_to_specifier(version_set: VersionSet) -> Specifier:
    """Converts a [`VersionSet`][versions.version_sets.VersionSet]
    to [`Specifier`][versions.specifiers.Specifier].

    Arguments:
        version_set: The version set to convert.

    Returns:
        The converted version specifier.
    """
    match version_set:
        case VersionEmpty():
            return SpecifierFalse()

        case VersionPoint(version):
            return SpecifierOne(OperatorType.DOUBLE_EQUAL, version)

        case VersionRange(min, max, include_min, include_max) as version_range:
            if version_range.is_empty():
                return SpecifierFalse()

            if version_range.is_universe():
                return SpecifierTrue()

            if version_range.is_point():
                return SpecifierOne(OperatorType.DOUBLE_EQUAL, version_range.version)

            min_specifier = None
            max_specifier = None

            if min:
                min_type = OperatorType.GREATER_OR_EQUAL if include_min else OperatorType.GREATER
                min_specifier = SpecifierOne(min_type, min)

            if max:
                max_type = OperatorType.LESS_OR_EQUAL if include_max else OperatorType.LESS
                max_specifier = SpecifierOne(max_type, max)

            if min_specifier and max_specifier:
                return SpecifierAll.of(min_specifier, max_specifier)

            specifier = min_specifier or max_specifier

            if specifier is None:
                raise InternalError(EXPECTED_MIN_OR_MAX)

            return specifier

        case VersionUnion(version_items) as version_union:
            exclude_version = version_union.exclude_version

            if exclude_version:
                return SpecifierOne(Operator.NOT_EQUAL, exclude_version)

            return SpecifierAny.of_iterable(map(version_set_to_specifier, version_items))

        case _:
            raise TypeError(UNEXPECTED_VERSION_SET.format(repr(version_set)))


specifier_from_version_set = version_set_to_specifier
"""An alias of [`version_set_to_specifier`][versions.converters.version_set_to_specifier]."""