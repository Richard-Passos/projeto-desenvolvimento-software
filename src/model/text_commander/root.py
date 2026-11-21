from collections.abc import Sequence
from typing import Protocol

from model.command import Command
from utils.error import Error
from utils.type import Match


class Rule[T](Protocol):
    def match(self, text: str) -> Match | None: ...

    def command(self, match: Match) -> Command[T]: ...


class TextCommander[T]:
    def __init__(self, rules: Sequence[Rule[T]]) -> None:
        self._rules = rules

    def commands(self, text: str) -> Sequence[Command[T]]:
        commands: list[Command[T]] = []

        while text:
            for rule in self._rules:
                match = rule.match(text)
                if not match or not self._valid_match(match):
                    continue

                commands.append(rule.command(match))
                text = text[match.end() :]
                break
            else:
                raise NoMatchError(text)

        return commands

    def _valid_match(self, match: Match) -> bool:
        return match.start() == 0 and match.end() > 0


class NoMatchError(Error[str]): ...
