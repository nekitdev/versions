from __future__ import annotations

from abc import abstractmethod as required
from typing import TYPE_CHECKING

from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from versions.version import Version

__all__ = ("Specification",)

EXPECTED_METHOD = "expected `{}` to define `{}` method"
expected_method = EXPECTED_METHOD.format

ACCEPTS = "accepts"


@runtime_checkable
class Specification(Protocol):
    """The specification protocol for defining version requirements."""

    @required
    def accepts(self, version: Version) -> bool:
        """Checks if the `version` matches the specification.

        Arguments:
            version: The version to check.

        Returns:
            Whether the `version` matches the specification.
        """
        raise NotImplementedError
