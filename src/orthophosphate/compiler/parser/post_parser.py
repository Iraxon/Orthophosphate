from . import abstract_syntax_tree as tree

def strip_empties(ast: tree.Node) -> tree.Node:
    """
    Strip empty STATEMENT nodes from the AST
    """
    if ast is None:
        return None
    # If AST.value is a tuple and that tuple is empty, return None
    if ast.type in frozenset((tree.NodeType.STATEMENT, tree.NodeType.PREFIX_EXPRESSION)) and isinstance(ast.value, tuple) and len(ast.value) == 0:
        return None
    return ast

def identity(x):
    return x

def simple_pass(node_in: tree.Node, f=identity) -> tree.Node:
    """
    Does a pass over the tree, building
    a new tree by passing every node
    through the provided function;

    if no function is provided, the identity
    function is used
    """
    if node_in is None:
        return None
    if isinstance(node_in.value, tuple):
        node_mid = f(node_in)
        if node_mid is None:
            return None
        value = tuple(
            simple_pass(item, f)
            for item in node_mid.value
            if simple_pass(item, f) is not None
        )
        return tree.Node(
            type=node_mid.type,
            value=value,
            data_type=node_mid.data_type
        )
    return f(node_in)

def _move_up_loose_functions(nodes: tuple[tree.Node]) -> tuple[tree.Node]:
    """
    Private function that shoves loose items into the default namespace
    """
    new_nodes = []
    contents_of_default_namespace = []

    for node in nodes:
            match (node.type, node.value):
                case "namespace", v:
                    new_nodes.append(node)
                case _:
                    contents_of_default_namespace.append(node)
    return (
        (
            tree.Node(
                type="namespace",
                value=(
                    tree.Node(
                        type="placeholder",
                        value="default_namespace"
                    ),
                    tree.Node(
                        type="block",
                        value=tuple(contents_of_default_namespace)
                    )
                )
            ),

        ) + tuple(new_nodes)
    )

def expand_tree(ast: tree.Node) -> tree.Node:
    """
    Expands convenient concisions such as top-level function
    definitions being placed into the default namespace
    """
    new_ast = tree.Node(
        type=ast.type,
        value=_move_up_loose_functions(nodes=ast.value),
        data_type=ast.type
    )
    return new_ast

def symbol_table_pass(ast: tree.Node) -> tree.Node:
    """
    This is the complex pass that handles
    variable references and data types
    """

    raise NotImplementedError

def post_parse(ast: tree.Node) -> tree.Node:
    """
    Transforms the AST to make it suitable
    for passing to the datapack generator
    """
    stripped_ast = simple_pass(ast, strip_empties)
    expanded_ast = expand_tree(stripped_ast)
    post_stripped_ast = simple_pass(expanded_ast, strip_empties)
    return post_stripped_ast
