from __future__ import annotations

from enum import Enum
from string import digits
from typing import TYPE_CHECKING, Any, Mapping, Optional, Tuple, TypeVar, Union

from attrs import frozen

from versions.constants import (
    CARET,
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
from versions.string import ToString, concat_empty_args, concat_space_args
from versions.typing import Binary, Unary, is_same_type

if TYPE_CHECKING:
    from versions.version import Version
    from versions.version_sets import VersionSet

    Matches = Binary[Version, Version, bool]
    """The `(version, against) -> bool` function."""
    PartialMatches = Unary[Version, bool]
    """The `(version) -> bool` function."""
    Translate = Unary[Version, VersionSet]
    """The `(version) -> version_set` function."""

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
    """Returns the next breaking version according to the *caret* (`^`) strategy.

    This function is slightly convoluted due to handling `0.x.y` versions.

    See [`next_breaking`][versions.version.Version.next_breaking] for more information.

    Example:
        ```python
        >>> from versions import next_caret_breaking, parse_version
        >>> version = parse_version("1.0.0")
        >>> version
        <Version (1.0.0)>
        >>> next_caret_breaking(version)
        <Version (2.0.0)>
        ```

    Arguments:
        version: The version to find next breaking version of.

    Returns:
        The next breaking version according to the `version`.
    """
    return version.next_breaking()


CAN_NOT_USE_TILDE_EQUAL = "`~=` can not be used with with a single version segment"


def next_tilde_equal_breaking(version: V) -> V:
    """Returns the next breaking version according to the *tilde-equal* (`~=`) strategy.

    This function simply bumps the second to last part of the release.

    Example:
        ```python
        >>> from versions import next_tilde_equal_breaking, parse_version
        >>> version = parse_version("1.2.0")
        >>> version
        <Version (1.2.0)>
        >>> next_tilde_equal_breaking(version)
        <Version (1.3.0)>
        ```

        ```python
        >>> invalid = parse_version("1")
        >>> next_tilde_equal_breaking(invalid)
        Traceback (most recent call last):
          ...
        ValueError: `~=` can not be used with with a single version segment
        ```

    Arguments:
        version: The version to find the next breaking version of.

    Returns:
        The next breaking [`Version`][versions.version.Version] according to the `version`.
    """
    index = version.last_index

    if index:
        return version.to_stable().next_at(index - 1)

    raise ValueError(CAN_NOT_USE_TILDE_EQUAL)


def next_tilde_breaking(version: V) -> V:
    """Returns the next breaking version according to the *tilde* (`~`) strategy.

    This function simply bumps the minor part of the release
    if it is present, otherwise the major part is bumped.

    Example:
        ```python
        >>> from versions import next_tilde_equal_breaking, parse_version
        >>> version = parse_version("2.1.0")
        >>> version
        <Version (2.1.0)>
        >>> next_tilde_breaking(version)
        <Version (2.2.0)>
        ```

    Arguments:
        version: The version to find the next breaking version of.

    Returns:
        The next breaking [`Version`][versions.version.Version] according to the `version`.
    """
    if version.has_minor():
        return version.next_minor()

    return version.next_major()


def next_wildcard_breaking(version: V) -> Optional[V]:
    """Returns the next breaking version according to the *wildcard* (`*`) strategy.

    There are three cases to handle:

    - If the wildcard is used within the *pre-release* tag of the version,
      next breaking version has the same release with *pre-release* tag removed.
      For example, `x.y.z-rc.*` is bumped to `x.y.z`.

    - If the wildcard is used within the *post-release* tag of the version,
      next breaking version has the last part of the release bumped.
      For instance, `x.y.z-post.*` is bumped to `x.y.z'`, where `z' = z + 1`.

    - Otherwise, the second to last part of the release is bumped.
      For example, `x.y.*` is bumped to `x.y'.0`, where `y' = y + 1`.

    Note:
        This function returns [`None`][None] if the given version is `*`.

    Example:
        ```python
        >>> from versions import next_wildcard_breaking, parse_version
        >>> version = parse_version("4.2.0")
        >>> version
        <Version (4.2.0)>
        >>> next_wildcard_breaking(version)
        <Version (4.3.0)>
        >>> other = parse_version("1.2.3-rc.0")
        >>> other
        <Version (1.2.3-rc.0)>
        >>> next_wildcard_breaking(other)
        <Version (1.2.3)>
        >>> another = parse_version("0.6.8-post.0")
        >>> another
        <Version (0.6.8-post.0)>
        >>> next_wildcard_breaking(another)
        <Version (0.6.9)>  # nice
        ```

    Arguments:
        version: The version to find the next breaking version of.

    Returns:
        The next breaking [`Version`][versions.version.Version] according
            to the `version`, or [`None`][None].
    """
    index = version.last_index

    if version.is_stable() and not version.is_post_release():
        # the wildcard was used within the release segment

        if not index:
            return None

        index -= 1

    return version.next_at(index)  # this will take care of unstable releases


def wildcard_string(string: str, wildcard: str = STAR) -> str:
    return concat_empty_args(string.rstrip(digits), wildcard)


def wildcard_type(string: str, wildcard: str = STAR) -> str:
    return string.strip(wildcard)


def partial_matches(matches: Matches, against: Version) -> PartialMatches:
    def partial(version: Version) -> bool:
        return matches(version, against)

    return partial


def matches_caret(version: Version, against: Version) -> bool:
    """Checks if the `version` matches the *caret* (`^`) specification.

    This is equivalent to:

    ```python
    against <= version < next_caret_breaking(against)
    ```

    Arguments:
        version: The version to check.
        against: The version to check the `version` against.

    Returns:
        Whether the `version` matches `against`.
    """
    return against <= version < next_caret_breaking(against)


def matches_tilde_equal(version: Version, against: Version) -> bool:
    """Checks if the `version` matches the *tilde-equal* (`~=`) specification.

    This is equivalent to:

    ```python
    against <= version < next_tilde_equal_breaking(against)
    ```

    Arguments:
        version: The version to check.
        against: The version to check the `version` against.

    Returns:
        Whether the `version` matches `against`.
    """
    return against <= version < next_tilde_equal_breaking(against)


def matches_tilde(version: Version, against: Version) -> bool:
    """Checks if the `version` matches the *tilde* (`~`) specification.

    This is equivalent to:

    ```python
    against <= version < next_tilde_breaking(against)
    ```

    Arguments:
        version: The version to check.
        against: The version to check the `version` against.

    Returns:
        Whether the `version` matches `against`.
    """
    return against <= version < next_tilde_breaking(against)


def matches_equal(version: Version, against: Version) -> bool:
    """Checks if the `version` matches the *equal* (`=`) specification.

    This is equivalent to:

    ```python
    version == against
    ```

    Arguments:
        version: The version to check.
        against: The version to check the `version` against.

    Returns:
        Whether the `version` matches `against`.
    """
    return version == against


def matches_not_equal(version: Version, against: Version) -> bool:
    """Checks if the `version` matches the *not-equal* (`!=`) specification.

    This is equivalent to:

    ```python
    version != against
    ```

    Arguments:
        version: The version to check.
        against: The version to check the `version` against.

    Returns:
        Whether the `version` matches `against`.
    """
    return version != against


def matches_less(version: Version, against: Version) -> bool:
    """Checks if the `version` matches the *less* (`<`) specification.

    This is equivalent to:

    ```python
    version < against
    ```

    Arguments:
        version: The version to check.
        against: The version to check the `version` against.

    Returns:
        Whether the `version` matches `against`.
    """

    return version < against


def matches_less_or_equal(version: Version, against: Version) -> bool:
    """Checks if the `version` matches the *less-or-equal* (`<=`) specification.

    This is equivalent to:

    ```python
    version <= against
    ```

    Arguments:
        version: The version to check.
        against: The version to check the `version` against.

    Returns:
        Whether the `version` matches `against`.
    """
    return version <= against


def matches_greater(version: Version, against: Version) -> bool:
    """Checks if the `version` matches the *greater* (`>`) specification.

    This is equivalent to:

    ```python
    version > against
    ```

    Arguments:
        version: The version to check.
        against: The version to check the `version` against.

    Returns:
        Whether the `version` matches `against`.
    """
    return version > against


def matches_greater_or_equal(version: Version, against: Version) -> bool:
    """Checks if the `version` matches the *greater-or-equal* (`>=`) specification.

    This is equivalent to:

    ```python
    version >= against
    ```

    Arguments:
        version: The version to check.
        against: The version to check the `version` against.

    Returns:
        Whether the `version` matches `against`.
    """
    return version >= against


def matches_wildcard_equal(version: Version, against: Version) -> bool:
    """Checks if the `version` matches the *wildcard-equal* (`=*`) specification.

    This is equivalent to:

    ```python
    wildcard = next_wildcard_breaking(against)

    wildcard is None or against <= version < wildcard
    ```

    Arguments:
        version: The version to check.
        against: The version to check the `version` against.

    Returns:
        Whether the `version` matches `against`.
    """
    wildcard = next_wildcard_breaking(against)

    if wildcard is None:
        return True

    return against <= version < wildcard


def matches_wildcard_not_equal(version: Version, against: Version) -> bool:
    """Checks if the `version` matches the *wildcard-not-equal* (`!=*`) specification.

    This is equivalent to:

    ```python
    wildcard = next_wildcard_breaking(against)

    wildcard is not None and (version < against or version >= wildcard)
    ```

    Arguments:
        version: The version to check.
        against: The version to check the `version` against.

    Returns:
        Whether the `version` matches `against`.
    """
    return not matches_wildcard_equal(version, against)


def translate_caret(version: Version) -> VersionRange:
    """Translates the `version` into a version set according to the *caret* (`^`) strategy.

    This function returns the `[version, next_caret_breaking(version))` range.

    Arguments:
        version: The version to translate.

    Returns:
        The version set representing the *caret* specification.
    """
    return VersionRange(
        min=version,
        max=next_caret_breaking(version),
        include_min=True,
        include_max=False,
    )


def translate_tilde_equal(version: Version) -> VersionRange:
    """Translates the `version` into a version set according to the *tilde-equal* (`~=`) strategy.

    This function returns the `[version, next_tilde_equal_breaking(version))` range.

    Arguments:
        version: The version to translate.

    Returns:
        The version set representing the *tilde-equal* specification.
    """
    return VersionRange(
        min=version,
        max=next_tilde_equal_breaking(version),
        include_min=True,
        include_max=False,
    )


def translate_tilde(version: Version) -> VersionRange:
    """Translates the `version` into a version set according to the *tilde* (`~`) strategy.

    This function returns the `[version, next_tilde_breaking(version))` range.

    Arguments:
        version: The version to translate.

    Returns:
        The version set representing the *tilde-equal* specification.
    """
    return VersionRange(
        min=version,
        max=next_tilde_breaking(version),
        include_min=True,
        include_max=False,
    )


def translate_equal(version: Version) -> VersionPoint:
    """Translates the `version` into a version set according to the *equal* (`=`) strategy.

    This function returns the `[version, version]` range (aka `version` point).

    Arguments:
        version: The version to translate.

    Returns:
        The version set representing the *equal* specification.
    """
    return VersionPoint(version)


UNEXPECTED_EQUAL_COMPLEMENT = "unexpected equal complement"


def translate_not_equal(version: Version) -> VersionUnion:
    """Translates the `version` into a version set according to the *not-equal* (`!=`) strategy.

    This function returns the `(ε, version) | (version, ω)` union.

    Arguments:
        version: The version to translate.

    Returns:
        The version set representing the *not-equal* specification.
    """
    result = translate_equal(version).complement()

    if is_version_union(result):
        return result

    raise InternalError(UNEXPECTED_EQUAL_COMPLEMENT)


def translate_less(version: Version) -> VersionRange:
    """Translates the `version` into a version set according to the *less* (`<`) strategy.

    This function returns the `(ε, version)` range.

    Arguments:
        version: The version to translate.

    Returns:
        The version set representing the *less* specification.
    """
    return VersionRange(max=version, include_max=False)


def translate_less_or_equal(version: Version) -> VersionRange:
    """Translates the `version` into a version set according to the *less-or-equal* (`<=`) strategy.

    This function returns the `(ε, version]` range.

    Arguments:
        version: The version to translate.

    Returns:
        The version set representing the *less-or-equal* specification.
    """
    return VersionRange(max=version, include_max=True)


def translate_greater(version: Version) -> VersionRange:
    """Translates the `version` into a version set according to the *greater* (`>`) strategy.

    This function returns the `(version, ω)` range.

    Arguments:
        version: The version to translate.

    Returns:
        The version set representing the *greater* specification.
    """
    return VersionRange(min=version, include_min=False)


def translate_greater_or_equal(version: Version) -> VersionRange:
    """Translates the `version` into a version set according to
    the *greater-or-equal* (`>=`) strategy.

    This function returns the `[version, ω)` range.

    Arguments:
        version: The version to translate.

    Returns:
        The version set representing the *greater-or-equal* specification.
    """
    return VersionRange(min=version, include_min=True)


def translate_wildcard_equal(version: Version) -> VersionRange:
    """Translates the `version` into a version set according to
    the *wildcard-equal* (`==*`) strategy.

    This function returns the `[version, next_wildcard_version(version))` range in most cases,
    except for when the version is `*`; then the `(ε, ω)` range is returned.

    Arguments:
        version: The version to translate.

    Returns:
        The version set representing the *wildcard-equal* specification.
    """
    wildcard = next_wildcard_breaking(version)

    if wildcard is None:
        return VersionRange()

    return VersionRange(min=version, max=wildcard, include_min=True, include_max=False)


UNEXPECTED_WILDCARD_EQUAL_COMPLEMENT = "unexpected wildcard-equal complement"


def translate_wildcard_not_equal(version: Version) -> Union[VersionEmpty, VersionUnion]:
    """Translates the `version` into a version set according to
    the *wildcard-not-equal* (`!=*`) strategy.

    This function returns the `(ε, version) | (next_wildcard_breaking(version), ω)` union
    in most cases, except for when the version is `*`; then the `{}` empty set is returned.

    Arguments:
        version: The version to translate.

    Returns:
        The version set representing the *wildcard-not-equal* specification.
    """
    result = translate_wildcard_equal(version).complement()

    if is_version_empty(result) or is_version_union(result):
        return result

    raise InternalError(UNEXPECTED_WILDCARD_EQUAL_COMPLEMENT)


class OperatorType(Enum):
    """Represents operator types."""

    # official constraints
    TILDE_EQUAL = TILDE_EQUAL
    """The binary `~=` operator."""
    DOUBLE_EQUAL = DOUBLE_EQUAL
    """The binary `==` operator."""
    NOT_EQUAL = NOT_EQUAL
    """The binary `!=` operator."""
    LESS = LESS
    """The binary `<` operator."""
    LESS_OR_EQUAL = LESS_OR_EQUAL
    """The binary `<=` operator."""
    GREATER = GREATER
    """The binary `>` operator."""
    GREATER_OR_EQUAL = GREATER_OR_EQUAL
    """The binary `>=` operator."""
    # additional constraints
    CARET = CARET
    """The unary `^` operator."""
    EQUAL = EQUAL
    """The binary `=` operator."""
    TILDE = TILDE
    """The unary `~` operator."""
    # wildcard constraints
    WILDCARD_DOUBLE_EQUAL = WILDCARD_DOUBLE_EQUAL
    """The wildcard binary `==*` operator."""
    WILDCARD_EQUAL = WILDCARD_EQUAL
    """The wildcard binary `=*` operator."""
    WILDCARD_NOT_EQUAL = WILDCARD_NOT_EQUAL
    """The wildcard binary `!=*` operator."""

    def is_wildcard(self) -> bool:
        """Checks if an operator is *wildcard*.

        Returns:
            Whether the operator is *wildcard*.
        """
        return self in WILDCARD

    def is_equals(self) -> bool:
        return self in EQUALS

    def is_wildcard_equals(self) -> bool:
        return self in WILDCARD_EQUALS

    def is_unary(self) -> bool:
        """Checks if an operator is *unary*.

        Returns:
            Whether the operator is *unary*.
        """
        return self in UNARY

    def __eq__(self, other: Any) -> bool:
        if is_same_type(other, self):
            return (
                (self.is_equals() and other.is_equals())
                or (self.is_wildcard_equals() and other.is_wildcard_equals())
                or super().__eq__(other)
            )

        return NotImplemented

    def __hash__(self) -> int:
        return super().__hash__()  # type: ignore

    @property
    def string(self) -> str:
        return wildcard_type(self.value)


EQUALS = {OperatorType.DOUBLE_EQUAL, OperatorType.EQUAL}

WILDCARD_EQUALS = {OperatorType.WILDCARD_DOUBLE_EQUAL, OperatorType.WILDCARD_EQUAL}

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
    """Represents operators."""

    type: OperatorType
    """The operator type."""

    version: Version
    """The operator version."""

    def __attrs_post_init__(self) -> None:
        if self.type is OperatorType.TILDE_EQUAL:
            next_tilde_equal_breaking(self.version)  # check whether `~=` can be used

    def is_unary(self) -> bool:
        """Checks if an operator is *unary*.

        Returns:
            Whether the operator is *unary*.
        """
        return self.type.is_unary()

    def is_wildcard(self) -> bool:
        """Checks if an operator is *wildcard*.

        Returns:
            Whether the operator is *wildcard*.
        """
        return self.type.is_wildcard()

    @property
    def matches_and_translate(self) -> Tuple[Matches, Translate]:
        return OPERATOR[self.type]

    @property
    def matches(self) -> Matches:
        """The `matches` function representing the operator."""
        matches, _translate = self.matches_and_translate

        return matches

    @property
    def translate(self) -> Translate:
        """The `translate` function representing the operator."""
        _matches, translate = self.matches_and_translate

        return translate

    @property
    def partial_matches(self) -> PartialMatches:
        """The partial `matches` function with `self.version` as the `against` version."""
        return partial_matches(self.matches, self.version)

    def to_string(self) -> str:
        """Converts an [`Operator`][versions.operators.Operator] to its string representation.

        Returns:
            The operator string.
        """
        string = self.version.to_string()

        if self.is_wildcard():
            string = wildcard_string(string)

        if self.is_unary():
            return concat_empty_args(self.type.string, string)

        return concat_space_args(self.type.string, string)

    def to_short_string(self) -> str:
        """Converts an [`Operator`][versions.operators.Operator] to its *short* string representation.

        Returns:
            The *short* operator string.
        """
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
