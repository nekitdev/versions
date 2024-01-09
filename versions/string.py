from typing import Iterable, List, Protocol, runtime_checkable

from typing_aliases import Parse, required
from typing_extensions import Self

from versions.constants import (
    BRACKETS,
    COMMA,
    COMMA_SPACE,
    DASH,
    DOT,
    DOUBLE_PIPE,
    DOUBLE_PIPE_SPACED,
    EMPTY,
    PIPE,
    SEPARATORS,
    SPACE,
    UNDER,
)

__all__ = (
    # simple from_string() and to_string() protocols
    "FromString",
    "ToString",
    "String",
    # checks
    "check_int",
    # clearing whitespace
    "clear_whitespace",
    # various concatenation
    "concat_comma",
    "concat_comma_space",
    "concat_dash",
    "concat_dot",
    "concat_dot_args",
    "concat_empty",
    "concat_empty_args",
    "concat_space",
    "concat_space_args",
    "concat_under",
    "concat_pipe",
    "concat_pipe_args",
    "concat_pipes",
    "concat_pipes_spaced",
    # wrapping
    "create_wrap_around",
    # splitting multiple characters
    "create_split_multiple",
    # splitting separators
    "split_separators",
    "split_comma",
    "split_dot",
    "split_pipes",
    # split function
    "Split",
)


@runtime_checkable
class FromString(Protocol):
    @classmethod
    @required
    def from_string(cls, string: str) -> Self:
        raise NotImplementedError

    @classmethod
    def parse(cls, string: str) -> Self:
        return cls.from_string(string)


@runtime_checkable
class ToString(Protocol):
    @required
    def to_string(self) -> str:
        raise NotImplementedError

    def to_short_string(self) -> str:
        return self.to_string()

    def __str__(self) -> str:
        return self.to_string()


@runtime_checkable
class String(FromString, ToString, Protocol):
    pass


check_int = str.isdigit


def concat_empty_args(*args: str) -> str:
    return concat_empty(args)


def concat_dot_args(*args: str) -> str:
    return concat_dot(args)


def concat_pipe_args(*args: str) -> str:
    return concat_pipe(args)


def concat_space_args(*args: str) -> str:
    return concat_space(args)


concat_comma = COMMA.join
concat_comma_space = COMMA_SPACE.join
concat_dash = DASH.join
concat_dot = DOT.join
concat_empty = EMPTY.join
concat_space = SPACE.join
concat_under = UNDER.join

concat_pipe = PIPE.join

concat_pipes = DOUBLE_PIPE.join
concat_pipes_spaced = DOUBLE_PIPE_SPACED.join


def clear_whitespace(string: str) -> str:
    return concat_empty(string.strip().split())


EXPECTED_PAIR = "expected a pair of characters"


def create_wrap_around(string: str, wrap: Iterable[str] = BRACKETS) -> str:
    try:
        left, right = wrap

    except (ValueError, TypeError):  # pragma: no cover  # not tested
        raise ValueError(EXPECTED_PAIR) from None

    return left + string + right


create_translation = str.maketrans
dict_from_keys = dict.fromkeys

Split = Parse[List[str]]


def create_split_multiple(main: str, *rest: str) -> Split:
    # the following implementation is faster than `re.split`
    # and it is fully suitable for parsing in this library

    table = create_translation(dict_from_keys(rest, main))

    def split_multiple(string: str) -> List[str]:
        return string.translate(table).split(main)

    return split_multiple


split_separators = create_split_multiple(*SEPARATORS)


def split_comma(string: str) -> List[str]:
    return string.split(COMMA)


def split_dot(string: str) -> List[str]:
    return string.split(DOT)


def split_pipes(string: str) -> List[str]:
    # analogous to `re.split` with optional second pipe
    return string.replace(DOUBLE_PIPE, PIPE).split(PIPE)
