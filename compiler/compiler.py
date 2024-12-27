if __name__ == "__main__":
    from parser import parser
    from parser import post_parser
    from tokenizer import Tokenizer as tokenizer
else:
    from .parser import parser
    from .parser import post_parser
    from .tokenizer import Tokenizer as tokenizer

import tkinter
from tkinter import filedialog

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