from functools import cache

type Opo4Primitive = int | str

type Term = tuple[str, *tuple[Term, ...]] | Opo4Primitive
"""
    A term always has a head;
    this could be the function being
    applied in an application or
    the lone value in an atomic
    value

    Children would be function args,
    data structure contents, etc.
    """

@cache
def term_of(head: str, children: tuple[Term, ...] = tuple()) -> Term:
    return (head, *children)

@cache
def children(term: Term) -> tuple[Term, ...]:
    match term:
        case tuple(v):
            return v[1:]
        case int(x):
            return (x - 1,)
        case str(s):
            return tuple(s)
