from abc import abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache
from typing import LiteralString, Never, Protocol, Self, override

from ..utils.copy_on_write_dict import COWDict
from ..utils.lazy_value import Lazy, lazy_of, lazy_of_value

type Opo4Primitive = int | str

type Context = COWDict[str, Lazy[Term]]
"""
A decription of what variable bindings
exist at a given point in evaluation
"""


@dataclass(frozen=True)
class Term(Protocol):

    @abstractmethod
    def render_contents(self) -> "tuple[str, tuple[Term, ...]]":
        raise NotImplementedError

    def _eval_step(self, env: Context) -> "Term | None":
        """
        If the term can be simplified, return the result. If not,
        return None.
        """

        return None

    def eval(self, env: Context | None = None) -> "Term":
        """
        Reduce the term as much as possible.
        """

        env = get_context(env)

        current = self
        current_env = env

        while True:
            next = current._eval_step(current_env)
            if next is None:
                return current
            else:
                current = next

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
    def _eval_step(self, env: Context) -> Never:
        raise NotImplementedError

    @override
    def eval(self, env: Context | None = None):
        """
        Reduce the term as much as possible.
        """
        env = get_context(env)
        return ProgramTerm(tuple(expr.eval() for expr in self.top_level_exprs))

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
    def _eval_step(self, env: Context):
        head = self.head.eval()
        args = self.args

        if head == let:
            # Term of term let(name, value, body)

            if len(args) != 3:
                raise ValueError(
                    f"Incorrect number of arguments for let expression: {len(args)}\n"
                    + "\n".join(str(arg) for arg in args)
                )

            name_unevaluated, value_unevaluated, body_unevaluated = args

            # Name can be either a reference term, used unevaluated,
            # or a different expression that evaluates to
            # a string

            name: str

            if isinstance(name_unevaluated, ReferenceTerm):
                name = name_unevaluated.name
            else:
                name_evaled = name_unevaluated.eval(env)
                if isinstance(name_evaled, StrTerm):
                    name = name_evaled.value
                else:
                    raise ValueError(
                        f"Invalid assignment target for let: {name_unevaluated}"
                    )

            value_lazy = lazy_of(lambda: value_unevaluated.eval(env))
            return body_unevaluated.eval(env.set(name, value_lazy))

        return None

    @override
    def render_contents(self):
        return self.head.display_node_inline(), self.args


@dataclass(frozen=True)
class ReferenceTerm(Term):
    name: str

    @override
    def _eval_step(self, env: Context):
        return env.get(self.name, lambda: None)()

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
        return self.value, ()


@dataclass(frozen=True)
class BuiltinTerm[T: LiteralString](Term):
    builtin_id: T

    @override
    def render_contents(self):
        return self.builtin_id, ()


let = BuiltinTerm("let")
fn = BuiltinTerm("fn")


def to_lazy(dict: Mapping[str, Term]) -> Context:
    return COWDict({k: lazy_of_value(v) for k, v in dict.items()})


DEFAULT_CONTEXT: Context = to_lazy(
    {
        "fn": fn,
        "let": let, # Unused at present
    }
)


def get_context(maybe_context: Context | None) -> Context:
    if maybe_context is None:
        return DEFAULT_CONTEXT
    return maybe_context
