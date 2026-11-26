from collections.abc import Sequence
from typing import Protocol

from model.command import Command
from model.music import MusicTimeline


class Commander(Protocol):
    def commands(self, text: str) -> Sequence[Command]: ...


class TimelineControl(Protocol):
    def clear_voices(self) -> None: ...

    def add_voice(self) -> None: ...

    def timeline(self) -> MusicTimeline: ...


class TextParser:
    def __init__(self, control: TimelineControl, commander: Commander) -> None:
        self._control = control
        self._commander = commander

    def parse(self, text: str) -> MusicTimeline:
        self._control.clear_voices()

        for content in text.splitlines():
            self._control.add_voice()
            commands = self._commander.commands(content)

            for command in commands:
                command.execute()

        return self._control.timeline()
