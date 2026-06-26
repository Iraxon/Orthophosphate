from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Any, Never, Self

from ..tokenizer.token import IndentType, Token, TokenType
from .parse_tree2 import (
    AnyInlineExpr,
    AnyMultilineExpr,
    InlineExpr,
    ParenthesizedInlineExprSeq,
    IntLiteral,
    ListLiteral,
    MultilineExpr,
    NewlineInlineExprSeq,
    MultilineExprSeq,
    Name,
    ParseTreeNode,
    StrLiteral,
)

type IntermediaryParseResult = Token | ParseTreeNode


@dataclass(frozen=True)
class ParseStack:
    previous: Self | None
    current: IntermediaryParseResult

    def pop(self) -> tuple[IntermediaryParseResult, Self | None]:
        return self.current, self.previous

    def push(self, result: IntermediaryParseResult):
        return type(self)(self, result)

    shift = push


def reduce_literals(
    literal: IntermediaryParseResult,
    *_: Any,
) -> IntermediaryParseResult | None:
    if isinstance(literal, Token):
        if literal.type is TokenType.INT:
            return IntLiteral(int(literal.value))
        if literal.type is TokenType.STR:
            return StrLiteral(literal.value)
        if literal.type is TokenType.NAME:
            return Name(literal.value)
    return None


def reduce_inline_expr_seq(
    first: IntermediaryParseResult,
    second: IntermediaryParseResult,
    *_: Any,
) -> IntermediaryParseResult | None:

    if isinstance(first, AnyInlineExpr):
        if isinstance(second, ParenthesizedInlineExprSeq) or isinstance(
            second, NewlineInlineExprSeq
        ):
            return second.prepend(first)
        elif isinstance(second, Token):
            if second.matches(TokenType.PUNC, ")"):
                return ParenthesizedInlineExprSeq(first, None)
            elif second.type is TokenType.NEWLINE:
                return NewlineInlineExprSeq(first, None)
    return None


def reduce_multiline_expr_seq(
    first: IntermediaryParseResult, second: IntermediaryParseResult, *_: Any
) -> IntermediaryParseResult | None:
    if isinstance(first, AnyMultilineExpr):
        if isinstance(second, MultilineExprSeq):
            return second.prepend(first)
        elif isinstance(second, Token) and (
            second.matches(TokenType.PUNC, "]")
            or second.matches(TokenType.INDENT_DEDENT, IndentType.DEDENT)
        ):
            return MultilineExprSeq(first, None)
    return None


def reduce_list(
    left_paren: IntermediaryParseResult,
    contents: IntermediaryParseResult,
    *_: Any,
) -> IntermediaryParseResult | None:
    if (
        isinstance(left_paren, Token)
        and left_paren.matches(TokenType.PUNC, "[")
        and isinstance(contents, MultilineExprSeq)
    ):
        return ListLiteral(tuple(contents))
    return None


def reduce_inline_expr(
    first: IntermediaryParseResult,
    left_paren: IntermediaryParseResult,
    args: IntermediaryParseResult,
    *_: Any,
) -> IntermediaryParseResult | None:
    if (
        isinstance(first, AnyInlineExpr)
        and isinstance(left_paren, Token)
        and left_paren.matches(TokenType.PUNC, "(")
        and isinstance(args, ParenthesizedInlineExprSeq)
    ):
        return InlineExpr(first, tuple(args))
    return None


def reduce_expr_with_indented_args(
    inline_args: IntermediaryParseResult,
    indent: IntermediaryParseResult,
    indented_args: IntermediaryParseResult,
    *_: Any,
) -> IntermediaryParseResult | None:
    if (
        isinstance(inline_args, ParenthesizedInlineExprSeq)
        and isinstance(indent, Token)
        and indent.matches(TokenType.INDENT_DEDENT, IndentType.INDENT)
        and isinstance(indented_args, MultilineExprSeq)
    ):
        return MultilineExpr(tuple(inline_args), tuple(indented_args))
    return None


reductions: Sequence[
    tuple[
        Callable[
            [*tuple[IntermediaryParseResult, ...]], IntermediaryParseResult | None
        ],
        int,
    ]
] = (
    (reduce_literals, 1),
    (reduce_inline_expr_seq, 2),
    (reduce_list, 3),
    (reduce_inline_expr, 4),
    (reduce_multiline_expr_seq, 2),
    (reduce_expr_with_indented_args, 5),
)


def apply_reductions(
    parse_stack: ParseStack,
) -> ParseStack | None:

    for reduction, length in reductions:
        if len(parse_stack) >= length:
            last = parse_stack[-length:]
            result = reduction(*last)
            if result is not None:
                return (*parse_stack[:-length], result)

    return None


def display_intermediate_result(r: IntermediaryParseResult) -> str:
    if isinstance(r, Sequence) and not isinstance(r, str):
        return f"<{" ".join(map(str, r))}>"
    return str(r)


def parse(src: Iterable[Token]) -> Never:
    parse_stack: ParseStack = tuple()
    print(parse_stack)
    for token in src:
        parse_stack = parse_stack.shift(token)
        if len(s := " : ".join(map(display_intermediate_result, parse_stack))) < 400:
            print(s)
        while True:
            inner_parse_stack = apply_reductions(parse_stack)
            if inner_parse_stack is None:
                break
            else:
                if (
                    len(
                        s := " : ".join(
                            map(display_intermediate_result, inner_parse_stack)
                        )
                    )
                    < 400
                ):
                    print(s)
                parse_stack = inner_parse_stack
    raise NotImplementedError(f"See the so-far-implemented output above traceback.")
