from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from typing_aliases import is_instance, required
from typing_extensions import TypeGuard

if TYPE_CHECKING:
    from versions.version import Version

__all__ = ("Specification", "is_specification")

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
        raise NotImplementedError(expected_method(ACCEPTS))


def is_specification(item: Any) -> TypeGuard[Specification]:
    return is_instance(item, Specification)
