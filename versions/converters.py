try:
    from versions.converters_modern import (
        simplify,
        specifier_from_version_set,
        specifier_to_version_set,
        version_set_from_specifier,
        version_set_to_specifier,
    )

except SyntaxError:
    from versions.converters_modern import (
        simplify,
        specifier_from_version_set,
        specifier_to_version_set,
        version_set_from_specifier,
        version_set_to_specifier,
    )

__all__ = (
    "simplify",
    "specifier_from_version_set",
    "specifier_to_version_set",
    "version_set_from_specifier",
    "version_set_to_specifier",
)
