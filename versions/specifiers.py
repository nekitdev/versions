from __future__ import annotations

from builtins import isinstance as is_instance
from typing import TYPE_CHECKING, Any, ClassVar, Iterable

from attrs import Attribute, field, frozen
from typing_extensions import Literal, TypeGuard

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
from versions.typing import DynamicTuple
from versions.utils import contains_only_item, first

if TYPE_CHECKING:
    from versions.version import Version

__all__ = (
    "Specifier",
    "SpecifierFalse",
    "SpecifierTrue",
    "SpecifierSingle",
    "SpecifierAny",
    "SpecifierAll",
    "is_specifier",
    "is_specifier_false",
    "is_specifier_true",
    "is_specifier_single",
    "is_specifier_any",
    "is_specifier_all",
)


class Specifier(Representation, ToString, Specification):
    """Represents all possible specifiers."""


Specifiers = DynamicTuple[Specifier]


@frozen(repr=False)
class SpecifierFalse(Specifier):
    """Represents specifiers that do not accept any version."""

    def accepts(self, version: Version) -> Literal[False]:
        return False

    def to_string(self) -> str:
        return EMPTY_VERSION


@frozen(repr=False)
class SpecifierTrue(Specifier):
    """Represents specifiers that accept all versions."""

    def accepts(self, version: Version) -> Literal[True]:
        return True

    def to_string(self) -> str:
        return UNIVERSE_VERSION


@frozen(repr=False)
class SpecifierSingle(Operator, Specifier):
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
            return SpecifierTrue()

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
            return SpecifierTrue()

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


def is_specifier_false(item: Any) -> TypeGuard[SpecifierFalse]:
    """Checks if an `item` is an instance of
    [`SpecifierFalse`][versions.specifiers.SpecifierFalse].

    Arguments:
        item: The item to check.

    Returns:
        Whether the `item` provided is an instance of
            [`SpecifierFalse`][versions.specifiers.SpecifierFalse].
    """
    return is_instance(item, SpecifierFalse)


def is_specifier_true(item: Any) -> TypeGuard[SpecifierTrue]:
    """Checks if an `item` is an instance of
    [`SpecifierTrue`][versions.specifiers.SpecifierTrue].

    Arguments:
        item: The item to check.

    Returns:
        Whether the `item` provided is an instance of
            [`SpecifierTrue`][versions.specifiers.SpecifierTrue].
    """
    return is_instance(item, SpecifierTrue)


def is_specifier_single(item: Any) -> TypeGuard[SpecifierSingle]:
    """Checks if an `item` is an instance of
    [`SpecifierSingle`][versions.specifiers.SpecifierSingle].

    Arguments:
        item: The item to check.

    Returns:
        Whether the `item` provided is an instance of
            [`SpecifierSingle`][versions.specifiers.SpecifierSingle].
    """
    return is_instance(item, SpecifierSingle)


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
