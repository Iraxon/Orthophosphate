from abc import ABC, abstractmethod
import dataclasses
import typing

from ...tokenizer.token import Token


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
class Ref[T](Node):
    """
    A reference to a value defined elsewhere,
    whether in Orthophosphate or in
    Minecraft itself; this will compile to some
    kind of resource location or ID as
    opposed to a definition
    """

    @typing.override
    def children(self) -> Children:
        return (self.compile(),)

    @abstractmethod
    def compile(self) -> str:
        raise NotImplementedError

@dataclasses.dataclass(frozen=True)
class NodeRef[T](Ref[T]):
    """
    A Ref that refers to
    something represented in the
    AST
    """
    referent: T

    @typing.override
    def children(self) -> Children:
        return (self.compile(),)

    @abstractmethod
    def compile(self) -> str:
        raise NotImplementedError

@dataclasses.dataclass(frozen=True)
class NamespacedIdentifier[T](NodeRef[T]):
    namespace: str
    rest: str

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

    @typing.override
    def __str__(self):
        return self.compile()

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

_placeholder_namespace: typing.Final = "this"

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
