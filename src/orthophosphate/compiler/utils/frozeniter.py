from collections.abc import Iterable, Iterator
from typing import overload

from .lazy_value import Lazy, lazy_of

type FrozenIter[T] = IterCons[T] | None

type IterCons[T] = tuple[T, Lazy[FrozenIter[T]]]

def next_frozen[T](frozeniter: FrozenIter[T]) -> FrozenIter[T]:
    match frozeniter:
        case (_, next_lazy):
            return next_lazy()
        case None:
            raise ValueError(f"Attempted to get next of zero-length FrozenIter")


@overload
def get(frozeniter: None) -> None: ...
@overload
def get[T](frozeniter: tuple[T, Lazy[FrozenIter[T]]]) -> T: ...


def get[T](frozeniter: FrozenIter[T]) -> T | None:
    match frozeniter:
        case (v, _):
            return v
        case None:
            return None


def frozeniter_of_iter[T](iterable: Iterable[T]) -> FrozenIter[T]:

    iterator = iter(iterable)

    def _supply_next() -> FrozenIter[T]:
        try:
            v = next(iterator)
        except StopIteration:
            return None
        return (v, lazy_of(_supply_next))

    return _supply_next()


def iter_of_frozeniter[T](frozeniter: FrozenIter[T]) -> Iterator[T]:
    next: FrozenIter[T] = frozeniter
    while isinstance(next, tuple):
        yield next[0]
        next = next[1]()

def display[T](frozeniter: FrozenIter[T], maxsize: int = 1000000, open_lazies: bool = False) -> str:
    if maxsize <= 0:
        return "..."
    match frozeniter:
        case None:
            return "NIL"
        case (item, _) as cons:
            return f"{item} : {display(next_frozen(cons), maxsize - 1, open_lazies)}"
