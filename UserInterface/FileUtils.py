#import and get the libraries
from tkinter import Tk, filedialog
import os

#prep boiler plate for file functionality
root = Tk()
root.withdraw()

#the name of the directory folder
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


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

#reads from a text file, returns the first string after the given key
def readFileFromKey(key):
    open("StoredValues.txt")


print(ROOT_DIR)