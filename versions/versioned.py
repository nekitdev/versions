from typing import Any, Protocol, Type, TypeVar, overload, runtime_checkable

from typing_aliases import is_instance
from typing_extensions import TypeGuard

from versions.functions import parse_version
from versions.version import Version

__all__ = (
    "VERSION",
    "Versioned",
    "get_version",
    "has_version",
    "is_versioned",
)

VERSION = "__version__"


@runtime_checkable
class Versioned(Protocol):
    """Represents versioned objects, that is, objects that have the `__version__`
    attribute of type [`str`][str].
    """

    __version__: str


def is_versioned(item: Any) -> TypeGuard[Versioned]:
    """Checks if the `item` implements the [`Versioned`][versions.versioned.Versioned] protocol.

    That is, whether the `item` has the `__version__` attribute of type [`str`][str].

    Parameters:
        item: The item to check.

    Returns:
        Whether the `item` implements the [`Versioned`][versions.versioned.Versioned] protocol.
    """
    return is_instance(item, Versioned)


has_version = is_versioned
"""An alias of [`is_versioned`][versions.versioned.is_versioned]."""


V = TypeVar("V", bound=Version)


@overload
def get_version(item: Versioned) -> Version:
    ...


@overload
def get_version(item: Versioned, version_type: Type[V]) -> V:
    ...


def get_version(item: Versioned, version_type: Type[Version] = Version) -> Version:
    """Fetches the `__version__` attribute of the `item`,
    parsing it into the version of `version_type`, without checking whether the attribute exists.

    Parameters:
        item: The item to fetch the version from.
        version_type: The type of the version to parse.

    Returns:
        The version of `version_type` of the item.
    """
    return parse_version(item.__version__, version_type)
