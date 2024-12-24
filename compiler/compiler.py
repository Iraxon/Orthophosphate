import parser.parser as parser
import tokenizer.Tokenizer as Tokenizer

import tkinter
from tkinter import filedialog

if __name__ == "__main__":
    root = tkinter.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Orthophosphate Files", "*.txt *.opo4")])

    with open(file_path, 'r') as file:
        src = file.read()
        tokens = Tokenizer.tokenize(src)
        print(tokens)
        ast = parser.parse(tokens)
        print(ast)