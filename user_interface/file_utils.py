#import and get the libraries
from tkinter import Tk, filedialog
import os

#prep boiler plate for file functionality
root = Tk()
root.withdraw()

#various important file/folder names. They are put here so they can be easily refactored
#the name of the directory folder
ROOT_DIR_PATH = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
USER_INPUT_PATH = os.path.join(ROOT_DIR_PATH, "stored_values", "user_input.log")

#says the prompt and returns the file path that the user inputs.
def getFilePath(prompt):
    print(prompt)

    file_path = filedialog.askopenfilename(
            filetypes=[("MIDI Files", "*.txt *.mcdp")]
        )
    
    return file_path

#says the prompt and returns the file path that the user inputs
def getDirPath(prompt):
    print(prompt)

    folder_path = filedialog.askdirectory()
    return folder_path

#creates a new copy of the file if there currently is none
def createFile(path):
    try:
        with open(path, "x") as f: # Using a with block is safer than open() and then close()
            # because it ensures close() is always executed even if there are errors
            pass
    except FileExistsError: # "x" mode for opening raises this error if the file already exists
        pass

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


#INTEGER: gets the index of the givne key in string terms, is best used in class
def fileIndexOfKey(key, path):

    keyIndex = 0

    #loops through every line and checks if it lines up right
    with open(path, "r") as f:
        for i in f:
            if(i.split(":")[0] == key):
                return keyIndex
            

    #default value of -1
    return -1
        

#VOID: deletes ALL occurrences of a key found in the file, will not remove whitespace
def fileKeyDelete(key, path):

    lines = ""

    #gets the file in list form
    with open(path, "r") as f:
        lines = f.readlines()
    
    with open(path, "w") as f:

        #rewrites all the lines except for the one we want to delete
        for line in lines:
            if(line.split(":")[0] != key):
                f.write(line)

#VOID: writes the string to the file, will go to the nearest available spot
def fileStringWrite(input, path):

    print("testing")

    lines = ""
    alreadyWrote = False

    with open(path, "r") as f:
        lines = f.readlines()

    with open(path, "w") as f:
        
        #goes through and makes sure there is no whitespace it can go to first
        for line in lines:
            #writes it if it sees a blank line and it hasn't already been written
            if(len(line) == 0 and not alreadyWrote):
                f.write(input)
                alreadyWrote = True

                print("writing specific line: " + input)
            else:
                f.write(line)
                print("writing line: " + line)

        #write if not written already
        if(not alreadyWrote):
            f.write(input)
            print("writing specifc line *2: " + input)

#puts the key into the file. Will replace and delete any other key values
def fileKeyPut(key, value, path):
    fileKeyDelete(key, path)
    fileStringWrite(key + ":" + value, path)



#am having problems with testing rn bc the userinput doesn't get written to for some reason. IDK why
if __name__ == "__main__":
    fileStringWrite("testingwrite", USER_INPUT_PATH)