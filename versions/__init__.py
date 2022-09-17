"""Parsing, inspecting and specifying versions.

## Example

```python
>>> from versions import parse_version, parse_version_set
>>> version = parse_version("1.0.0")
>>> version
<Version (1.0.0)>
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
__version__ = "1.2.0"

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
from versions.segments import DevTag, Epoch, Local, PostTag, PreTag, Release, Tag
from versions.specification import Specification
from versions.specifiers import (
    Specifier,
    SpecifierAll,
    SpecifierAny,
    SpecifierFalse,
    SpecifierSingle,
    SpecifierTrue,
    is_specifier,
    is_specifier_all,
    is_specifier_any,
    is_specifier_false,
    is_specifier_single,
    is_specifier_true,
)
from versions.version import Version
from versions.version_sets import (
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
    "Specifier",
    "SpecifierFalse",
    "SpecifierTrue",
    "SpecifierSingle",
    "SpecifierAll",
    "SpecifierAny",
    # specifiers type guards
    "is_specifier",
    "is_specifier_false",
    "is_specifier_true",
    "is_specifier_single",
    "is_specifier_all",
    "is_specifier_any",
    # version sets
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
)
