from typing import ClassVar

from named import get_type_name

from versions.string import create_wrap_around

__all__ = ("TEMPLATE", "Representation")

TEMPLATE = "<{name} {string}>"


class Representation:
    WRAP: ClassVar[bool] = True

    def __repr__(self) -> str:
        return TEMPLATE.format(
            name=get_type_name(self),
            string=create_wrap_around(str(self)) if self.WRAP else str(self),
        )
