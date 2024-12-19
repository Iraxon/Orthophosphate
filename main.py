# Eventual entry point of the program here

import user_interface.file_utils
from tkinter import Tk, filedialog

if __name__ == "__main__":

    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("<ProjectName> Files", "*.txt")])