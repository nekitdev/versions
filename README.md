# `versions`

[![License][License Badge]][License]
[![Version][Version Badge]][Package]
[![Downloads][Downloads Badge]][Package]
[![Discord][Discord Badge]][Discord]

[![Documentation][Documentation Badge]][Documentation]
[![Check][Check Badge]][Actions]
[![Test][Test Badge]][Actions]
[![Coverage][Coverage Badge]][Coverage]

> *Parsing, inspecting and specifying versions.*

## Installing

**Python 3.8 or above is required.**

### pip

Installing the library with `pip` is quite simple:

```console
$ pip install versions
```

Alternatively, the library can be installed from source:

```console
$ git clone https://github.com/nekitdev/versions.git
$ cd versions
$ python -m pip install .
```

### poetry

You can add `versions` as a dependency with the following command:

```console
$ poetry add versions
```

Or by directly specifying it in the configuration like so:

```toml
[tool.poetry.dependencies]
versions = "^2.1.0"
```

Alternatively, you can add it directly from the source:

```toml
[tool.poetry.dependencies.versions]
git = "https://github.com/nekitdev/versions.git"
```

## Examples

### Versions

[`parse_version`][versions.functions.parse_version] is used to parse versions:

```python
from versions import parse_version

version = parse_version("1.0.0-dev.1+build.1")

print(version)  # 1.0.0-dev.1+build.1
```

### Segments

All version segments can be fetched with their respective names:

```python
>>> print(version.release)
1.0.0
>>> version.release.parts
(1, 0, 0)
>>> print(version.dev)
dev.1
>>> (version.dev.phase, version.dev.value)
("dev", 1)
>>> print(version.local)
build.1
>>> version.local.parts
("build", 1)
```

### Comparison

Versions support total ordering:

```python
>>> v1 = parse_version("1.0.0")
>>> v2 = parse_version("2.0.0")
>>> v1 == v2
False
>>> v1 != v2
True
>>> v1 >= v2
False
>>> v1 <= v2
True
>>> v1 > v2
False
>>> v1 < v2
True
```

### Specification

`versions` also supports specifying version requirements and matching version against them.

Since versions support total ordering, they can be checked using *version sets*
(via [`parse_version_set`][versions.functions.parse_version_set]):

```python
>>> from versions import parse_version, parse_version_set
>>> version_set = parse_version_set("^1.0.0")
>>> version_set
<VersionRange (>= 1.0.0, < 2.0.0)>
>>> version = parse_version("1.3.0")
>>> version.matches(version_set)
True
>>> another = parse_version("2.2.0")
>>> another.matches(version_set)
False
```

Alternatively, one can use *specifiers*, which are similar to version sets, except they retain
the structure of specifications given (via [`parse_specifier`][versions.functions.parse_specifier]):

```python
>>> from versions import parse_specifier, parse_version
>>> specifier = parse_specifier("^1.0.0")
>>> specifier
<SpecifierOne (^1.0.0)>
>>> version = parse_version("1.3.0")
>>> version.matches(specifier)
True
>>> another = parse_version("2.2.0")
>>> another.matches(specifier)
False
```

## Versioned

`versions` allows users to access versions of items that have the `__version__` attribute:

```python
>>> from versions import get_version
>>> import versions
>>> get_version(versions)
<Version (2.1.0)>
```

## Documentation

You can find the documentation [here][Documentation].

## Support

If you need support with the library, you can send an [email][Email]
or refer to the official [Discord server][Discord].

## Changelog

You can find the changelog [here][Changelog].

## Security Policy

You can find the Security Policy of `versions` [here][Security].

## Contributing

If you are interested in contributing to `versions`, make sure to take a look at the
[Contributing Guide][Contributing Guide], as well as the [Code of Conduct][Code of Conduct].

## License

`versions` is licensed under the MIT License terms. See [License][License] for details.

[Email]: mailto:support@nekit.dev

[Discord]: https://nekit.dev/discord

[Actions]: https://github.com/nekitdev/versions/actions

[Changelog]: https://github.com/nekitdev/versions/blob/main/CHANGELOG.md
[Code of Conduct]: https://github.com/nekitdev/versions/blob/main/CODE_OF_CONDUCT.md
[Contributing Guide]: https://github.com/nekitdev/versions/blob/main/CONTRIBUTING.md
[Security]: https://github.com/nekitdev/versions/blob/main/SECURITY.md

[License]: https://github.com/nekitdev/versions/blob/main/LICENSE

[Package]: https://pypi.org/project/versions
[Coverage]: https://codecov.io/gh/nekitdev/versions
[Documentation]: https://nekitdev.github.io/versions

[Discord Badge]: https://img.shields.io/badge/chat-discord-5865f2
[License Badge]: https://img.shields.io/pypi/l/versions
[Version Badge]: https://img.shields.io/pypi/v/versions
[Downloads Badge]: https://img.shields.io/pypi/dm/versions

[Documentation Badge]: https://github.com/nekitdev/versions/workflows/docs/badge.svg
[Check Badge]: https://github.com/nekitdev/versions/workflows/check/badge.svg
[Test Badge]: https://github.com/nekitdev/versions/workflows/test/badge.svg
[Coverage Badge]: https://codecov.io/gh/nekitdev/versions/branch/main/graph/badge.svg

[versions.functions.parse_specifier]: https://nekitdev.github.io/versions/reference/functions#versions.functions.parse_specifier
[versions.functions.parse_version]: https://nekitdev.github.io/versions/reference/functions#versions.functions.parse_version
[versions.functions.parse_version_set]: https://nekitdev.github.io/versions/reference/functions#versions.functions.parse_version_set
