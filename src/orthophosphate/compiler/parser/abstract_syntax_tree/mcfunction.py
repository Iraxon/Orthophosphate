from abc import abstractmethod
import dataclasses
from enum import Enum
import typing

from .meta import Children, DotIdentifier, Node, Ref

@dataclasses.dataclass(frozen=True)
class CMD(Node):
    @abstractmethod
    def compile(self) -> str:
        raise NotImplementedError

@dataclasses.dataclass(frozen=True)
class LiteralCMD(CMD):
    value: str

    @typing.override
    def children(self) -> Children:
        return (self.value,)

    @typing.override
    def compile(self):
        return f"{self.value}\n"

class SelectorVariable(Enum):
    P = "p"
    R = "r"
    A = "a"
    E = "e"
    S = "s"

    @staticmethod
    def of(s:str) -> "SelectorVariable":
        v = _sel_map.get(s)
        if v is None:
            raise ValueError(f"Not a target selector: @{s}")
        return v

_sel_map: typing.Final = {sel.value: sel for sel in SelectorVariable}

@dataclasses.dataclass(frozen=True)
class TargetSelector(Node):
    var: SelectorVariable
    arguments: str

    @typing.override
    def children(self) -> Children:
        return (self.compile()[1],)

    def compile(self) -> str:
        return f"@{self.var.value}{f'[{self.arguments}]' if self.arguments != '' else ''}"

    @classmethod
    def of(cls, s: str):
        match tuple(s):
            case ("@", x):
                return cls(SelectorVariable.of(x), "")
            case ("@", x, "[", *args, "]"):
                return cls(SelectorVariable.of(x), "".join(args))
            case _:
                raise ValueError(f"Invalid target selector: {s}")

@dataclasses.dataclass(frozen=True)
class Block(Node):
    value: tuple[CMD, ...]

    @typing.override
    def children(self) -> Children:
        return self.value

    def compile(self) -> str:
        return f"{"".join(cmd.compile() for cmd in self.value)}\n"
