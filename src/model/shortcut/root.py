from collections.abc import Sequence
from typing import Protocol


class Command(Protocol):
    def execute(self) -> None: ...


class Shortcut:
    type Key = str | Sequence[str]

    def __init__(self, command: Command, keys: Sequence[Key]) -> None:
        self._command = command
        self._keys = keys

    def keys(self) -> Sequence[Key]:
        return self._keys

    def command(self) -> Command:
        return self._command

    def match(self, key: Shortcut.Key) -> bool:
        return key in self.keys()
