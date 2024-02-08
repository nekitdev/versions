"""Parsing, inspecting and specifying versions.

## Example

```python
>>> from versions import parse_specifier, parse_version, parse_version_set
>>> version = parse_version("1.0.0")
>>> version
<Version (1.0.0)>
>>> specifier = parse_specifier("^1.0.0")
>>> specifier
<SpecifierOne (^1.0.0)>
>>> assert version.matches(specifier)
>>> version_set = parse_version_set("^1.0.0")
>>> version_set
<VersionRange (>= 1.0.0, < 2.0.0)>
>>> assert version.matches(version_set)
```
"""

__description__ = "Parsing, inspecting and specifying versions."
__url__ = "https://github.com/nekitdev/versions"

__title__ = "versions"
__author__ = "nekitdev"
__license__ = "MIT"
__version__ = "2.1.0"

from versions.converters import (
    simplify,
    specifier_from_version_set,
    specifier_to_version_set,
    version_set_from_specifier,
    version_set_to_specifier,
)
from versions.errors import ParseError, ParseSpecificationError, ParseVersionError
from versions.functions import parse_specifier, parse_version, parse_version_set
from versions.meta import python_version_info, version_info
from versions.operators import Operator, OperatorType
from versions.segments.epoch import Epoch
from versions.segments.local import Local
from versions.segments.release import Release
from versions.segments.tags import DevTag, PostTag, PreTag, Tag
from versions.specification import Specification
from versions.specifiers import (
    ALWAYS,
    NEVER,
    Specifier,
    SpecifierAll,
    SpecifierAlways,
    SpecifierAny,
    SpecifierNever,
    SpecifierOne,
    is_specifier,
    is_specifier_all,
    is_specifier_always,
    is_specifier_any,
    is_specifier_never,
    is_specifier_one,
)
from versions.version import Version
from versions.version_sets import (
    EMPTY_SET,
    UNIVERSAL_SET,
    VersionEmpty,
    VersionItem,
    VersionPoint,
    VersionRange,
    VersionSet,
    VersionUnion,
    is_version_empty,
    is_version_item,
    is_version_point,
    is_version_range,
    is_version_set,
    is_version_union,
)
from versions.versioned import VERSION, Versioned, get_version, has_version, is_versioned

__all__ = (
    # versions
    "Version",
    # segments
    "Epoch",
    "Release",
    "Tag",
    "PreTag",
    "PostTag",
    "DevTag",
    "Local",
    # operators
    "Operator",
    "OperatorType",
    # specification
    "Specification",
    # specifiers
    "NEVER",
    "ALWAYS",
    "Specifier",
    "SpecifierNever",
    "SpecifierAlways",
    "SpecifierOne",
    "SpecifierAll",
    "SpecifierAny",
    # specifiers type guards
    "is_specifier",
    "is_specifier_never",
    "is_specifier_always",
    "is_specifier_one",
    "is_specifier_all",
    "is_specifier_any",
    # version sets
    "EMPTY_SET",
    "UNIVERSAL_SET",
    "VersionEmpty",
    "VersionPoint",
    "VersionRange",
    "VersionUnion",
    "VersionItem",
    "VersionSet",
    # version sets type guards
    "is_version_empty",
    "is_version_point",
    "is_version_range",
    "is_version_union",
    "is_version_item",
    "is_version_set",
    # errors
    "ParseError",
    "ParseSpecificationError",
    "ParseVersionError",
    # converters
    "simplify",
    "specifier_from_version_set",
    "specifier_to_version_set",
    "version_set_from_specifier",
    "version_set_to_specifier",
    # functions
    "parse_specifier",
    "parse_version",
    "parse_version_set",
    # meta
    "version_info",
    "python_version_info",
    # versioned
    "VERSION",
    "Versioned",
    "get_version",
    "has_version",
    "is_versioned",
)
