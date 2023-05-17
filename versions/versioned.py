from builtins import hasattr as has_attribute
from typing import Any, Optional, Type, TypeVar, overload

from typing_extensions import Protocol, TypeGuard, runtime_checkable

from versions.functions import parse_version
from versions.typing import is_string
from versions.version import Version

__all__ = (
    "VERSION",
    "Versioned",
    "is_versioned",
    "has_version",
    "get_version",
    "get_version_unchecked",
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
    return has_attribute(item, VERSION) and is_string(item.__version__)


has_version = is_versioned
"""An alias of [`is_versioned`][versions.versioned.is_versioned]."""


V = TypeVar("V", bound=Version)


@overload
def get_version(item: Any) -> Optional[Version]:
    ...


@overload
def get_version(item: Any, version_type: Type[V]) -> Optional[V]:
    ...


def get_version(item: Any, version_type: Type[Version] = Version) -> Optional[Version]:
    """Parses the version of the `item` if [`has_version(item)`][versions.versioned.has_version],
    otherwise this function returns [`None`][None].

    Parameters:
        item: The item to fetch the version from.
        version_type: The type of the version to parse.

    Returns:
        The version of `version_type` of the `item`, if one is present, otherwise [`None`][None].
    """
    return get_version_unchecked(item, version_type) if has_version(item) else None


@overload
def get_version_unchecked(item: Versioned) -> Version:
    ...


@overload
def get_version_unchecked(item: Versioned, version_type: Type[V]) -> V:
    ...


def get_version_unchecked(item: Versioned, version_type: Type[Version] = Version) -> Version:
    """Fetches the `__version__` attribute of the `item`,
    parsing it into the version of `version_type`, without checking whether the attribute exists.

    Parameters:
        item: The item to fetch the version from.
        version_type: The type of the version to parse.

    Returns:
        The version of `version_type` of the item.
    """
    return parse_version(item.__version__, version_type)
