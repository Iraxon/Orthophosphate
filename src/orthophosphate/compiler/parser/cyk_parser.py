from collections.abc import Iterable

from .parse_tree import LiteralNode, PyLiteralNode

from ..tokenizer.token import Token, TokenType


def parse_one_token_literal(src: Iterable[Token]) -> tuple[Token | LiteralNode, ...]:
    def process_one(token: Token) -> Token | LiteralNode:
        match token.type:
            case TokenType.INT:
                return PyLiteralNode(int, int(token.value))
            case _:
                raise ValueError(token)

    return tuple(process_one(token) for token in src)


def parse(src: Iterable[Token]):
    pass
