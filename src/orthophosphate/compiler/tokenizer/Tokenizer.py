from enum import Enum, auto
import string
import typing

from .tokenizer_module_base import TokenizerModuleBase
from .token import Token, TokenType

# NEEDED CHANGES:
# finish class lol
# one character sub for tokens in the code


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


def tokenize(input: str) -> tuple[Token, ...]:

    output: list[Token] = []

    i: int = 0
    j: int = 0
    current_str: str
    matched_str: str
    possible_token: Token | SpecialCase | None

    output.append(Token(TokenType.PUNC, "file_start"))

    while i < len(input):

        j = i + 1
        current_str = ""
        matched_str = ""
        possible_token = None

        while j < len(input) + 1:  # j is an exclusive range closer

            current_str = input[i:j]
            char = current_str[-1]  # The thing just added

            if char.isspace() and not needs_whitespace(current_str):
                if not current_str.isspace():
                    # We hit whitespace after a token, and we don't need the whitespace, so we're done
                    break
                else:
                    # The whole thing is whitespace, so we report that to properly skip it
                    matched_str = current_str
                    possible_token = SpecialCase.WHITESPACE
                    break

            match token_of(current_str):
                case Token() | SpecialCase() as t:
                    matched_str = current_str
                    possible_token = t
                case None:
                    pass  # Invalid token; don't overwrite

            print(
                f"{i}:{j}, over <{input[i:j].replace("\n", "\\n")}>, with str {current_str}"
            )
            j += 1

        if possible_token is None:
            raise ValueError(
                f"No token match for {current_str} or any fragment thereof; last token: {output.pop()}"
                # Never an index error because of file_start Token
            )
        if isinstance(possible_token, Token):
            print(f"Matched {matched_str} -> {possible_token}")
            output.append(possible_token)
        i += len(matched_str)

    output.append(Token(TokenType.PUNC, "EOF"))  # End of file

    return tuple(output)


def is_whitespace(s: str) -> bool:
    return s.isspace()


def needs_whitespace(s: str) -> bool:
    """
    Returns whether this token fragment
    indicates that the tokenizer has to check
    for match possibilities that include whitespace.

    (i.e. Could this be the beginning of a string or comment?)
    """
    return any(s.startswith(prefix) for prefix in ('"', "//", "/*", "#"))


class SpecialCase(Enum):
    COMMENT = auto()
    WHITESPACE = auto()  # Not used by token_of() but by lexing logic directly


def token_of(s: str) -> Token | SpecialCase | None:
    """
    Returns the type of Token s is, or
    None if its not a valid token.

    Returns SpecialCase.COMMENT if this token is a comment.
    """

    if s.isdigit():
        return Token(TokenType.INT, s)

    if len(s) >= 2 and s.startswith('"') and s.endswith('"'):
        return Token(TokenType.STR, s[1:-1])

    if ((s.startswith("#") or s.startswith("//")) and s.endswith("\n")) or (
        s.startswith("/*") and s.endswith("*/")
    ):
        return SpecialCase.COMMENT

    match s:

        # Punctuation
        case (";" | "(" | ")" | "{" | "}" | "[" | "]" | "$" | "->") as p:
            return Token(TokenType.PUNC, p)

        # Name token or invalid
        case _:

            if (
                s != ""
                and s[0] in NAME_MATCHES
                and all(char in NAME_CAN_CONTAIN for char in s)
            ):
                return Token(TokenType.NAME, s)

            # Not a valid token
            return None


NAME_MATCHES = string.ascii_letters + "_$"
NAME_CAN_CONTAIN = NAME_MATCHES + string.digits + ".:/"


# helper function to print all the tokens
def printTokens(compiledTokens: list[Token]):
    for token in compiledTokens:
        print(token)
