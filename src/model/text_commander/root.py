from collections.abc import Sequence
from typing import Protocol

from model.command import Command
from utils.error import Error
from utils.type import Match


class Rule(Protocol):
    def match(self, text: str) -> Match | None: ...

    def command(self) -> Command: ...


class TextCommander:
    def __init__(self, rules: Sequence[Rule]) -> None:
        self._rules = rules

    def commands(self, text: str) -> Sequence[Command]:
        commands: list[Command] = []

        while text:
            for rule in self._rules:
                match = rule.match(text)
                if match is None or match.end() == 0:
                    continue

                commands.append(rule.command())
                text = text[match.end() :]
                break
            else:
                raise NoMatchError(text)

        return commands


class NoMatchError(Error[str]): ...
