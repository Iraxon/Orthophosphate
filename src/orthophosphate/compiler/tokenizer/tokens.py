from .tokenizer_module_base import TokenizerModuleBase
from .token import Token, TokenType
import string

#
#
# Remember to add new token modules to the tuple at the bottom of the file!
#
#


class AlphanumericToken(TokenizerModuleBase):

    matches = tuple(char for char in string.ascii_letters) + ("_", "$")
    can_contain = matches + tuple(char for char in string.digits) + (".", ":", "/")

    @staticmethod
    def calculate(cursor, compiledTokens, data):

        fullString = ""

        while cursor < len(data) and data[cursor] in AlphanumericToken.can_contain:

            fullString += data[cursor]
            cursor += 1

        compiledTokens.append(Token(TokenType.NAME, fullString))

        cursor -= 1

        return cursor, compiledTokens, data


class NumberToken(TokenizerModuleBase):
    matches = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")

    @staticmethod
    def calculate(cursor: int, compiledTokens: list[Token], data: str):

        fullNum = ""

        # adds the whole number
        while cursor < len(data) and data[cursor] in NumberToken.matches:

            fullNum += data[cursor]
            cursor += 1

        # remove leading zeros; set value to "0" if this empties the string
        # (because the number was 0)
        for i in range(len(fullNum)):
            if fullNum[i] == "0":
                fullNum = fullNum[1:]
            else:
                break
        if fullNum == "":
            fullNum = "0"

        cursor -= 1

        compiledTokens.append(Token(TokenType.INT, fullNum))

        return cursor, compiledTokens, data


class WhiteSpaceToken(TokenizerModuleBase):
    matches = (" ", "", "\n")

    isTerminating = True

    @staticmethod
    def calculate(cursor: int, compiledTokens: list[Token], data: str):

        return cursor, compiledTokens, data


class StringToken(TokenizerModuleBase):

    matches = ('"',)

    isTerminating = True

    @staticmethod
    def calculate(cursor, compiledTokens, data):

        # getting past first token
        cursor += 1

        fullString = ""

        while data[cursor] != '"':

            fullString += data[cursor]
            cursor += 1

        compiledTokens.append(Token(TokenType.STRING, fullString))

        return cursor, compiledTokens, data


class MCFunctionLiteralToken(TokenizerModuleBase):

    matches = ("|",)

    isTerminating = True

    @staticmethod
    def calculate(cursor, compiledTokens, data):
        # getting past the first character
        cursor += 1

        fullString = ""

        while (data[cursor] != "|") and cursor < len(data):

            # making this command valid by resolving all whitespace to a single space
            if data[cursor] in WhiteSpaceToken.matches:
                if fullString[-1] != " ":
                    fullString += " "
            else:
                fullString += data[cursor]

            cursor += 1

        compiledTokens.append(Token(TokenType.LITERAL, fullString))

        return cursor, compiledTokens, data


class PunctuationToken(TokenizerModuleBase):
    matches = (";", "(", ")", "{", "}")

    isTerminating = True

    @staticmethod
    def calculate(cursor, compiledTokens, data):
        if data[cursor] in PunctuationToken.matches:
            compiledTokens.append(Token(TokenType.PUNC, data[cursor]))
        return cursor, compiledTokens, data


# Constant function that returns the paren count for
# the least binding operator currently in
# the language
MAX_PAREN_COUNT = 5


def paren(compiledTokens, p):
    # """
    # Applies the equivalent of a single source-code paren
    # """
    # if p not in ("(", ")"):
    #     raise ValueError(f"'{p}' is not a paren")
    # for _ in range(MAX_PAREN_COUNT + 1):
    #     compiledTokens.append(Token(TokenType.PUNC, p))
    pass


class OperatorToken(TokenizerModuleBase):
    matches = (
        "+",
        "-",
        "*",
        "/",
        "%",
        "**",
        "=",
        "+=",
        "-=",
        "*=",
        "/=",
        "%=",
        "**=",
        "==",
        "!=",
        "<",
        ">",
        "<=",
        ">=",
        "<==",
        ">==",
        "><",
    )

    # Scoreboard assign operators;
    # <== : assign if the value is less than current value
    # >== : assign if the value is greater than current value
    # >< : swap values of two scores (might not be supported)
    # These operators are added for low-level score management;
    # Minecraft has them

    isTerminating = True

    @staticmethod
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
            compiledTokens.append(Token(TokenType.PUNC, ")"))

        def single_paren_open():
            compiledTokens.append(Token(TokenType.PUNC, "("))

        def parenthesize(paren_count, operator):
            """
            Applies n closing parens,
            appends the operator, and then
            applies n opening parens
            """
            # for _ in range(paren_count):
            #     single_paren_close()
            compiledTokens.append(Token(TokenType.OP, operator))
            # for _ in range(paren_count):
            #     single_paren_open()

        # In the special case of scoreboard operations, there
        # should not be any operator precedence because only
        # one operator is allowed there.

        if (compiledTokens[-3].type, compiledTokens[-3].value) == (
            TokenType.NAME,
            "score",
        ):
            match op_string:
                case "=" | "+=" | "-=" | "/=" | "%=" | "<==" | ">==" | "><" as o:
                    compiledTokens.append(Token(TokenType.OP, o))
                case _ as o:
                    raise ValueError(f"Not a scoreboard operation: {o}")
            return cursor, compiledTokens, data

        # !!! Higher precedence = lower paren count

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
                raise ValueError(
                    f"Tokenizer does not support operator {o}; cursor = {cursor}"
                )

        return cursor, compiledTokens, data


class CommentToken(TokenizerModuleBase):

    matches = ("#", "//")

    isTerminating = True

    @staticmethod
    def calculate(cursor, compiledTokens, data):

        cursor += 1  # No need to compensate for two
        # char start in case of // because loop
        # will roll over it all anyway

        while cursor < len(data) and data[cursor] != "\n":
            cursor += 1

        return cursor, compiledTokens, data


class MultilineCommentToken(TokenizerModuleBase):

    matches = ("/*",)

    isTerminating = True

    @staticmethod
    def calculate(cursor, compiledTokens, data):

        cursor += 1  # We don't need to compensate for
        # two character start because the loop will roll over
        # the asterisk anyway

        while cursor < len(data) - 2 and data[cursor : cursor + 2] != "*/":
            cursor += 1

        cursor += 1  # Compensate for two-character end marker

        return cursor, compiledTokens, data


class SelectorToken(TokenizerModuleBase):

    matches = tuple("@,")
    can_contain = (
        AlphanumericToken.matches
        + WhiteSpaceToken.matches
        + tuple(char for char in string.digits)
        + (".", ":", "!", "[", "]", "=", "*")
    )

    @staticmethod
    def calculate(cursor, compiledTokens, data):

        fullString = data[cursor]  # Capture the starting @ sign
        cursor += 1

        while (
            cursor < len(data)
            and data[cursor] in SelectorToken.can_contain
            and data[cursor] != "]"
        ):

            fullString += data[cursor]
            cursor += 1

        if data[cursor] == "]":  # Bring in ending delimeter
            fullString += "]"

        compiledTokens.append(Token(TokenType.SELECTOR, fullString))

        return cursor, compiledTokens, data


# the list of all the recognized token modules. Used this to add new tokens
TOKEN_MODULES = (
    AlphanumericToken,
    NumberToken,
    WhiteSpaceToken,
    StringToken,
    MCFunctionLiteralToken,
    PunctuationToken,
    CommentToken,
    MultilineCommentToken,
    OperatorToken,
    SelectorToken,
)
