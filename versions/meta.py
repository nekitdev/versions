from sys import version_info as python_version_tuple
from typing import Literal

import versions
from versions.segments.tags import PreTag
from versions.version import Version
from versions.versioned import get_version

__all__ = ("version_info", "python_version_info")

version_info = get_version(versions)  # type: ignore
"""The library version represented as a [`Version`][versions.version.Version]."""

FINAL: Literal["final"] = "final"

python_major, python_minor, python_micro, python_phase, python_value = python_version_tuple

if python_phase == FINAL:  # pragma: no cover
    python_version_info = Version.from_parts(python_major, python_minor, python_micro)
    """The python version represented as a [`Version`][versions.version.Version]."""

else:  # pragma: no cover
    python_version_info = Version.from_parts(
        python_major, python_minor, python_micro, pre=PreTag(python_phase, python_value)
    ).normalize()
    """The python version represented as a [`Version`][versions.version.Version]."""
