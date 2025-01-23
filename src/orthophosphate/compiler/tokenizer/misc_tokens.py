from .tokenizer_module_base import TokenizerModuleBase
from .token import Token
import string

class AlphanumericToken(TokenizerModuleBase):

    matches = tuple(char for char in string.ascii_letters) + ("_", "$")
    can_contain = matches + tuple(char for char in string.digits) + (".",)

    def calculate(cursor, compiledTokens, data):

        fullString = ""

        while(cursor < len(data) and data[cursor] in AlphanumericToken.can_contain):

            fullString += data[cursor]
            cursor += 1

        match fullString:
            case (
                "func" | "tick_func" | "return"
                | "while"
                | "namespace" | "tag"
                | "obj" | "scoreboard" | "constant"
            ) as kw:
                compiledTokens.append(Token("keyword", kw))
            case "int" | "bool" as typ:
                compiledTokens.append(Token("type", typ))
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

    def semicolon(compiledTokens, include_start=True):
            """
            A function for adding a semicolon,
            to avoid reduplication of associated logic
            """
            paren(compiledTokens, ")")
            compiledTokens.append(Token("punc", ";"))
            if include_start:
                PunctuationToken.start(compiledTokens)

    def start(compiledTokens):
        """
        For adding invisible start tokens; exists for the
        same reason as the semicolon one
        """
        compiledTokens.append(Token("punc", "start"))
        paren(compiledTokens, "(")

    def calculate(cursor, compiledTokens, data):
        if(data[cursor] in PunctuationToken.matches):

            # Some of the punctuation characters have special actions,
            # so we handle those with this statement
            match data[cursor]:
                case ";":
                    PunctuationToken.semicolon(compiledTokens)
                case "{":
                    compiledTokens.append(Token("punc", "{"))
                    PunctuationToken.start(compiledTokens)
                case "}":
                    PunctuationToken.semicolon(compiledTokens, include_start=False)
                    compiledTokens.append(Token("punc", "}"))
                    PunctuationToken.semicolon(compiledTokens)
                case "(" | ")" as p:
                    # Parens need to be multiplied because of the
                    # operator-precedence algorithm used by the
                    # operators
                    paren(compiledTokens, p)

                case _:
                    compiledTokens.append(Token("punc", data[cursor]))
        return cursor, compiledTokens, data

# Constant function that returns the paren count for
# the least binding operator currently in
# the language
MAX_PAREN_COUNT = 5

def paren(compiledTokens, p):
    """
    Applies the equivalent of a single source-code paren
    """
    if p not in ("(", ")"):
        raise ValueError(f"'{p}' is not a paren")
    for _ in range(MAX_PAREN_COUNT + 1):
        compiledTokens.append(Token("punc", p))

class OperatorToken(TokenizerModuleBase):
    matches = ("+", "-", "*", "/", "%", "**", "=", "+=", "-=",
        "*=", "/=", "%=", "**=", "==", "!=", "<", ">", "<=", ">=",
        "<==", ">==", "><")

        # Scoreboard assign operators;
        # <== : assign if the value is less than current value
        # >== : assign if the value is greater than current value
        # >< : swap values of two scores (might not be supported)
        # These operators are added for low-level score management;
        # Minecraft has them

    isTerminating = True

    def calculate(cursor, compiledTokens, data):
        op_string = ""
        while cursor < len(data) and op_string + data[cursor] in OperatorToken.matches:
            op_string += data[cursor]
            cursor += 1

        # We use full parenthesization to do operator precedence.
        # https://en.wikipedia.org/wiki/Operator-precedence_parser#Full_parenthesization

        # If Wikipedia doesn't know how it works, I definitely don't know how it works.
        # But it worked for FORTRAN.

        # Small sub-functions to save typing
        def single_paren_close():
            compiledTokens.append(Token("punc", ")"))
        def single_paren_open():
            compiledTokens.append(Token("punc", "("))

        def parenthesize(paren_count, operator):
            """
            Applies n closing parens,
            appends the operator, and then
            applies n opening parens
            """
            for _ in range(paren_count):
                single_paren_close()
            compiledTokens.append(Token("op", operator))
            for _ in range(paren_count):
                single_paren_open()

        # In the special case of scoreboard operations, there
        # should not be any operator precedence because only
        # one operator is allowed there.

        if (compiledTokens[-3].type, compiledTokens[-3].value) == ("keyword", "scoreboard"):
            match op_string:
                case "=" | "+=" | "-=" | "/=" | "%=" | "<==" | ">==" | "><" as o:
                    compiledTokens.append(Token("op", o))
                case _ as o:
                    raise ValueError(f"Not a scoreboard operation: {o}")
            return cursor, compiledTokens, data

        # Higher precedence = lower paren count
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
                parenthesize(5, o)
            case "+" | "-" as o:
                parenthesize(3, o)
            case "*" | "/" as o:
                parenthesize(2, o)
            case "**" as o:
                parenthesize(1, o)
            case _ as o:
                raise ValueError(f"Tokenizer does not support operator {o}; cursor = {cursor}")

        return cursor, compiledTokens, data



"""
class ParenthesesToken(TokenizerModuleBase):

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

    matches = ("#", "//")

    isTerminating = True


    def calculate(cursor, compiledTokens, data):

        cursor += 1

        while(cursor < len(data) and data[cursor] != "\n"):
            cursor += 1

        return cursor, compiledTokens, data

class MultilineCommentToken(TokenizerModuleBase):

    matches = ("/*",)

    isTerminating = True

    def calculate(cursor, compiledTokens, data):

        cursor += 1

        while(cursor < len(data) - 2 and data[cursor:cursor+2] != "*/"):
            cursor += 1

        cursor += 1

        return cursor, compiledTokens, data