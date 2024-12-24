from .tokenizer_module_base import TokenizerModuleBase
from .token import Token

class FunctionToken(TokenizerModuleBase):

    matches = ("func",)

    isTerminating = False

    def calculate(cursor: int, compiledTokens: list[Token], data: str):        
        name = ""

        cursor += 1

        print("len(data): " + str(len(data)))

        while(cursor < len(data) and not data[cursor] in [" ","("]):

            print("cursor: " + str(cursor))

            name += data[cursor]
            cursor += 1

        cursor -= 1


        compiledTokens.append(Token("function", name))

        return cursor, compiledTokens, data

class LoopToken(TokenizerModuleBase):
    
    matches = ("while",)

    isTerminating = False

    def calculate(cursor: int, compiledTokens: list[Token], data: str):        

        compiledTokens.append(Token("loop", "while"))


        return cursor, compiledTokens, data