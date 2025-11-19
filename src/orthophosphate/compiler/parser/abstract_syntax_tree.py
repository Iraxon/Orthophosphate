from abc import ABC, abstractmethod
import dataclasses
from enum import Enum
import typing

from ..tokenizer.token import Token
from .parse_state import ParseState

type Children = "tuple[Node | str, ...]"

@dataclasses.dataclass(frozen=True)
class Node(ABC):
    """
    A node in the abstract syntax tree

    Other than the specified abstract methods, many Node subclasses
    have a compile() method that returns a str or bytes object
    that the node will compile to.

    Some may also implement a ref() method that returns a Ref pointing
    to the object itself given a ParseState
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
class Root(Node):
    value: "tuple[TextFile, ...]"

    @typing.override
    def children(self) -> Children:
        return self.value

@dataclasses.dataclass(frozen=True)
class Ref[T](Node):
    """
    A reference to a value defined by another
    node; this will compile to some
    kind of resource location or ID as
    opposed to a definition
    """

    referent: T

    @typing.override
    def children(self) -> Children:
        return (self.compile(),)

    @abstractmethod
    def compile(self) -> str:
        raise NotImplementedError

@dataclasses.dataclass(frozen=True)
class NamespacedIdentifier[T](Ref[T]):
    namespace: str
    rest: str

    @typing.override
    def __str__(self):
        return self.compile()

    def compile(self) -> str:
        return f"{self.namespace}{self.sep()}{self.rest}"

    @classmethod
    @abstractmethod
    def sep(cls) -> typing.Literal[":", "."]:
        """
        Returns the separator character used by this
        kind of namespace
        """
        raise NotImplementedError

    @classmethod
    def of(cls, s: str | Token, referent: T) -> typing.Self:
        """
        Returns an instance of this class from
        a str or Token and performs input validation
        """
        if isinstance(s, Token):
            s = s.require_name().value
        namespace, name = cls.split_namespace(s)
        return cls(referent, namespace, name)

    @classmethod
    def of_sequence(cls, *parts: str, referent: T) -> typing.Self:
        if len(parts) <= 1:
            raise ValueError(f"{parts} does not describe a valid namespace because it is too short")
        return cls(referent, parts[0], "/".join(parts[1:]))

    @classmethod
    def split_namespace(cls, s: str) -> tuple[str, str]:
        """
        Splits a full namespace into the namespace part and
        the rest (e.g. this:core --> (this, core))

        Further divisions aren't touched: (e.g.this.globals.x -->
        this, globals.x)

        Throws an error if the name is malformed
        """
        split_char = cls.sep()
        match s.split(split_char):
            case (name,):
                return (_placeholder_namespace, name)
            case first, second:
                return (first, second)
            case _:
                raise ValueError(f"Malformed namespace: {s}")

_placeholder_namespace: typing.Final = "x"

@dataclasses.dataclass(frozen=True)
class ColonIdentifier[T](NamespacedIdentifier[T]):
    @classmethod
    @typing.override
    def sep(cls) -> typing.Literal[":"]:
        return ":"

@dataclasses.dataclass(frozen=True)
class DotIdentifier[T](NamespacedIdentifier[T]):
    @classmethod
    @typing.override
    def sep(cls) -> typing.Literal["."]:
        return "."

@dataclasses.dataclass(frozen=True)
class TextFile(Node):
    @abstractmethod
    def compile(self) -> str:
        raise NotImplementedError

@dataclasses.dataclass(frozen=True)
class MCFunction(TextFile):
    id: str
    body: "Block"

    def ref(self, state: ParseState) -> "Ref[MCFunction]":
        return state.get_ref(self.id, MCFunction)

    @typing.override
    def children(self) -> Children:
        return (self.id, self.body)

    @typing.override
    def compile(self):
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
    id: str
    content: "tuple[Ref[T] | Ref[Tag[T]], ...]"
    replace: bool = False

    def ref(self, state: ParseState) -> "Ref[MCFunction]":
        return state.get_ref(self.id, MCFunction)

    @typing.override
    def children(self) -> Children:
        return (str(self.replace),) + tuple(item for item in self.content)

    @typing.override
    def compile(self) -> str:
        return (
            "{\n"
            + f"  \"replace\": {'true' if self.replace else 'false'},\n"
            + "  \"values\": [\n"
            + "".join(tuple(
                f"    \"{item.compile()}\"{',' if i < len(self.content) - 1 else ''}\n" for i, item in enumerate(self.content)
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
    operand1: "Score"
    operand2: "Score"
    operation: ScoreboardOperator

    @typing.override
    def children(self) -> Children:
        return (self.operand1, self.operation.value, self.operand2)

    @typing.override
    def compile(self) -> str:
        first_pre, first = self.operand1.compile()
        second_pre, second = self.operand2.compile()
        return (
            f"{first_pre}\n{second_pre}\n"
            + f"scoreboard players operation {first} {self.operation.value} {second}\n"
        )

@dataclasses.dataclass(frozen=True)
class CMDFragment(Node):
    @abstractmethod
    def compile(self) -> tuple[str, str]:
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
    def compile(self) -> tuple[str, str]:
        return ("", f"{self.name if isinstance(self.name, str) else self.name.compile()} {self.objective.compile()}")

@dataclasses.dataclass(frozen=True)
class ConstantScore(Score):
    value: int

    @typing.override
    def children(self) -> Children:
        return (str(self.value),)

    @typing.override
    def compile(self) -> tuple[str, str]:
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
    def compile(self) -> tuple[str, str]:
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
        return (self.compile()[1],)

    def compile(self) -> tuple[str, str]:
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
    def compile(self) -> tuple[str, str]:
        return ("", f"{"".join(cmd.compile() for cmd in self.value)}\n")
