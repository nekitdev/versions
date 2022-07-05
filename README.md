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

**Python 3.7 or above is required.**

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
versions = "^1.0.0-alpha.1"
```

Alternatively, you can add it directly from the source:

```toml
[tool.poetry.dependencies.versions]
git = "https://github.com/nekitdev/versions.git"
```

## Examples

### Versions

```python
from versions import parse_version

version = parse_version("1.0.0-dev.1+build.1")

print(version)  # 1.0.0-dev.1+build.1
```

### Segments

```python
print(version.release)  # 1.0.0
print(version.dev)      # dev.1
print(version.local)    # build.1
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
