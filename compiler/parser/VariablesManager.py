#not sure which folder this goes into so I'm putting it here(WILL DEFINITELY NEED A REFACTOR) This is used to find and generate unique names for every variable
#VARIABLE NAMING SYSTEM: LOCAL: <FILENAME>.<PATH>.<VARIABLENAME>, GLOBAL: <FILENAME>.<VARIABLENAME>

#IMPORTANT: if given multiple blocks in the same function(such as two whiles in one block, in code this will be converted to while1 and while2)

from Variable import PrimitiveVariable, PrimitiveVariableType

localVarMap : dict[str, PrimitiveVariable]

globalVarMap : dict[str, PrimitiveVariable]

"""
helper function that converts the given inputs to an usable path using the conversion system
"""
def _convertPath(varName: str, fileName: str, path : str = "") -> str:

    #this is not a global variable
    if(path != ""):
        return (fileName + "." + path + "." + varName)
    
    #this is a global variable
    else:
        return (fileName + "." + varName)


"""
gets an instance of the specific variable. 
"""
def getVar(varName : str, fileName : str, path : str = "") -> str:

    #quick peace of mind that the var actually exists
    if(not varExists(varName=varName, fileName=fileName, path=path)):
        return None
    
    #local and global scope path are different! If the given path is global these variables will be same however
    localPath: str = _convertPath(varName=varName, fileName=fileName, path=path)
    globalPath: str = _convertPath(varName=varName, fileName=fileName)

    #encapsulation
    encapsulatedVariable : PrimitiveVariable = PrimitiveVariable
    
    #this path is global and we just need to check global variables
    if(path == ""):
        encapsulatedVariable.type = globalVarMap[globalPath].type
        encapsulatedVariable.value = globalVarMap[globalPath].value
    
    #we know the path is local so we need to check both tenses
    else:

        #we already know that the variable is a thing locally, this will check if it's a thing globally as well
        if(varExists(varName=varName, fileName=fileName)):
            encapsulatedVariable.type = globalVarMap[globalPath].type
            encapsulatedVariable.value = globalVarMap[globalPath].value

        #this variable is only a thing locally so we need to scan the local map
        else:
            encapsulatedVariable.type = localVarMap[globalPath].type
            encapsulatedVariable.value = localVarMap[globalPath].value

    return encapsulatedVariable

            

"""
returns wether or not the given variable already exists in this scope(if the scope is local it will check both local and global scope)
if not given a path it will assume this is a global variable
"""
def varExists(varName : str, fileName : str, path : str = "") -> bool:

    #local and global path scope are different! If the given path is global these variables will be same however
    localPath: str = _convertPath(varName=varName, fileName=fileName, path=path)
    globalPath: str = _convertPath(varName=varName, fileName=fileName)

    #this is global, so we just need to check if a variable exists on a global scope
    if(path == ""):
        return path in globalVarMap
    
    #this is local, so we need to check for global AND local scope.
    else:
        return (globalPath in globalVarMap or localPath in localVarMap)
        

"""
creates the variable given the all of the data, cefaults to the zero value. the final boolean decides wether it throws an error(defaults to not)
"""
def createVar(variable: PrimitiveVariableType, varName : str, fileName : str, path : str = "", throwError: bool = True) -> bool:
    
    #encapsulate this to stop any wierd stuff
    encapsulatedVariable: PrimitiveVariable = PrimitiveVariable
    encapsulatedVariable.type = variable
    encapsulatedVariable.value = 0

    localPath = _convertPath(varName=varName, fileName=fileName path=path)
    globalPath = _convertPath(varName=varName, fileName=fileName, path=path)



    #it is global
    if(str == ""):

        #if it already exists we gotta either throw an error or return false depending on the erro specifier
        if(varExists(globalPath)):
            if(throwError):
                raise SystemError("VARIABLES MANAGER, CREATE VAR. Cannot create two variables in the same global scope, path: " + globalPath)
            else:
                return False
            
        #create the variable
        globalVarMap[globalPath] = encapsulatedVariable

    #it is local
    else:
        #if it already exists we gotta either throw an error or return false depending on the error specifier
        if(varExists(localPath)):
            if(throwError):
                raise SystemError("VARIABLES MANAGER, CREATE VAR. Cannot create two variables in the same local scope, path: " + localPath)
            else:
                return False
            
        #create the variable
        localVarMap[localVarMap] = encapsulatedVariable

    return True
            
"""
creates the variable, the booleaen decides wether it throws an error on fail.
"""
def setVar(value: int, varName: str, fileName: str, path: str = "", throwError: bool = True) -> bool:

    # Check if the variable exists
    if not varExists(varName=varName, fileName=fileName, path=path):
        if throwError:
            raise SystemError(f"VARIABLES MANAGER, SET VAR. Variable does not exist, path: {_convertPath(varName=varName, fileName=fileName, path=path)}")
        else:
            return False

    # Determine the path
    localPath: str = _convertPath(varName=varName, fileName=fileName, path=path)
    globalPath: str = _convertPath(varName=varName, fileName=fileName)

    # Set the variable value
    if path == "":
        globalVarMap[globalPath].value = value
    else:
        if globalPath in globalVarMap:
            globalVarMap[globalPath].value = value
        else:
            localVarMap[localPath].value = value

    return True



        
