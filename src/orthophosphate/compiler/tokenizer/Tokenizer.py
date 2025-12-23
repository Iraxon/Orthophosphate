from collections.abc import Iterator
from enum import Enum, auto
import re

from .token import Token, TokenType


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
