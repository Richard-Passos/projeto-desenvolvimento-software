from collections.abc import Callable, Sequence
from typing import Protocol

from model.command import Command
from model.music import MusicTimeline


class Commander[T](Protocol):
    def commands(self, text: str) -> Sequence[Command[T]]: ...


class TimelineControl(Protocol):
    def add_voice(self) -> None: ...

    def timeline(self) -> MusicTimeline: ...


class TextParser[T: TimelineControl]:
    def __init__(self, creator: Callable[[], T], commander: Commander[T]) -> None:
        self._creator = creator
        self._commander = commander

    def parse(self, text: str) -> MusicTimeline:
        control = self._creator()

        for content in text.splitlines():
            commands = self._commander.commands(content)
            control.add_voice()

            for command in commands:
                command.execute(control)

        return control.timeline()
