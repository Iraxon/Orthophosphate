from .tokenizer_module_base import TokenizerModuleBase
from .token import Token
from .misc_tokens import *
from .declaration_tokens import *

#NEEDED CHANGES:
#finish class lol
#one character sub for tokens in the code

def get_ln_and_col(s: str, index) -> tuple[int, int]:
    """
    Returns the line and column of
    an index in a string with newlines
    """
    if s == "":
        return 0, 0
    elif len(s) == 1:
        return 1, 1
    lines = "\n".split(s[:index + 1])
    col = len(lines[-1])
    return len(lines), col

#the list of all the recognized token modules. Used this to add new tokens
tokens = (AlphanumericToken, NumberToken, WhiteSpaceToken, StringToken, MCFunctionLiteralToken, PunctuationToken, CommentToken, MultilineCommentToken, OperatorToken)

#helper data set. Maps every token string to the token it is a part of
tokenStrings: dict[str, TokenizerModuleBase]= {
    string: token
    for token in tokens
    for string in token.matches
}

def tokenize(input : str) -> list[Token]:
    """
    for k, v in tokenStrings.items():
        print(f"key: {k}, value: {v}")
    """

    data : str = input

    #where the tokenizer is in the data
    cursor : int = 0

    #the current token. This is needed because most tokens are more than one character long
    token : str = ""

    #the currently compiled tokens
    compiledTokens : list[Token] = []

    # Invisible punctuation added to start of file
    compiledTokens.append(Token("punc", "file_start"))
    PunctuationToken.start(compiledTokens)

    #logic
    while(cursor < len(data)):
        token = data[cursor]

        if token not in WhiteSpaceToken.matches: # We don't do anything for whitespace

            # Look ahead with an inner loop
            # and try to see what tokens
            # this character could be the start of
            possible_tokens = []
            inner_token = ""
            inner_cursor = cursor
            while (inner_cursor < len(data)) and (data[inner_cursor] not in WhiteSpaceToken.matches):
                inner_token += data[inner_cursor]
                if inner_token in tokenStrings:
                    possible_tokens.append(inner_token)
                inner_cursor += 1
                # print(f"Inner tokenizer loop running: {cursor}:{inner_cursor} on {inner_token}")
            # print(possible_tokens)
            
            # Decide on which token module to get calculate() from
            if len(possible_tokens) >= 1:
                chosen_token = sorted(possible_tokens, key=len)[0] # Get the longest of the possible tokens
            else:
                raise ValueError(f"Token {token} has no matches")
            
            # Apply calculate()
            cursor, compiledTokens, data = tokenStrings[chosen_token].calculate(
                cursor=cursor,
                compiledTokens=compiledTokens,
                data=data
            )
        cursor += 1
        # print(f"Outer tokenizer loop running: {cursor} on {token}")
    
    # Close the excess start token that will be found
    # after the last semicolon
    PunctuationToken.semicolon(compiledTokens, include_start=False)
    compiledTokens.append(Token("punc", "EOF"))
    
    return compiledTokens

    """
        printTokens(compiledTokens)
        nextChar : str = data[cursor]

        # if the next character is a terminating token, then we
        # need to run the token regardless if it is a token or not,
        # errors will be handled in the run token method
        # but we don't want to do this if this token plus the next char could be a valid token
        # or if this token is the empty string
        
        if(
            isTerminatingToken(nextChar)
            and token + nextChar not in tokenStrings
            and token + nextChar + data[cursor + 1] not in tokenStrings
        ):
            # takes the output and sets all the values
            cursor, compiledTokens, data = runToken(token=token, cursor=cursor, compiledTokens=compiledTokens, data=data)
            token = ""
        
        
        # If the token is whitespace (SPECIFICALLY whitespace; other terminating tokens can be
        # multiple characters) then no continuation is required
        if token in WhiteSpaceToken.matches:
            cursor, compiledTokens, data = runToken(token=token, cursor=cursor, compiledTokens=compiledTokens, data=data)
            token = ""
        
        token += nextChar
        cursor += 1

    #if the token is not empty, we need to run it
    cursor, compiledTokens, data = runToken(token=token, cursor=cursor, compiledTokens=compiledTokens, data=data)

    # Close the excess start token that will be found
    # after the last semicolon
    PunctuationToken.semicolon(compiledTokens, include_start=False)
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
        raise ValueError(f"Unknown token: '{token}' at index {cursor}, ln col {get_ln_and_col(data, cursor)}")

#checks if a token is terminating
def isTerminatingToken(token: str):

    #it is not terminating if it is not a token
    if token not in tokenStrings:
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
"""
#helper function to print all the tokens
def printTokens(compiledTokens : list[Token]):
    for token in compiledTokens:
        print(token)



