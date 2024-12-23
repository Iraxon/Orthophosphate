import typing
import Token
import enum

class NodeType(enum.Enum):
    """
    The types of nodes in the abstract syntax tree
    """
    ROOT = enum.auto()

class AbstractSyntaxTree(typing.NamedTuple):
    type: NodeType = NodeType.ROOT
    body: list["AbstractSyntaxTree"] = []

def parse(tokens: list[Token.Token]) -> AbstractSyntaxTree:
    pass