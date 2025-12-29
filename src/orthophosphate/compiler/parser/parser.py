import typing

from ..tokenizer.token import IndentType, Token, TokenType
from .parse_state import ParseState, err
from .parse_tree import (
    ConcreteApplicationNode,
    ConcreteExprNode,
    ListLiteralNode,
    ProgramNode,
    PyLiteralNode,
)


def parse(tokens: tuple[Token, ...]) -> ProgramNode:
    """
    Accepts a tuple of tokens from the tokenizer

    Returns the root node of an abstract syntax tree
    representing the program specified

    This method is the entry point for this module
    """
    state = ParseState(tokens)

    require_token(state, TokenType.PUNC, "file_start")
    if check_token(state, TokenType.NEWLINE, ""):
        state.next_token()

    return ProgramNode(_parse_expr_sequence(state, TokenType.PUNC, "EOF"))


"""
All of the parse_* methods below take the current ParseState
and return the parse tree node that the tokens at the cursor represent.

Parse methods can mutate the state
of the passed ParseState object. They call other parse
methods according to what elements of the language
should appear next.
"""


def _parse_expr(state: ParseState) -> ConcreteExprNode:
    t = state.next_token()
    match t.type, t.value:

        case (TokenType.NAME, n) | (TokenType.PUNC, "$" as n) if not check_token(
            state, TokenType.PUNC, "("
        ):
            inline_args = _parse_inline_expr_sequence(state, TokenType.NEWLINE, "")

            indented_args: tuple[ConcreteExprNode, ...] = tuple()
            if check_token(state, TokenType.INDENT_DEDENT, IndentType.INDENT):
                state.next_token()
                indented_args = _parse_expr_sequence(
                    state, TokenType.INDENT_DEDENT, IndentType.DEDENT
                )

            return ConcreteApplicationNode(n, inline_args + indented_args)

        case _:
            state.reset()
            r_val = _parse_inline_expr(state)
            require_token(state, TokenType.NEWLINE, "")
            return r_val


def _parse_inline_expr(state: ParseState) -> ConcreteExprNode:
    t = state.next_token()
    # print(f"Parsing inline expr on {t}")
    match t.type, t.value:

        case (
            (TokenType.NAME, n)
            | (TokenType.PUNC, "$" as n)
            | (TokenType.PUNC, "->" as n)
        ):
            if check_token(state, TokenType.PUNC, "("):
                state.next_token()
                return ConcreteApplicationNode(
                    n, _parse_inline_expr_sequence(state, TokenType.PUNC, ")")
                )
            # A variable is a function of zero arguments
            return ConcreteApplicationNode(n, tuple())

        case (TokenType.INT, x):
            return PyLiteralNode(int, int(x))

        case (TokenType.STR, s):
            return PyLiteralNode(str, s)

        case (TokenType.PUNC, "["):
            return ListLiteralNode(
                _parse_inline_expr_sequence(state, TokenType.PUNC, "]")
            )

        case (TokenType.PUNC, "{"):
            return ListLiteralNode(
                _parse_inline_expr_sequence(state, TokenType.PUNC, "}")
            )

        case _:
            err(state)


# def parse_id(state: ParseState) -> str:
#     return state.next_token().require_name().value


def _parse_expr_sequence(
    state: ParseState, terminator_type: TokenType, terminator_value: str
) -> tuple[ConcreteExprNode, ...]:

    return _parse_sequence(state, terminator_type, terminator_value, _parse_expr)


def _parse_inline_expr_sequence(
    state: ParseState, terminator_type: TokenType, terminator_value: str
) -> tuple[ConcreteExprNode, ...]:

    return _parse_sequence(state, terminator_type, terminator_value, _parse_inline_expr)


def _parse_sequence[T](
    state: ParseState,
    end_type: TokenType,
    end_value: str,
    parse_function: typing.Callable[[ParseState], T],
) -> tuple[T, ...]:
    """
    Makes a flat tuple of nodes from the tokens
    until it hits the specfied end token or EOF

    Expects cursor to be on the beginning of the
    first sequence element (not a delimiter, if there
    is one)
    """

    # print(f"Starting on {state.peek()}; is this the first element?")

    output: list[T] = []

    while state.cursor_in_range() and not check_token(state, end_type, end_value):
        output.append(parse_function(state))

    # print(f"Detected end token: {state.peek()}")

    state.next_token()  # Skip end token

    return tuple(output)


def check_token(state: ParseState, type: TokenType, value: str) -> bool:
    """
    Returns whether the next token matches the
    provided type and value. Does not consume tokens.
    """
    next = state.peek()
    if next is None:
        return False
    return (next.type, next.value) == (type, value)


def require_token(state: ParseState, type: TokenType, value: str) -> None:
    """
    Throws an error if the next token doesn't
    match. Consumes the next token if it does.
    """
    if check_token(state, type, value):
        state.skip()
    else:
        err(state, f"Expected token type {type} with value {value})")


def is_semicolon(state: ParseState) -> bool:
    """
    Checks whether the next token is a semicolon
    without consuming it
    """
    return check_token(state, TokenType.PUNC, ";")


def require_semicolon(state: ParseState) -> None:
    """
    Throws an error if there is not a semicolon at the
    current cursor position
    """
    require_token(state, TokenType.PUNC, ";")


if __name__ == "__main__":
    pass
    # It is prefered that tests be run from compiler.py,
    # because that module can import token and other
    # modules that are cousins to parser.py
