from abc import ABC, abstractmethod

from model.command import Command
from utils.type import Match


class Rule[T](ABC):
    @abstractmethod
    def match(self, text: str) -> Match | None: ...

    @abstractmethod
    def command(self, match: Match) -> Command[T]: ...
