from .tokenizer_module_base import TokenizerModuleBase
from .token import Token

# In the course of making the logic for
# the name token, I ran into a conflict.
# That has been solved with a match case
# statement over in misc_tokens.NameToken

# All of this is kept here in commented-out form
# in case it needs to be used again later.

"""
class FunctionToken(TokenizerModuleBase):

    matches = ("func",)

    isTerminating = False

    def calculate(cursor: int, compiledTokens: list[Token], data: str):        
        name = ""

        cursor += 1

        print("len(data): " + str(len(data)))

        # I am leaving this bit here for you to remove because I don't fully
        # understand what edits need to be made to keep this functional

        raise NotImplementedError(f"The FunctionToken class still needs its logic cleaned up")

        while(cursor < len(data) and not data[cursor] in [" ","("]):

            print("cursor: " + str(cursor))

            name += data[cursor]
            cursor += 1

        cursor -= 1


        compiledTokens.append(Token("keyword", "func"))

        return cursor, compiledTokens, data

class LoopToken(TokenizerModuleBase):
    
    matches = ("while",)

    isTerminating = False

    def calculate(cursor: int, compiledTokens: list[Token], data: str):        

        compiledTokens.append(Token("keyword", "while"))


        return cursor, compiledTokens, data
    
class ReturnToken(TokenizerModuleBase):
    
    matches = ("return",)

    isTerminating = False

    def calculate(cursor: int, compiledTokens: list[Token], data: str):        

        compiledTokens.append(Token("keyword", "return"))


        return cursor, compiledTokens, data
    


"""