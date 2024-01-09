__all__ = (
    # release constants
    "ALPHA",
    "A_LITERAL",
    "BETA",
    "B_LITERAL",
    "CANDIDATE",
    "C_LITERAL",
    "RC",
    "PREVIEW",
    "PRE",
    "POST",
    "REV",
    "R_LITERAL",
    "DEV",
    # empty and space constants
    "EMPTY",
    "SPACE",
    # zero string
    "ZERO",
    # empty and universe
    "EMPTY_VERSION",
    "UNIVERSE_VERSION",
    # punctuation constants
    "COMMA",
    "COMMA_SPACE",
    "DASH",
    "DOT",
    "EXCLAMATION",
    "PIPE",
    "PLUS",
    "STAR",
    "QUESTION",
    "UNDER",
    # brackets
    "BRACKETS",
    "SQUARE_BRACKETS",
    # separators allowed in versions
    "SEPARATORS",
    # official specifications
    "TILDE_EQUAL",
    "DOUBLE_EQUAL",
    "NOT_EQUAL",
    "LESS_OR_EQUAL",
    "GREATER_OR_EQUAL",
    "LESS",
    "GREATER",
    # additional specifications
    "CARET",
    "EQUAL",
    "TILDE",
    # wildcard specifications
    "WILDCARD_DOUBLE_EQUAL",
    "WILDCARD_EQUAL",
    "WILDCARD_NOT_EQUAL",
    # version literal
    "V_LITERAL",
    # cross constants (X -> *)
    "X_LITERAL",
    # specification union
    "DOUBLE_PIPE",
    "DOUBLE_PIPE_SPACED",
)

# alpha release
ALPHA = "alpha"
A_LITERAL = "a"

# beta release
BETA = "beta"
B_LITERAL = "b"

# candidate release
CANDIDATE = "candidate"
C_LITERAL = "c"

RC = "rc"  # preferred

# preview (post) release
PREVIEW = "preview"
PRE = "pre"

# post release
POST = "post"

# revision (post) release
REV = "rev"
R_LITERAL = "r"

# development release
DEV = "dev"

# phases (in order of precedence, used in patterns)
PRE_PHASES = (ALPHA, BETA, A_LITERAL, B_LITERAL, C_LITERAL, RC, PREVIEW, PRE)
POST_PHASES = (POST, REV, R_LITERAL)
DEV_PHASES = (DEV,)

# empty and space strings
EMPTY = str()
SPACE = " "

# zero string
ZERO = "0"

# empty and universe
EMPTY_VERSION = ZERO
UNIVERSE_VERSION = "*"

# some punctuation
COMMA = ","
DASH = "-"
DOT = "."
EXCLAMATION = "!"
PIPE = "|"
PLUS = "+"
STAR = "*"
QUESTION = "?"
UNDER = "_"

COMMA_SPACE = COMMA + SPACE

# separators that can be used in versions
SEPARATORS = (DOT, DASH, UNDER)

# official specification syntax
TILDE_EQUAL = "~="
DOUBLE_EQUAL = "=="
NOT_EQUAL = "!="
LESS_OR_EQUAL = "<="
GREATER_OR_EQUAL = ">="
LESS = "<"
GREATER = ">"

# additional specification syntax
CARET = "^"
EQUAL = "="
TILDE = "~"

# wildcard specification syntax
WILDCARD_DOUBLE_EQUAL = DOUBLE_EQUAL + STAR
WILDCARD_EQUAL = EQUAL + STAR
WILDCARD_NOT_EQUAL = NOT_EQUAL + STAR

# version literal
V_LITERAL = "v"

# X -> *
X_LITERAL = "x"

# specification union syntax
DOUBLE_PIPE = PIPE + PIPE

DOUBLE_PIPE_SPACED = SPACE + DOUBLE_PIPE + SPACE

# brackets
BRACKETS = "()"
SQUARE_BRACKETS = "[]"
