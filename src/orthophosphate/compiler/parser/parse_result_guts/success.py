from dataclasses import dataclass
from typing import Generic, TypeVar

from ...utils.frozeniter import FrozenIter

V = TypeVar("V", covariant=True)  # Necessary for covariance
SRC = TypeVar("SRC")


@dataclass(frozen=True)
class Success(Generic[V, SRC]):
    value: V
    continuation_src: FrozenIter[SRC]
