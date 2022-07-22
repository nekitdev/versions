from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, Optional, Pattern, Type, TypeVar

from attrs import frozen
from typing_extensions import Protocol, runtime_checkable

from versions.constants import STAR, ZERO
from versions.converters import specifier_to_version_set
from versions.errors import InternalError, ParseSpecificationError, ParseTagError, ParseVersionError
from versions.operators import OperatorType
from versions.patterns import (
    CARET_SPECIFICATION,
    DEV,
    EPOCH,
    EQUAL_SPECIFICATION,
    LOCAL,
    OPERATOR_NAME,
    ORDER_SPECIFICATION,
    PHASE,
    POST,
    POST_IMPLICIT,
    PRE,
    RELEASE,
    TAG,
    TILDE_SPECIFICATION,
    VALUE,
    VERSION,
    VERSION_NAME,
    WILDCARD_SPECIFICATION,
)
from versions.specifiers import Specifier, SpecifierAll, SpecifierAny, SpecifierSingle
from versions.string import clear_whitespace, split_comma, split_pipes
from versions.typing import get_name
from versions.version_sets import VersionSet

if TYPE_CHECKING:
    from versions.segments import Tag
    from versions.version import Version

__all__ = ("Parser", "SpecifierParser", "TagParser", "VersionParser", "VersionSetParser")

V = TypeVar("V", bound="Version")
T = TypeVar("T", bound="Tag")

R = TypeVar("R", covariant=True)

CAN_NOT_PARSE = "can not parse `{}` to `{}`"


@runtime_checkable
class Parser(Protocol[R]):
    @abstractmethod
    def parse(self, string: str) -> R:
        raise NotImplementedError


@frozen()
class TagParser(Parser[T]):
    tag_type: Type[T]

    def parse(self, string: str) -> T:
        tag_type = self.tag_type

        match = TAG.fullmatch(string)

        if match is None:
            raise ParseTagError(CAN_NOT_PARSE.format(string, get_name(tag_type)))

        phase = match.group(PHASE)

        if phase is None:
            phase = tag_type.DEFAULT_PHASE

        value_string = match.group(VALUE)

        if value_string is None:
            return tag_type(phase)

        value = int(value_string)

        return tag_type(phase, value)


@frozen()
class VersionParser(Parser[V]):
    version_type: Type[V]

    @staticmethod
    def parse_epoch_optional(string: Optional[str]) -> Epoch:
        return Epoch() if string is None else Epoch.from_string(string)

    @staticmethod
    def parse_release_optional(string: Optional[str]) -> Release:
        return Release() if string is None else Release.from_string(string)

    @staticmethod
    def parse_pre_optional(string: Optional[str]) -> Optional[PreTag]:
        return None if string is None else PreTag.from_string(string)

    @staticmethod
    def parse_post_optional(string: Optional[str]) -> Optional[PostTag]:
        return None if string is None else PostTag.from_string(string)

    @staticmethod
    def parse_post_implicit_optional(string: Optional[str]) -> Optional[PostTag]:
        return None if string is None else PostTag.default_phase_with_value(int(string))

    @staticmethod
    def parse_dev_optional(string: Optional[str]) -> Optional[DevTag]:
        return None if string is None else DevTag.from_string(string)

    @staticmethod
    def parse_local_optional(string: Optional[str]) -> Optional[Local]:
        return None if string is None else Local.from_string(string)

    def parse(self, string: str) -> V:
        match = VERSION.fullmatch(string)

        if match is None:
            raise ParseVersionError(CAN_NOT_PARSE.format(string, get_name(self.version_type)))

        return self.version_type(
            epoch=self.parse_epoch_optional(match.group(EPOCH)),
            release=self.parse_release_optional(match.group(RELEASE)),
            pre=self.parse_pre_optional(match.group(PRE)),
            post=(
                self.parse_post_implicit_optional(match.group(POST_IMPLICIT))
                or self.parse_post_optional(match.group(POST))
            ),
            dev=self.parse_dev_optional(match.group(DEV)),
            local=self.parse_local_optional(match.group(LOCAL)),
        )


@frozen()
class SpecifierParser(Generic[V], Parser[Specifier]):
    version_parser: VersionParser[V]

    def parse(self, string: str) -> Specifier:
        return self.parse_any(clear_whitespace(string))

    def parse_any(self, string: str) -> Specifier:
        return SpecifierAny.of_iterable(map(self.parse_all, split_pipes(string)))

    def parse_all(self, string: str) -> Specifier:
        return SpecifierAll.of_iterable(map(self.parse_single, split_comma(string)))

    def parse_single(self, string: str) -> Specifier:
        for try_parse in (
            self.try_parse_wildcard,
            self.try_parse_order,
            self.try_parse_equal,
            self.try_parse_caret,
            self.try_parse_tilde,
        ):
            specifier = try_parse(string)

            if specifier:
                return specifier

        raise ParseSpecificationError  # TODO: message?

    def try_parse_caret(self, string: str) -> Optional[Specifier]:
        return self.try_parse_with(CARET_SPECIFICATION, string)

    def try_parse_tilde(self, string: str) -> Optional[Specifier]:
        return self.try_parse_with(TILDE_SPECIFICATION, string)

    def try_parse_order(self, string: str) -> Optional[Specifier]:
        return self.try_parse_with(ORDER_SPECIFICATION, string)

    def try_parse_with(self, pattern: Pattern[str], string: str) -> Optional[Specifier]:
        match = pattern.fullmatch(string)

        if match is None:
            return None

        operator_string = match.group(OPERATOR_NAME)

        if operator_string is None:
            raise InternalError  # TODO: message?

        operator_type = OperatorType(operator_string)

        version_string = match.group(VERSION_NAME)

        if version_string is None:
            raise InternalError  # TODO: message?

        version = self.version_parser.parse(version_string)

        return SpecifierSingle(operator_type, version)

    def try_parse_equal(self, string: str) -> Optional[Specifier]:
        match = EQUAL_SPECIFICATION.fullmatch(string)

        if match is None:
            return None

        operator_string = match.group(OPERATOR_NAME)

        if operator_string is None:
            operator_type = OperatorType.DOUBLE_EQUAL

        else:
            operator_type = OperatorType(operator_string)

        version_string = match.group(VERSION_NAME)

        if version_string is None:
            raise InternalError  # TODO: message?

        version = self.version_parser.parse(version_string)

        return SpecifierSingle(operator_type, version)

    def try_parse_wildcard(self, string: str) -> Optional[Specifier]:
        match = WILDCARD_SPECIFICATION.fullmatch(string)

        if match is None:
            return None

        operator_string = match.group(OPERATOR_NAME)

        if operator_string is None:
            operator_type = OperatorType.WILDCARD_DOUBLE_EQUAL

        else:
            operator_type = OperatorType(operator_string + STAR)

        version_string = match.group(VERSION_NAME)

        if version_string is None:
            raise InternalError  # TODO: message?

        version = self.version_parser.parse(version_string.replace(STAR, ZERO))

        return SpecifierSingle(operator_type, version)


@frozen()
class VersionSetParser(Generic[V], Parser[VersionSet]):
    specifier_parser: SpecifierParser[V]

    def parse(self, string: str) -> VersionSet:
        return specifier_to_version_set(self.specifier_parser.parse(string))


# another import cycle solution
from versions.segments import DevTag, Epoch, Local, PostTag, PreTag, Release
