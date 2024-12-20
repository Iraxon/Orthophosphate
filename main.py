# Eventual entry point of the program here

import user_interface.file_utils
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

# VOID, changes file_path Tkinter variable
def browse_for_file(*args):
    """
    Opens system file dialog
    and assigns the user-selected
    file to file_path

    (which puts it in the entry box
    as well)
    """

    file_path_str = filedialog.askopenfilename(filetypes=[("Orthophosphate Files", "*.txt *.orph")])
    
    if file_path_str:
        pass
    else:
        file_path_str = "No file selected"
    file_path_in.set(file_path_str)

if __name__ == "__main__":

    root = Tk()
    root.title("Orthophosphate")

    (mainframe := ttk.Frame(root)).grid(column=0, row=0, sticky=NSEW) # Main grid;
    # Walrus operator := is just assignment. You use it instead of =
    # inside expressions. Python has this to prevent errors
    # arising from confusion of = and ==

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    for x in (1, 2, 3):
        for y in (1, 2, 3):
            mainframe.columnconfigure(x, weight=1)
            mainframe.rowconfigure(y, weight=1)

    # The Tkinter tutorial says this is necessary
    # to make things scale or something. Idk

    ttk.Label(mainframe, text="Input", justify="center").grid(column=1, row=1, columnspan=2, sticky=NSEW)

    ttk.Button(mainframe, text="Select file", command=browse_for_file).grid(column=1, row=2, sticky=EW)
    
    file_path_in = StringVar(value="No file selected") # Variable obviously set to "No file selected"
    
    (file_path_entry := ttk.Entry(mainframe, textvariable=file_path_in, width=30)).grid(column=2, row=2, sticky=EW)
    (file_path_label := ttk.Label(mainframe, textvariable=file_path_in, width=30)).grid(column=2, row=3, sticky=NSEW)

    print(file_path_in.get()) # Prints "No file selected" as expected

    # Entry and label still somehow display as blank for no good reason

    root.mainloop()