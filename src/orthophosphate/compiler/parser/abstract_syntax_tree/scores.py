import dataclasses
from enum import Enum
import typing

from .mcfunction import CMD
from .meta import Children, Ref

raise NotImplementedError

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
    operand1: "Ref[ScoreValue]"
    operand2: "Ref[ScoreValue]" | "ConstantScore"
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
                + _operation_line(first, self.operation, second)
            )
        else:
            return _operation_line(first, self.operation, second)

def _operation_line(target: "VariableScore", op: ScoreboardOperator, source: "VariableScore | ConstantScore") -> str:
    return f"scoreboard players operation {target.compile()} {op.value} {source.compile()}\n"

@dataclasses.dataclass(frozen=True)
class ScoreValue(Node):
    @typing.override
    def children(self) -> Children:
        return ()

    @abstractmethod
    def compile(self) -> str:
        raise NotImplementedError

@dataclasses.dataclass(frozen=True)
class Expression(ScoreValue):
    left: Ref[ScoreValue]
    operator: ScoreboardOperator
    right: Ref[ScoreValue]

    @typing.override
    def children(self) -> Children:
        raise NotImplementedError

    @typing.override
    def compile(self) -> str:
        raise NotImplementedError

type Score = Ref[ScoreValue] | ConstantScore

@dataclasses.dataclass(frozen=True)
class VariableScore(Ref[ScoreValue]):
    score_holder: "str | TargetSelector"
    obj: "Ref[ScoreboardObjective]"

    @typing.override
    def children(self) -> Children:
        return (self.score_holder, self.obj)

    def compile(self) -> str:
        score_holder_str = self.score_holder if isinstance(self.score_holder, str) else self.score_holder.compile()
        return (f"{score_holder_str} {self.obj.compile()}")

@dataclasses.dataclass(frozen=True)
class ConstantScore(ScoreValue):
    value: int

    @typing.override
    def children(self) -> Children:
        return (str(self.value),)

    @typing.override
    def compile(self) -> str:
        return self.get_declaration()

    def get_declaration(self) -> str:
        """
        Returns the line of mcfunction needed
        to make sure the constant exists before it
        is referenced
        """
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
class ScoreboardObjective(CMD):
    id: str

    @typing.override
    def children(self):
        return (self.id,)

    @typing.override
    def compile(self) -> str:
        return f"scoreboard objectives add {self.id} dummy\n"
