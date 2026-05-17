"""
A purely functional system for handling
errors
"""

from collections.abc import Callable
from dataclasses import dataclass

from or_supplier import OrSupplier, get

type Result[T] = T | Error

@dataclass(frozen=True)
class Error:
    errors: tuple[str, ...]

def mapResult[T, R](result: Result[T], fn: Callable[[T], R]) -> Result[R]:
    if isinstance(result, Error):
        return result
    else:
        return fn(result)

def error[T](msg: str, result: Result[T] | None = None) -> Error:
    if isinstance(result, Error):
        return Error(result.errors + (msg,))
    else:
        return Error((msg,))

def first_success[T, U](first: OrSupplier[Result[T]], second: OrSupplier[Result[U]]) -> Result[T | U]:
    f = get(first)
    if isinstance(f, Error):
        return get(second)
    return f
