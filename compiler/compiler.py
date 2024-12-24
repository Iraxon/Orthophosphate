import parser.parser as parser
import tokenizer.tokenizer as tokenizer

import tkinter
from tkinter import filedialog

if __name__ == "__main__":
    root = tkinter.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Orthophosphate Files", "*.txt *.opo4")])

    SEPARATOR = "\n--- --- ---\n"

    with open(file_path, 'r') as file:
        src = file.read()

        print (SEPARATOR)

        tokens = tokenizer.tokenize(src)
        print(tokens)

        print(SEPARATOR)

        ast = parser.parse(tokens)
        print(ast)

        print(SEPARATOR)