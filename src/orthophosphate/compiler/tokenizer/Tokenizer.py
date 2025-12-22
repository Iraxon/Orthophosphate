from enum import Enum, auto
import string

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


def tokenize(input: str) -> tuple[Token, ...]:

    output: list[Token] = []

    i: int = 0
    j: int = 0
    current_str: str
    matched_str: str
    matched_token: Token | SpecialCase | None

    # Indentation tracking counters
    indent_counter: int = 0
    paren_counter: int = 0  # Needed because indentation inside parens doesn't matter

    output.append(Token(TokenType.PUNC, "file_start"))

    while i < len(input):

        j = i + 1
        current_str = ""
        matched_str = ""
        matched_token = None

        while j < len(input) + 1:  # j is an exclusive range closer

            current_str = input[i:j]

            if can_terminate(current_str):
                # Stop looking ahead if we can
                break

            match token_of(
                current_str,
                indents_matter=(paren_counter == 0),
                current_indentation=indent_counter,
            ):
                case Token() | SpecialCase() as t:
                    matched_str = current_str
                    matched_token = t

                case None:
                    pass  # Invalid token; don't overwrite

            print(
                f"{i}:{j}, over <{input[i:j].replace("\n", "\\n")}>, with str {current_str}"
            )
            j += 1

        if matched_token is None:

            raise ValueError(
                f"No token match for {current_str} or any fragment thereof; last token: {output.pop()}"
                # Never an index error because of file_start Token
            )

        elif isinstance(matched_token, Token):

            print(f"Matched {matched_str} -> {matched_token}")
            output.append(matched_token)

            # Paren counting
            if matched_token == Token(TokenType.PUNC, "("):
                paren_counter += 1
            elif matched_token == Token(TokenType.PUNC, ")"):
                paren_counter -= 1

            if paren_counter < 0:
                raise ValueError(
                    f"Unmatched closing parenthesis at {get_ln_and_col(input, i)}"
                )

            # Indent counting
            if matched_token.type == TokenType.NEWLINE_INDENT:
                indent_counter += int(matched_token.value)

        i += len(matched_str)

    output.append(Token(TokenType.PUNC, "EOF"))  # End of file

    return tuple(output)


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


def token_of(
    s: str, indents_matter: bool, current_indentation: int
) -> Token | SpecialCase | None:
    """
    Returns the type of Token s is, or
    None if its not a valid token.

    Returns SpecialCase instances for things the lexer
    recognizes that must be ignored (e.g. comments).
    """

    if s.isspace():

        if indents_matter and "\n" in s:

            new_indentation = len(s) - len(s.rstrip(" "))
            indentation_delta = new_indentation - current_indentation

            # Indentation logic to be turned on later when the Parser
            # is upgraded to understand indentation

            # return Token(TokenType.NEWLINE_INDENT, str(indentation_delta))
            return SpecialCase.WHITESPACE

        else:
            return SpecialCase.WHITESPACE

    if s.isdigit():
        return Token(TokenType.INT, s)

    if len(s) >= 2 and s.startswith('"') and s.endswith('"'):
        return Token(TokenType.STR, s[1:-1])

    if (
        (
            (s.startswith("#") or s.startswith("//"))
            and s.endswith("\n")
            and "\n" not in s[0:-1]  # Line comments can't contain newlines!
        )
        or s.startswith("/*")
        and s.endswith("*/")
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
