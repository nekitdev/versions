from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar, overload

from versions.parsers import SpecifierParser, VersionParser, VersionSetParser
from versions.utils import cache
from versions.version import Version

if TYPE_CHECKING:
    from versions.specifiers import Specifier
    from versions.version_sets import VersionSet

__all__ = ("parse_version", "parse_specifier", "parse_version_set")

V = TypeVar("V", bound=Version)


@overload
def parse_version(string: str) -> Version:
    ...


@overload
def parse_version(string: str, version_type: Type[V]) -> V:
    ...


@cache
def parse_version(string: str, version_type: Type[Version] = Version) -> Version:
    """Parses a `string` into a version of `version_type`.

    Arguments:
        string: The string to parse.
        version_type: The version type to use in conversion.

    Returns:
        The newly parsed [`Version`][versions.version.Version].
    """
    return VersionParser(version_type).parse(string)


@cache
def parse_specifier(string: str, version_type: Type[Version] = Version) -> Specifier:
    """Parses a `string` into a version specifier with versions of `version_type`.

    Arguments:
        string: The string to parse.
        version_type: The version type to use in conversion.

    Returns:
        The newly parsed [`Specifier`][versions.specifiers.Specifier].
    """
    return SpecifierParser(VersionParser(version_type)).parse(string)


@cache
def parse_version_set(string: str, version_type: Type[Version] = Version) -> VersionSet:
    """Parses a `string` into a version set with versions of `version_type`.

    Arguments:
        string: The string to parse.
        version_type: The version type to use in conversion.

    Returns:
        The newly parsed [`VersionSet`][versions.version_sets.VersionSet].
    """
    return VersionSetParser(SpecifierParser(VersionParser(version_type))).parse(string)
