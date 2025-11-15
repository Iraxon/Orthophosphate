from abc import ABC, abstractmethod
import dataclasses
from enum import Enum
import os
import typing

from ..tokenizer.token import Token

type Children = "tuple[Node | str, ...]"

@dataclasses.dataclass(frozen=True)
class Node(ABC):
    """
    A node in the abstract syntax tree
    """
    @abstractmethod
    def children(self) -> Children:
        """
        Provides that which the node should display as its children when rendered
        """
        raise NotImplementedError

    def __str__(self) -> str:
        return self.render()

    def render(self, pre="") -> str:
        """
        Provides a nice readable string
        rep of the AST with nesting

        This function is recursive and
        dangerous to the sanity of anyone
        who works on it
        """
        children = self.children()

        render_contents: tuple[str, ...] = tuple(
            child.render(f"{pre}{'║ ' if i < len(children) - 1 else '  '}")
            if isinstance(child, Node)
            else f"═ {child}"
            for i, child in enumerate(children)
        )
        return (
            f"{'' if pre == '' else'═'} {self.__class__.__name__}\n"
            + "".join(
                    tuple(
                        f"{pre}╠{element}\n"
                        if i < len(render_contents) - 1
                        else f"{pre}╚{element}"
                        for i, element in enumerate(render_contents)
                    )
                )
        )

@dataclasses.dataclass(frozen=True)
class Ref[T](Node):
    referent: T

    @typing.override
    def children(self) -> Children:
        return (self.realize(),)

    @abstractmethod
    def realize(self) -> str:
        raise NotImplementedError

@dataclasses.dataclass(frozen=True)
class Root(Node):
    value: "tuple[TextFile, ...]"

    @typing.override
    def children(self) -> Children:
        return self.value

@dataclasses.dataclass(frozen=True)
class NamespacedIdentifier[T](Ref[T]):
    namespace: str
    name: str

    @typing.override
    def __str__(self):
        return self.show()

    def show(self) -> str:
        return f"{self.namespace}{self.sep()}{self.name}"

    @classmethod
    @abstractmethod
    def sep(cls) -> typing.Literal[":", "."]:
        raise NotImplementedError

    @classmethod
    def of(cls, s: str | Token) -> typing.Self:
        if isinstance(s, Token):
            s = s.require_name().value
        return NamespacedIdentifier._of_helper(s, cls.sep(), cls)

    @staticmethod
    def _of_helper[T](s: str, split_char: str, constructor: typing.Callable[[str, str], T]) -> T:
        match s.split(split_char):
            case (name,):
                return constructor(_placeholder_namespace, name)
            case first, second:
                return constructor(first, second)
            case _:
                raise ValueError(f"Malformed namespace: {s}")

_placeholder_namespace: typing.Final = "x"

@dataclasses.dataclass(frozen=True)
class ColonIdentifier(NamespacedIdentifier):
    @classmethod
    @typing.override
    def sep(cls) -> typing.Literal[":"]:
        return ":"

    @classmethod
    def of_sequence(cls, *parts: str) -> typing.Self:
        return cls(parts[0], "/".join(parts[1:]))

@dataclasses.dataclass(frozen=True)
class DotIdentifier(NamespacedIdentifier):
    @classmethod
    @typing.override
    def sep(cls) -> typing.Literal["."]:
        return "."

    @classmethod
    def of_sequence(cls, *parts: str) -> typing.Self:
        return cls(parts[0], ".".join(parts[1:]))

@dataclasses.dataclass(frozen=True)
class TextFile(Node):
    @abstractmethod
    def realize(self) -> str:
        raise NotImplementedError

@dataclasses.dataclass(frozen=True)
class MCFunction(TextFile):
    id: ColonIdentifier
    body: "Block"

    @typing.override
    def children(self) -> Children:
        return (self.id.show(), self.body)

    @typing.override
    def realize(self):
        return (self.id, self.body)

type Taggable = MCFunction

# class TagType(Enum):
#     BLOCK = "blocks"
#     ITEM = "items"
#     FUNCTION = "function"
#     FLUID = "fluids"
#     ENTITY_TYPE = "entity_types"
#     GAME_EVENT = "game_events"
#     BIOME = "biome"
#     FLAT_LEVEL_GENERATOR_PRESET = "flat_level_generator_preset"
#     WORLD_PRESET = "world_preset"
#     STRUCTURE = "structure"
#     CAT_VARIANT = "cat_variant"
#     POINT_OF_INTERST_TYPE = "point_of_interest_type"
#     PAINTING_VARIANT = "painting_variant"
#     BANNER_PATTERN = "banner_pattern"
#     INSTRUMENT = "instrument"
#     DAMAGE_TYPE = "damage_type"

@dataclasses.dataclass(frozen=True)
class Tag[T: Taggable](TextFile):
    id: ColonIdentifier
    content: "tuple[Ref[T] | Ref[Tag[T]], ...]"
    replace: bool = False

    @typing.override
    def children(self) -> Children:
        return (str(self.replace),) + tuple(item for item in self.content)

    @typing.override
    def realize(self) -> str:
        raise NotImplementedError # Got to figure out how to get IDs and not str() output
        return (
        "{\n"
        + f"  \"replace\": {'true' if self.replace else 'false'},\n"
        + "  \"values\": [\n"
        + "".join(tuple(
            f"    \"{item}\"{',' if i < len(self.content) - 1 else ''}\n" for i, item in enumerate(self.content)
        ))
        + "  ]\n"
        + "}"
    )

@dataclasses.dataclass(frozen=True)
class LiteralValue[T](Node):
    value: T

    @typing.override
    def children(self) -> Children:
        return (str(self.value),)

@dataclasses.dataclass(frozen=True)
class CMD(Node):
    @abstractmethod
    def realize(self) -> str:
        raise NotImplementedError

@dataclasses.dataclass(frozen=True)
class LiteralCMD(CMD):
    value: str

    @typing.override
    def children(self) -> Children:
        return (self.value,)

    @typing.override
    def realize(self):
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
    operand1: "Score"
    operand2: "Score"
    operation: ScoreboardOperator

    @typing.override
    def children(self) -> Children:
        return (self.operand1, self.operation.value, self.operand2)

    @typing.override
    def realize(self) -> str:
        first_pre, first = self.operand1.realize()
        second_pre, second = self.operand2.realize()
        return (
            f"{first_pre}\n{second_pre}\n"
            + f"scoreboard players operation {first} {self.operation.value} {second}\n"
        )

@dataclasses.dataclass(frozen=True)
class CMDFragment(Node):
    @abstractmethod
    def realize(self) -> tuple[str, str]:
        """
        The first str is any preparation commands that must be run to calculate the value;
        the second is the name under which this value has been stored, for higher nodes to retrieve

        See {ConstantScore} for an example
        """
        raise NotImplementedError

@dataclasses.dataclass(frozen=True)
class Score(CMDFragment):
    pass

@dataclasses.dataclass(frozen=True)
class VariableScore(Score):
    name: "str | TargetSelector"
    objective: "OBJ"

    @typing.override
    def children(self) -> Children:
        return (self.name, self.objective)

    @typing.override
    def realize(self) -> tuple[str, str]:
        return ("", f"{self.name if isinstance(self.name, str) else self.name.realize()} {self.objective.realize()}")

@dataclasses.dataclass(frozen=True)
class ConstantScore(Score):
    value: int

    @typing.override
    def children(self) -> Children:
        return (str(self.value),)

    @typing.override
    def realize(self) -> tuple[str, str]:
        return (
            "scoreboard objectives add opo4.constants dummy\n"
            + f"scoreboard players set C{self.value} opo4.constants {self.value}\n",
            f"C{self.value} opo4.constants"
        )

@dataclasses.dataclass(frozen=True)
class OBJ(CMDFragment):
    name: str

    @typing.override
    def children(self):
        return (self.name,)

    @typing.override
    def realize(self) -> tuple[str, str]:
        return ("", self.name)

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
class TargetSelector(CMDFragment):
    var: SelectorVariable
    arguments: str

    @typing.override
    def children(self) -> Children:
        return (self.realize()[1],)

    def realize(self) -> tuple[str, str]:
        return ("", f"@{self.var.value}{f'[{self.arguments}]' if self.arguments != '' else ''}")

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
class Block(CMDFragment):
    value: tuple[CMD, ...]

    @typing.override
    def children(self) -> Children:
        return self.value

    @typing.override
    def realize(self) -> tuple[str, str]:
        return ("", f"{"".join(cmd.realize() for cmd in self.value)}\n")
