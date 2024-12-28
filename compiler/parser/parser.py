import typing
from .abstract_syntax_tree import NodeType
from .abstract_syntax_tree import Node

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
                type=NodeType.LITERAL_VALUE,
                value=int(t.value),
                data_type="int"
            )
        case ("string", s):
            node = Node(
                type=NodeType.LITERAL_VALUE,
                value=t.value,
                data_type="str"
            )
        case ("literal", x):
            node = Node(
                type=NodeType.LITERAL_VALUE,
                value=t.value,
                data_type="cmd"
            )
        case ("name", n):
            node = Node(
                type=NodeType.NAME,
                value=t.value,
                data_type= "*"
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
        case ("keyword", "namespace"):
            value, new_cursor = _resolve_finite_tuple(
                tokens=tokens,
                cursor=_cursor,
                description=(
                    (NodeType.NAME,),
                    (NodeType.BLOCK,)
                )
            )
            node = Node(
                type=NodeType.NAMESPACE,
                value=value
            )
        case ("keyword", "tag"):
            value, new_cursor = _resolve_finite_tuple(
                tokens=tokens,
                cursor=_cursor,
                description=(
                    (NodeType.NAME,),
                    (NodeType.NAME,),
                    (NodeType.BLOCK,),
                )
            )
            node = Node(
                type=NodeType.TAG_DEF,
                value=value
            )
        case ("keyword", "let"):
            value, new_cursor = _resolve_finite_tuple(
                tokens=tokens,
                cursor=_cursor,
                description=(
                    (NodeType.NAME,),
                    (NodeType.NAME,)
                )
            )
            node = Node(
                type=NodeType.DECLARATION,
                value=value,
                data_type=(value[0].value) # THe first of the two names after "let" specifies the data type; the other
                # one is the name of the new variable
            )
        case ("keyword", "while"):
            value, new_cursor = _resolve_finite_tuple(
                tokens=tokens,
                cursor=_cursor,
                description=(
                    (NodeType.LITERAL_VALUE, NodeType.PREFIX_EXPRESSION),
                    (NodeType.BLOCK,),
                )
            )
            node = Node(
                type=NodeType.WHILE,
                value=value
            )
            pass
        case ("keyword", "func" | "tick_func" as second_word):
            value, new_cursor = _resolve_finite_tuple(
                tokens=tokens,
                cursor=_cursor,
                description=(
                    (NodeType.NAME,),
                    (NodeType.BLOCK,),
                )
            )
            node = Node(
                type=(
                    {
                        "func": NodeType.FUNC_DEF,
                        "tick_func": NodeType.TICK_FUNC_DEF
                    }[second_word]
                ),
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
                + "".join(tuple(f"\t{(tokens[_cursor + n]) if (_cursor + n >= 0 and _cursor + n < len(tokens)) else ''}\n" for n in range(-10, 0)))
                + f"\t{t} <<< HERE\n"
                + "".join(tuple(f"\t{(tokens[_cursor + n]) if (_cursor + n >= 0 and _cursor + n < len(tokens)) else ''}\n" for n in range(1, 3)))
            )
        case _:
            raise ValueError(f"Token {t} unknown to parser")

    return node, new_cursor

if __name__ == "__main__":
    pass
    # It is prefered that tests be run from compiler.py,
    # because that module can import token and other
    # modules that are cousins to parser.py