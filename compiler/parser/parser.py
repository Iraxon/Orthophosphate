import typing
import compiler.tokenizer.Token as Token
import enum

class NodeType(enum.Enum):
    """
    The types of nodes in the abstract syntax tree
    """
    ROOT = enum.auto()

    STRING_LITERAL = enum.auto()
    MCFUNCTION_LITERAL = enum.auto()

    INT = enum.auto()

    STATEMENT = enum.auto()

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

class ParserTarget(enum.Enum):
    STATEMENT_START = enum.auto()
    OTHER = enum.auto()

def _parse_individual(tokens: list[Token.Token], cursor: int, target=ParserTarget.STATEMENT, nodes = tuple()) -> Node:
    """
    Private, recursive function for processing each token individually
    """

    t = tokens[cursor]

    if target == ParserTarget.STATEMENT_START:
        if t.type == "start":
            node = _parse_individual(tokens, cursor + 1, target=ParserTarget.STATEMENT)
        else:
            raise ValueError(f"Token {t} begins statement instead of start token")
    match t.type:
        case "start" | "statementEnding":
            node_value = []
            while t.type != "statementEnding":
                node_value.append(_parse_individual(tokens, cursor))
        case "number":
            node = Node(
                type=NodeType.INT,
                value=int(t.value)
            )
        case "statementEnding":
            pass
        case "string":
            node = Node(
                type=NodeType.STRING_LITERAL,
                value = t.value
            )
        case "literal":
            node = Node(
                type=NodeType.MCFUNCTION_LITERAL,
                value=t.value
            )
        case _:
            raise ValueError(f"Token {t} unknown to parser")
    if len(nodes) == 0:
        return node
    return nodes

def parse(tokens: list[Token.Token]) -> Node:
    """
    Accepts a list of tokens from the tokenizer

    Returns the root node of an abstract syntax tree
    representing the program specified
    """

    ast = Node(
        type=NodeType.ROOT,
        # We do not care about the tokens themselves; we only
        # want to run _parse_individual the right number of times.
        # Therefore, we use _ and subsequently ignore it
        value=root_value
    )
    return ast

if __name__ == "__main__":
    from ..tokenizer import Tokenizer
    parse([
        Tokenizer.tokenize(
            """
            :say hello:;
            123;
            "hello";
            """
        ),
    ])