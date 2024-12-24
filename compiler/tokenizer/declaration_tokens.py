from .tokenizer_module_base import TokenizerModuleBase
from .token import Token

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
    


