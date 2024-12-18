#import and get the libraries
from tkinter import Tk, filedialog
import os

#prep boiler plate for file functionality
root = Tk()
root.withdraw()

#various important file/folder names. They are put here so they can be easily refactored
#the name of the directory folder
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
STORED_VALUES_FOLDER_NAME = "StoredValues"


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

#creates a new copy of the file if there currently is none
def createFile(path):
    f = open(path)
    f.close()

#STRING: reads from a text file, returns the first string after the given key
def fileValueFromKey(key, path):  
    #creates the file if it is not currently created, SHOULD NOT OVERRIDE THE FILE IF IT IS ALREADY
    createFile(path)
    
    with open(path, "r") as f:
        
        #iterates through every line and scans for the key
        for i in f:
            splitString = i.split(":")

            if(splitString[0] == key):
                return splitString[1]

    #default return if the output doesn't exist  
    return ""

#BOOLEAN: returns true or false depending if a key exists in that file
def fileKeyExists(key, path):
    #creates the file if it is not currently created, SHOULD NOT OVERRIDE THE FILE IF IT IS ALREADY
    createFile(path)

    with open(path, "r") as f:
        
        #iterates through every line and scans for the key
        for i in f:
            splitString = i.split(":")

            if(splitString[0] == key):
                return True
    
    #default return value
    return False