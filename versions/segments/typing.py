from typing import Tuple, Union

from typing_aliases import DynamicTuple

from versions.types import NegativeInfinity

__all__ = (
    # releases
    "Part",
    "Parts",
    "Extra",
    # local
    "LocalPart",
    "LocalParts",
    "CompareLocalPart",
    "CompareLocalParts",
)

Part = int

# technically parts are never empty (this is their invariant)
# but we can not enforce this in the type system
Parts = DynamicTuple[Part]

Extra = DynamicTuple[Part]

LocalPart = Union[int, str]

# technically local parts are never empty (this is their invariant)
# but we can not enforce this in the type system
LocalParts = DynamicTuple[LocalPart]

CompareLocalIntPart = Tuple[int, str]
CompareLocalStringPart = Tuple[NegativeInfinity, str]

CompareLocalPart = Union[CompareLocalIntPart, CompareLocalStringPart]

# technically compare local parts are never empty (this is their invariant)
# but we can not enforce this in the type system
CompareLocalParts = DynamicTuple[CompareLocalPart]
