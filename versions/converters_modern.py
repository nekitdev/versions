from functools import reduce

from versions.converters_utils import (
    pin_version,
    try_exclude_version,
    try_range_simple,
    try_range_unwrap,
    version_set_intersection,
    version_set_union,
)
from versions.specifiers import (
    NEVER,
    Specifier,
    SpecifierAll,
    SpecifierAlways,
    SpecifierAny,
    SpecifierNever,
    SpecifierOne,
)
from versions.utils import cache
from versions.version_sets import (
    EMPTY_SET,
    UNIVERSAL_SET,
    VersionEmpty,
    VersionPoint,
    VersionRange,
    VersionSet,
    VersionUnion,
)

__all__ = (
    "simplify",
    "specifier_from_version_set",
    "specifier_to_version_set",
    "version_set_from_specifier",
    "version_set_to_specifier",
)


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


@cache
def specifier_to_version_set(specifier: Specifier) -> VersionSet:
    """Converts a [`Specifier`][versions.specifiers.Specifier]
    to [`VersionSet`][versions.version_sets.VersionSet].

    Arguments:
        specifier: The version specifier to convert.

    Returns:
        The converted version set.
    """
    match specifier:
        case SpecifierOne(_, version) as specifier_one:
            return specifier_one.translate(version)

        case SpecifierNever():
            return EMPTY_SET

        case SpecifierAlways():
            return UNIVERSAL_SET

        case SpecifierAll(specifiers):
            return reduce(version_set_intersection, map(specifier_to_version_set, specifiers))

        case SpecifierAny(specifiers):
            return reduce(version_set_union, map(specifier_to_version_set, specifiers))

        case _:
            raise TypeError(UNEXPECTED_SPECIFIER.format(repr(specifier)))


version_set_from_specifier = specifier_to_version_set
"""An alias of [`specifier_to_version_set`][versions.converters.specifier_to_version_set]."""


UNEXPECTED_VERSION_SET = "unexpected version set provided: {}"


@cache
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
            return NEVER

        case VersionPoint(version):
            return pin_version(version)

        case VersionRange(min, max, include_min, include_max) as version_range:
            return try_range_simple(version_range) or try_range_unwrap(
                min, max, include_min, include_max
            )

        case VersionUnion(version_items) as version_union:
            return try_exclude_version(version_union) or SpecifierAny.of_iterable(
                map(version_set_to_specifier, version_items)
            )

    raise TypeError(UNEXPECTED_VERSION_SET.format(repr(version_set)))


specifier_from_version_set = version_set_to_specifier
"""An alias of [`version_set_to_specifier`][versions.converters.version_set_to_specifier]."""
