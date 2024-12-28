from . import abstract_syntax_tree as tree

def handle_variables(ast: tree.Node) -> tree.Node:
    new_ast = ast
    return new_ast

def post_parse(ast: tree.Node) -> tree.Node:
    """
    Eventually, this will handle variables, functions,
    and other mechanics that require the use of a symbol
    table

    At present it is the identity function
    """
    new_ast = handle_variables(ast)
    return new_ast