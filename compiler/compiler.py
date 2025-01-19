import tkinter
from tkinter import filedialog
import typing
import os

if __name__ == "__main__":
    from parser import parser
    from parser import post_parser
    from tokenizer import Tokenizer as tokenizer
    from datapack_generator import datapack_generator
    from datapack_generator import datapack_directory_management as ddm
else:
    from .parser import parser
    from .parser import post_parser
    from .tokenizer import Tokenizer as tokenizer
    from .datapack_generator import datapack_generator
    from .datapack_generator import datapack_directory_management as ddm

def compile(src_file_path: str, destination_file_path: typing.Optional[str], do_prints=False) -> None:
    with open(src_file_path) as file:
        src = file.read()
    tokens = tokenizer.tokenize(src)

    SEPARATOR = "\n### ### ###\n"

    if do_prints:
        print(SEPARATOR)
        print(src)
        print(SEPARATOR)
        print(tokens)
        print(SEPARATOR)
    ast = parser.parse(tokens)

    if do_prints:
        print(ast)
        print(SEPARATOR)
    ast2 = post_parser.post_parse(ast)

    if do_prints:
        print(ast2)
        print(SEPARATOR)
    
    directory_rep = datapack_generator.generate_datapack(
        ast2,
        name=os.path.splitext(os.path.basename(src_file_path))[0]
    )
    if destination_file_path is not None:
        directory_rep.realize(destination_file_path)
    else:
        print(directory_rep)

if __name__ == "__main__":
    root = tkinter.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Orthophosphate Files", "*.opo4")])

    compile(file_path, None, True)