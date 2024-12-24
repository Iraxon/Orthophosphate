import typing
# from ..tokenizer import token as Token
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

    def __repr__(self) -> str:
        return f"Node(type={self.type}, value={self.value})"

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
    STATEMENT_BODY = enum.auto()
    OTHER = enum.auto()

def _parse_individual(tokens: list, cursor: int=0, seek_multiple=False, end_token_type=None, end_token_value=None) -> typing.Union[Node, tuple[Node]]:
    """
    Private, recursive function for processing each token individually;
    tokens and cursor are self-explanatory; if seek_multiple is true,
    this function will return a tuple of nodes instead of one; the end_token
    is used with seek_multiple to determine when the series of tokens is over

    Returns tuple [Node | tuple[Node]], cursor: int
    """

    if seek_multiple:
        nodes = []
        # Make a tuple of all the nodes ahead until either end of file or
        # the end token
        new_cursor = cursor + 1
        while new_cursor < len(tokens) and not (tokens[new_cursor].type == end_token_type and tokens[new_cursor].value == end_token_value):
            next_token, new_cursor = _parse_individual(tokens, new_cursor)
            nodes.append(next_token)
        return tuple(nodes), new_cursor + 1
    
    t = tokens[cursor]

    default_return = True

    match t.type:
        case "start" | "statementEnding":
            node = Node(
                type=NodeType.STATEMENT,
                value=_parse_individual(tokens, cursor + 1, seek_multiple=True)
            )
        case "int":
            node = Node(
                type=NodeType.INT,
                value=int(t.value)
            )
        case "statementEnding":
            raise ValueError(
                f"Unexpected end token: "
                f"{tokens[cursor - 1] if cursor > 0 else ""} "
                f">>> {t} <<< "
                f"{tokens[cursor + 1] if cursor < len(tokens) - 1 else ""}"
            )
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
    if default_return:
        return node, cursor + 1

def parse(tokens: list) -> Node:
    """
    Accepts a list of tokens from the tokenizer

    Returns the root node of an abstract syntax tree
    representing the program specified
    """

    root_value, cursor = _parse_individual(tokens, 0, seek_multiple=True, end_token_type="end_of_file")
    # "end_of_file" is not a token type, so it will never match. This is fine,
    # because seek_multiple will also stop at the end of the file if there is no end token.

    ast = Node(
        type=NodeType.ROOT,
        value=root_value
    )
    return ast

if __name__ == "__main__":


    class VirtualToken(typing.NamedTuple):
        type: str
        value: str



    print(
        parse(
            [
                VirtualToken("start", ""),
                VirtualToken("literal", "say hello world"),
            ]
        )
    )
    # It is preferred that tests be run from compiler.py,
    # because that module can import token and other
    # modules that are cousins to parser.py