from abc import ABC, abstractmethod
from collections.abc import Sequence


# TODO tests
class Shortcut(ABC):
    type Key = str | Sequence[Key]

    def __init__(self, *keys: Key) -> None:
        self._keys: Sequence[Shortcut.Key] = keys

    def keys(self) -> Sequence[Key]:
        return self._keys

    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def image(self) -> str: ...

    @abstractmethod
    def execute(self) -> None: ...
