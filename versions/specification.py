from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from versions.version import Version

__all__ = ("Specification",)


@runtime_checkable
class Specification(Protocol):
    """The specification protocol for defining version requirements."""

    @abstractmethod
    def accepts(self, version: Version) -> bool:
        """Checks if the `version` matches the specification.

        Arguments:
            version: The version to check.

        Returns:
            Whether the `version` matches the specification.
        """
        raise NotImplementedError
