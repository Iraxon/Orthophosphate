#import and get the library
from tkinter import Tk, filedialog

#prep boiler plate
root = Tk()
root.withdraw()

#says the prompt and returns the file path that the user inputs.
def getFilePath(prompt):
    print(print)

    file_path = filedialog.askopenfilename(
            filetypes=[("MIDI Files", "*.txt *.mcdp")]
        )
    
    return file_path

#says the prompt and returns the file path that the user inputs
def getDirPath(prompt):
    print(print)

    folder_path = filedialog.askdirectory()
    return folder_path


