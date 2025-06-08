import enum
import typing

class NodeType(enum.StrEnum):
    """
    The types of nodes in the abstract syntax tree
    """

    LITERAL_VALUE = enum.auto()
    CONCAT = enum.auto()
    NAME = enum.auto()
    PLACEHOLDER = enum.auto() # It gets filled in the post-parser

    ASSIGNMENT = enum.auto()
    OPERATION = enum.auto()

    STATEMENT = enum.auto()
    EXPRESSION = enum.auto()
    DECLARATION = enum.auto()
    OBJ_DEF = enum.auto()

    TARGET_SELECTOR = enum.auto()

    SCOREBOARD_OPERATION = enum.auto()
    CONSTANT_SCORE = enum.auto()
    SCOREBOARD_RESET = enum.auto()

    CALL = enum.auto()

    BLOCK = enum.auto()
    AFTER = enum.auto()
    WHILE = enum.auto()

    NAMESPACE = enum.auto()

    FUNC_DEF = enum.auto()
    TICK_FUNC_DEF = enum.auto()
    TAG_DEF = enum.auto()

    ROOT = enum.auto()

class Node(typing.NamedTuple):
    """
    A node in the abstract syntax tree
    """
    type: NodeType = NodeType.ROOT

    value: tuple["Node", ...] | str | int | bool | None = None

    data_type: str = "untyped"

    def check_statement(self) -> "Node | None":
        """
        This function removes empty or one-element statements
        """
        assert isinstance(self.value, tuple)
        if len(self.value) == 0 or (len(self.value) == 1 and self.value[0] is None):
            return None
        if len(self.value) == 1 and self.value[0].type in (
            NodeType.NAMESPACE, NodeType.FUNC_DEF, NodeType.TICK_FUNC_DEF, NodeType.TAG_DEF
        ):
            return self.value[0]
        return self

    def __repr__(self) -> str:
        return f"Node(type={self.type}, value={self.value})"

    def __str__(self) -> str:
        return self.render()

    def render(self, pre="") -> str:
        """
        Provides a nice readable string
        rep of the AST with nesting

        This function is recursive and
        dangerous to the sanity of anyone
        who works on it
        """
        line_tuple = tuple(
            element.render(pre + ("║ " if i < len(self.value) - 1 else "  "))
            if isinstance(element, Node)
            else "═ " + str(element)
            for i, element in enumerate(self.value)
        ) if isinstance(self.value, tuple) else ("═ " + str(self.value),)

        return (
            f"{"" if pre == "" else'═'}{self.type}{': ' + self.data_type if self.data_type != "untyped" else ''}\n"
            + "".join(
                    tuple(
                        f"{pre}╠{element}\n"
                        if i < len(line_tuple) - 1
                        else f"{pre}╚{element}"
                        for i, element in enumerate(line_tuple)
                    )
                )
        )

if __name__ == "__main__":
    for node_type in NodeType:
        print(f"{node_type.name} = {node_type.value}; {node_type == node_type.value}")
