import typing
import os

from .parser import parser
from .parser import post_parser
from .parser.abstract_syntax_tree import Node
from .tokenizer import Tokenizer as tokenizer
from .datapack_generator import datapack_generator
from .datapack_generator import datapack_directory_management as ddm

def pure_function_compile(src_file_path: str, do_prints: bool=False) -> ddm.FolderRep:
    """
    This compiles everything and returns the resulting FolderRep without realizing it

    When do_prints is False, this is a pure function
    """
    SEPARATOR = "\n### ### ###\n"

    with open(src_file_path) as file:
        src = file.read()

    if do_prints:
        print(SEPARATOR)
        print(src)
        print(SEPARATOR)

    tokens = tokenizer.tokenize(src)

    if do_prints:
        print(src)
        print(SEPARATOR)
        print("\n".join(str(token) for token in tokens))
    ast = parser.parse(tokens)

    if do_prints:
        print(ast)
        print(SEPARATOR)
    assert isinstance(ast, Node)

    ast2 = post_parser.post_parse(ast)

    if do_prints:
        print(ast2)
        print(SEPARATOR)

    directory_rep = datapack_generator.generate_datapack(
        ast2,
        name=os.path.splitext(os.path.basename(src_file_path))[0]
    )
    return directory_rep

def compile(src_file_path: str, destination_file_path: str | None, do_prints: bool=False) -> None:
    """
    It compiles Orthophosphate. Datapack goes to specified destination.

    If destination_file_path is None then the result is printed to terminal instead of realized
    """

    directory_rep = pure_function_compile(src_file_path=src_file_path, do_prints=do_prints)

    if destination_file_path is not None:
        directory_rep.realize(destination_file_path)
    else:
        print(directory_rep)
