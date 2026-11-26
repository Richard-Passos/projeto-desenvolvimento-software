from collections.abc import Sequence
from typing import Protocol


class Command(Protocol):
    def execute(self) -> None: ...


class Shortcut:
    type Key = str | Sequence[str]

    def __init__(self, key: Key, command: Command) -> None:
        self._key = key
        self._command = command

    def key(self) -> Key:
        return self._key

    def execute(self) -> None:
        self._command.execute()
