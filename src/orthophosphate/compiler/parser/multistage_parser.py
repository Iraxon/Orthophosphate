from collections.abc import Iterable

from .parse_tree import LiteralNode, PyLiteralNode

from ..tokenizer.token import Token, TokenType


def parse_one_token_literal(src: Iterable[Token]) -> tuple[Token | LiteralNode, ...]:
    def process_one(token: Token) -> Token | LiteralNode:
        match token.type:
            case TokenType.STR:
                return PyLiteralNode(str, token.value)
            case TokenType.INT:
                return PyLiteralNode(int, int(token.value))
            case _:
                return token

    return tuple(process_one(token) for token in src)


def parse(src: Iterable[Token]) -> ...:
    result = parse_one_token_literal(src)
    print(result)
    raise NotImplementedError(f"See the so-far-implemented output above traceback.")
