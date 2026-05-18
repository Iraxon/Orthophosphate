from dataclasses import dataclass

from ...utils.frozeniter import FrozenIter


@dataclass(frozen=True)
class Failure[SRC]:
    errors: tuple[str, ...]
    src_iter: FrozenIter[SRC]
