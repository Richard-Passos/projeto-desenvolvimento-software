import re
from collections.abc import Callable

from model.command import Command
from utils.type import Match


class Rule:
    PATTERN: str = r''

    def __init__(
        self, creator: Callable[[Match], Command], pattern: str | None = None
    ) -> None:
        self._creator = creator
        self._pattern = re.compile(pattern or self.PATTERN)
        self._match: Match | None = None

    def match(self, text: str) -> Match | None:
        match = self._pattern.match(text)
        if match is None or match.end() == 0:
            return None

        self._match = match
        return match

    def command(self) -> Command:
        if self._match is None:
            raise NoActiveMatchError()

        return self._creator(self._match)


class NoActiveMatchError(ValueError): ...
