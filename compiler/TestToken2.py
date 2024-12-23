from TokenizerModuleBase import TokenizerModuleBase
from Token import Token

class TestToken2(TokenizerModuleBase):
    tokens = ("1")

    def calculate(cursor: int, compiledTokens: list[Token], data: str):
        print("found 1")

class TestToken1(TokenizerModuleBase):
    tokens = ("2")

    def calculate(cursor: int, compiledTokens: list[Token], data: str):
        print("found 2")