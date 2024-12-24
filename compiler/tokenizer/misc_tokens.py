from .tokenizer_module_base import TokenizerModuleBase
from .token import Token
import string

class NameToken(TokenizerModuleBase):

    matches = tuple(char for char in string.ascii_letters) + ("_",)
    can_contain = matches + tuple(char for char in string.digits) + (".",)

    def calculate(cursor, compiledTokens, data):

        fullString = ""

        while(data[cursor] in NameToken.can_contain):

            fullString += data[cursor]
            cursor += 1
        
        # Reserved keywords will be picked up by the matches,
        # so those are also handled here.
        match fullString:
            case "func":
                compiledTokens.append(Token("keyword", "func"))
            case "while":
                compiledTokens.append(Token("keyword", "while"))
            case "return":
                compiledTokens.append(Token("keyword", "return"))
            case _:
                compiledTokens.append(Token("name", fullString))

        return cursor, compiledTokens, data

class NumberToken(TokenizerModuleBase):
    matches = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")

    def calculate(cursor: int, compiledTokens: list[Token], data: str):
        
        fullNum = ""

        #adds the whole number
        while(cursor < len(data) and data[cursor] in NumberToken.matches):

            fullNum += data[cursor]
            cursor += 1

        #remove leading zeros; set value to "0" if this empties the string
        #(because the number was 0)
        for i in range(len(fullNum)):
            if(fullNum[i] == "0"):
                fullNum = fullNum[1:]
            else:
                break
        if fullNum == "":
            fullNum = "0"
        
        cursor -= 1

        compiledTokens.append(Token("int", fullNum))

        return cursor, compiledTokens, data

class WhiteSpaceToken(TokenizerModuleBase):
    matches = (" ", "", "\n")

    isTerminating = True

    def calculate(cursor: int, 
                  compiledTokens: list[Token], data: str):

        return cursor, compiledTokens, data
    
class StatementEndingToken(TokenizerModuleBase):
    matches = (";")

    isTerminating = True

    def calculate(cursor: int, compiledTokens: list[Token], data: str):

        compiledTokens.append(Token("punc", ";"))
        compiledTokens.append(Token("punc", "start"))
        
        return cursor, compiledTokens, data

class StringToken(TokenizerModuleBase):

    matches = ("\"")

    isTerminating = True

    def calculate(cursor, compiledTokens, data):

        #getting past first token
        cursor += 1

        fullString = ""

        while(data[cursor] != "\""):

            fullString += data[cursor]
            cursor += 1

        compiledTokens.append(Token("string", fullString))

        return cursor, compiledTokens, data

class MCFunctionLiteralToken(TokenizerModuleBase):

    matches = (":")

    isTerminating = True

    def calculate(cursor, compiledTokens, data):
        #getting past the first character
        cursor += 1

        fullString = ""
    
        while(data[cursor] != ":"):
            
            #making this command valid by removing backslash n's
            if(data[cursor] != "\n"):
                fullString += data[cursor]
            
            cursor += 1

        compiledTokens.append(Token("literal", fullString))

        return cursor, compiledTokens, data

class ParanthesesToken(TokenizerModuleBase):

    matches = ("(", ")")

    isTerminating = True

    def calculate(cursor, compiledTokens, data):

        if(data[cursor] == "("):
            compiledTokens.append(Token("punc", "("))
        else:
            compiledTokens.append(Token("punc", ")"))


        return cursor, compiledTokens, data
    
class CurlyBracketsToken(TokenizerModuleBase):
    
    matches = ("{", "}")

    isTerminating = True

    def calculate(cursor, compiledTokens, data):

        if(data[cursor] == "{"):
            compiledTokens.append(Token("punc", "{"))
            compiledTokens.append(Token("punc", "start"))
        else:
            if compiledTokens[-1].type == "punc" and compiledTokens[-1].value == "start":
                compiledTokens.pop() # Remove start token from the last curly brace if there was one
            compiledTokens.append(Token("punc", "}"))
            compiledTokens.append(Token("punc", ";"))
            compiledTokens.append(Token("punc", "start"))
        return cursor, compiledTokens, data
    

class CommentToken(TokenizerModuleBase):

    matches = ("#")

    isTerminating = True


    def calculate(cursor, compiledTokens, data):

        cursor += 1

        while(cursor < len(data) and data[cursor] != "\n"):
            cursor += 1

        return cursor, compiledTokens, data