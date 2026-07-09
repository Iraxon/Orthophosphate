from abc import abstractmethod
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from functools import cache
from typing import Protocol, Self, cast, override

from .term_graph import (
    FunctionCallTerm,
    IntTerm,
    ProgramTerm,
    ReferenceTerm,
    StrTerm,
    Term,
)

type AnyExprNode = AnyMultilineExpr | AnyInlineExpr | InlineListLiteral
"""
A node on the parse tree that stands for a real expression
"""


@dataclass(frozen=True)
class ParseTreeNode(Protocol):
    """
    Only exists to override __str__ for all the nodes

    Use type alias ParseTreeNode for literally all practical purposes
    """

    @override
    def __str__(self) -> str:
        return _inline_display(cast(ParseTreeNode, self))

    @abstractmethod
    def get_render_contents(self) -> "tuple[str, Sequence[ParseTreeNode | str]]":
        raise NotImplementedError

    @abstractmethod
    def to_term(self) -> Term:
        raise NotImplementedError

    def inline_display(self) -> str:
        head, args = self.get_render_contents()
        if len(args) > 0:
            args_display = " ".join(
                arg if isinstance(arg, str) else arg.inline_display() for arg in args
            )
            return f"{head}({args_display})"
        return head


@dataclass(frozen=True)
class Program(ParseTreeNode):
    content: "Sequence[AnyMultilineExpr]"

    @override
    def get_render_contents(self):
        return ("program", self.content)

    @override
    def to_term(self):
        return ProgramTerm(tuple(item.to_term() for item in self.content))


@dataclass(frozen=True)
class AnyMultilineExpr(ParseTreeNode): ...


@dataclass(frozen=True)
class MultilineExpr(AnyMultilineExpr):
    inline_args: "Sequence[AnyInlineExpr]"
    args: Sequence[AnyMultilineExpr]

    @override
    def get_render_contents(self):
        combined = (*self.inline_args, r"/n", *self.args)
        return (_inline_display(combined[0]), combined[1:])

    @override
    def to_term(self):
        combined = (*self.inline_args, *self.args)
        combined_terms = tuple(item.to_term() for item in combined)
        return FunctionCallTerm.of_tuple(combined_terms)


@dataclass(frozen=True)
class ListLiteral(AnyMultilineExpr):
    content: Sequence[AnyMultilineExpr]

    @override
    def get_render_contents(self):
        return ("list", self.content)

    @override
    def inline_display(self) -> str:
        return f"[{" ".join(arg.inline_display() for arg in self.content)}]"

    @override
    def to_term(self):
        return FunctionCallTerm(
            ReferenceTerm("opo4:list"), tuple(item.to_term() for item in self.content)
        )


@dataclass(frozen=True)
class AnyInlineExpr(ParseTreeNode): ...


@dataclass(frozen=True)
class InlineExpr(AnyInlineExpr):
    head: AnyInlineExpr
    contents: Sequence[AnyInlineExpr]

    @override
    def get_render_contents(self):
        return (self.head.inline_display(), self.contents)

    @override
    def to_term(self):
        return FunctionCallTerm(
            self.head.to_term(), tuple(item.to_term() for item in self.contents)
        )


@dataclass(frozen=True)
class SimpleLiteralOrVarNode(AnyInlineExpr):
    value: int | str

    @override
    def get_render_contents(self):
        return (str(self.value), ())


@dataclass(frozen=True)
class Name(SimpleLiteralOrVarNode):
    value: str

    @override
    def to_term(self):
        return ReferenceTerm(self.value)


@dataclass(frozen=True)
class IntLiteral(SimpleLiteralOrVarNode):
    value: int

    @override
    def to_term(self):
        return IntTerm(self.value)


@dataclass(frozen=True)
class StrLiteral(SimpleLiteralOrVarNode):
    value: str

    @override
    def to_term(self):
        return StrTerm(self.value)


@dataclass(frozen=True)
class InlineListLiteral(AnyInlineExpr):
    content: Sequence[AnyInlineExpr]

    @override
    def get_render_contents(self):
        return ("list", self.content)

    @override
    def inline_display(self) -> str:
        return f"[{" ".join(arg.inline_display() for arg in self.content)}]"

    @override
    def to_term(self):
        return FunctionCallTerm(
            ReferenceTerm("opo4:list"), tuple(item.to_term() for item in self.content)
        )


@dataclass(frozen=True)
class AnyNodeSeq(ParseTreeNode):

    content: ParseTreeNode
    next: Self | None

    @abstractmethod
    def __iter__(self) -> Iterator[ParseTreeNode]:
        raise NotImplementedError

    @override
    def get_render_contents(self) -> tuple[str, tuple[ParseTreeNode, ...]]:
        return ("<>", tuple(self))

    @override
    def inline_display(self) -> str:
        return f"<{" ".join(arg.inline_display() for arg in iter(self))}>"


@cache
def _render_contents(
    node: ParseTreeNode | str,
) -> tuple[str, Sequence[ParseTreeNode | str]]:
    """
    Provides the header and children that a
    Node should display when rendered (see below
    _display_node function)
    """
    if isinstance(node, str):
        return (node, ())
    return node.get_render_contents()


@cache
def _display_node(node: ParseTreeNode | str, pre: str = "") -> str:
    """
    Provides a nice readable string
    rep of the Node with nesting

    This function is recursive and
    dangerous to the sanity of anyone
    who works on it
    """
    header, children = _render_contents(node)

    render_contents: tuple[str, ...] = tuple(
        _display_node(child, pre + ("║ " if i < len(children) - 1 else "  "))
        for i, child in enumerate(children)
    )

    return f"{'' if pre == '' else'═'} {header}\n" + "".join(
        (
            f"{pre}╠{element}"  # Normal case
            if i < len(render_contents) - 1
            else f"{pre}╚{element}"  # Last element
        )
        for i, element in enumerate(render_contents)
    )


@cache
def _inline_display(node: ParseTreeNode | str) -> str:
    """
    Produces an inline representation (e.g. "head(arg1 arg2 arg3)")

    Does not handle indentation
    """

    if isinstance(node, str):
        return node
    return node.inline_display()
