"""
A purely functional system for handling
errors
"""

from collections.abc import Callable
from typing import Any, Literal, overload

from ..utils.frozeniter import FrozenIter, get, next_frozen
from .parse_result_guts.failure import Failure
from .parse_result_guts.success import Success

type ParseResult[T, SRC] = Success[T, SRC] | Failure[SRC]

type Parser[T, SRC] = Callable[[FrozenIter[SRC]], ParseResult[T, SRC]]
"""
Parsers should return a "moved-forward" src FrozenIter
on success and an unchanged one on failure
"""


def success[T, S](v: T, src: FrozenIter[S]) -> Success[T, S]:
    return Success(v, src)


def failure[SRC](msg: str | tuple[str, ...], src: FrozenIter[SRC]) -> Failure[SRC]:
    return Failure((msg,) if isinstance(msg, str) else msg, src)


@overload
def is_successful[T, SRC](result: Success[T, SRC]) -> Literal[True]: ...
@overload
def is_successful[SRC](result: Failure[SRC]) -> Literal[False]: ...


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


def flat_map_result[T, R, SRC](
    result: ParseResult[T, SRC], fn: Callable[[T], ParseResult[R, SRC]]
) -> ParseResult[R, SRC]:
    match result:
        case Success(v, _):
            return fn(v)
        case Failure() as f:
            return f


def chain_map[T, R, SRC](
    parser: Parser[T, SRC], fn: Callable[[T], R]
) -> Parser[R, SRC]:
    return lambda src: map_result(parser(src), fn)


def chain_flat_map[T, R, SRC](
    parser: Parser[T, SRC], fn: Callable[[T], ParseResult[R, SRC]]
) -> Parser[R, SRC]:
    return lambda src: flat_map_result(parser(src), fn)


# def error[T, SRC](
#     msg: str, context: ParseContext, result: ParseResult[T] | None = None
# ) -> Failure:

#     other_errors: tuple[IndividualError, ...]
#     match result:
#         case Success() | None:
#             other_errors = tuple()
#         case Failure(oe):
#             other_errors = oe
#         case _:
#             assert_never()

#     return Failure(other_errors + ((msg, context),))

# Parser combinators


def _alternative_raw[T, SRC](
    src: FrozenIter[SRC], *alternatives: Parser[T, SRC]
) -> ParseResult[T, SRC]:
    """
    Parsing expression grammar ordered choice operator
    """

    failure_errors: list[str] = []

    for alt in alternatives:
        match alt(src):
            case Success(v, src):
                return Success(v, src)
            case Failure() as f:
                failure_errors.extend(f.errors)
    return failure(tuple(failure_errors), src)


def alternative[T, SRC](*alternatives: Parser[T, SRC]) -> Parser[T, SRC]:
    """
    Parsing expression grammar ordered choice operator
    """

    return lambda src: _alternative_raw(src, *alternatives)


def _chain_2_raw[T, U, R, SRC](
    src: FrozenIter[SRC],
    collector: Callable[[T, U], R],
    first: Parser[T, SRC],
    second: Parser[U, SRC],
) -> ParseResult[R, SRC]:

    src_cursor = src

    first_val: T
    match first(src_cursor):
        case Success(v, src):
            first_val = v
            src_cursor = src
        case Failure() as f:
            return f

    second_val: U
    match second(src_cursor):
        case Success(v, src):
            second_val = v
            src_cursor = src
        case Failure() as f:
            return f

    return success(collector(first_val, second_val), src_cursor)


# Begin chain implementations


def chain[T, U, R, SRC](
    function: Callable[[T, U], R],
    first: Parser[T, SRC],
    second: Parser[U, SRC],
) -> Parser[R, SRC]:
    return lambda src: _chain_2_raw(src, function, first, second)


def chain3[T, U, V, R, SRC](
    function: Callable[[T, U, V], R],
    first: Parser[T, SRC],
    second: Parser[U, SRC],
    third: Parser[V, SRC],
) -> Parser[R, SRC]:
    return chain(
        lambda fs, t: function(*fs, t),
        chain(lambda f, s: (f, s), first, second),
        third,
    )


def chain4[T, U, V, W, R, SRC](
    function: Callable[[T, U, V, W], R],
    first: Parser[T, SRC],
    second: Parser[U, SRC],
    third: Parser[V, SRC],
    fourth: Parser[W, SRC],
) -> Parser[R, SRC]:
    return chain(
        lambda fs, tf: function(*fs, *tf),
        chain(lambda f, s: (f, s), first, second),
        chain(lambda t, f: (t, f), third, fourth),
    )


# End chain implementations


def _repeat_sequence_raw[T, SRC](
    src: FrozenIter[SRC],
    end_token_predicate: Callable[[SRC], bool],
    parser: Parser[T, SRC],
    allow_empty_sequence: bool = False,
    allow_eof: bool = False,
) -> ParseResult[tuple[T, ...], SRC]:

    r_val: list[T] = []
    current_src: FrozenIter[SRC] = src

    while True:

        if current_src is None:
            if allow_eof:
                break
            else:
                return eof_failure(current_src)

        if end_token_predicate(get(current_src)):
            break

        match parser(current_src):
            case Success() as s:
                r_val.append(s.value)
            case Failure() as f:
                return f
        current_src = next_frozen(current_src)

    if not allow_empty_sequence and len(r_val) == 0:
        return failure(f"Empty sequence", src)

    return success(tuple(r_val), current_src)


def repeat_sequence[T, SRC](
    end_token_predicate: Callable[[SRC], bool],
    parser: Parser[T, SRC],
    *,
    allow_empty_sequence: bool = False,
    allow_eof: bool = False,
) -> Parser[tuple[T, ...], SRC]:
    return lambda src: _repeat_sequence_raw(
        src, end_token_predicate, parser, allow_empty_sequence, allow_eof
    )


def repeat_sequence_bracketed[T, SRC](
    beginning_token_predicate: Callable[[SRC], bool],
    end_token_predicate: Callable[[SRC], bool],
    parser: Parser[T, SRC],
    *,
    allow_empty_sequence: bool = False,
    allow_eof: bool = False,
) -> Parser[tuple[T, ...], SRC]:
    return chain(
        return_second_arg,
        match_one(
            beginning_token_predicate, error_msg=f"No opening symbol for sequence"
        ),
        repeat_sequence(
            end_token_predicate,
            parser,
            allow_empty_sequence=allow_empty_sequence,
            allow_eof=allow_eof,
        ),
    )


def _optional_raw[T, SRC](
    src: FrozenIter[SRC],
    option: Parser[T, SRC],
) -> ParseResult[T | None, SRC]:

    match option(src):
        case Success(v, src):
            return Success(v, src)
        case Failure() as f:
            return success(None, f.src_iter)


def optional[T, SRC](
    option: Parser[T, SRC],
) -> Parser[T | None, SRC]:
    return lambda src: _optional_raw(src, option)


def _negate_raw[T, SRC](
    src: FrozenIter[SRC],
    parser: Parser[T, SRC],
    msg: str | Callable[[Success[T, SRC]], str],
    value: T,
) -> ParseResult[T, SRC]:
    match parser(src):
        case Success() as s:
            return failure(msg(s) if callable(msg) else msg, src)
        case Failure():
            return success(value, src)


def negate[T, SRC](
    parser: Parser[T, SRC],
    msg: (
        str | Callable[[Success[T, SRC]], str]
    ) = lambda s: f"Should not have succeeded: {s}",
    value: T = None,
) -> Parser[T, SRC]:
    return lambda src: _negate_raw(src, parser, msg, value)


# Atomic parser


def _match_one_raw[SRC](
    src: FrozenIter[SRC],
    predicate: Callable[[SRC], bool],
    error_msg: str | Callable[[SRC], str] = lambda t: f"Token {t} did not match",
) -> ParseResult[SRC, SRC]:
    match get(src):
        case None:
            return eof_failure(src)
        case t if predicate(t):
            return success(t, next_frozen(src))
        case t:
            return failure(error_msg(t) if callable(error_msg) else error_msg, src)


def match_one[SRC](
    predicate: Callable[[SRC], bool],
    *,
    error_msg: str | Callable[[SRC], str] = lambda t: f"Token {t} did not match",
) -> Parser[SRC, SRC]:
    return lambda src: _match_one_raw(src, predicate, error_msg)


# Util


def empty_string_match[SRC](src: FrozenIter[SRC]) -> Success[None, SRC]:
    return success(None, src)


def eof_failure[SRC](src: FrozenIter[SRC]) -> Failure[SRC]:
    return failure(f"Unexpcted end of input", src)


def return_second_arg[T](_: object, second: T) -> T:
    return second
