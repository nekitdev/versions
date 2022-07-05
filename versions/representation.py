from typing import ClassVar

from versions.string import create_wrap_around
from versions.typing import get_name

__all__ = ("TEMPLATE", "Representation")

TEMPLATE = "<{name} {string}>"


class Representation:
    WRAP: ClassVar[bool] = True

    def __repr__(self) -> str:
        return TEMPLATE.format(
            name=get_name(type(self)),  # type: ignore
            string=create_wrap_around(str(self)) if self.WRAP else str(self),
        )
