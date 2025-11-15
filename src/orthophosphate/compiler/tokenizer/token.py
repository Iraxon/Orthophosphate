import enum
import typing

class TokenType(enum.Enum):
    NAME = enum.auto()
    PUNC = enum.auto()
    INT = enum.auto()
    STRING = enum.auto()
    LITERAL = enum.auto()
    SELECTOR = enum.auto()
    OP = enum.auto()

class Token(typing.NamedTuple):
    type: TokenType
    value: str

    def require_name(self) -> typing.Self:
        return self.require(TokenType.NAME)

    def require(self, type: TokenType) -> typing.Self:
        if (self.type != type):
            raise ValueError(f"Expected {type}, which {self} is not")
        return self

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value})"
