import typing
import compiler.tokenizer.Token as Token
import enum

class NodeType(enum.Enum):
    """
    The types of nodes in the abstract syntax tree
    """
    ROOT = enum.auto()
    MCFUNCTION_LITERAL = enum.auto()

    INT = enum.auto()

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

def parse(tokens: list[Token.Token]) -> Node:
    """
    Accepts a list of tokens from the tokenizer

    Returns the root node of an abstract syntax tree
    representing the program specified
    """

    cursor = 0
    # A cursor is used because some tokens
    # may need to be processed as a group

    def _parse_individual(tokens) -> Node:
        """
        Private function: accepts a single token
        and returns a Node representing it and
        applicable sub-tokens;

        this function is recursive;

        this function ACCESSES and MUTATES the
        cursor variable from the parent function.
        """

        t = tokens[cursor]

        match t.type:
            case "number":
                cursor += 1
                return Node(
                    type=NodeType.INT,
                    value=int(t.value)
                )
            case "statementEnding":
                cursor += 1
            case "string":
                cursor += 1
            case "literal":
                cursor += 1
                return Node(
                    type=NodeType.MCFUNCTION_LITERAL,
                    value=t.value
                )
            case _:
                raise ValueError(f"Token {t} unknown to parser")

    ast = Node(
        type=NodeType.ROOT,
        # We do not care about the tokens themselves; we only
        # want to run _parse_individual the right number of times.
        # Therefore, we use _ and subsequently ignore it
        value=tuple(
            _parse_individual(tokens) for _ in tokens
        )
    )