from collections.abc import Callable


type orSupplier[T] = T | Callable[[], T]
"""
T must NOT be a Callable type
"""


def get[T](v: orSupplier[T]) -> T:
    if callable(v):
        return v() # type: ignore ; This errors for the case that T is a Callable itself
    else:
        return v
