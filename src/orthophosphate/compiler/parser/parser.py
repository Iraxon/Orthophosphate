import functools
import typing
from .abstract_syntax_tree import NodeType
from .abstract_syntax_tree import Node
from ..tokenizer.token import Token

@functools.cache
def _resolve_finite_tuple(
    tokens: tuple[Token, ...],
    cursor: int,
    description: tuple[tuple[str, ...], ...] | None = None,
    count: int = -1
):
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
        description = tuple(
            ("*",) for _ in range(count)
        )
    assert description is not None

    iterating_cursor = cursor + 1 # Skip opening token
    node_list: list = []
    counter = 0

    while iterating_cursor < len(tokens):
        if len(node_list) >= len(description):
            break
        next_node, iterating_cursor = parse(tokens, _cursor=iterating_cursor)

        if next_node is None:
            raise ValueError(f"Expected Node of a type in {description[counter]}; got None")

        if next_node.type not in description[counter] and description[counter] != ("*",):
            raise ValueError(f"Expected Node of a type in {description[counter]}; got {repr(next_node)}")

        node_list.append(next_node)
        counter += 1

    return tuple(node_list), iterating_cursor # No +1 because no closing token to skip

@functools.cache
def _resolve_node_tuple(tokens: tuple[Token, ...], cursor: int, end_token):
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

@typing.overload
def parse(tokens: tuple[Token, ...]) -> Node: ...

@typing.overload
def parse(tokens: tuple[Token, ...], _cursor: int) -> tuple[Node | None, int]: ...

@functools.cache
def parse(tokens: tuple[Token, ...], _cursor: int = 0) -> Node | tuple[Node | None, int]:
    """
    Accepts a tuple of tokens from the tokenizer

    Returns the root node of an abstract syntax tree
    representing the program specified

    This function is recursive, both itself and
    mutually with _resolve_node_tuple and _resolve_finite_tuple;
    it uses the private cursor parameter
    in the recursion calls; that parameter should not be set
    by outsider callers
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
                end_token=Token("punc", "EOF")
            )[0]
        )

    # The recursive sorcery begins here

    # This value might be changed by a case block;
    # if it is not, then we default to cursor + 1
    new_cursor: int = _cursor + 1
    node: Node | None

    match (t.type, t.value):
        case ("punc", "start"):
            value, new_cursor = _resolve_node_tuple(
                tokens=tokens,
                cursor=_cursor,
                end_token=Token("punc", ";")
            )
            pre_node = Node(
                type=NodeType.STATEMENT,
                value=value
            )
            node = pre_node.check_statement()
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
                data_type="*"
            )
        case ("selector", s):
            node = Node(
                type=NodeType.NAME,
                value=t.value,
                data_type="sel"
            )
        case ("op", o):
            if ("=" in o and o != "==" and o != "!=") or o in ("><",):
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
        case ("keyword", "obj"):
            value, new_cursor = _resolve_finite_tuple(
                tokens=tokens,
                cursor=_cursor,
                description=(
                    (NodeType.NAME,),
                )
            )
            node = Node(
                type=NodeType.OBJ_DEF,
                value=value
            )
        case ("keyword", "score"):
            # The description for _resolve_finite_tuple
            # depends on whether it's a score or a constant
            # as the second operand ("source score"). So we
            # look ahead in the tokens to check which it is.
            # If an index error arises, it's because the user didn't
            # supply the correct arguments to the scoreboard keyword
            ahead_token = tokens[_cursor + 4]
            match (ahead_token.type, ahead_token.value):
                case ("keyword", "constant"):
                    value, new_cursor = _resolve_finite_tuple(
                        tokens=tokens,
                        cursor=_cursor,
                        description=(
                            (NodeType.NAME, NodeType.TARGET_SELECTOR),
                            (NodeType.NAME,),
                            (NodeType.ASSIGN_OPERATOR,),
                            (NodeType.CONSTANT_SCORE,),
                        )
                    )
                case ("name", _):
                    value, new_cursor = _resolve_finite_tuple(
                        tokens=tokens,
                        cursor=_cursor,
                        description=(
                            (NodeType.NAME, NodeType.TARGET_SELECTOR),
                            (NodeType.NAME,),
                            (NodeType.ASSIGN_OPERATOR,),
                            (NodeType.NAME, NodeType.TARGET_SELECTOR),
                            (NodeType.NAME,),
                        )
                    )
                case _:
                    raise ValueError(f"Unexpected scoreboard token {t} with ahead_token {ahead_token}")
            node = Node(
                type=NodeType.SCOREBOARD_OPERATION,
                value=value
            )
        case ("keyword", "constant"):
            value, new_cursor = _resolve_finite_tuple(
                tokens=tokens,
                cursor=_cursor,
                description=(
                    (NodeType.LITERAL_VALUE,),
                )
            )
            node = Node(
                type=NodeType.CONSTANT_SCORE,
                value=value
            )
        case ("keyword", "reset"):
            value, new_cursor = _resolve_finite_tuple(
                tokens=tokens,
                cursor=_cursor,
                description=(
                    (NodeType.TARGET_SELECTOR, NodeType.NAME,),
                    (NodeType.NAME,),
                )
            )
            node = Node(
                type=NodeType.SCOREBOARD_RESET,
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
        case ("type", typ):
            value, new_cursor = _resolve_finite_tuple(
                tokens=tokens,
                cursor=_cursor,
                description=(
                    (NodeType.NAME,),
                )
            )
            node = Node(
                type=NodeType.DECLARATION,
                value=value,
                data_type=typ
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
        case ("keyword", "call"):
            value, new_cursor = _resolve_finite_tuple(
                tokens=tokens,
                cursor=_cursor,
                description=(
                    (NodeType.NAME,),
                )
            )
            node = Node(
                type=NodeType.CALL,
                value=value
            )
        case ("keyword", "after"):
            value, new_cursor = _resolve_finite_tuple(
                tokens=tokens,
                cursor=_cursor,
                description=(
                    (NodeType.LITERAL_VALUE,),
                    (NodeType.BLOCK,)
                )
            )
            node = Node(
                type=NodeType.AFTER,
                value=value
            )
        case ("punc", "{"):
            value, new_cursor = _resolve_node_tuple(
                tokens=tokens,
                cursor=_cursor,
                end_token=Token("punc", "}")
            )
            node = Node(
                type=NodeType.BLOCK,
                value=value
            )
        case ("punc", "("):
            value, new_cursor = _resolve_node_tuple(
                tokens=tokens,
                cursor=_cursor,
                end_token=Token("punc", ")")
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
                + "".join(tuple(f"\t{(tokens[_cursor + n]) if (_cursor + n >= 0 and _cursor + n < len(tokens)) else ''}\n" for n in range(-20, 0)))
                + f"\t{t} <<< HERE\n"
                + "".join(tuple(f"\t{(tokens[_cursor + n]) if (_cursor + n >= 0 and _cursor + n < len(tokens)) else ''}\n" for n in range(1, 10)))
            )
        case _:
            raise ValueError(f"Token {t} unknown to parser")

    return node, new_cursor

if __name__ == "__main__":
    pass
    # It is prefered that tests be run from compiler.py,
    # because that module can import token and other
    # modules that are cousins to parser.py
