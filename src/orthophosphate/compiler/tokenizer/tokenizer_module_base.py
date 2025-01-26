import typing
from .token import Token

class TokenizerModuleBase(typing.NamedTuple):
    """
    extend this to add a seperate module to the tokenizer.. (ADD IT TO THE LIST OF MODULES)
    """


    #all the strings that this token matches
    matches: tuple[str, ...]

    #OUTPUT: tokenizer output
    #calculates the tokenizer output given the data
    @staticmethod
    def calculate(cursor: int, compiledTokens: list[Token], data: str) -> tuple[int, list, str]:
        """
        OUTPUT: tokenizer output
        calculates the tokenizer output given the data
        """
        token_string = ""
        while cursor < len(data) and token_string + data[cursor] in TokenizerModuleBase.matches:
            token_string += data[cursor]
            cursor += 1
        return cursor, compiledTokens, data
