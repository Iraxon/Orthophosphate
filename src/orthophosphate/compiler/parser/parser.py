import typing

from ..tokenizer.token import Token, TokenType
from .parse_tree import (
    ApplicationNode,
    DefNode,
    ExprNode,
    ListLiteralNode,
    ProgramNode,
    PyLiteralNode,
)
from .parse_state import ParseState, err


def parse(tokens: tuple[Token, ...]) -> ProgramNode:
    """
    Accepts a tuple of tokens from the tokenizer

    Returns the root node of an abstract syntax tree
    representing the program specified

    This method is the entry point for this module
    """
    state = ParseState(tokens)
    require_token(state, Token(TokenType.PUNC, "file_start"))
    return ProgramNode(_parse_expr_sequence(state, "EOF"))


"""
All of the parse_* methods below take the current ParseState
and return the parse tree node that the tokens at the cursor represent.

Parse methods can mutate the state
of the passed ParseState object. They call other parse
methods according to what elements of the language
should appear next.
"""


def _parse_expr(state: ParseState) -> ExprNode:
    t = state.next_token()
    match t:

        case (TokenType.PUNC, "$"):
            return parse_def(state)

        case (TokenType.NAME, n):
            if state.peek() == (TokenType.PUNC, "("):
                state.next_token()
                return ApplicationNode(n, _parse_expr_sequence(state, ")"))
            return ApplicationNode(n, tuple())

        case (TokenType.INT, x):
            return PyLiteralNode(int, int(x))

        case (TokenType.STR, s):
            return PyLiteralNode(str, s)

        case (TokenType.PUNC, "["):
            return ListLiteralNode(_parse_expr_sequence(state, "]"))

        case (TokenType.PUNC, "{"):
            return ListLiteralNode(_parse_expr_sequence(state, "}"))

        case _:
            err(state)


def parse_def(state: ParseState) -> DefNode:

    name = state.next_token().require_name().value

    require_token(state, Token(TokenType.PUNC, "["))
    params = _parse_sequence(state, Token(TokenType.PUNC, "]"), parse_id)
    require_token(state, Token(TokenType.PUNC, "["))
    param_types = _parse_expr_sequence(state, "]")

    param_map = {
        params[i]: param_types[i] for i in range(min(len(params), len(param_types)))
    }

    require_token(state, Token(TokenType.PUNC, "->"))
    return_type = _parse_expr(state)

    body = _parse_expr(state)

    return DefNode(name, param_map, return_type, body)


def parse_id(state: ParseState) -> str:
    return state.next_token().require_name().value


def _parse_str(state: ParseState) -> str:
    t = state.next_token()
    match t:
        case (TokenType.STR, s):
            return s
        case _:
            err(state)


def _parse_expr_sequence(state: ParseState, terminator: str) -> tuple[ExprNode, ...]:
    return _parse_sequence(state, Token(TokenType.PUNC, terminator), _parse_expr)


def _parse_sequence[T](
    state: ParseState,
    end_token: Token,
    parse_function: typing.Callable[[ParseState], T],
) -> tuple[T, ...]:
    """
    Makes a flat tuple of nodes from the tokens
    until it hits the specfied end token or EOF
    """
    node_list: list[T] = []

    # While not out of file and it is not the case
    # that the current token matches end_token

    while state.cursor_in_range():

        # Check for end tokens
        next_token = state.peek()
        if next_token is not None and next_token == end_token:
            state.skip()  # Skip closing token
            break

        next_node = parse_function(state)
        node_list.append(next_node)
    return tuple(node_list)


def check_token(state: ParseState, t: Token) -> bool:
    """
    Returns whether the next token equals the
    provided one. Does not consume tokens.
    """
    return state.peek() == t


def require_token(state: ParseState, t: Token) -> None:
    """
    Throws an error if the next token doesn't
    equal t. Consumes the next token if it does.
    """
    if check_token(state, t):
        state.skip()
    else:
        err(state, f"Expected token {t}")


def is_semicolon(state: ParseState) -> bool:
    """
    Checks whether the next token is a semicolon
    without consuming it
    """
    return check_token(state, Token(TokenType.PUNC, ";"))


def require_semicolon(state: ParseState) -> None:
    """
    Throws an error if there is not a semicolon at the
    current cursor position
    """
    require_token(state, Token(TokenType.PUNC, ";"))


if __name__ == "__main__":
    pass
    # It is prefered that tests be run from compiler.py,
    # because that module can import token and other
    # modules that are cousins to parser.py
