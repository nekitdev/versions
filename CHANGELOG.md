# Changelog

<!-- changelogging: start -->

## 2.1.2 (2024-02-26)

No significant changes.

## 2.1.1 (2024-02-25)

No significant changes.

## 2.1.0 (2024-02-08)

### Internal

- Removed `versions.converters_modern` and renamed
  `versions.converter_normal -> versions.converters`.

## 2.0.0 (2024-01-09)

### Internal

- Improved type annotations.
- Dropped support for Python 3.7.

## 1.6.1 (2023-05-24)

### Fixes

- Fixed types of `get_version`.

## 1.6.0 (2023-05-24)

### Removals

- `get_version_unchecked` has been renamed to `get_version`,
  which now returns `str` instead of `Optional[str]`.

## 1.5.0 (2023-05-21)

### Internal

- Migrated to using `typing-aliases` library.

## 1.4.0 (2023-05-18)

Partial rewrite.

## 1.3.0 (2022-10-23)

### Changes

- `OperatorType.DOUBLE_EQUAL` and `OperatorType.EQUAL` are now considered equal.

## 1.2.1 (2022-09-17)

No significant changes.

## 1.2.0 (2022-09-17)

### Features

- Add `meta` module with python and library versions.
  ([#3](https://github.com/nekitdev/versions/pull/3))

## 1.1.0 (2022-07-24)

### Changes

- Export type guards, allowing their usage in public API.
  ([#1](https://github.com/nekitdev/versions/pull/1))

## 1.0.0 (2022-07-24)

Initial release.
