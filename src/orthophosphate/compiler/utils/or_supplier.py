from collections.abc import Callable


type OrSupplier[T] = T | Callable[[], T]
"""
T must NOT be a Callable type
"""


def get[T](v: OrSupplier[T]) -> T:
    if callable(v):
        return v() # type: ignore ; This errors for the case that T is a Callable itself
    else:
        return v
