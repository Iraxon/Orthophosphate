from abc import abstractmethod
from dataclasses import dataclass
from functools import cache
from typing import Protocol, Self, override

type Opo4Primitive = int | str


@dataclass(frozen=True)
class Term(Protocol):

    @abstractmethod
    def render_contents(self) -> "tuple[str, tuple[Term, ...]]":
        raise NotImplementedError

    @cache
    def display_node_inline(self) -> str:
        """
        Provides a nice readable string rep
        of the Node without nesting
        """
        header, children = self.render_contents()
        if len(children) > 0:
            args_str = " ".join(child.display_node_inline() for child in children)
            return f"{header}({args_str})"
        return f"{header}"

    @cache
    def display_node(self, pre: str = "") -> str:
        """
        Provides a nice readable string
        rep of the Node with nesting

        This function is recursive and
        dangerous to the sanity of anyone
        who works on it
        """
        header, children = self.render_contents()

        render_contents: tuple[str, ...] = tuple(
            child.display_node(pre + ("║ " if i < len(children) - 1 else "  "))
            for i, child in enumerate(children)
        )

        return f"{'' if pre == '' else'═'} {header}\n" + "".join(
            (
                f"{pre}╠{element}"  # Normal case
                if i < len(render_contents) - 1
                else f"{pre}╚{element}"  # Last element
            )
            for i, element in enumerate(render_contents)
        )

    @override
    def __str__(self):
        return self.display_node()


@dataclass(frozen=True)
class ProgramTerm(Term):
    top_level_exprs: tuple[Term, ...]

    @override
    def render_contents(self):
        return "Program", self.top_level_exprs


@dataclass(frozen=True)
class FunctionCallTerm(Term):
    head: Term
    args: tuple[Term, ...]

    @classmethod
    def of_tuple(cls, t: tuple[Term, ...]) -> Self:
        return cls(t[0], t[1:])

    @override
    def render_contents(self):
        return self.head.display_node_inline(), self.args


@dataclass(frozen=True)
class ReferenceTerm(Term):
    name: str

    @override
    def render_contents(self):
        return self.name, ()


@dataclass(frozen=True)
class IntTerm(Term):
    value: int

    @override
    def render_contents(self):
        return str(self.value), ()


@dataclass(frozen=True)
class StrTerm(Term):
    value: str

    @override
    def render_contents(self):
        return str(self.value), ()
