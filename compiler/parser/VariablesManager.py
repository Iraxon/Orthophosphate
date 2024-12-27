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

def getVar(varName : str, fileName : str, path : str = "") -> str:

    #quick peace of mind that the var actually exists
    if(not isVar(varName=varName, fileName=fileName, path=path)):
        return None
    
    #local and global scope path are different! If the given path is global these variables will be same however
    localPath: str = _convertPath(varName=varName, fileName=fileName, path=path)
    globalPath: str = _convertPath(varName=varName, fileName=fileName)
    
    #this path is global and we just need to check global variables
    if(path == ""):
        return globalVarMap[globalPath]
    
    #we know the path is local so we need to check both tenses
    else:
        
        #instantiate a new class for encapsulation(makes sure that changing variable does change the given data structure)
        var : PrimitiveVariable = PrimitiveVariable

        #we already know that the variable is a thing locally, this will check if it's a thing globally as well
        if(isVar(varName=varName, fileName=fileName)):
            var.type = globalVarMap[globalPath].type
            var.type = globalVarMap[globalPath].value

        #this variable is only a thing locally so we need to scan the local map
        else:
            var.type = localVarMap[localPath].type
            var.type = localVarMap[localPath].value

        return var
            

"""
returns wether or not the given variable already exists in this scope(if the scope is local it will check both local and global scope)
if not given a path it will assume this is a global variable
"""
def isVar(varName : str, fileName : str, path : str = "") -> bool:

    #local and global path scope are different! If the given path is global these variables will be same however
    localPath: str = _convertPath(varName=varName, fileName=fileName, path=path)
    globalPath: str = _convertPath(varName=varName, fileName=fileName)

    #this is global, so we just need to check if a variable exists on a global scope
    if(path == ""):
        return path in globalVarMap
    
    #this is local, so we need to check for global AND local scope.
    else:
        return (globalPath in globalVarMap or localPath in localVarMap)
        

