from collections.abc import Mapping
from dataclasses import dataclass

@dataclass(frozen=True)
class ProgramNode:
    content: "tuple[ExprNode, ...]"


type ExprNode = ApplicationNode | LiteralNode | DefNode


@dataclass(frozen=True)
class ApplicationNode:
    id: str
    args: tuple[ExprNode, ...]


@dataclass(frozen=True)
class DefNode:
    id: str
    args: Mapping[str, ExprNode]
    """
    Params for keys, types for values
    """
    return_type: ExprNode
    body: ExprNode


type LiteralNode = PyLiteralNode[int] | PyLiteralNode[str] | ListLiteralNode


@dataclass(frozen=True)
class PyLiteralNode[T: (int, str)]:
    type: type[T]
    value: T


@dataclass(frozen=True)
class ListLiteralNode:
    content: "tuple[ExprNode, ...]"
