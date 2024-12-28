from . import abstract_syntax_tree as tree

def strip_empties(ast: tree.Node) -> tree.Node:
    if isinstance(ast.value, tuple) and len(ast.value) == 0:
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

def post_parse(ast: tree.Node) -> tree.Node:
    """
    Eventually, this will handle variables, functions,
    and other mechanics that require the use of a symbol
    table
    """
    stripped_ast = simple_pass(ast, strip_empties)
    new_ast = stripped_ast
    return new_ast