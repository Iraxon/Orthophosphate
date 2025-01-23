"""
This file allows quickly test-running the compiler
without realizing the resulting FolderRep
"""

# A rather ugly solution to making the import happen from src
import sys, os
sys.path.insert(0, os.path.abspath('...'))

from src.orthophosphate.compiler.compiler import *
import tkinter
from tkinter import filedialog

if __name__ == "__main__":
    root = tkinter.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Orthophosphate Files", "*.opo4")])

    compile(file_path, None, True)
