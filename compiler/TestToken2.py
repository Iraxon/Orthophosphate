from TokenizerModuleBase import TokenizerModuleBase
from Token import Token

class TestToken2(TokenizerModuleBase):
    tokens = ("1")

    def calculate(cursor: int, compiledTokens: list[Token], data: str):
        print("found 1")

        compiledTokens.append(Token("number", "1"))

        return cursor, compiledTokens, data

class TestToken1(TokenizerModuleBase):
    tokens = ("2")

    def calculate(cursor: int, compiledTokens: list[Token], data: str):
        print("found 2")

        compiledTokens.append(Token("number", "2"))

        return cursor, compiledTokens, data

class TestToken3(TokenizerModuleBase):
    tokens = (" ", "", "\n")

    isTerminating = True

    def calculate(cursor: int, compiledTokens: list[Token], data: str):
        print("found space")

        return cursor, compiledTokens, data