from TokenizerModuleBase import TokenizerModuleBase
from Token import Token
from TestToken2 import *

#NEEDED CHANGES:
#finish class lol
#one character sub for tokens in the code

#the list of all the recognized tokens. Used this to add new tokens
tokens = (NumberToken, WhiteSpaceToken, StatementEndingToken, StringToken, MCFunctionLiteralToken)

#helper data set. Stores every token string to the token it is a part of
tokenStrings = dict() 

#adds a dictionary that stores each specific token string to the overall token it is a part of
def initTokenMap():
    for token in tokens:
        for string in token.matches:
            tokenStrings[string] = token

initTokenMap()

def tokenize(input : str) -> list[Token]:

    data : str = input

    #where the tokenizer is in the data
    cursor : int = 0

    #the current token. This is needed because most tokens are more than one character long
    token : str = ""

    #the currently compiled tokens
    compiledTokens : list[Token] = []

    #logic
    while(cursor < len(data)):
        nextChar : str = data[cursor]

        #if the next character is a space, then we need to run the token regardless if it is a token or not, errors will be handled in the run token method
        if(isTerminatingToken(nextChar)):
            # takes the output and sets all the values
            #takes the output and sets all the values
            cursor, compiledTokens, data = runToken(token=token, cursor=cursor, compiledTokens=compiledTokens, data=data)

            token = ""
        
        token += nextChar

        #if the token is a terminating token we run it regardless of the spaces
        if(isTerminatingToken(token)):
            #takes the output and sets all the values
            cursor, compiledTokens, data = runToken(token=token, data=data, cursor=cursor, compiledTokens=compiledTokens)

            token = ""

        cursor += 1

    #if the token is not empty, we need to run it
    cursor, compiledTokens, data = runToken(token=token, cursor=cursor, compiledTokens=compiledTokens, data=data)
        
    return compiledTokens

#runs the specific token string, will return an error if not a token
def runToken(token: str, cursor: int, compiledTokens : list[Token], data : str) -> tuple:
    #run token if it is in the token base
    if(token in tokenStrings):
        compiledToken : TokenizerModuleBase = tokenStrings[token]

        cursor, compiledTokens, data = compiledToken.calculate(cursor, compiledTokens, data)

        #returns the values
        return cursor, compiledTokens, data
    
    #if not throw error
    else:
        #fix this later
        raise TypeError("Token |" + token + "| is not a valid token") 
    
#checks if a token is terminating
def isTerminatingToken(token):

    #it is not terminating if it is not a taken
    if(not token in tokenStrings):
        return False
    
    #get the token
    compiledToken : TokenizerModuleBase = tokenStrings[token]

    #returns wether the final token is terminating
    return compiledToken.isTerminating

#helper function to print all the tokens
def printTokens(compiledTokens : list[Token]):
    for token in compiledTokens:
        print(token)

