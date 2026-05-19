"""
A purely functional system for PEG parsing
"""

from collections.abc import Callable
from typing import Literal, overload

from ..utils.frozeniter import FrozenIter, get, next_frozen
from .parse_result_guts.failure import Failure
from .parse_result_guts.success import Success

type ParseResult[T, SRC] = Success[T, SRC] | Failure

type Parser[T, SRC] = Callable[[FrozenIter[SRC]], ParseResult[T, SRC]]
"""
Parsers should return a "moved-forward" src FrozenIter
on success and an unchanged one on failure
"""


def success[T, S](v: T, src: FrozenIter[S]) -> Success[T, S]:
    return Success(v, src)


def failure(msg: str | tuple[str, ...]) -> Failure:
    return Failure((msg,) if isinstance(msg, str) else msg)


@overload
def is_successful[T, SRC](result: Success[T, SRC]) -> Literal[True]: ...
@overload
def is_successful[SRC](result: Failure) -> Literal[False]: ...


def is_successful[T, SRC](result: ParseResult[T, SRC]) -> bool:
    match result:
        case Success():
            return True
        case Failure():
            return False


def map_result[T, R, SRC](
    result: ParseResult[T, SRC], fn: Callable[[T], R]
) -> ParseResult[R, SRC]:
    match result:
        case Success(v, src):
            return Success(fn(v), src)
        case Failure() as f:
            return f


# def flat_map_result[T, R, SRC](
#     result: ParseResult[T, SRC], fn: Callable[[T], ParseResult[R, SRC]]
# ) -> ParseResult[R, SRC]:
#     match result:
#         case Success(v, _):
#             return fn(v)
#         case Failure() as f:
#             return f

# Error message utils

type ErrorMessageProvider[SRC] = Callable[[FrozenIter[SRC]], str]


def EMPTY_ERROR[SRC](src: FrozenIter[SRC]) -> str:
    """
    Useful for structural calls that don't
    represent another unit of meaning
    """
    return ""


def chain_map[T, R, SRC](
    parser: Parser[T, SRC], fn: Callable[[T], R]
) -> Parser[R, SRC]:
    return lambda src: map_result(parser(src), fn)


# def chain_flat_map[T, R, SRC](
#     parser: Parser[T, SRC], fn: Callable[[T], ParseResult[R, SRC]]
# ) -> Parser[R, SRC]:
#     return lambda src: flat_map_result(parser(src), fn)


def _alternative_raw[T, SRC](
    src: FrozenIter[SRC],
    error_msg: ErrorMessageProvider[SRC],
    *alternatives: Parser[T, SRC],
) -> ParseResult[T, SRC]:
    """
    Parsing expression grammar ordered choice operator
    """

    failure_errors: list[str] = []

    for alt in alternatives:
        match alt(src):
            case Success(v, new_src):
                return Success(v, new_src)
            case Failure(errors):
                failure_errors.extend(errors)
    return failure(error_msg(src)).with_reasons(tuple(failure_errors))


def alternative[T, SRC](
    error_msg: ErrorMessageProvider[SRC], *alternatives: Parser[T, SRC]
) -> Parser[T, SRC]:
    """
    Parsing expression grammar ordered choice operator
    """

    return lambda src: _alternative_raw(src, error_msg, *alternatives)


def _chain_2_raw[T, U, R, SRC](
    src: FrozenIter[SRC],
    collector: Callable[[T, U], R],
    first: Parser[T, SRC],
    second: Parser[U, SRC],
    error_msg: ErrorMessageProvider[SRC],
) -> ParseResult[R, SRC]:

    src_cursor = src

    first_val: T
    match first(src_cursor):
        case Success(v, src):
            first_val = v
            src_cursor = src
        case Failure() as f:
            return f.elaborate_on(error_msg(src))

    second_val: U
    match second(src_cursor):
        case Success(v, new_src):
            second_val = v
            src_cursor = new_src
        case Failure() as f:
            return f.elaborate_on(error_msg(src))

    return success(collector(first_val, second_val), src_cursor)


# Begin chain implementations


def chain2[T, U, R, SRC](
    function: Callable[[T, U], R],
    first: Parser[T, SRC],
    second: Parser[U, SRC],
    error_msg: ErrorMessageProvider[SRC] = EMPTY_ERROR,
) -> Parser[R, SRC]:
    return lambda src: _chain_2_raw(src, function, first, second, error_msg)


def chain3[T, U, V, R, SRC](
    function: Callable[[T, U, V], R],
    first: Parser[T, SRC],
    second: Parser[U, SRC],
    third: Parser[V, SRC],
    error_msg: ErrorMessageProvider[SRC] = EMPTY_ERROR,
) -> Parser[R, SRC]:
    return chain2(
        lambda fs, t: function(*fs, t),
        chain2(lambda f, s: (f, s), first, second, EMPTY_ERROR),
        third,
        error_msg,
    )


def chain4[T, U, V, W, R, SRC](
    function: Callable[[T, U, V, W], R],
    first: Parser[T, SRC],
    second: Parser[U, SRC],
    third: Parser[V, SRC],
    fourth: Parser[W, SRC],
    error_msg: ErrorMessageProvider[SRC] = EMPTY_ERROR,
) -> Parser[R, SRC]:
    return chain2(
        lambda fs, tf: function(*fs, *tf),
        chain2(lambda f, s: (f, s), first, second, EMPTY_ERROR),
        chain2(lambda t, f: (t, f), third, fourth, EMPTY_ERROR),
        error_msg,
    )


# End chain implementations


def _repeat_sequence_raw[T, SRC](
    src: FrozenIter[SRC],
    parser: Parser[T, SRC],
    allow_eof: bool,
) -> ParseResult[tuple[T, ...], SRC]:

    r_val: list[T] = []
    current_src: FrozenIter[SRC] = src

    while True:

        if current_src is None:
            if allow_eof:
                break
            else:
                return eof_failure(current_src)

        match parser(current_src):
            case Success(v, new_src):
                if new_src is current_src:
                    raise ValueError(
                        f"Success without advancing: {parser} at {current_src}"
                    )
                r_val.append(v)
                current_src = new_src
            case Failure():
                break

    return success(tuple(r_val), current_src)


def repeat_sequence[T, SRC](
    parser: Parser[T, SRC],
    error_msg: ErrorMessageProvider[SRC],
    *,
    allow_empty_sequence: bool = False,
    allow_eof: bool = False,
) -> Parser[tuple[T, ...], SRC]:
    def repeat_sequence_parser(src: FrozenIter[SRC]) -> ParseResult[tuple[T, ...], SRC]:
        return _repeat_sequence_raw(src, parser, allow_eof)

    if allow_empty_sequence:
        return override_error_message(repeat_sequence_parser, lambda src: f"No items in sequence at {src}")
    return chain2(
        lambda first, rest: (first,) + rest, parser, repeat_sequence_parser, error_msg
    )


def _optional_raw[T, SRC](
    src: FrozenIter[SRC],
    option: Parser[T, SRC],
) -> ParseResult[T | None, SRC]:

    match option(src):
        case Success(v, s_src):
            return Success(v, s_src)
        case Failure():
            return success(None, src)


def optional[T, SRC](
    option: Parser[T, SRC],
) -> Parser[T | None, SRC]:
    return lambda src: _optional_raw(src, option)


def _negate_raw[T, SRC](
    src: FrozenIter[SRC],
    parser: Parser[T, SRC],
    error_msg: ErrorMessageProvider[SRC],
    value: T,
) -> ParseResult[T, SRC]:
    match parser(src):
        case Success():
            return failure(error_msg(src))
        case Failure():
            return success(value, src)


def negate[T, SRC](
    parser: Parser[T, SRC],
    error_msg: ErrorMessageProvider[SRC],
    value: T = None,
) -> Parser[T, SRC]:
    return lambda src: _negate_raw(src, parser, error_msg, value)


# Atomic parser


def _match_one_raw[SRC](
    src: FrozenIter[SRC],
    predicate: Callable[[SRC], bool],
    error_msg: ErrorMessageProvider[SRC],
) -> ParseResult[SRC, SRC]:
    # print(f"SRC-start {src}")
    match get(src):
        case None:
            return eof_failure(src)
        case t if predicate(t):
            return success(t, next_frozen(src))
        case _:
            return failure(error_msg(src) if callable(error_msg) else error_msg)


def match_one[SRC](
    predicate: Callable[[SRC], bool],
    *,
    error_msg: ErrorMessageProvider[SRC],
) -> Parser[SRC, SRC]:
    return lambda src: _match_one_raw(src, predicate, error_msg)


def override_error_message[T, SRC](
    parser: Parser[T, SRC], error_msg: ErrorMessageProvider[SRC]
) -> Parser[T, SRC]:
    def parser_overridden(src: FrozenIter[SRC]) -> ParseResult[T, SRC]:
        match parser(src):
            case Failure():
                return failure(error_msg(src))
            case Success() as s:
                return s

    return parser_overridden


# Util


def empty_string_match[SRC](src: FrozenIter[SRC]) -> Success[None, SRC]:
    return success(None, src)


def eof_failure[SRC](src: FrozenIter[SRC]) -> Failure:
    return failure(f"Unexpected end of input at {src}")

def return_first_arg[T](first: T, *__: object) -> T:
    return first

def return_second_arg[T](_: object, second: T, *___: object) -> T:
    return second


def return_third_arg[T](_: object, __: object, third: T = None, *____: object) -> T:
    return third
