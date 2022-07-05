from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Mapping, Optional, Tuple, TypeVar, Union

from attrs import frozen

from versions.constants import (
    CARET,
    DOT,
    DOUBLE_EQUAL,
    EQUAL,
    GREATER,
    GREATER_OR_EQUAL,
    LESS,
    LESS_OR_EQUAL,
    NOT_EQUAL,
    STAR,
    TILDE,
    TILDE_EQUAL,
    WILDCARD_DOUBLE_EQUAL,
    WILDCARD_EQUAL,
    WILDCARD_NOT_EQUAL,
)
from versions.errors import InternalError
from versions.representation import Representation
from versions.string import ToString, concat_dot_args, concat_empty_args, concat_space_args
from versions.typing import Binary, Unary

if TYPE_CHECKING:
    from versions.version import Version
    from versions.version_sets import VersionSet

    Matches = Binary[Version, Version, bool]
    PartialMatches = Unary[Version, bool]
    Translate = Unary[Version, VersionSet]

__all__ = (
    # matching versions against specifiers
    "matches_caret",
    "matches_tilde",
    "matches_tilde_equal",
    "matches_equal",
    "matches_not_equal",
    "matches_less",
    "matches_less_or_equal",
    "matches_greater",
    "matches_greater_or_equal",
    "matches_wildcard_equal",
    "matches_wildcard_not_equal",
    # translating versions to constraints
    "translate_caret",
    "translate_tilde",
    "translate_tilde_equal",
    "translate_equal",
    "translate_not_equal",
    "translate_less",
    "translate_less_or_equal",
    "translate_greater",
    "translate_greater_or_equal",
    "translate_wildcard_equal",
    "translate_wildcard_not_equal",
    # get next breaking versions of different types
    "next_caret_breaking",
    "next_tilde_breaking",
    "next_tilde_equal_breaking",
    "next_wildcard_breaking",
    # operators
    "Operator",
    "OperatorType",
    # types that represent functions and their signatures
    "Matches",
    "PartialMatches",
    "Translate",
)

V = TypeVar("V", bound="Version")


def next_caret_breaking(version: V) -> V:
    return version.next_breaking()


def next_tilde_equal_breaking(version: V) -> V:
    index = version.last_index

    if index:
        return version.to_stable().next_at(index - 1)

    raise ValueError  # TODO: message?


def next_tilde_breaking(version: V) -> V:
    if version.has_minor():
        return version.next_minor()

    return version.next_major()


def next_wildcard_breaking(version: V) -> Optional[V]:
    # x.y.* -> x.y'.0
    # x.y.z-post.* -> x.y.z'
    # x.y.z-pre.* -> x.y.z

    index = version.last_index

    if version.is_stable() and not version.is_post_release():
        # the wildcard was used within the release segment

        if not index:
            return None

        index -= 1

    return version.next_at(index)  # this will take care of unstable releases


def wildcard_string(string: str, wildcard: str = STAR) -> str:
    string, _dot, _last = string.rpartition(DOT)

    return concat_dot_args(string, wildcard)


def wildcard_type(string: str, wildcard: str = STAR) -> str:
    return string.strip(wildcard)


def partial_matches(matches: Matches, against: Version) -> PartialMatches:
    def partial(version: Version) -> bool:
        return matches(version, against)

    return partial


def matches_caret(version: Version, against: Version) -> bool:
    return against <= version < next_caret_breaking(against)


def matches_tilde_equal(version: Version, against: Version) -> bool:
    return against <= version < next_tilde_equal_breaking(against)


def matches_tilde(version: Version, against: Version) -> bool:
    return against <= version < next_tilde_breaking(against)


def matches_equal(version: Version, against: Version) -> bool:
    return version == against


def matches_not_equal(version: Version, against: Version) -> bool:
    return version != against


def matches_less(version: Version, against: Version) -> bool:
    return version < against


def matches_less_or_equal(version: Version, against: Version) -> bool:
    return version <= against


def matches_greater(version: Version, against: Version) -> bool:
    return version > against


def matches_greater_or_equal(version: Version, against: Version) -> bool:
    return version >= against


def matches_wildcard_equal(version: Version, against: Version) -> bool:
    wildcard = next_wildcard_breaking(against)

    if wildcard is None:
        return True

    return against <= version < wildcard


def matches_wildcard_not_equal(version: Version, against: Version) -> bool:
    return not matches_wildcard_equal(version, against)


def translate_caret(version: Version) -> VersionRange:
    return VersionRange(
        min=version,
        max=next_caret_breaking(version),
        include_min=True,
        include_max=False,
    )


def translate_tilde_equal(version: Version) -> VersionRange:
    return VersionRange(
        min=version,
        max=next_tilde_equal_breaking(version),
        include_min=True,
        include_max=False,
    )


def translate_tilde(version: Version) -> VersionRange:
    return VersionRange(
        min=version,
        max=next_tilde_breaking(version),
        include_min=True,
        include_max=False,
    )


def translate_equal(version: Version) -> VersionPoint:
    return VersionPoint(version)


def translate_not_equal(version: Version) -> VersionUnion:
    result = translate_equal(version).complement()

    if is_version_union(result):
        return result

    raise InternalError  # TODO: message?


def translate_less(version: Version) -> VersionRange:
    return VersionRange(max=version, include_max=False)


def translate_less_or_equal(version: Version) -> VersionRange:
    return VersionRange(max=version, include_max=True)


def translate_greater(version: Version) -> VersionRange:
    return VersionRange(min=version, include_min=False)


def translate_greater_or_equal(version: Version) -> VersionRange:
    return VersionRange(min=version, include_min=True)


def translate_wildcard_equal(version: Version) -> VersionRange:
    wildcard = next_wildcard_breaking(version)

    if wildcard is None:
        return VersionRange()

    return VersionRange(min=version, max=wildcard, include_min=True, include_max=False)


def translate_wildcard_not_equal(version: Version) -> Union[VersionEmpty, VersionUnion]:
    result = translate_wildcard_equal(version).complement()

    if is_version_empty(result) or is_version_union(result):
        return result

    raise InternalError  # TODO: message?


class OperatorType(Enum):
    # official constraints
    TILDE_EQUAL = TILDE_EQUAL
    DOUBLE_EQUAL = DOUBLE_EQUAL
    NOT_EQUAL = NOT_EQUAL
    LESS = LESS
    LESS_OR_EQUAL = LESS_OR_EQUAL
    GREATER = GREATER
    GREATER_OR_EQUAL = GREATER_OR_EQUAL
    # additional constraints
    CARET = CARET
    EQUAL = EQUAL
    TILDE = TILDE
    # wildcard constraints
    WILDCARD_DOUBLE_EQUAL = WILDCARD_DOUBLE_EQUAL
    WILDCARD_EQUAL = WILDCARD_EQUAL
    WILDCARD_NOT_EQUAL = WILDCARD_NOT_EQUAL

    def is_wildcard(self) -> bool:
        return self in WILDCARD

    def is_unary(self) -> bool:
        return self in UNARY

    @property
    def string(self) -> str:
        return wildcard_type(self.value)


UNARY = {OperatorType.CARET, OperatorType.TILDE}

WILDCARD = {
    OperatorType.WILDCARD_DOUBLE_EQUAL,
    OperatorType.WILDCARD_EQUAL,
    OperatorType.WILDCARD_NOT_EQUAL,
}

OPERATOR: Mapping[OperatorType, Tuple[Matches, Translate]] = {
    OperatorType.TILDE_EQUAL: (matches_tilde_equal, translate_tilde_equal),
    OperatorType.DOUBLE_EQUAL: (matches_equal, translate_equal),
    OperatorType.NOT_EQUAL: (matches_not_equal, translate_not_equal),
    OperatorType.LESS: (matches_less, translate_less),
    OperatorType.LESS_OR_EQUAL: (matches_less_or_equal, translate_less_or_equal),
    OperatorType.GREATER: (matches_greater, translate_greater),
    OperatorType.GREATER_OR_EQUAL: (matches_greater_or_equal, translate_greater_or_equal),
    OperatorType.CARET: (matches_caret, translate_caret),
    OperatorType.EQUAL: (matches_equal, translate_equal),
    OperatorType.TILDE: (matches_tilde, translate_tilde),
    OperatorType.WILDCARD_DOUBLE_EQUAL: (matches_wildcard_equal, translate_wildcard_equal),
    OperatorType.WILDCARD_EQUAL: (matches_wildcard_equal, translate_wildcard_equal),
    OperatorType.WILDCARD_NOT_EQUAL: (matches_wildcard_not_equal, translate_wildcard_not_equal),
}


@frozen(repr=False)
class Operator(Representation, ToString):
    type: OperatorType
    version: Version

    def is_unary(self) -> bool:
        return self.type.is_unary()

    def is_wildcard(self) -> bool:
        return self.type.is_wildcard()

    @property
    def matches_and_translate(self) -> Tuple[Matches, Translate]:
        return OPERATOR[self.type]

    @property
    def matches(self) -> Matches:
        matches, _translate = self.matches_and_translate

        return matches

    @property
    def translate(self) -> Translate:
        _matches, translate = self.matches_and_translate

        return translate

    @property
    def partial_matches(self) -> PartialMatches:
        return partial_matches(self.matches, self.version)

    def to_string(self) -> str:
        string = self.version.to_string()

        if self.is_wildcard():
            string = wildcard_string(string)

        if self.is_unary():
            return concat_empty_args(self.type.string, string)

        return concat_space_args(self.type.string, string)

    def to_short_string(self) -> str:
        string = self.version.to_short_string()

        if self.is_wildcard():
            string = wildcard_string(string)

        return concat_empty_args(self.type.string, string)


# simple import cycle solution
from versions.version_sets import (
    VersionEmpty,
    VersionPoint,
    VersionRange,
    VersionUnion,
    is_version_empty,
    is_version_union,
)
