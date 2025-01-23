import typing
from .token import Token

class TokenizerModuleBase(typing.NamedTuple):
    """
    extend this to add a seperate module to the tokenizer.. (ADD IT TO THE LIST OF MODULES)
    """


    #all the tokens that will call this module
    tokens: tuple = tuple()

    #if the module needs white space to be considered a token. CAN ONLY BE ONE CHARACTER!! THIS IS A VERY DANGEROUS VARIABLE TO CHANGE!!!
    isTerminating: bool = True

    #OUTPUT: tokenizer output
    #calculates the tokenizer output given the data
    @staticmethod
    def calculate(cursor: int, compiledTokens: list[Token], data: str) -> tuple:
        """
        OUTPUT: tokenizer output
        calculates the tokenizer output given the data
        """
        raise NotImplementedError(f"Tokenizer module fails to implement calculate")
