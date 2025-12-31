from dataclasses import dataclass

type TermGraph = Term

type Term = TermApplication | NestedTerm | AtomicTerm[int] | AtomicTerm[str]


@dataclass(frozen=True)
class TermApplication:
    """
    Function application node pointing
    to the function itself; tree as code
    """

    function: Term
    args: tuple[Term, ...]


@dataclass(frozen=True)
class NestedTerm:
    """
    Tree as data, as with a list() call
    """

    type: Term
    children: tuple[Term, ...]


@dataclass(frozen=True)
class AtomicTerm[T: (int, str)]():
    """
    Primitive terms like integers
    and strings
    """

    value: T
