from abc import abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from functools import cache
from typing import TYPE_CHECKING, LiteralString, Never, Protocol, Self, final, override

from ..utils.copy_on_write_dict import COWDict
from ..utils.lazy_value import Lazy, lazy_of, lazy_of_value

# Throughout this file, the suffix "ue" is used to denote
# a Term that has not been evaluated.

type Opo4Primitive = int | str

type Context = COWDict[str, Lazy[Term]]
"""
A decription of what variable bindings
exist at a given point in evaluation
"""

if TYPE_CHECKING:

    class Term(Protocol):

        @abstractmethod
        def render_contents(self) -> "tuple[str, tuple[Term, ...]]":
            raise NotImplementedError

        def eval_step(self, env: Context) -> "Term | None":
            """
            If the term can be simplified, return the result. If not,
            return None.
            """
            raise RuntimeError("Stub method")

        def eval(self) -> "Term":
            """
            Reduce the term as much as possible.
            The default context is assumed.
            """
            raise RuntimeError("Stub method")

        def eval_with_env(self, env: Context) -> "Term":
            """
            Reduce the term as much as possible.
            The provided context is used.
            """
            raise RuntimeError("Stub method")

        def display_node_inline(self) -> str:
            """
            Provides a nice readable string rep
            of the Node without nesting
            """
            raise RuntimeError("Stub method")

        def display_node(self, pre: str = "") -> str:
            """
            Provides a nice readable string
            rep of the Node with nesting

            This function is recursive and
            dangerous to the sanity of anyone
            who works on it
            """
            raise RuntimeError("Stub method")

else:

    @dataclass(frozen=True)
    class Term:

        def _eval_step(self, env: Context) -> "Term | None":
            """
            If the term can be simplified, return the result. If not,
            return None.
            """

            return None

        def eval(self) -> "Term":
            return self.eval_with_env(DEFAULT_CONTEXT)

        def eval_with_env(self, env: Context) -> "Term":
            """
            Reduce the term as much as possible.
            """

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
            return header

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
@final
class ProgramTerm(Term):
    top_level_exprs: tuple[Term, ...]

    @override
    def eval_step(self, env: Context) -> Never:
        raise NotImplementedError

    @override
    def eval_with_env(self, env: Context):
        """
        Reduce the term as much as possible.
        """
        return ProgramTerm(
            tuple(expr_ue.eval_with_env(env) for expr_ue in self.top_level_exprs)
        )

    if TYPE_CHECKING:

        # The type checker doesn't know on its own
        # that eval always returns a ProgramTerm

        @override
        def eval(self) -> "ProgramTerm": ...

    @override
    def render_contents(self):
        return "Program", self.top_level_exprs


@dataclass(frozen=True)
@final
class FunctionCallTerm(Term):
    head: Term
    args: tuple[Term, ...]

    @classmethod
    def of_tuple(cls, t: tuple[Term, ...]) -> Self:
        return cls(t[0], t[1:])

    @override
    def eval_step(self, env: Context):
        head_ue = self.head
        args_ue = self.args

        head = head_ue.eval_step(env)
        if head is not None:
            return FunctionCallTerm(head, args_ue)
        else:
            head = head_ue

        if head == let:
            # Term of term let(name, value, body)

            if len(args_ue) != 3:
                raise ValueError(
                    f"Incorrect number of arguments for let expression: {len(args_ue)}\n"
                    + "\n".join(str(arg) for arg in args_ue)
                )

            name_ue, value_ue, body_ue = args_ue

            # Name can be either a reference term, used unevaluated,
            # or a different expression that evaluates to
            # a string

            name: str

            if isinstance(name_ue, ReferenceTerm):
                name = name_ue.name
            else:
                name_evaled = name_ue.eval_with_env(env)
                if isinstance(name_evaled, StrTerm):
                    name = name_evaled.value
                else:
                    raise ValueError(f"Invalid assignment target for let: {name_ue}")

            value_lazy = lazy_of(lambda: value_ue.eval_with_env(env))
            return body_ue.eval_with_env(env.set(name, value_lazy))

        elif head == mcfunction:
            path_ue, *cmds_ue = args_ue
            file_content = "\n".join(
                cmd_ue.eval_with_env(env).display_node_inline() for cmd_ue in cmds_ue
            )
            return FunctionCallTerm(
                file,
                (
                    path_ue.eval_with_env(env),
                    StrTerm(file_content),
                ),
            )

        return None

    @override
    def render_contents(self):
        return self.head.display_node_inline(), self.args


@dataclass(frozen=True)
@final
class ReferenceTerm(Term):
    name: str

    @override
    def eval_step(self, env: Context):
        return env.get(self.name, lambda: None)()

    @override
    def render_contents(self):
        return self.name, ()


@dataclass(frozen=True)
@final
class IntTerm(Term):
    value: int

    @override
    def render_contents(self):
        return str(self.value), ()


@dataclass(frozen=True)
@final
class StrTerm(Term):
    value: str

    @override
    def render_contents(self):
        return self.value, ()


@dataclass(frozen=True)
class _BuiltinTermPrivateImpl[T: LiteralString | str](Term):
    builtin_id: T

    def render_contents(self) -> tuple[T, tuple[()]]:
        return self.builtin_id, ()


@final
class BuiltinTerm(_BuiltinTermPrivateImpl[str], Enum):
    FILE = "file"  # file behavior is handled by the datapack generator
    FN = "fn"  # fn is not yet implemented
    LET = "let"
    MCFUNCTION = "mcfunction"


file = BuiltinTerm.FILE
fn = BuiltinTerm.FN
let = BuiltinTerm.LET
mcfunction = BuiltinTerm.MCFUNCTION


def to_lazy(dict: Mapping[str, Term]) -> Context:
    return COWDict({k: lazy_of_value(v) for k, v in dict.items()})


DEFAULT_CONTEXT: Context = to_lazy(
    {builtin.builtin_id: builtin for builtin in BuiltinTerm}
)
