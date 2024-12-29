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

import tkinter
from tkinter import filedialog

def compile(src_file_path, destination_file_path) -> None:
    raise NotImplementedError
    
    src = ""

    with open(src_file_path) as f:
        src = f.read()
    ast = parser.parse(tokens)
    ast2 = post_parser.post_parse(ast)
    directory_rep = datapack_generator.generate_datapack(ast2)
    directory_rep.realize(destination_file_path)

if __name__ == "__main__":
    root = tkinter.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Orthophosphate Files", "*.txt *.opo4")])

    SEPARATOR = "\n### ### ###\n"
    LESSER_SEPERATOR = "\n--- --- ---\n"

    with open(file_path, 'r') as file:
        src = file.read()

        tokens = tokenizer.tokenize(src)

        print(SEPARATOR)
        print(src)
        print(SEPARATOR)
        print(tokens)
        print(SEPARATOR)
        ast = parser.parse(tokens)
        # print(repr(ast))
        # print(LESSER_SEPERATOR)
        print(ast)
        print(SEPARATOR)
        ast2 = post_parser.post_parse(ast)
        print(ast2)
        print(SEPARATOR)
        directory_rep = datapack_generator.generate_datapack(ast2)
        print(directory_rep)