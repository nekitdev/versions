from sys import version_info as python_version_tuple

from typing_extensions import Final

from versions import __version__ as version
from versions.functions import parse_version
from versions.segments import PreTag
from versions.version import Version

__all__ = ("version_info", "python_version_info")

version_info = parse_version(version)
"""The library version represented as a [`Version`][versions.version.Version]."""

FINAL: Final[str] = "final"

python_major, python_minor, python_micro, python_phase, python_value = python_version_tuple

if python_phase == FINAL:  # pragma: no cover
    python_version_info = Version.from_parts(python_major, python_minor, python_micro)
    """The python version represented as a [`Version`][versions.version.Version]."""

else:  # pragma: no cover
    python_version_info = Version.from_parts(
        python_major, python_minor, python_micro, pre=PreTag(python_phase, python_value).normalize()
    )
    """The python version represented as a [`Version`][versions.version.Version]."""