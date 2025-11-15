import enum
import typing

class TokenType(enum.Enum):
    ALPHANUMERIC = enum.auto()
    PUNC = enum.auto()
    INT = enum.auto()
    STRING = enum.auto()
    LITERAL = enum.auto()
    SELECTOR = enum.auto()
    OP = enum.auto()

class Token(typing.NamedTuple):
    type: TokenType
    value: str

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value})"
