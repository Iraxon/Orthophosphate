import typing

from .tokenizer_module_base import TokenizerModuleBase
from .token import Token, TokenType
from .tokens import TOKEN_MODULES, PunctuationToken, WhiteSpaceToken

#NEEDED CHANGES:
#finish class lol
#one character sub for tokens in the code

def get_ln_and_col(s: str, index) -> tuple[int, int]:
    """
    Returns the line and column of
    an index in a string with newlines
    """
    if s == "":
        return 0, 0
    elif len(s) == 1:
        return 1, 1
    lines = "\n".split(s[:index + 1])
    col = len(lines[-1])
    return len(lines), col

#helper data set. Maps every token string to the token it is a part of
token_strings: dict[str, typing.Callable[[int, list[Token], str], tuple[int, list[Token], str]]] = {
    match: token.calculate
    for token in TOKEN_MODULES #this is defined in token_modules
    for match in token.matches
}

def tokenize(input : str) -> tuple[Token, ...]:

    data : str = input

    #where the tokenizer is in the data
    cursor : int = 0

    #the current token. This is needed because most tokens are more than one character long
    token : str = ""

    #the currently compiled tokens
    compiledTokens : list[Token] = []

    # Invisible punctuation added to start of file
    compiledTokens.append(Token(TokenType.PUNC, "file_start"))
    PunctuationToken.start(compiledTokens)

    #logic
    while(cursor < len(data)):
        token = data[cursor]

        if token not in WhiteSpaceToken.matches: # We don't do anything for whitespace

            # Look ahead with an inner loop
            # and try to see what tokens
            # this character could be the start of
            possible_tokens = []
            inner_token = ""
            inner_cursor = cursor
            while (inner_cursor < len(data)) and (data[inner_cursor] not in WhiteSpaceToken.matches):
                inner_token += data[inner_cursor]
                if inner_token in token_strings:
                    possible_tokens.append(inner_token)
                inner_cursor += 1
                # print(f"Inner tokenizer loop running: {cursor}:{inner_cursor} on {inner_token}")
            # print(possible_tokens)

            # Decide on which token module to get calculate() from
            if len(possible_tokens) >= 1:
                chosen_token = sorted(possible_tokens, key=len, reverse=True)[0] # Get the longest of the possible tokens
            else:
                raise ValueError(f"Token {token} has no matches")

            # Apply calculate()
            cursor, compiledTokens, data = token_strings[chosen_token](
                cursor,
                compiledTokens,
                data
            )
            # print(compiledTokens[-1])
        cursor += 1
        # print(f"Outer tokenizer loop running: {cursor} on {token}")

    # Close the excess start token that will be found
    # after the last semicolon
    PunctuationToken.semicolon(compiledTokens, include_start=False)
    compiledTokens.append(Token(TokenType.PUNC, "EOF"))

    return tuple(compiledTokens)

#helper function to print all the tokens
def printTokens(compiledTokens : list[Token]):
    for token in compiledTokens:
        print(token)
