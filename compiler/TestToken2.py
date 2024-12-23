from TokenizerModuleBase import TokenizerModuleBase
from Token import Token

class NumberToken(TokenizerModuleBase):
    matches = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")

    def calculate(cursor: int, compiledTokens: list[Token], data: str):
        
        print("len(data): ", len(data))

        fullNum = ""

        #adds the whole number
        while(cursor < len(data) and data[cursor] in NumberToken.matches):

            print("cursor: ", cursor)
            fullNum += data[cursor]
            cursor += 1

        #remove leading zeros
        for i in range(len(fullNum)):
            if(fullNum[i] == "0"):
                fullNum = fullNum[1:]
            else:
                break

        compiledTokens.append(Token("number", fullNum))

        return cursor, compiledTokens, data

class WhiteSpaceToken(TokenizerModuleBase):
    matches = (" ", "", "\n")

    isTerminating = True

    def calculate(cursor: int, 
                  compiledTokens: list[Token], data: str):

        return cursor, compiledTokens, data
    