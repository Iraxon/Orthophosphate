import typing
import enum

class NodeType(enum.Enum):
    """
    The types of nodes in the abstract syntax tree
    """
    
    STRING_LITERAL = enum.auto()
    INT_LITERAL = enum.auto()
    MCFUNCTION_LITERAL = enum.auto()
    NAME = enum.auto()

    ASSIGN_OPERATOR = enum.auto()
    OPERATOR = enum.auto()

    STATEMENT = enum.auto()
    GROUPED_EXPRESSION = enum.auto()
    PREFIX_EXPRESSION = enum.auto()

    BLOCK = enum.auto()

    WHILE = enum.auto()
    FUNC_DEF = enum.auto()

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
            NodeType.INT_LITERAL,
            NodeType.STRING_LITERAL,
            NodeType.MCFUNCTION_LITERAL,
            NodeType.NAME
        )

        match self.value:
            case (operand,):
                return operand
            case (operand1, operator, operand2) if (
                operand1.type in VALID_OPERANDS
                and operator.type in (NodeType.OPERATOR, NodeType.ASSIGN_OPERATOR)
                and operand2.type in VALID_OPERANDS
            ):
                if not (
                    operand1.data_type == operand2.data_type
                    or
                    operand1.type == "name" and operator.type == NodeType.ASSIGN_OPERATOR
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
                value=int(t.value),
                data_type="int"
            )
        case ("string", s):
            node = Node(
                type=NodeType.STRING_LITERAL,
                value=t.value,
                data_type="str"
            )
        case ("literal", x):
            node = Node(
                type=NodeType.MCFUNCTION_LITERAL,
                value=t.value,
                data_type="cmd"
            )
        case ("name", n):
            node = Node(
                type=NodeType.NAME,
                value=t.value,
                data_type= (
                    (
                        tokens[_cursor - 2].value
                        if (
                            tokens[_cursor - 1].type == "op" and tokens[_cursor - 1].value == "@"
                        )
                        else "*" # If we can't find a type assignment we make this a wildcard type,
                        # which is compatible with everything else
                    )
                    if _cursor - 2 >= 0
                    else "*" # We DEFINITELY do that if looking back would give an index error
                )
            )
        case ("op", o):
            if "=" in o and o != "==" and o != "!=":
                node = Node(
                    type=NodeType.ASSIGN_OPERATOR,
                    value=t.value
                )
            else:
                node = Node(
                    type=NodeType.OPERATOR,
                    value=t.value
                )
        case ("keyword", "while"):
            value, new_cursor = _resolve_finite_tuple(
                tokens=tokens,
                cursor=_cursor,
                description=(
                    (NodeType.INT_LITERAL, NodeType.PREFIX_EXPRESSION),
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
                    (NodeType.NAME,),
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
            pre_node = Node(
                type=NodeType.GROUPED_EXPRESSION,
                value=value,
                data_type="*"
            )
            node = pre_node.reorder_expr()
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