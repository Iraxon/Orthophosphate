from modules.TestToken1 import TestToken1
from modules.TestToken2 import TestToken2

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


def tokenize(data):
    #where the tokenizer is in the data
    cursor = 0

    #the current token. This is needed because most tokens are more than one character long
    token = ""

    #logic
    while(cursor < len(data)):
        nextChar = data[cursor]

        #if the next character is a space, then we need to run the token regardless if it is a token or not, errors will be handled in the run token method
        if(nextChar.isTerminating):
            runToken(token)

            #reset the token
            token = ""

            runToken(nextChar)

            continue

        token += nextChar

        #if the token is a terminating token we run it regardless of the spaces
        if(isTerminatingToken(token)):
            runToken(token)
            token = ""

        cursor += 1

def runToken(data):
    pass

def isTerminatingToken(token):
    return token in tokenStrings
        


        
