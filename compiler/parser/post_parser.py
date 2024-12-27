from . import abstract_syntax_tree as tree

def post_parse(t: tree.Node) -> tree.Node:
    """
    Eventually, this will handle variables, functions,
    and other mechanics that require the use of a symbol
    table

    At present it is the identity function
    """
    return t