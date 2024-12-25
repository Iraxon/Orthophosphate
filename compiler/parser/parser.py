import typing
import enum

class NodeType(enum.Enum):
    """
    The types of nodes in the abstract syntax tree
    """
    ROOT = enum.auto()

    STATEMENT = enum.auto()
    GROUPED_EXPRESSION = enum.auto()
    NAME = enum.auto()

    STRING_LITERAL = enum.auto()
    INT_LITERAL = enum.auto()
    MCFUNCTION_LITERAL = enum.auto()

    BLOCK = enum.auto()

    WHILE = enum.auto()

    FUNC_DEF = enum.auto()

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
            f"{"" if pre == "" else'═'}{self.type.name}\n"
            + "".join(
                    tuple(
                        f"{pre}╠{element}\n"
                        if i < len(line_tuple) - 1
                        else f"{pre}╚{element}"
                        for i, element in enumerate(line_tuple)
                    )
                )
        )

class VirtualToken(typing.NamedTuple):
    """
    A fake token that provides the necessary
    interface for the parser to understand
    tokenizer.Token objects
    """
    type: str
    value: str

def _resolve_finite_tuple(tokens: list, cursor: int, description: tuple[tuple[str]] = None, count: int = -1):
    """
    Makes a flat tuple of nodes from the tokens
    until the tuple contains the specified count and
    type of nodes

    The description should be a tuple of tuples of NodeTypes
    where each inner tupple contains all node types allowed
    in that position or the string "*" if any should
    be permitted

    If a count is specified, the description will be auto-intialized
    to accept the correct number of tokens of any type
    """

    if count != -1:
        description = tuple(("*",) for _ in range(count))
    
    iterating_cursor = cursor + 1 # Skip opening token
    node_list = []
    counter = 0

    while iterating_cursor < len(tokens):
        if len(node_list) >= len(description):
            break
        next_node, iterating_cursor = parse(tokens, _cursor=iterating_cursor)

        if next_node.type not in description[counter] and description[counter] != ("*",):
            raise ValueError(f"Expected Node of a type in {description[counter]}; got {repr(next_node)}")
        
        node_list.append(next_node)
        counter += 1
    
    return tuple(node_list), iterating_cursor # No +1 because no closing token to skip
        

def _resolve_node_tuple(tokens: list, cursor: int, end_token):
    """
    Makes a flat tuple of nodes from the tokens
    until it hits the specfied end token or EOF
    """
    iterating_cursor = cursor + 1 # Skip opening token
    next_token = tokens[iterating_cursor]
    node_list = []

    # While not out of file and it is not the case
    # that the current token matches end_token

    while iterating_cursor < len(tokens):
        # print(f"cursor at {iterating_cursor}-- RNT(), selecting {tokens[iterating_cursor]}")

        # Check for end tokens
        if next_token.type == end_token.type and (next_token.value == end_token.value or end_token.value == "*"):
            break

        next_node, iterating_cursor = parse(tokens, _cursor=iterating_cursor)
        node_list.append(next_node)
        next_token = tokens[iterating_cursor]

    return tuple(node_list), iterating_cursor + 1 # Skip closing token

def parse(tokens: list, _cursor: int = 0) -> Node:
    """
    Accepts a list of tokens from the tokenizer

    Returns the root node of an abstract syntax tree
    representing the program specified

    This function is recursive, both itself and
    mutually with _resolve_node_tuple; it uses the private cursor parameter
    in the recursion calls; that parameter should not be set
    by outsider callers

    @reutrn Node [outside calls]

    @return (Node, cursor) [recursive calls]
    """
    # print(f"cursor at {_cursor}-- parse(), selecting {tokens[_cursor]}")
    t = tokens[_cursor]

    # inits root node
    if _cursor == 0:
        return Node(
            type=NodeType.ROOT,
            value=_resolve_node_tuple(
                tokens=tokens,
                cursor=0,
                end_token=VirtualToken("punc", "EOF")
            )[0]
        )
    
    # The recursive sorcery begins here

    # This value might be changed by a case block;
    # if it is not, then we default to cursor + 1 
    new_cursor = _cursor + 1

    match (t.type, t.value):
        case ("punc", "start"):
            value, new_cursor = _resolve_node_tuple(
                tokens=tokens,
                cursor=_cursor,
                end_token=VirtualToken("punc", ";")
            )
            node = Node(
                type=NodeType.STATEMENT,
                value=value
            )
        case ("int", n):
            node = Node(
                type=NodeType.INT_LITERAL,
                value=int(t.value)
            )
        case ("string", s):
            node = Node(
                type=NodeType.STRING_LITERAL,
                value=t.value
            )
        case ("literal", x):
            node = Node(
                type=NodeType.MCFUNCTION_LITERAL,
                value=t.value
            )
        case ("name", n):
            node = Node(
                type=NodeType.NAME,
                value=t.value
            )
        case ("keyword", "while"):
            value, new_cursor = _resolve_finite_tuple(
                tokens=tokens,
                cursor=_cursor,
                description=(
                    (NodeType.GROUPED_EXPRESSION,),
                    (NodeType.BLOCK,),
                )
            )
            node = Node(
                type=NodeType.WHILE,
                value=value
            )
            pass
        case ("keyword", "func"):
            value, new_cursor = _resolve_finite_tuple(
                tokens=tokens,
                cursor=_cursor,
                description=(
                    (NodeType.NAME,), # Needs to be changed to a function header or something
                    (NodeType.BLOCK,),
                )
            )
            node = Node(
                type=NodeType.FUNC_DEF,
                value=value
            )
        case ("punc", "{"):
            value, new_cursor = _resolve_node_tuple(
                tokens=tokens,
                cursor=_cursor,
                end_token=VirtualToken("punc", "}")
            )
            node = Node(
                type=NodeType.BLOCK,
                value=value
            )
        case ("punc", "("):
            value, new_cursor = _resolve_node_tuple(
                tokens=tokens,
                cursor=_cursor,
                end_token=VirtualToken("punc", ")")
            )
            node = Node(
                type=NodeType.GROUPED_EXPRESSION,
                value=value
            )
        case ("punc", ";") | ("punc", "}") | ("punc", ")") | ("punc", "EOF"):
            raise ValueError(
                f"Found unexpected closing token:\n"
                + "".join(tuple(f"\t{tokens[_cursor - n] if _cursor - n >= 0 else ''}\n" for n in range(0, -11, -1)))
                + f"\t{t} <<< HERE\n"
                + f"\t{tokens[_cursor + 1] if _cursor + 1 < len(tokens) else ''}\n"
                + f"\t{tokens[_cursor + 2] if _cursor + 2 < len(tokens) else ''}\n"
            )
        case _:
            raise ValueError(f"Token {t} unknown to parser")

    return node, new_cursor

if __name__ == "__main__":
    pass
    # It is prefered that tests be run from compiler.py,
    # because that module can import token and other
    # modules that are cousins to parser.py