from dataclasses import dataclass
from functools import cache
from typing import Self

type TermGraph = Term

type Opo4Primitive = str | int

@dataclass(frozen=True)
class Term:
    """
    A term always has a head;
    this could be the function being
    applied in an application or
    the lone value in an atomic
    value

    Children would be function args,
    data structure contents, etc.
    """

    head: Self | Opo4Primitive
    children: tuple[Self, ...] = tuple()

    @classmethod
    @cache
    def of(cls, head: Self | Opo4Primitive, children: tuple[Self, ...] = tuple()) -> Self:
        """
        Use instead of constructor for cache optimization
        """
        return cls(head, children)
