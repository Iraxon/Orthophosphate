import os
import typing

from .parser import parser
from .tokenizer import Tokenizer as tokenizer
from .datapack_generator import datapack_generator as dg

def partial_compile(src_file_path: str, do_prints: bool=False) -> dg.DataPack:
    """
    This compiles everything and returns the resulting data pack
    without writing it to the file system
    """
    PRINT_SEPARATOR: typing.Final = "\n### ### ###\n"
    source_file_name: typing.Final = os.path.splitext(os.path.basename(src_file_path))[0]

    with open(src_file_path) as file:
        src = file.read()

    if do_prints:
        print(PRINT_SEPARATOR)
        print(src)
        print(PRINT_SEPARATOR)

    tokens = tokenizer.tokenize(src)

    if do_prints:
        print(src)
        print(PRINT_SEPARATOR)
        print("\n".join(str(token) for token in tokens))
    ast = parser.parse(tokens)

    if do_prints:
        print(PRINT_SEPARATOR)
        print(ast)
        print(PRINT_SEPARATOR)

    directory_rep = dg.generate_datapack(
        ast,
        source_file_name
    )
    return directory_rep

def compile(src_file_path: str, destination_file_path: str | None, do_prints: bool=True) -> None:
    """
    It compiles Orthophosphate. Datapack goes to specified destination.

    If destination_file_path is None then the result is printed to terminal instead of realized
    """

    directory_rep = partial_compile(src_file_path=src_file_path, do_prints=do_prints)

    if destination_file_path is None:
        print(directory_rep)
    else:
        dg.write_to_files(directory_rep, destination_file_path)
