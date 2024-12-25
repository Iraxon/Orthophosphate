from .tokenizer_module_base import TokenizerModuleBase
from .token import Token
from .misc_tokens import *
from .declaration_tokens import *

#NEEDED CHANGES:
#finish class lol
#one character sub for tokens in the code

#the list of all the recognized tokens. Used this to add new tokens
tokens = (NameToken, NumberToken, WhiteSpaceToken, StringToken, MCFunctionLiteralToken, PunctuationToken, CommentToken)

#helper data set. Maps every token string to the token it is a part of
tokenStrings: dict[str, Token]= {
    string: token for token in tokens for string in token.matches
}

def tokenize(input : str) -> list[Token]:

    for k, v in tokenStrings.items():
        print(f"key: {k}, value: {v}")

    data : str = input

    #where the tokenizer is in the data
    cursor : int = 0

    #the current token. This is needed because most tokens are more than one character long
    token : str = ""

    #the currently compiled tokens
    compiledTokens : list[Token] = []

    # Invisible punctuation added to start of file
    compiledTokens.append(Token("punc", "file_start"))
    compiledTokens.append(Token("punc", "start"))

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
    
    # Get rid of the excess start token
    # that will follow the last semicolon the programmer wrote
    if compiledTokens[-1].type == "punc" and compiledTokens[-1].value == "start":
        compiledTokens.pop()
    compiledTokens.append(Token("punc", "EOF"))

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
        compiledToken : TokenizerModuleBase = tokenStrings[token]

        cursor, compiledTokens, data = compiledToken.calculate(cursor, compiledTokens, data)
    
#checks if a token is terminating
def isTerminatingToken(token):

    #it is not terminating if it is not a taken
    if(not token in tokenStrings):
        return False
    
    #get the token
    compiledToken : TokenizerModuleBase = tokenStrings[token]

    #returns wether the final token is terminating
    return compiledToken.isTerminating

def handleUnkownToken(token: str, cursor: int, compiledTokens : list[Token], data : str) -> tuple:

    # This still needs to be replaced
    raise NotImplementedError(f"Proper name token logic is still forthcoming")

    compiledTokens.append(Token("name", token))
    return cursor, compiledTokens, data

#helper function to print all the tokens
def printTokens(compiledTokens : list[Token]):
    for token in compiledTokens:
        print(token)



