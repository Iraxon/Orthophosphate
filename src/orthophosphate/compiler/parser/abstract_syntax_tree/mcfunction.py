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

class ScoreboardOperator(Enum):
    EQ = "="
    ADD = "+="
    SUB = "-="
    MUL = "*="
    DIV = "/="
    MOD = "%="
    MIN = "<"
    MAX = ">"
    SWP = "><"

    @staticmethod
    def of(s:str) -> "ScoreboardOperator":
        v = _op_map.get(s)
        if v is None:
            raise ValueError(f"Not a scoreboard operation: {s}")
        return v

_op_map: typing.Final = {op.value: op for op in ScoreboardOperator}

@dataclasses.dataclass(frozen=True)
class ScoreboardOperation(CMD):
    operand1: "Ref[VariableScore]"
    operand2: "Ref[VariableScore]" | "ConstantScore"
    operation: ScoreboardOperator

    @typing.override
    def children(self) -> Children:
        return (self.operand1, self.operation.value, self.operand2)

    @typing.override
    def compile(self) -> str:
        first = self.operand1
        second = self.operand2
        if isinstance(second, ConstantScore):
            return (
                f"{second.compile()}\n"
                + _operation_line(first, self.operation, second.ref())
            )
        else:
            return _operation_line(first, self.operation, second)

def _operation_line[S: Score](target: "Ref[VariableScore]", op: ScoreboardOperator, source: "Ref[S]") -> str:
    return f"scoreboard players operation {target.compile()} {op.value} {source.compile()}\n"

@dataclasses.dataclass(frozen=True)
class Score(Node):
    @abstractmethod
    def compile(self) -> str:
        raise NotImplementedError

@dataclasses.dataclass(frozen=True)
class VariableScore(Score):
    name: "str | TargetSelector"
    obj_ref: "Ref[OBJ]"

    @typing.override
    def children(self) -> Children:
        return (self.name, self.obj_ref)

    def compile(self) -> str:
        return f"{self.name if isinstance(self.name, str) else self.name.compile()} {self.obj_ref.compile()}"

@dataclasses.dataclass(frozen=True)
class ConstantScore(Score):
    value: int

    @typing.override
    def children(self) -> Children:
        return (str(self.value),)

    @typing.override
    def compile(self) -> str:
        return (
            "scoreboard objectives add opo4.constants dummy\n"
            + f"scoreboard players set C{self.value} opo4.constants {self.value}\n"
        )

    def ref(self) -> "Ref[ConstantScore]":
        """
        Returns a reference to this constant;
        it is possible for this to be done
        without ParseState because constants
        are always stored in the same place
        """
        return DotIdentifier.of(
            f"C{self.value} opo4.constants",
            self
        )

@dataclasses.dataclass(frozen=True)
class OBJ(CMD):
    name: str

    @typing.override
    def children(self):
        return (self.name,)

    @typing.override
    def compile(self) -> str:
        return f"scoreboard objectives add {self.name} dummy"

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
            raise ValueError(f"Not a scoreboard operation: {s}")
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
