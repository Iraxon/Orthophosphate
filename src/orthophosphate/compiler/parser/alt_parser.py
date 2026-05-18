from collections.abc import Iterable
from itertools import chain as iterchain
from typing import cast

from ..tokenizer.token import IndentType, Token, TokenType
from ..utils.frozeniter import FrozenIter, frozeniter_of_iter
from .parse_tree import (
    ConcreteApplicationNode,
    ConcreteExprNode,
    LiteralNode,
    ProgramNode,
)
from .result import (
    Failure,
    ParseResult,
    Success,
    chain,
    map_result,
    match_one,
    optional,
    repeat_sequence,
)


def parse_program(tokens: Iterable[Token]) -> ProgramNode:

    tokens_frozen = frozeniter_of_iter(tokens)

    result = map_result(
        repeat_sequence(lambda _: False, parse_expr, allow_eof=True)(tokens_frozen),
        lambda expr_tuple: ProgramNode(expr_tuple),
    )

    match result:
        case Success() as s:
            return s.value
        case Failure() as f:
            error_lines = "\n".join(f"    {error}" for error in f.errors)
            raise ValueError(f"Failed to parse:\n{error_lines}")


def _parse_inline_expr_terms(
    tokens: FrozenIter[Token],
) -> ParseResult[tuple[ConcreteExprNode, ...], Token]:
    return repeat_sequence(
        lambda token: token.type == TokenType.NEWLINE,
        parse_inline_expr,
    )(tokens)


def _parse_nested_expr_terms(
    tokens: FrozenIter[Token],
) -> ParseResult[tuple[ConcreteExprNode, ...] | None, Token]:
    return optional(
        chain(
            # Discard indent; we just need to confirm it's there, not do anything with it
            lambda indent_token, exprs: exprs,
            match_one(
                lambda token: token.matches(TokenType.INDENT_DEDENT, IndentType.INDENT)
            ),
            repeat_sequence(
                lambda token: token.matches(TokenType.INDENT_DEDENT, IndentType.DEDENT),
                parse_expr,
            ),
        ),
    )(tokens)


def parse_expr(
    tokens: FrozenIter[Token],
) -> ParseResult[ConcreteExprNode, Token]:

    return chain(
        lambda inline, nested: ConcreteApplicationNode.of(
            *(
                expr
                for expr in iterchain(inline, nested if nested is not None else tuple())
            )
        ),
        _parse_inline_expr_terms,
        _parse_nested_expr_terms,
    )(tokens)


def parse_inline_expr(
    tokens: FrozenIter[Token],
) -> ParseResult[ConcreteExprNode, Token]: ...


def parse_literal(tokens: FrozenIter[Token]) -> ParseResult[LiteralNode, Token]: ...


# Combinators and atomic parsers
