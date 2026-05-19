from dataclasses import dataclass
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
    NEWLINE = enum.auto()
    INDENT_DEDENT = enum.auto()


class IndentType(enum.StrEnum):
    INDENT = enum.auto()
    DEDENT = enum.auto()


@dataclass(frozen=True, eq=False)
class Token:
    type: TokenType
    value: str

    def matches(self, type: TokenType, value: str) -> bool:
        return self.type == type and self.value == value

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

    def __repr__(self) -> str:
        match self.type, self.value:
            case TokenType.NEWLINE, _:
                return str(TokenType.NEWLINE)
            case TokenType.INDENT_DEDENT, i:
                return i
            case _:
                return f"({self.type}, {self.value})"
