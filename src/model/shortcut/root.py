from abc import ABC, abstractmethod
from collections.abc import Sequence

from model.command import Command


class Shortcut[T](ABC):
    type Key = str | Sequence[str]

    @abstractmethod
    def keys(self) -> Sequence[Key]: ...

    @abstractmethod
    def match(self, key: Shortcut.Key) -> Command[T] | None: ...
