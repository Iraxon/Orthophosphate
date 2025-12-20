from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast, override

type ParseTreeNode = ProgramNode | ExprNode
"""
A node on the parse tree
"""


@dataclass(frozen=True)
class _AbstractParseTreeNode:
    """
    Only exists to override __str__ for all the nodes

    Use type alias ParseTreeNode for literally all practical purposes
    """

    @override
    def __str__(self) -> str:
        return _display_node(cast(ParseTreeNode, self))


@dataclass(frozen=True)
class ProgramNode(_AbstractParseTreeNode):
    content: "tuple[ExprNode, ...]"


type ExprNode = ApplicationNode | LiteralNode | DefNode


@dataclass(frozen=True)
class ApplicationNode(_AbstractParseTreeNode):
    id: str
    args: tuple[ExprNode, ...]


@dataclass(frozen=True)
class DefNode(_AbstractParseTreeNode):
    id: str
    params: Mapping[str, ExprNode]
    """
    Params for keys, types for values
    """
    return_type: ExprNode
    body: ExprNode

    def _str_args(self) -> str:
        """
        Str rep of the params:
        [p1 p2 ...]
        """
        return "[" + " ".join(self.params.keys()) + "]"


type LiteralNode = PyLiteralNode[int] | PyLiteralNode[str] | ListLiteralNode


@dataclass(frozen=True)
class PyLiteralNode[T: (int, str)](_AbstractParseTreeNode):
    type: type[T]
    value: T


@dataclass(frozen=True)
class ListLiteralNode(_AbstractParseTreeNode):
    content: "tuple[ExprNode, ...]"


def _children(node: ParseTreeNode) -> tuple[ParseTreeNode | str, ...]:
    """
    Provides that which the Node should display
    underneath itself when rendered (see below)
    """
    match node:
        case ProgramNode() as p:
            return p.content
        case ApplicationNode() as a:
            return (a.id,) + a.args
        case DefNode() as d:
            return (d.id, d._str_args(), *d.params.values(), d.return_type, d.body)
        case PyLiteralNode() as p:
            return (str(p.type), str(p.value))
        case ListLiteralNode() as l:
            return l.content


def _display_node(node: ParseTreeNode, pre="") -> str:
    """
    Provides a nice readable string
    rep of the AST node with nesting

    This function is recursive and
    dangerous to the sanity of anyone
    who works on it
    """
    children = _children(node)

    render_contents: tuple[str, ...] = tuple(
        (
            _display_node(child, pre + ("║ " if i < len(children) - 1 else "  "))
            if not isinstance(child, str)
            else f"═ {child}"
        )
        for i, child in enumerate(children)
    )
    return f"{'' if pre == '' else'═'} {node.__class__.__name__}\n" + "".join(
        tuple(
            (
                f"{pre}╠{element}\n"
                if i < len(render_contents) - 1
                else f"{pre}╚{element}"
            )
            for i, element in enumerate(render_contents)
        )
    )
