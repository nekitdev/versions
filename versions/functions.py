from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar, overload

from versions.parsers import SpecifierParser, VersionParser, VersionSetParser
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


def parse_version(string: str, version_type: Type[Version] = Version) -> Version:
    return VersionParser(version_type).parse(string)


def parse_specifier(string: str, version_type: Type[Version] = Version) -> Specifier:
    return SpecifierParser(VersionParser(version_type)).parse(string)


def parse_version_set(string: str, version_type: Type[Version] = Version) -> VersionSet:
    return VersionSetParser(SpecifierParser(VersionParser(version_type))).parse(string)
