"""
A purely functional system for handling
errors
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import assert_never

from ..utils.or_supplier import OrSupplier, get
from .context import ParseContext

type ParseResult[T] = Success[T] | Failure

@dataclass(frozen=True)
class Success[T]:
    v: T

    # context: ParseContext

def success[T](v: T) -> Success[T]:
    return Success(v)

type IndividualError = tuple[str, ParseContext]

@dataclass(frozen=True)
class Failure:
    errors: tuple[IndividualError, ...]

def failure(msg: str) -> Failure:
    return Failure(((msg, ParseContext("", (0, 0))),))

def mapResult[T, R](result: ParseResult[T], fn: Callable[[T], R]) -> ParseResult[R]:
    match result:
        case Success(v):
            return Success(fn(v),)
        case Failure() as f:
            return f

def error[T](msg: str, context: ParseContext, result: ParseResult[T] | None = None) -> Failure:

    other_errors: tuple[IndividualError, ...]
    match result:
        case Success() | None:
            other_errors = tuple()
        case Failure(oe):
            other_errors = oe
        case _:
            assert_never()

    return Failure(other_errors + ((msg, context),))

def first_success[T, U](first: OrSupplier[ParseResult[T]], second: OrSupplier[ParseResult[U]]) -> ParseResult[T] | ParseResult[U]:

    match get(first):
        case Success() as v1:
            return v1
        case Failure() as f1:
            pass

    match get(second):
        case Success() as v2:
            return v2
        case Failure() as f2:
            return Failure(f1.errors + f2.errors)
