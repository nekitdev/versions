from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from versions.version import Version

__all__ = ("Specification",)


@runtime_checkable
class Specification(Protocol):
    @abstractmethod
    def accepts(self, version: Version) -> bool:
        raise NotImplementedError
