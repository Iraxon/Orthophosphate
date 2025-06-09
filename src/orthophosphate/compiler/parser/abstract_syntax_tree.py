from enum import StrEnum, auto
import typing

class NodeType(StrEnum):
    """
    The types of nodes in the abstract syntax tree
    """

    LITERAL_VALUE = auto()
    CONCAT = auto()
    NAME = auto()
    PLACEHOLDER = auto() # It gets filled in the post-parser

    ASSIGNMENT = auto()
    OPERATION = auto()

    STATEMENT = auto()
    EXPRESSION = auto()
    DECLARATION = auto()
    OBJ_DEF = auto()

    TARGET_SELECTOR = auto()

    SCOREBOARD_OPERATION = auto()
    CONSTANT_SCORE = auto()
    SCOREBOARD_RESET = auto()

    CALL = auto()

    BLOCK = auto()
    AFTER = auto()
    WHILE = auto()

    NAMESPACE = auto()

    FUNC_DEF = auto()
    TICK_FUNC_DEF = auto()
    TAG_DEF = auto()

    ROOT = auto()

    EMPTY = auto()

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

        render_contents = (
            ("═ " + str(self.value),)
            if not isinstance(self.value, tuple)
            else tuple(
                value_tuple_node.render(pre + ("║ " if i < len(self.value) - 1 else "  "))
                # if isinstance(element, Node) # UNCOMMENT IF NON-NODE TUPLE ELEMENTS BECOME ALLOWED
                # else "═ " + str(element)
                for i, value_tuple_node in enumerate(self.value)
            )
        )

        return (
            f"{"" if pre == "" else'═'}{self.type}{': ' + self.data_type if self.data_type != "untyped" else ''}\n"
            + "".join(
                    tuple(
                        f"{pre}╠{element}\n"
                        if i < len(render_contents) - 1
                        else f"{pre}╚{element}"
                        for i, element in enumerate(render_contents)
                    )
                )
        )

if __name__ == "__main__":
    for node_type in NodeType:
        print(f"{node_type.name} = {node_type.value}; {node_type == node_type.value}")
