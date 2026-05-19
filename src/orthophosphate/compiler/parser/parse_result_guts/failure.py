from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class Failure:
    errors: tuple[str, ...]

    def elaborate_on(self, new_info: str) -> Self:
        """
        For when the info in self.errors is the
        reason behind new_info
        """
        return type(self)((new_info, *self.errors))

    def with_reasons(self, reasons: tuple[str, ...]) -> Self:
        """
        For when you have reasons that describe
        the why behind the info in self.errors
        """
        return type(self)((*self.errors, *reasons))
