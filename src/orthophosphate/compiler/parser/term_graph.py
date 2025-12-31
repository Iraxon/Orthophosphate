from dataclasses import dataclass
from typing import Self

type TermGraph = Term

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

    head: Self | str | int
    children: tuple[Self, ...] = tuple()
