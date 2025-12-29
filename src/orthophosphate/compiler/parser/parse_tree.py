from dataclasses import dataclass
from typing import cast, override

type ParseTreeNode = ProgramNode | ConcreteExprNode
"""
A node on the parse tree
"""


@dataclass(frozen=True)
class _DisplaysAsNode:
    """
    Only exists to override __str__ for all the nodes

    Use type alias ParseTreeNode for literally all practical purposes
    """

    @override
    def __str__(self) -> str:
        return _display_node(cast(ParseTreeNode, self))


@dataclass(frozen=True)
class ProgramNode(_DisplaysAsNode):
    content: "tuple[ConcreteExprNode, ...]"


type ConcreteExprNode = ConcreteApplicationNode | LiteralNode


@dataclass(frozen=True)
class ConcreteApplicationNode(_DisplaysAsNode):
    """
    Function application node storing the
    str name for the function; AbstractApplicationNode
    will point directly to the function definition
    """

    id: str
    args: tuple[ConcreteExprNode, ...]


type LiteralNode = PyLiteralNode[int] | PyLiteralNode[str] | ListLiteralNode


@dataclass(frozen=True)
class PyLiteralNode[T: (int, str)](_DisplaysAsNode):
    type: type[T]
    value: T


@dataclass(frozen=True)
class ListLiteralNode(_DisplaysAsNode):
    content: "tuple[ConcreteExprNode, ...]"


def _render_contents(
    node: ParseTreeNode | str,
) -> tuple[str, tuple[ParseTreeNode | str, ...]]:
    """
    Provides the header and children that a
    Node should display when rendered (see below
    _display_node function)
    """
    match node:

        case str(s):
            return (s, tuple())

        case ProgramNode() as p:
            return ("Program", p.content)

        case ConcreteApplicationNode() as a:
            return (a.id, a.args)

        case PyLiteralNode() as p:
            return (f"Literal {str(p.type)} {str(p.value)}", tuple())

        case ListLiteralNode() as l:
            return ("List Literal", l.content)


def _display_node(node: ParseTreeNode | str, pre="") -> str:
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
