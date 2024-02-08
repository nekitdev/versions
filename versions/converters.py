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
    SpecifierAny,
    is_specifier_all,
    is_specifier_always,
    is_specifier_any,
    is_specifier_never,
    is_specifier_one,
)
from versions.utils import cache
from versions.version_sets import (
    EMPTY_SET,
    UNIVERSAL_SET,
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
    if is_specifier_one(specifier):
        return specifier.translate(specifier.version)

    if is_specifier_never(specifier):
        return EMPTY_SET

    if is_specifier_always(specifier):
        return UNIVERSAL_SET

    if is_specifier_all(specifier):
        return reduce(version_set_intersection, map(specifier_to_version_set, specifier.specifiers))

    if is_specifier_any(specifier):
        return reduce(version_set_union, map(specifier_to_version_set, specifier.specifiers))

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
    if is_version_empty(version_set):
        return NEVER

    if is_version_point(version_set):
        return pin_version(version_set.version)

    if is_version_range(version_set):
        return try_range_simple(version_set) or try_range_unwrap(
            version_set.min,
            version_set.max,
            version_set.include_min,
            version_set.include_max,
        )

    if is_version_union(version_set):
        return try_exclude_version(version_set) or SpecifierAny.of_iterable(
            map(version_set_to_specifier, version_set.items)
        )

    raise TypeError(UNEXPECTED_VERSION_SET.format(repr(version_set)))


specifier_from_version_set = version_set_to_specifier
"""An alias of [`version_set_to_specifier`][versions.converters.version_set_to_specifier]."""
