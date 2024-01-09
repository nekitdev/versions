__all__ = (
    "DEFAULT_PARTS",
    "DEFAULT_VALUE",
    "DEFAULT_PADDING",
    "MAJOR",
    "MINOR",
    "MICRO",
    "TOTAL",
    "PATCH",
)

DEFAULT_PARTS = (0, 0, 0)  # makes sense as the default for semantic versions
"""The default parts of the [`Release`][versions.segments.release.Release]."""

DEFAULT_VALUE = 0
"""The default value to use."""

DEFAULT_PADDING = 0
"""The default padding to use."""

MAJOR = 0
"""The index of the *major* part of the release."""
MINOR = 1
"""The index of the *minor* part of the release."""
MICRO = 2
"""The index of the *micro* part of the release."""
TOTAL = 3
"""The total count of handled parts in the release."""

PATCH = MICRO  # alias
"""An alias of [`MICRO`][versions.segments.constants.MICRO]."""
