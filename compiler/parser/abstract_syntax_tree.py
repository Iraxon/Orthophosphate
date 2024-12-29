import enum
import typing

class NodeType(enum.StrEnum):
    """
    The types of nodes in the abstract syntax tree
    """
    
    LITERAL_VALUE = enum.auto()
    NAME = enum.auto()

    ASSIGN_OPERATOR = enum.auto()
    OPERATOR = enum.auto()

    STATEMENT = enum.auto()
    GROUPED_EXPRESSION = enum.auto()
    PREFIX_EXPRESSION = enum.auto()
    DECLARATION = enum.auto()

    BLOCK = enum.auto()

    WHILE = enum.auto()
    FUNC_DEF = enum.auto()
    TICK_FUNC_DEF = enum.auto()
    NAMESPACE = enum.auto()
    TAG_DEF = enum.auto()

    ROOT = enum.auto()

class Node(typing.NamedTuple):
    """
    A node in the abstract syntax tree
    """
    type: NodeType = NodeType.ROOT

    value: typing.Optional[any] = None

    data_type: str = "untyped"

    def reorder_expr(self) -> "Node":
        """
        Specifically for type=GROUPED EXPRESSION
        Nodes, this function reorders the operands
        to use prefix notation; e.g.

        3 + 5 --> + 3 5

        The resulting prefix expression is also properly
        typed
        """
        if self.type != NodeType.GROUPED_EXPRESSION:
            raise TypeError(f"reorder_expr() called on non-expr or an expr that has already been ordered")
        if len(self.value) != 3 and len(self.value) != 1:
            raise ValueError(
                f"Expression has {len(self.value)} elements, not 3 or 1; anatomy:\n"
                f"{self}"
            )
        
        VALID_OPERANDS = (
            NodeType.PREFIX_EXPRESSION,
            NodeType.LITERAL_VALUE,
            NodeType.NAME,
            NodeType.DECLARATION
        )

        match self.value:
            case (operand,):
                # If this expression has only one thing in it,
                # then we just return it instead of bothering with
                # expressions
                return operand
            case (operand1, operator, operand2) if (
                operand1.type in VALID_OPERANDS
                and operator.type in (NodeType.OPERATOR, NodeType.ASSIGN_OPERATOR)
                and operand2.type in VALID_OPERANDS
            ):
                if not (
                    # If it is not the case that either the data types are the same,
                    # the phrase is an assignment, or one or both of the two elements
                    # is of wildcard type, then this is a type error and not allowed
                    operand1.data_type == operand2.data_type
                    or
                    operator.type == NodeType.ASSIGN_OPERATOR
                    or
                    (
                        operand1.data_type == "*"
                        or
                        operand2.data_type == "*"
                    )
                ):
                    raise TypeError(
                        f"Incompatible types for operands:\n"
                        f"{operand1}\n"
                        f"and\n"
                        f"{operand2}\n"
                    )
                return Node(
                    type=NodeType.PREFIX_EXPRESSION,
                    value=(
                        operator,
                        operand1,
                        operand2
                    ),
                    # If the first operand is of wildcard type, then use the second operaand's
                    # type for the whole expression.
                    # This means that wildcard only gets propagated up if both operands are wildcards.
                    data_type=operand1.data_type if operand1.data_type != "*" else operand2.data_type
                )
            case _:
                raise ValueError(
                    f"No match for (operand, operator, operand) or (operand,):\n"
                    f"{self.render()}"
                )

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
            f"{"" if pre == "" else'═'}{self.type.name}{': ' + self.data_type if self.data_type != "untyped" else ''}\n"
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
        print(f"{node_type.name} = {node_type.value}")