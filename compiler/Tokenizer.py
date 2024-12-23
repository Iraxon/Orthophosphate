from modules.TestToken1 import TestToken1
from modules.TestToken2 import TestToken2
from TokenizerModuleBase import TokenizerModuleBase
from helper.TokenizerInfo import TokenizerInfo
from helper.TokenizerOutput import TokenizerOutput
from Token import Token

#NEEDED CHANGES:
#finish class lol
#one character sub for tokens in the code

#the list of all the recognized tokens. Used this to add new tokens
tokens = (TestToken1, TestToken2)

#helper data set. Stores every token string to the token it is a part of
tokenStrings = dict() 

#adds a dictionary that stores each specific token string to the overall token it is a part of
def initTokenMap():
    for token in tokens:
        for string in token.tokens:
            tokenStrings[string] = token

#all of the compiled tokens
compiledTokens: list[Token]


def tokenize(data):
    #where the tokenizer is in the data
    cursor = 0

    #the current token. This is needed because most tokens are more than one character long
    token = ""

    #logic
    while(cursor < len(data)):
        nextChar = data[cursor]

        #if the next character is a space, then we need to run the token regardless if it is a token or not, errors will be handled in the run token method
        if(nextChar.isTerminating()):
            #takes the output and sets all the values
            output : TokenizerOutput = runToken(token, TokenizerInfo(data, cursor, compiledTokens))

            cursor = output.cursor
            compiledTokens = output.tokens
            data = output.data

            #reset the token
            token = ""

        token += nextChar

        #if the token is a terminating token we run it regardless of the spaces
        if(isTerminatingToken(token)):
            #takes the output and sets all the values
            output : TokenizerOutput = runToken(token, TokenizerInfo(data, cursor, compiledTokens))

            cursor = output.cursor
            compiledTokens = output.tokens
            data = output.data

            token = ""

        cursor += 1
        
    return compiledTokens

#runs the specific token string, will return an error if not a token
def runToken(token, info):
    #run token if it is in the token base
    if(token in tokenStrings):
        compiledToken : TokenizerModuleBase = tokenStrings[token]

        compiledToken.calculate(info)
    
    #if not throw error
    else:
        #fix this later
        raise TypeError
    
#checks if a token is terminating
def isTerminatingToken(token):

    #it is not terminating if it is not a taken
    if(not token in tokenStrings):
        return False
    
    #get the token
    compiledToken : TokenizerModuleBase = tokenStrings[token]

    #returns wether the final token is terminating
    return compiledToken.isTerminating