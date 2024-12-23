import typing
from compiler.Token import Token

class TokenizerOutput(typing.NamedTuple):
    """
    the output from the tokenizer module base class. Allows expandability
    """

    #the data that will be tokenized
    data: str

    #where the cursor is in the data
    cursor: int

    #the tokens that have been found
    tokens: list[Token]
