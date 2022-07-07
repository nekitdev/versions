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
>>> version.matches(version_set)
True
```
"""

__description__ = "Parsing, inspecting and specifying versions."
__url__ = "https://github.com/nekitdev/versions"

__title__ = "versions"
__author__ = "nekitdev"
__license__ = "MIT"
__version__ = "1.0.0-alpha.1"

from versions.converters import (
    simplify,
    specifier_from_version_set,
    specifier_to_version_set,
    version_set_from_specifier,
    version_set_to_specifier,
)
from versions.errors import ParseError, ParseSpecificationError, ParseVersionError
from versions.functions import parse_specifier, parse_version, parse_version_set
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
)
from versions.version import Version
from versions.version_sets import (
    VersionEmpty,
    VersionItem,
    VersionPoint,
    VersionRange,
    VersionSet,
    VersionUnion,
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
    # version sets
    "VersionEmpty",
    "VersionPoint",
    "VersionRange",
    "VersionUnion",
    "VersionItem",
    "VersionSet",
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
)

version_info = parse_version(__version__)
