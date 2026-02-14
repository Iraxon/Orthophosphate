from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto


def lazy_value[T](supplier: Callable[[], T]) -> Callable[[], T]:
    """
    Makes a lazy value from the given supplier; the lazy value
    uses the supplier the first time it is called, then uses
    a cached value if called more

    :param supplier: A supplier/constructor with no args
    :type supplier: Callable[[], T]
    :return: A lazy value from that supplier
    :rtype: Callable[[], T]
    """
    return _LazyValue(supplier)


class _NoValue(Enum):
    NO_VALUE = auto()


@dataclass
class _LazyValue[T]:
    supplier: Callable[[], T]
    _cache: T | _NoValue = field(init=False, default=_NoValue.NO_VALUE)

    def __call__(self) -> T:
        if self._cache is _NoValue.NO_VALUE:
            self._cache = self.supplier()
        return self._cache
