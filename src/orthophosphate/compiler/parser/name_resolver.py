from dataclasses import dataclass
from typing import Self
from .term_graph import Term, term_of
from .parse_tree import (
    ConcreteApplicationNode,
    ConcreteExprNode,
    ListLiteralNode,
    ProgramNode,
    PyLiteralNode,
)


@dataclass
class SymbolTable:
    """
    Keeps track of variable bindings
    """

    bindings: dict[str, Term]
    outer: Self | None = None

    def bind(self, target: str, value: Term) -> None:
        self.bindings[target] = value

    def deref(self, name: str) -> Term:
        try:
            return self.bindings[name]
        except KeyError:
            raise ValueError(f"Name {name} not defined")

    def enter_scope(self) -> Self:
        return type(self)(dict(), self)

    def exit_scope(self) -> Self:
        if self.outer is None:
            raise ValueError(f"Attempted to exit top-level scope")
        return self.outer

    @classmethod
    def new(cls) -> Self:
        return cls(OPO4_BUILTINS, None)


OPO4_BUILTINS = {"list": term_of("list", tuple(), False)}


def name_resolved_from_concrete(tree: ProgramNode) -> Term:
    table = SymbolTable.new()
    return term_of(
        table.deref("prgm"),
        tuple(_name_resolve_recursive(c, table) for c in tree.content),
    )


ARROW = ConcreteApplicationNode("->", tuple())


def _name_resolve_recursive(tree: ConcreteExprNode, table: SymbolTable) -> Term:
    match tree:

        case ConcreteApplicationNode(id, args):
            return term_of(
                _name_resolve_recursive(id, table),
                tuple(_name_resolve_recursive(arg, table) for arg in args),
            )

        case PyLiteralNode(_, v):
            return term_of(v)

        case str(n):
            return table.deref(n)

        case ListLiteralNode(content):
            return term_of(
                table.deref("list"),
                tuple(_name_resolve_recursive(item, table) for item in content),
            )
