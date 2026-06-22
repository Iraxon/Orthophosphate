from collections.abc import Callable, Iterable
from functools import cache
from itertools import chain as iterchain

from ..tokenizer.token import IndentType, Token, TokenType
from ..utils.frozeniter import FrozenIter, display, frozeniter_of_iter
from .parse_tree import (
    ConcreteApplicationNode,
    ConcreteExprNode,
    ListLiteralNode,
    LiteralNode,
    ProgramNode,
    PyLiteralNode,
)
from .result import (
    ErrorMessageProvider,
    Failure,
    Parser,
    ParseResult,
    Success,
    alternative,
    chain2,
    chain3,
    chain_map,
    match_one,
    optional,
    repeat_sequence,
    return_first_arg,
    return_second_arg,
)


def parse_program(tokens: Iterable[Token]) -> ProgramNode:

    tokens_frozen = frozeniter_of_iter(tokens)

    result = chain2(
        lambda _, expr_tuple: ProgramNode(expr_tuple),
        match_token(
            TokenType.PUNC, "file_start", lambda src: f"File start token not added at {display(src)}"
        ),
        repeat_sequence(
            parse_expr,
            error_msg=lambda src: f"Failed to parse top-level expressions at {display(src)}",
        ),
        # match_token(
        #     TokenType.PUNC, "EOF", lambda src: "Expression parsing failed before EOF"
        # ),
    )(tokens_frozen)

    match result:
        case Success(v, continuation_src) as s:
            if s.continuation_src is not None:
                raise ValueError(
                    f"Parsed:\n{v}\n with leftover unparsed tokens:\n{continuation_src}"
                )
            return v
        case Failure(errors):
            error_lines = "\n".join(f"    {error}" for error in errors)
            raise ValueError(f"Failed to parse:\n{error_lines}\n")


@cache
def parse_expr(
    tokens: FrozenIter[Token],
) -> ParseResult[ConcreteExprNode, Token]:

    print(f"Parsing expr: {display(tokens)}")

    return alternative(
        lambda src: f"Failed to parse expression at {display(src)}",
        chain2(
            _combine_expr,
            _parse_inline_expr_terms,
            optional(_parse_nested_expr_terms),
        ),
    )(tokens)


def _combine_expr(
    inline: tuple[ConcreteExprNode, ...],
    nested: tuple[ConcreteExprNode, ...] | None,
) -> ConcreteApplicationNode:
    return ConcreteApplicationNode.of(
        *(expr for expr in iterchain(inline, nested if nested is not None else tuple()))
    )


def _parse_inline_expr_terms(
    tokens: FrozenIter[Token],
) -> ParseResult[tuple[ConcreteExprNode, ...], Token]:
    return chain2(
        return_first_arg,
        repeat_sequence(
            parse_inline_expr,
            error_msg=lambda src: f"Failed to parse unparenthesized args at {display(src)}",
            allow_empty_sequence=False,
        ),
        match_token(TokenType.NEWLINE),
    )(tokens)


def _parse_nested_expr_terms(
    tokens: FrozenIter[Token],
) -> ParseResult[tuple[ConcreteExprNode, ...], Token]:
    return chain3(
        return_second_arg,
        match_token(
            TokenType.INDENT_DEDENT,
            IndentType.INDENT,
            lambda src: f"No indent at {display(src)}",
        ),
        repeat_sequence(
            parse_expr,
            lambda src: f"Failed to parse indented args at {display(src)}",
            allow_empty_sequence=False,
        ),
        match_token(
            TokenType.INDENT_DEDENT,
            IndentType.DEDENT,
            lambda src: f"No dedent at {display(src)}",
        ),
    )(tokens)


@cache
def parse_inline_expr(
    tokens: FrozenIter[Token],
) -> ParseResult[ConcreteExprNode, Token]:
    print(f"Parsing inline expr: {display(tokens)}")
    return alternative(
        lambda src: f"Failed to parse inline expression at {display(src)}",
        chain2(
            lambda name, sequence: ConcreteApplicationNode(
                name, sequence if sequence is not None else tuple()
            ),
            parse_name,
            optional(
                chain3(
                    return_second_arg,
                    match_token(
                        TokenType.PUNC,
                        "(",
                        lambda src: f"No opening parenthesis at {display(src)}",
                    ),
                    repeat_sequence(
                        parse_inline_expr,
                        error_msg=lambda src: f"Failed to parse parenthesized args at {display(src)}",
                        allow_empty_sequence=False,
                    ),
                    match_token(
                        TokenType.PUNC,
                        ")",
                        lambda src: f"No closing parenthesis at {display(src)}",
                    ),
                )
            ),
        ),
        parse_literal,
    )(tokens)


def parse_name(tokens: FrozenIter[Token]) -> ParseResult[str, Token]:
    return chain_map(match_token(TokenType.NAME), _get_value)(tokens)


def _get_value(t: Token) -> str:
    return t.value


def parse_literal(tokens: FrozenIter[Token]) -> ParseResult[LiteralNode, Token]:
    return alternative(
        lambda src: f"Failed to parse literal at {display(src)}",
        chain_map(
            match_token(TokenType.INT, None), lambda x: PyLiteralNode(int, int(x.value))
        ),
        chain_map(
            match_token(TokenType.STR, None), lambda s: PyLiteralNode(str, s.value)
        ),
        chain_map(
            alternative(
                lambda src: f"Failed to parse list literal at {display(src)}",
                chain3(
                    return_second_arg,
                    match_token(TokenType.PUNC, "["),
                    repeat_sequence(
                        parse_expr,
                        error_msg=lambda src: f"{display(src)}",
                        allow_empty_sequence=True,
                    ),
                    match_token(
                        TokenType.PUNC,
                        "]",
                        lambda src: f"Expected ']' at {display(src)}",
                    ),
                ),
                chain3(
                    return_second_arg,
                    match_token(TokenType.PUNC, "{"),
                    repeat_sequence(
                        parse_expr,
                        error_msg=lambda src: f"{display(src)}",
                        allow_empty_sequence=True,
                    ),
                    match_token(
                        TokenType.PUNC,
                        "}",
                        lambda src: f"Expected '}}' at {display(src)}",
                    ),
                ),
            ),
            lambda exprs: ListLiteralNode(exprs),
        ),
    )(tokens)


# Token utils


def match_token(
    type: TokenType,
    value: str | None = None,
    error_msg: ErrorMessageProvider[Token] | None = None,
) -> Parser[Token, Token]:
    return match_one(
        match_token_predicate(type, value),
        error_msg=(
            error_msg
            if error_msg is not None
            else (
                lambda src: f"Failed to match token {str(Token(type, value if value is not None else "*"))} at {display(src)}"
            )
        ),
    )


def match_token_predicate(
    type: TokenType, value: str | None = None
) -> Callable[[Token], bool]:
    def pred(t: Token) -> bool:
        return t.type == type and (value is None or t.value == value)

    return pred
