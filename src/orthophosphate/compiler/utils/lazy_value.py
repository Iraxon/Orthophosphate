from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import cache


class _NoValue(Enum):
    NO_VALUE = auto()

@dataclass
class Lazy[T]:
    supplier: Callable[[], T]
    _cached_value: T | _NoValue = field(init=False, default=_NoValue.NO_VALUE)

    def __call__(self) -> T:
        if self._cached_value is _NoValue.NO_VALUE:
            self._cached_value = self.supplier()
        return self._cached_value
@cache
def lazy_of[T](supplier: Callable[[], T]) -> Lazy[T]:
    """
    Makes a lazy value from the given supplier; the lazy value
    uses the supplier the first time it is called, then uses
    a cached value if called more

    :param supplier: A supplier/constructor with no args
    :type supplier: Callable[[], T]
    :return: A lazy value from that supplier
    :rtype: Callable[[], T]
    """
    return Lazy(supplier)
