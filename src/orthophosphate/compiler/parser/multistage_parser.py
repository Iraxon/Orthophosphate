from abc import abstractmethod
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from typing import Never, Protocol, Self, override

from ..tokenizer.token import IndentType, Token, TokenType
from .parse_tree2 import (
    AnyInlineExpr,
    AnyMultilineExpr,
    ListLiteral,
    Program,
    SimpleLiteralOrVarNode,
    InlineExpr,
    IntLiteral,
    InlineListLiteral,
    MultilineExpr,
    Name,
    ParseTreeNode,
    StrLiteral,
)

type IntermediaryParseResult = Token | ParseTreeNode


@dataclass(frozen=True)
class PrependList[T]:

    item: T
    next: Self | None

    def __iter__(self) -> Iterator[T]:
        current = self
        while current is not None:
            yield current.item
            current = current.next


@dataclass(frozen=True)
class ParseStack:
    previous: Self | None
    item: IntermediaryParseResult

    def pop(self) -> tuple[IntermediaryParseResult, Self | None]:
        return self.item, self.previous

    def push(self, result: IntermediaryParseResult):
        return type(self)(self, result)

    shift = push

    def __iter__(self) -> Iterator[IntermediaryParseResult]:
        def reverse_iterator() -> Iterator[IntermediaryParseResult]:
            current = self
            while current is not None:
                yield current.item
                current = current.previous

        return reversed(tuple(reverse_iterator()))

    def __len__(self) -> int:
        l = 0
        current = self
        while current is not None:
            l += 1
            current = current.previous
        return l


class ReductionRule(Protocol):
    @staticmethod
    @abstractmethod
    def apply(stack: ParseStack) -> ParseStack | None:
        raise NotImplementedError


def chain_2_rules(
    first: type[ReductionRule], second: type[ReductionRule]
) -> type[ReductionRule]:
    class ChainedRule(ReductionRule):
        @staticmethod
        @override
        def apply(stack: ParseStack) -> ParseStack | None:
            r1 = first.apply(stack)
            if r1 is None:
                return second.apply(stack)
            return r1

    return ChainedRule


def chain_rules(*rules: type[ReductionRule]) -> type[ReductionRule]:
    """
    Two or more args are required.
    """
    current = rules[0]
    for arg in rules[1:]:
        current = chain_2_rules(current, arg)
    return current


class ReduceLiterals(ReductionRule):
    @staticmethod
    @override
    def apply(stack: ParseStack) -> ParseStack | None:
        last, chopped_stack = stack.pop()
        new_last: SimpleLiteralOrVarNode

        if isinstance(last, Token):
            if last.type is TokenType.INT:
                new_last = IntLiteral(int(last.value))
            elif last.type is TokenType.STR:
                new_last = StrLiteral(last.value)
            elif last.type is TokenType.NAME:
                new_last = Name(last.value)
            else:
                return None
            return ParseStack(chopped_stack, new_last)

        return None


class ReduceListLiteral(ReductionRule):
    @staticmethod
    @override
    def apply(stack: ParseStack) -> ParseStack | None:
        last, current_stack = stack.pop()

        if (
            isinstance(last, Token)
            and last.matches(TokenType.PUNC, "]")
            and current_stack is not None
        ):
            items: PrependList[AnyMultilineExpr] | None = None
            while True:
                if current_stack is None:
                    return None
                current_item, current_stack = current_stack.pop()

                if isinstance(current_item, Token) and current_item.matches(
                    TokenType.PUNC, "["
                ):
                    break
                elif isinstance(current_item, AnyMultilineExpr):
                    items = PrependList(current_item, items)
                else:
                    return None

            return ParseStack(
                current_stack,
                ListLiteral(tuple(items) if items is not None else ()),
            )
        return None


class ReduceInlineListLiteral(ReductionRule):
    @staticmethod
    @override
    def apply(stack: ParseStack) -> ParseStack | None:
        last, current_stack = stack.pop()

        if (
            isinstance(last, Token)
            and last.matches(TokenType.PUNC, "]")
            and current_stack is not None
        ):
            items: PrependList[AnyInlineExpr] | None = None
            while True:
                if current_stack is None:
                    return None
                current_item, current_stack = current_stack.pop()
                if isinstance(current_item, Token) and current_item.matches(
                    TokenType.PUNC, "["
                ):
                    break
                elif isinstance(current_item, AnyInlineExpr):
                    items = PrependList(current_item, items)
                else:
                    return None

            return ParseStack(
                current_stack,
                InlineListLiteral(tuple(items) if items is not None else ()),
            )
        return None


class ReduceInlineExpr(ReductionRule):
    @staticmethod
    @override
    def apply(stack: ParseStack) -> ParseStack | None:
        last, current_stack = stack.pop()

        if (
            isinstance(last, Token)
            and last.matches(TokenType.PUNC, ")")
            and current_stack is not None
        ):
            items: PrependList[AnyInlineExpr] | None = None
            while True:
                if current_stack is None:
                    return None
                current_item, current_stack = current_stack.pop()
                if isinstance(current_item, Token) and current_item.matches(
                    TokenType.PUNC, "("
                ):
                    break
                elif isinstance(current_item, AnyInlineExpr):
                    items = PrependList(current_item, items)
                else:
                    return None
            if current_stack is None:
                return None
            head, current_stack = current_stack.pop()
            if isinstance(head, AnyInlineExpr):
                return ParseStack(
                    current_stack,
                    InlineExpr(head, tuple(items) if items is not None else ()),
                )
        return None


class ReduceSimpleExpr(ReductionRule):

    @override
    @staticmethod
    def apply(stack: ParseStack) -> ParseStack | None:
        last, current_stack = stack.pop()

        if (
            isinstance(last, Token)
            and last.type is TokenType.NEWLINE
            and current_stack is not None
        ):
            items: PrependList[AnyInlineExpr] | None = None
            inner_current_stack = current_stack
            while True:
                if inner_current_stack is None:
                    break
                current_item, inner_current_stack = inner_current_stack.pop()
                if isinstance(current_item, AnyInlineExpr):
                    items = PrependList(current_item, items)
                    current_stack = inner_current_stack
                else:
                    break

            if items is None:
                return None

            return ParseStack(
                current_stack,
                MultilineExpr(tuple(items), ()),
            )
        return None


class ReduceMultilineExpr(ReductionRule):
    @staticmethod
    @override
    def apply(stack: ParseStack) -> ParseStack | None:
        last, current_stack = stack.pop()

        if (
            isinstance(last, Token)
            and last.matches(TokenType.INDENT_DEDENT, IndentType.DEDENT)
            and current_stack is not None
        ):
            items: PrependList[AnyMultilineExpr] | None = None
            while True:
                if current_stack is None:
                    return None
                current_item, current_stack = current_stack.pop()
                if isinstance(current_item, Token) and current_item.matches(
                    TokenType.INDENT_DEDENT, IndentType.INDENT
                ):
                    break
                elif isinstance(current_item, AnyMultilineExpr):
                    items = PrependList(current_item, items)
                else:
                    return None

            if current_stack is None:
                return None

            head, current_stack = current_stack.pop()
            if isinstance(head, MultilineExpr) and len(head.args) == 0:
                return ParseStack(
                    current_stack,
                    (
                        MultilineExpr(head.inline_args, tuple(items))
                        if items is not None
                        else head
                    ),
                )
        return None

class ReduceProgram(ReductionRule):
    @staticmethod
    @override
    def apply(stack: ParseStack) -> ParseStack | None:
        last, current_stack = stack.pop()

        if (
            isinstance(last, Token)
            and last.matches(TokenType.PUNC, "EOF")
            and current_stack is not None
        ):
            items: PrependList[AnyMultilineExpr] | None = None
            while True:
                if current_stack is None:
                    return None
                current_item, current_stack = current_stack.pop()
                if isinstance(current_item, Token) and current_item.matches(
                    TokenType.PUNC, "file_start"
                ):
                    break
                elif isinstance(current_item, AnyMultilineExpr):
                    items = PrependList(current_item, items)
                else:
                    return None

            return ParseStack(
                current_stack,
                Program(tuple(items) if items is not None else ()),
            )
        return None

reductions = chain_rules(
    ReduceLiterals,
    ReduceInlineExpr,
    ReduceInlineListLiteral,
    ReduceSimpleExpr,
    ReduceMultilineExpr,
    ReduceListLiteral,
    ReduceProgram
)


def display_intermediate_result(r: IntermediaryParseResult) -> str:
    if isinstance(r, Sequence) and not isinstance(r, str):
        return f"<{" ".join(map(str, r))}>"
    return str(r)


def display_parse_stack(stack: ParseStack, max: int | None = None) -> None:
    if max is None:
        max = 10**10
    full_display = " : ".join(display_intermediate_result(result) for result in stack)
    if len(full_display) <= max:
        print(full_display)
    else:
        print(f"{full_display[:max]} [...] ")
    type_display = " : ".join(type(result).__name__ for result in stack)
    print(f"   (Types) {type_display}\n")


def parse(src: Iterable[Token]) -> Never:
    parse_stack: ParseStack | None = None
    print(parse_stack)
    for token in src:

        parse_stack = ParseStack(parse_stack, token)
        display_parse_stack(parse_stack)

        inner_stack = parse_stack

        while True:
            inner_stack = reductions.apply(inner_stack)
            if inner_stack is None:
                break
            else:
                parse_stack = inner_stack
                display_parse_stack(parse_stack)

    print(len(parse_stack) if parse_stack is not None else 0)

    raise NotImplementedError(f"See the so-far-implemented output above traceback.")
