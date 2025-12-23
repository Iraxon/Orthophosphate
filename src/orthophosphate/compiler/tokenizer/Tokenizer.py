from collections.abc import Iterator
from enum import Enum, auto
import re

from .token import Token, TokenType


def get_ln_and_col(s: str, index) -> tuple[int, int]:
    """
    Returns the line and column of
    an index in a string with newlines
    """
    if s == "":
        return 0, 0
    elif len(s) == 1:
        return 1, 1
    lines = "\n".split(s[: index + 1])
    col = len(lines[-1])
    return len(lines), col


TOKENS: tuple[tuple[str, str], ...] = (
    ("INT", r"[0-9]+"),
    ("STR", r'"(?:\\"|[^"])*?"'),
    ("COMMENT", r"(?:(?:#|//).*?$)|/\*.*?\*/"),
    ("PUNC", r"[;(){}\[\]\$]|->"),
    # (";" | "(" | ")" | "{" | "}" | "[" | "]" | "$" | "->")
    ("NAME", r"[a-zA-Z_\$][a-zA-Z0-9_\.:/]*"),
    # NAME_MATCHES = string.ascii_letters + "_$"
    # NAME_CAN_CONTAIN = NAME_MATCHES + string.digits + ".:/"
    ("NEWLINE", r"\n"),
    ("WHITESPACE", r"\s"),
    ("UNEXPECTED", r"."),
)


TOKEN_REGEX = re.compile(
    "(?m)" + "|".join(rf"(?P<{name}>{pattern})" for name, pattern in TOKENS)
)


def tokenize(input: str) -> Iterator[Token]:

    yield Token(TokenType.PUNC, "file_start")

    line_start = 0
    line_num = 1

    for match_object in re.finditer(TOKEN_REGEX, input):

        type_string = match_object.lastgroup
        lexeme = match_object.group()
        col_num = match_object.start() - line_start

        match type_string:

            case "INT":
                yield Token(TokenType.INT, lexeme)

            case "STR":
                yield Token(TokenType.STR, lexeme)

            case "COMMENT":
                pass

            case "PUNC":
                yield Token(TokenType.PUNC, lexeme)

            case "NAME":
                yield Token(TokenType.NAME, lexeme)

            case "NEWLINE":
                line_start = match_object.end()
                line_num += 1

            case "WHITESPACE":
                pass

            case _:  # UNEXPECTED
                raise ValueError(
                    f"Unexpected character '{lexeme}' at line {line_num} col {col_num} (categorized {type_string})"
                )

    yield Token(TokenType.PUNC, "EOF")


def can_terminate(s: str) -> bool:
    """
    Notices things such as "A token
    made of non whitespace characters usually
    can't contain whitespace, so we don't
    need to keep looking ahead if we hit it"

    s is the string being considered; s[-1] is
    the newest character
    """
    before, char = s[:-1], s[-1]

    if char.isspace() and not needs_whitespace(s):
        return True

    # Whitespace can't ever contain non-whitespace
    if before.isspace() and not char.isspace():
        return True

    return False


def needs_whitespace(s: str) -> bool:
    """
    Returns whether this token fragment
    indicates that the tokenizer has to check
    for match possibilities that include whitespace.

    (i.e. Could this be the beginning of a string or comment?)
    """
    return any(s.startswith(prefix) for prefix in ('"', "//", "/*", "#")) or s.isspace()


class SpecialCase(Enum):
    COMMENT = auto()
    WHITESPACE = auto()


# helper function to print all the tokens
def printTokens(compiledTokens: list[Token]):
    for token in compiledTokens:
        print(token)
