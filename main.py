# Eventual entry point of the program here

import user_interface.file_utils
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

# VOID, changes file_path Tkinter variable
def browse_for_file():
    """
    Opens system file dialog
    and assigns the user-selected
    file to file_path

    (which puts it in the entry box
    as well)
    """
    global file_path

    file_path_str = filedialog.askopenfilename(filetypes=[("<ProjectName> Files", "*.txt")])
    
    if file_path_str:
        pass
    else:
        file_path_str = "No file selected"
    file_path.set(file_path_str)

if __name__ == "__main__":

    root = Tk()
    root.title("<ProjectName>")

    (mainframe := ttk.Frame(root, padding="3 3 12 12")).grid(column=0, row=0, sticky=NSEW) # Main grid;
    # Walrus operator := is just assignment. You use it instead of =
    # inside expressions. Python has this to prevent errors
    # arising from confusion of = and ==

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    # The Tkinter tutorial says this is necessary
    # to make things scale or something. Idk

    ttk.Label(mainframe, text="Input", justify="center").grid(column=1, row=1, columnspan=2, sticky=NSEW)
    ttk.Button(mainframe, text="Select file", command=browse_for_file).grid(column=1, row=2, sticky=NSEW)
    
    file_path = StringVar() # If-blocks don't create scope in Python, so no need for global keyword
    (file_path_entry := ttk.Entry(mainframe, textvariable=file_path, width=20)).grid(column=2, row=2, sticky=NSEW)

    file_path_entry.focus()
    root.mainloop()