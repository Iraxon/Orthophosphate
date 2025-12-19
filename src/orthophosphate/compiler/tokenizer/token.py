import enum
import typing


class TokenType(enum.Enum):
    NAME = enum.auto()
    PUNC = enum.auto()
    INT = enum.auto()
    STR = enum.auto()
    LITERAL = enum.auto()
    SELECTOR = enum.auto()
    OP = enum.auto()


class Token(typing.NamedTuple):
    type: TokenType
    value: str

    def require_name(self) -> typing.Self:
        """
        Raises an error if the token isn't of type TokenType.NAME

        Returns self so you can chain it
        """
        return self.require_type(TokenType.NAME)

    def require_type(self, type: TokenType) -> typing.Self:
        """
        Raises an error if the token does not have the provided type

        Returns self so you can chain it
        """

        if self.type != type:
            raise ValueError(f"Expected {type}, which {self} is not")
        return self

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value})"
