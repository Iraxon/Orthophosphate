from .tokenizer_module_base import TokenizerModuleBase
from .token import Token
import string

class AlphanumericToken(TokenizerModuleBase):

    matches = tuple(char for char in string.ascii_letters) + ("_",)
    can_contain = matches + tuple(char for char in string.digits) + (".",)

    def calculate(cursor, compiledTokens, data):

        fullString = ""

        while(cursor < len(data) and data[cursor] in AlphanumericToken.can_contain):

            fullString += data[cursor]
            cursor += 1
        
        match fullString:
            case "let" | "func" | "tick_func" | "while" | "return" | "namespace" | "tag" as kw:
                compiledTokens.append(Token("keyword", kw))
            case _:
                compiledTokens.append(Token("name", fullString))
        
        cursor -= 1

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

""" 
class StatementEndingToken(TokenizerModuleBase):
    matches = (";")

    isTerminating = True

    def calculate(cursor: int, compiledTokens: list[Token], data: str):

        compiledTokens.append(Token("punc", ";"))
        compiledTokens.append(Token("punc", "start"))
        
        return cursor, compiledTokens, data
"""
     
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
    
        while(data[cursor] != ":" and cursor < len(data)):
            
            #making this command valid by removing backslash n's
            if(data[cursor] != "\n"):
                fullString += data[cursor]
            
            cursor += 1

        compiledTokens.append(Token("literal", fullString))

        return cursor, compiledTokens, data

class PunctuationToken(TokenizerModuleBase):
    matches = (";", "(", ")", "{", "}")

    isTerminating = True

    def calculate(cursor, compiledTokens, data):
        if(data[cursor] in PunctuationToken.matches):

            # Some of the punctuation characters have special actions,
            # so we handle those with this statement
            match data[cursor]:
                case ";":
                    compiledTokens.append(Token("punc", ";"))
                    compiledTokens.append(Token("punc", "start"))
                case "{":
                    compiledTokens.append(Token("punc", "{"))
                    compiledTokens.append(Token("punc", "start"))
                case "}":
                    compiledTokens.append(Token("punc", ";"))
                    compiledTokens.append(Token("punc", "}"))
                    compiledTokens.append(Token("punc", ";"))
                    compiledTokens.append(Token("punc", "start"))
                case "(" | ")" as p:
                    # Parans need to be multiplied because of the
                    # operator-precedence algorithm used by the
                    # operators
                    for _ in range(MAX_PARAN_COUNT + 1):
                        compiledTokens.append(Token("punc", p))

                case _:
                    compiledTokens.append(Token("punc", data[cursor]))
        return cursor, compiledTokens, data

# Constant that stores the paran count for
# the least binding operator currently in
# the language
MAX_PARAN_COUNT = 5

class OperatorToken(TokenizerModuleBase):
    matches = ("+", "-", "*", "/", "%", "**", "=", "+=", "-=", "*=", "/=", "%=", "**=", "==", "!=", "<", ">", "<=", ">=")

    isTerminating = True

    def calculate(cursor, compiledTokens, data):
        op_string = ""
        if data[cursor] in OperatorToken.matches:
            op_string += data[cursor]
            cursor += 1
        if cursor < len(data) and op_string + data[cursor] in OperatorToken.matches:
            op_string += data[cursor]
            cursor += 1
        if cursor < len(data) and op_string + data[cursor] in OperatorToken.matches:
            op_string += data[cursor]
        
        # We use full paranthetization to do operator precedence.
        # https://en.wikipedia.org/wiki/Operator-precedence_parser#Full_parenthesization

        # If Wikipedia doesn't know how it works, I definitely don't know how it works.
        # But it worked for FORTRAN.

        # Small sub-functions to save typing
        def paran_close():
            compiledTokens.append(Token("punc", ")"))
        def paran_open():
            compiledTokens.append(Token("punc", "("))
        
        def paranthesize(paran_count, operator):
            """
            Applies n closing parans,
            runs the func, and then
            applies n opening parans
            """
            for _ in range(paran_count):
                paran_close()
            compiledTokens.append(Token("op", operator))
            for _ in range(paran_count):
                paran_open()
        
        # Higher precedence = lower paran count
        # Unary operators are a complication, but we may not need
        # to support them. We could also add tokens to make them
        # unary for the user but binary to a constant for the
        # parser
        #
        # e.g. (-1) generates tokens for (0 - 1)
        # and sin(x) is turned into 0 sin x where the first
        # operand does nothing

        match op_string:
            case "=" | "+=" | "-=" | "*=" | "/=" | "%=" | "**=" as o:
                paranthesize(5, o)
            
            case "@" as o:
                paranthesize(4, o)

            case "+" | "-" as o:
                paranthesize(3, o)
            
            case "*" | "/" as o:
                paranthesize(2, o)
            
            case "**" as o:
                paranthesize(1, o)

        return cursor, compiledTokens, data



"""
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
"""
    

class CommentToken(TokenizerModuleBase):

    matches = ("#")

    isTerminating = True


    def calculate(cursor, compiledTokens, data):

        cursor += 1

        while(cursor < len(data) and data[cursor] != "\n"):
            cursor += 1

        return cursor, compiledTokens, data