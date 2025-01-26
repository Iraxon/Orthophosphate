import os.path
import typing

import src.orthophosphate.compiler.compiler as compiler
import src.orthophosphate.compiler.datapack_generator.datapack_directory_management as ddm
import src.orthophosphate.compiler.parser.abstract_syntax_tree as tree
import src.orthophosphate.compiler.parser.parser as parser
import src.orthophosphate.compiler.tokenizer.Tokenizer as tokenizer

TEST_SRC_PATH = os.path.join(os.path.abspath("."), "src", "orthophosphate", "compiler", "test_src_files")

# Complete tests: compiling testsrc files

def compile_test_src(name: str, nameIncludesExtension: bool = False) -> ddm.FolderRep:
    """
    Name should not include the .opo4 extension unless
    specified by boolean arg
    """
    return compiler.pure_function_compile(
            os.path.join(TEST_SRC_PATH, name + (".opo4" if not nameIncludesExtension else ""))
        )

def compile_hello_world() -> ddm.FolderRep:
    return compile_test_src("hello_world")

def compile_all() -> tuple[ddm.FolderRep, ...]:
    return tuple(
        compile_test_src(name, nameIncludesExtension=True) for name in os.listdir(TEST_SRC_PATH)
    )

def test_that_everything_compiles():
    for item in compile_all():
        assert isinstance(
            item,
            ddm.FolderRep
        )

# Partial tests: testing compiler components

def generate_expected_parse_for_equation(
    op: str,
    opand1: typing.Any,
    opand2: typing.Any,
    typ: str = "int"
) -> tree.Node:
    return tree.Node(
            type=tree.NodeType.ROOT,
            value=(
                tree.Node(
                    type=tree.NodeType.STATEMENT,
                    value=(
                        tree.Node(
                            type=tree.NodeType.PREFIX_EXPRESSION,
                            value=(
                                tree.Node(
                                    type=tree.NodeType.OPERATOR,
                                    value=op
                                ),
                                tree.Node(
                                    type=tree.NodeType.LITERAL_VALUE,
                                    value=opand1,
                                    data_type=typ
                                ),
                                tree.Node(
                                    type=tree.NodeType.LITERAL_VALUE,
                                    value=opand2,
                                    data_type=typ
                                ),
                            ),
                            data_type=typ
                        ),
                    )
                ),
            )
        )
def generate_eq_pair(
    op: str, opand1: typing.Any, opand2: typing.Any, typ: str = "int"
) -> tuple[str, tree.Node]:
    return (
        f"{opand1} {op} {opand2}",
        generate_expected_parse_for_equation(op, opand1, opand2, typ)
    )

def test_expression_parsing() -> None:
    EQUATIONS: tuple[tuple[str, typing.Any, typing.Any, str], ...] = (
        ("+", 3, 4, "int"),
        ("-", 7, 5, "int"),
        ("**", 2, 2, "int")
    )
    for expression, parse in {
        eq: parse
        for eq, parse in map(
            lambda desc: generate_eq_pair(desc[0], desc[1], desc[2], desc[3]),
            EQUATIONS
        )
    }.items():
        assert parser.parse(tokenizer.tokenize(expression)) == parse
