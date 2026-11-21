from collections.abc import Sequence
from typing import Protocol

from model.command import Command
from model.music import Music, MusicControl, MusicTimeline
from utils.error import Error
from utils.type import Match


class Matcher(Protocol):
    def match(self, text: str) -> Match | None: ...

    def command(self, match: Match) -> Command[MusicControl]: ...


class TextParser:
    def __init__(self, matchers: Sequence[Matcher]) -> None:
        self._matchers = matchers

    def parse(self, text: str, music: Music) -> MusicTimeline:
        control = MusicControl(music)

        for content in text.splitlines():
            control.add_voice()
            commands = self._commands(content)

            for command in commands:
                command.execute(control)

        return control.timeline()

    def _commands(self, text: str) -> Sequence[Command[MusicControl]]:
        commands: list[Command[MusicControl]] = []

        while text:
            for matcher in self._matchers:
                if match := matcher.match(text):
                    commands.append(matcher.command(match))
                    text = text[match.end() :]
                    break
            else:
                raise NoMatchTextParserError(text)

        return commands


class NoMatchTextParserError(Error[str]): ...
