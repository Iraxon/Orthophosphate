import typing
import Token
import enum

class NodeType(enum.Enum):
    """
    The types of nodes in the abstract syntax tree
    """
    ROOT = enum.auto()
    MCFUNCTION_LITERAL = enum.auto()

    SCOREBOARD_OPERATION = enum.auto()
    SCORE = enum.auto()
    SCOREBOARD_ENTITY = enum.auto()
    SCOREBOARD_OBJECTIVE = enum.auto()
    SCOREBOARD_CONSTANT = enum.auto()

class Node(typing.NamedTuple):
    """
    A node in the abstract syntax tree
    """
    type: NodeType = NodeType.ROOT

    value: typing.Optional[any] = None
    # The data type of self.value depends on
    # the value of self.type

# Example AST for:
#
# | /say hello
# | @a <<NS>>.test = 1;
# | /execute as @e at @s if score @s test matches 1.. run say my score is positive!

EXAMPLE_AST = Node(
    type=NodeType.ROOT,
    value=(
        Node(
            type=NodeType.MCFUNCTION_LITERAL,
            value="say hello"
        ),
        Node(
            type=NodeType.SCOREBOARD_OPERATION,
            value=(
                Node(
                    type=NodeType.SCORE,
                    value=(
                        Node(
                            type=NodeType.SCOREBOARD_ENTITY,
                            value="@a"
                        ),
                        Node(
                            type=NodeType.SCOREBOARD_OBJECTIVE,
                            value="<<NS>>.test"
                        ),
                    )
                ),
                Node(
                    type=NodeType.SCOREBOARD_OPERATION,
                    value="="
                ),
                Node(
                    type=NodeType.SCOREBOARD_CONSTANT,
                    value="1"
                )
            )
        ),
        Node(
            type=NodeType.MCFUNCTION_LITERAL,
            value="execute as @e at @s if score @s test matches 1.. run say my score is positive!"
        ),
    )
)

def _parse_individual(t: Token.Token) -> Node:
    """
    Private function: accepts a single token
    and returns a Node representing it and
    applicable sub-tokens;

    this function is recursive
    """

    match t.type:
        case "Literal":
            return Node(
                type=NodeType.MCFUNCTION_LITERAL,
                value=t.value
            )
        case _: # else case
            raise ValueError(f"Token {t} unknown to parser")

def parse(tokens: list[Token.Token]) -> Node:
    """
    Accepts a list of tokens from the tokenizer

    Returns the root node of an abstract syntax tree
    representing the program specified
    """

    ast = Node(
        type=NodeType.ROOT,
        value=tuple(
            _parse_individual(t) for t in tokens
        )
    )