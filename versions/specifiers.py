from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Iterable, Literal

from attrs import Attribute, field, frozen
from typing_aliases import DynamicTuple, is_instance
from typing_extensions import TypeGuard

from versions.constants import EMPTY_VERSION, UNIVERSE_VERSION
from versions.operators import Operator
from versions.representation import Representation
from versions.specification import Specification
from versions.string import (
    ToString,
    concat_comma,
    concat_comma_space,
    concat_pipes,
    concat_pipes_spaced,
    create_wrap_around,
)
from versions.utils import contains_only_item, first

if TYPE_CHECKING:
    from versions.version import Version

__all__ = (
    "NEVER",
    "ALWAYS",
    "Specifier",
    "SpecifierNever",
    "SpecifierAlways",
    "SpecifierOne",
    "SpecifierAny",
    "SpecifierAll",
    "is_specifier",
    "is_specifier_never",
    "is_specifier_always",
    "is_specifier_one",
    "is_specifier_any",
    "is_specifier_all",
)


class Specifier(Representation, ToString, Specification):
    """Represents all possible specifiers."""


Specifiers = DynamicTuple[Specifier]


@frozen(repr=False)
class SpecifierNever(Specifier):
    """Represents specifiers that do not accept any versions."""

    def accepts(self, version: Version) -> Literal[False]:
        return False

    def to_string(self) -> str:
        return EMPTY_VERSION


NEVER = SpecifierNever()


@frozen(repr=False)
class SpecifierAlways(Specifier):
    """Represents specifiers that accept all versions."""

    def accepts(self, version: Version) -> Literal[True]:
        return True

    def to_string(self) -> str:
        return UNIVERSE_VERSION


ALWAYS = SpecifierAlways()


@frozen(repr=False)
class SpecifierOne(Operator, Specifier):
    """Represents specifiers that accept versions according to the
    [`Operator`][versions.operators.Operator] type.
    """

    def accepts(self, version: Version) -> bool:
        return self.partial_matches(version)


NO_SPECIFIERS = "expected at least 2 specifiers, 0 found"
ONE_SPECIFIER = "expected at least 2 specifiers, 1 found; consider using it directly"


def check_specifiers(specifiers: Specifiers) -> None:
    if not specifiers:
        raise TypeError(NO_SPECIFIERS)

    if contains_only_item(specifiers):
        raise TypeError(ONE_SPECIFIER)


@frozen(repr=False)
class SpecifierAny(Specifier):
    """Represents collections of two or more specifiers that accept versions
    if *any* of the contained specifiers accept it.
    """

    WRAP: ClassVar[bool] = False

    specifiers: Specifiers = field()

    @specifiers.validator
    def check_specifiers(self, attribute: Attribute[Specifiers], specifiers: Specifiers) -> None:
        check_specifiers(specifiers)

    @classmethod
    def of_specifiers(cls, specifiers: Specifiers) -> Specifier:
        if not specifiers:
            return SpecifierNever()

        if contains_only_item(specifiers):
            return first(specifiers)

        return cls(specifiers)

    @classmethod
    def of(cls, *specifiers: Specifier) -> Specifier:
        return cls.of_specifiers(specifiers)

    @classmethod
    def of_iterable(cls, iterable: Iterable[Specifier]) -> Specifier:
        return cls.of_specifiers(tuple(iterable))

    def accepts(self, version: Version) -> bool:
        return any(specifier.accepts(version) for specifier in self.specifiers)

    def to_string(self) -> str:
        return create_wrap_around(
            concat_pipes_spaced(specifier.to_string() for specifier in self.specifiers)
        )

    def to_short_string(self) -> str:
        return create_wrap_around(
            concat_pipes(specifier.to_short_string() for specifier in self.specifiers)
        )


@frozen(repr=False)
class SpecifierAll(Specifier):
    """Represents collections of two or more specifiers that accept versions
    if and only if *all* of the contained specifiers accept it.
    """

    WRAP: ClassVar[bool] = False

    specifiers: Specifiers = field()

    @specifiers.validator
    def check_specifiers(self, attribute: Attribute[Specifiers], specifiers: Specifiers) -> None:
        check_specifiers(specifiers)

    @classmethod
    def of_specifiers(cls, specifiers: Specifiers) -> Specifier:
        if not specifiers:
            return SpecifierAlways()

        if contains_only_item(specifiers):
            return first(specifiers)

        return cls(specifiers)

    @classmethod
    def of(cls, *specifiers: Specifier) -> Specifier:
        return cls.of_specifiers(specifiers)

    @classmethod
    def of_iterable(cls, iterable: Iterable[Specifier]) -> Specifier:
        return cls.of_specifiers(tuple(iterable))

    def accepts(self, version: Version) -> bool:
        return all(specifier.accepts(version) for specifier in self.specifiers)

    def to_string(self) -> str:
        return create_wrap_around(
            concat_comma_space(specifier.to_string() for specifier in self.specifiers)
        )

    def to_short_string(self) -> str:
        return create_wrap_around(
            concat_comma(specifier.to_short_string() for specifier in self.specifiers)
        )


def is_specifier(item: Any) -> TypeGuard[Specifier]:
    """Checks if an `item` is an instance of [`Specifier`][versions.specifiers.Specifier].

    Arguments:
        item: The item to check.

    Returns:
        Whether the `item` provided is an instance of [`Specifier`][versions.specifiers.Specifier].
    """
    return is_instance(item, Specifier)


def is_specifier_never(item: Any) -> TypeGuard[SpecifierNever]:
    """Checks if an `item` is an instance of
    [`SpecifierNever`][versions.specifiers.SpecifierNever].

    Arguments:
        item: The item to check.

    Returns:
        Whether the `item` provided is an instance of
            [`SpecifierNever`][versions.specifiers.SpecifierNever].
    """
    return is_instance(item, SpecifierNever)


def is_specifier_always(item: Any) -> TypeGuard[SpecifierAlways]:
    """Checks if an `item` is an instance of
    [`SpecifierAlways`][versions.specifiers.SpecifierAlways].

    Arguments:
        item: The item to check.

    Returns:
        Whether the `item` provided is an instance of
            [`SpecifierAlways`][versions.specifiers.SpecifierAlways].
    """
    return is_instance(item, SpecifierAlways)


def is_specifier_one(item: Any) -> TypeGuard[SpecifierOne]:
    """Checks if an `item` is an instance of
    [`SpecifierOne`][versions.specifiers.SpecifierOne].

    Arguments:
        item: The item to check.

    Returns:
        Whether the `item` provided is an instance of
            [`SpecifierOne`][versions.specifiers.SpecifierOne].
    """
    return is_instance(item, SpecifierOne)


def is_specifier_any(item: Any) -> TypeGuard[SpecifierAny]:
    """Checks if an `item` is an instance of
    [`SpecifierAny`][versions.specifiers.SpecifierAny].

    Arguments:
        item: The item to check.

    Returns:
        Whether the `item` provided is an instance of
            [`SpecifierAny`][versions.specifiers.SpecifierAny].
    """
    return is_instance(item, SpecifierAny)


def is_specifier_all(item: Any) -> TypeGuard[SpecifierAll]:
    """Checks if an `item` is an instance of
    [`SpecifierAll`][versions.specifiers.SpecifierAll].

    Arguments:
        item: The item to check.

    Returns:
        Whether the `item` provided is an instance of
            [`SpecifierAll`][versions.specifiers.SpecifierAll].
    """
    return is_instance(item, SpecifierAll)
