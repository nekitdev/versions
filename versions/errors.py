__all__ = (
    "InternalError",
    "ParseError",
    "ParseSpecificationError",
    "ParseTagError",
    "ParseVersionError",
)


class ParseError(ValueError):
    """Parsing has failed."""


class ParseSpecificationError(ParseError):
    """Parsing a specification has failed."""


class ParseTagError(ParseError):
    """Parsing a version tag has failed."""


class ParseVersionError(ParseError):
    """Parsing a version has failed."""


class InternalError(RuntimeError):
    """An internal error has occurred."""
