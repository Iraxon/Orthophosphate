"""
This file allows quickly test-running the compiler
without realizing the resulting FolderRep
"""
import os
import sys
OPO4_PATH = os.path.join(
        os.path.abspath(""), # Repo
        "src", # src
        "orthophosphate" # orthophosphate dir in src
    )

sys.path.insert(
    0,
    OPO4_PATH
)

from compiler.compiler import compile #type: ignore
import tkinter
from tkinter import filedialog

if __name__ == "__main__":
    root = tkinter.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Orthophosphate Files", "*.opo4")])

    compile(file_path, None, True)
