from collections.abc import Iterator
import re

from .token import Token, TokenType, IndentType


def tokenize(input: str) -> tuple[Token, ...]:
    return strip_trailing_newline(remove_blank_lines(tuple(raw_tokenize(input))))


BLANK_LINE_CONTENT = frozenset({TokenType.NEWLINE, TokenType.INDENT_DEDENT})


def remove_blank_lines(raw: tuple[Token, ...]) -> tuple[Token, ...]:

    return tuple(
        t
        for i, t in enumerate(raw)
        if t.type != TokenType.NEWLINE
        or i == 0
        or raw[i - 1].type not in BLANK_LINE_CONTENT
    )


def strip_trailing_newline(raw: tuple[Token, ...]) -> tuple[Token, ...]:

    if raw[-2].type == TokenType.NEWLINE:
        return raw[:-2] + raw[-1:]

    return raw



TOKENS: tuple[tuple[str, str], ...] = (
    ("INT", r"[0-9]+"),
    ("STR", r'"(?:\\"|[^"])*?"'),
    ("COMMENT", r"(?:#|//)[^\n]*?(?=\n)|/\*(?:.|\n)*?\*/"),
    ("PUNC", r"[;(){}\[\]]|->"),
    # (";" | "(" | ")" | "{" | "}" | "[" | "]" | "$" | "->")
    ("NAME", r"[a-zA-Z_\$][a-zA-Z0-9_\.:/]*"),
    # NAME_MATCHES = string.ascii_letters + "_$"
    # NAME_CAN_CONTAIN = NAME_MATCHES + string.digits + ".:/"
    ("LINE", r"(?:\n|^)[ ]*"),
    ("WHITESPACE", r"\s+"),
    ("UNEXPECTED", r"."),
)


TOKEN_REGEX = re.compile(
    "|".join(rf"(?P<{name}>{pattern})" for name, pattern in TOKENS)
)


def raw_tokenize(input: str) -> Iterator[Token]:

    yield Token(TokenType.PUNC, "file_start")

    line_start = 0
    line_num = 1

    current_indent = 0

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

                newline_count = count_newlines(lexeme)

                if newline_count > 0:
                    line_num += newline_count
                    line_start = 0

            case "PUNC":
                yield Token(TokenType.PUNC, lexeme)

            case "NAME":
                yield Token(TokenType.NAME, lexeme)

            case "LINE":

                line_start = match_object.start() + 1
                line_num += 1

                yield Token(TokenType.NEWLINE, "")

                new_indent_raw = len(lexeme) - 1  # Exclude newline itself
                assert (
                    new_indent_raw % 4 == 0
                ), f"Indentation on line {line_num} is not divisible by 4"
                new_indent = round(new_indent_raw / 4)
                indentation_delta = new_indent - current_indent
                is_dedent = indentation_delta < 0

                for _ in range(abs(indentation_delta)):
                    yield Token(
                        TokenType.INDENT_DEDENT,
                        IndentType.DEDENT if is_dedent else IndentType.INDENT,
                    )

                current_indent = new_indent

            case "WHITESPACE":
                pass

            case _:  # UNEXPECTED
                raise ValueError(
                    f"Unexpected character '{lexeme}' at line {line_num} col {col_num} (categorized {type_string})"
                )

    yield Token(TokenType.PUNC, "EOF")


def count_newlines(s: str) -> int:
    return sum(1 if char == "\n" else 0 for char in s)
