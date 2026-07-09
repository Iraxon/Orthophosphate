from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import cast


class _NoValue(Enum):
    NO_VALUE = auto()


@dataclass
class Lazy[T]:
    supplier: Callable[[], T]
    _cached_value: T | _NoValue = field(init=False, default=_NoValue.NO_VALUE)

    def unevaluated(self) -> bool:
        """
        Whether this Lazy has been evaluated

        WARNING: Not a pure function
        """
        return self._cached_value is _NoValue.NO_VALUE

    def __call__(self) -> T:
        if self._cached_value is _NoValue.NO_VALUE:
            self._cached_value = self.supplier()
        return self._cached_value

    def __repr__(self) -> str:
        return f"Lazy({self._cached_value})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self() == other()
        return self() == other

    def __hash__(self):
        return hash(self())


def lazy_of[T](supplier: Callable[[], T]) -> Lazy[T]:
    """
    Make a lazy value from the given supplier. The lazy value
    uses the supplier the first time it is called, then
    a cached value if called more.
    """
    return Lazy(supplier)


def lazy_of_value[T](value: T) -> Lazy[T]:
    """
    Make a lazy value from a given, already-known value
    for compatability with logic that requires it.
    """

    # First, make a lazy with no supplier
    l = Lazy(None) # pyright: ignore[reportUnknownVariableType, reportArgumentType]

    # Then, set its cached value to the given one so it'll provide that.
    l._cached_value = value  # pyright: ignore[reportPrivateUsage]
    return cast(Lazy[T], l)
