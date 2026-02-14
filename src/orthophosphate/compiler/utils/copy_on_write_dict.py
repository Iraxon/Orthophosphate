from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass
class COWDict[K, V](Mapping[K, V]):
    _dict: dict[K, V] = field(default_factory=dict[K, V])

    def __getitem__(self, key: K):
        return self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

assert issubclass(COWDict, Mapping)
