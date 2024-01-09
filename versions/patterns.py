# NOTE: very magical :)

import re

from versions.constants import (
    CARET,
    DASH,
    DEV_PHASES,
    DOT,
    DOUBLE_EQUAL,
    EQUAL,
    EXCLAMATION,
    GREATER,
    GREATER_OR_EQUAL,
    LESS,
    LESS_OR_EQUAL,
    NOT_EQUAL,
    PLUS,
    POST_PHASES,
    PRE_PHASES,
    QUESTION,
    SEPARATORS,
    SQUARE_BRACKETS,
    STAR,
    TILDE,
    TILDE_EQUAL,
    V_LITERAL,
    X_LITERAL,
)
from versions.string import (
    concat_empty,
    concat_empty_args,
    concat_pipe,
    concat_pipe_args,
    create_wrap_around,
)

__all__ = (
    # version parts
    "EPOCH",
    "RELEASE",
    "PRE",
    "PRE_PHASE",
    "PRE_VALUE",
    "POST",
    "POST_IMPLICIT",
    "POST_PHASE",
    "POST_VALUE",
    "DEV",
    "DEV_PHASE",
    "DEV_VALUE",
    "LOCAL",
    # version tags
    "TAG_PATTERN",
    "TAG",
    "PHASE",
    "VALUE",
    # full version
    "VERSION_PATTERN",
    "VERSION",
    # public (excluding local) version
    "PUBLIC_VERSION_PATTERN",
    "PUBLIC_VERSION",
    # group names
    "OPERATOR_NAME",
    "VERSION_NAME",
    # constraints
    "CARET_SPECIFICATION_PATTERN",
    "CARET_SPECIFICATION",
    "EQUAL_SPECIFICATION_PATTERN",
    "EQUAL_SPECIFICATION",
    "ORDER_SPECIFICATION_PATTERN",
    "ORDER_SPECIFICATION",
    "TILDE_SPECIFICATION_PATTERN",
    "TILDE_SPECIFICATION",
    "WILDCARD_SPECIFICATION_PATTERN",
    "WILDCARD_SPECIFICATION",
)

# FUNCTIONS

COMPILE = re.compile
ESCAPE = re.escape

COMBINE = concat_empty_args
COMBINE_ITERABLE = concat_empty

UNION = concat_pipe_args
UNION_ITERABLE = concat_pipe


def OPTIONAL(string: str) -> str:
    return string + QUESTION


def SET(string: str) -> str:
    return create_wrap_around(string, SQUARE_BRACKETS)


# CONSTANTS

ALPHA_DIGIT = r"[a-z0-9]"
ALPHA = r"[a-z]"
DIGIT = r"[0-9]"

SEPARATOR = SET(ESCAPE(COMBINE_ITERABLE(SEPARATORS)))

FLAGS = re.IGNORECASE | re.VERBOSE

# VERSION PARTS

EPOCH = "epoch"

RELEASE = "release"

PHASE = "phase"
VALUE = "value"

PRE = "pre"
PRE_PHASE = "pre_phase"
PRE_VALUE = "pre_value"

POST_IMPLICIT = "post_implicit"

POST = "post"
POST_PHASE = "post_phase"
POST_VALUE = "post_value"

DEV = "dev"
DEV_PHASE = "dev_phase"
DEV_VALUE = "dev_value"

LOCAL = "local"

# TAGS

TAG_PATTERN = rf"^(?P<{PHASE}>{ALPHA}+)(?:{SEPARATOR}?(?P<{VALUE}>{DIGIT}+))?$"
TAG = COMPILE(TAG_PATTERN, FLAGS)

# VERSIONS

PUBLIC_VERSION_PATTERN = rf"""
    {V_LITERAL}?

    (?:
        (?P<{EPOCH}>{DIGIT}+){ESCAPE(EXCLAMATION)}
    )?

    (?P<{RELEASE}>{DIGIT}+(?:{ESCAPE(DOT)}{DIGIT}+)*)

    (?:
        {SEPARATOR}?

        (?P<{PRE}>
            (?P<{PRE_PHASE}>{UNION_ITERABLE(PRE_PHASES)})
            (?:
                {SEPARATOR}?
                (?P<{PRE_VALUE}>{DIGIT}+)
            )?
        )
    )?

    (?:
        (?:{DASH}(?P<{POST_IMPLICIT}>{DIGIT}+))
        |
        (?:
            {SEPARATOR}?

            (?P<{POST}>
                (?P<{POST_PHASE}>{UNION_ITERABLE(POST_PHASES)})
                (?:
                    {SEPARATOR}?
                    (?P<{POST_VALUE}>{DIGIT}+)
                )?
            )
        )
    )?

    (?:
        {SEPARATOR}?

        (?P<{DEV}>
            (?P<{DEV_PHASE}>{UNION_ITERABLE(DEV_PHASES)})
            (?:
                {SEPARATOR}?
                (?P<{DEV_VALUE}>{DIGIT}+)
            )?
        )
    )?
"""

PUBLIC_VERSION = COMPILE(PUBLIC_VERSION_PATTERN, FLAGS)

LOCAL_PATTERN = rf"""
    (?:
        {ESCAPE(PLUS)}(?P<{LOCAL}>{ALPHA_DIGIT}+(?:{SEPARATOR}{ALPHA_DIGIT}+)*)
    )?
"""

VERSION_PATTERN = COMBINE(PUBLIC_VERSION_PATTERN, LOCAL_PATTERN)

VERSION = COMPILE(VERSION_PATTERN, FLAGS)

# SPECIFICATIONS

OPERATOR_NAME = "operator"
VERSION_NAME = "version"

CREATE_GROUP = r"(?P<{}>{{}})".format

OPERATOR_GROUP = CREATE_GROUP(OPERATOR_NAME).format
VERSION_GROUP = CREATE_GROUP(VERSION_NAME).format

WILDCARD = UNION(X_LITERAL, ESCAPE(STAR))

WILDCARD_VERSION_PATTERN = rf"""
    {V_LITERAL}?

    (?:
        (?:{DIGIT}+){ESCAPE(EXCLAMATION)}
    )?

    (?:
        (?:{WILDCARD})
        |
        (?:
            (?:{DIGIT}+(?:{ESCAPE(DOT)}{DIGIT}+)*)

            (?:
                (?:{ESCAPE(DOT)}(?:{WILDCARD}))
                |
                (?:
                    (?:
                        {SEPARATOR}?

                        (?:
                            (?:{UNION_ITERABLE(PRE_PHASES)})
                            {SEPARATOR}?
                            (?:{WILDCARD})
                        )
                    )
                    |
                    (?:
                        (?:
                            {SEPARATOR}?

                            (?:
                                (?:{UNION_ITERABLE(PRE_PHASES)})
                                (?:
                                    {SEPARATOR}?
                                    (?:{DIGIT}+)
                                )?
                            )
                        )?
                        (?:
                            (?:
                                (?:{DASH}(?:{WILDCARD}))
                                |
                                (?:
                                    {SEPARATOR}?

                                    (?:
                                        (?:{UNION_ITERABLE(POST_PHASES)})
                                        {SEPARATOR}?
                                        (?:{WILDCARD})
                                    )
                                )
                            )
                            |
                            (?:
                                (?:
                                    (?:{DASH}(?:{DIGIT}+))
                                    |
                                    (?:
                                        {SEPARATOR}?

                                        (?:
                                            (?:{UNION_ITERABLE(POST_PHASES)})
                                            (?:
                                                {SEPARATOR}?
                                                (?:{DIGIT}+)
                                            )?
                                        )
                                    )
                                )?
                                (?:
                                    {SEPARATOR}?

                                    (?:
                                        (?:{UNION_ITERABLE(DEV_PHASES)})
                                        {SEPARATOR}?
                                        (?:{WILDCARD})
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )
"""

WILDCARD_VERSION = COMPILE(WILDCARD_VERSION_PATTERN, FLAGS)

WILDCARD_SPECIFICATION_PATTERN = COMBINE(
    OPTIONAL(OPERATOR_GROUP(UNION(DOUBLE_EQUAL, EQUAL, NOT_EQUAL))),
    VERSION_GROUP(WILDCARD_VERSION_PATTERN),
)

WILDCARD_SPECIFICATION = COMPILE(WILDCARD_SPECIFICATION_PATTERN, FLAGS)

ORDER_SPECIFICATION_PATTERN = COMBINE(
    OPERATOR_GROUP(UNION(LESS_OR_EQUAL, GREATER_OR_EQUAL, LESS, GREATER)),
    VERSION_GROUP(PUBLIC_VERSION_PATTERN),
)

ORDER_SPECIFICATION = COMPILE(ORDER_SPECIFICATION_PATTERN, FLAGS)

CARET_SPECIFICATION_PATTERN = COMBINE(
    OPERATOR_GROUP(ESCAPE(CARET)), VERSION_GROUP(PUBLIC_VERSION_PATTERN)
)

CARET_SPECIFICATION = COMPILE(CARET_SPECIFICATION_PATTERN, FLAGS)

TILDE_SPECIFICATION_PATTERN = COMBINE(
    OPERATOR_GROUP(UNION(TILDE_EQUAL, TILDE)), VERSION_GROUP(PUBLIC_VERSION_PATTERN)
)

TILDE_SPECIFICATION = COMPILE(TILDE_SPECIFICATION_PATTERN, FLAGS)

EQUAL_SPECIFICATION_PATTERN = COMBINE(
    OPTIONAL(OPERATOR_GROUP(UNION(DOUBLE_EQUAL, EQUAL, NOT_EQUAL))),
    VERSION_GROUP(VERSION_PATTERN),
)

EQUAL_SPECIFICATION = COMPILE(EQUAL_SPECIFICATION_PATTERN, FLAGS)
