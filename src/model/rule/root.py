import re
from abc import ABC, abstractmethod
from typing import Any

from model.note import Note


class Rule[Map: dict[Any, Any] | None](ABC):
    type Match = re.Match[str]

    def __init__(self, map: Map | None = None) -> None:
        self._map = self.__resolve_map(map)
        self.__pattern = re.compile(self._pattern())

    @abstractmethod
    def _default_map(self) -> Map: ...

    @abstractmethod
    def _pattern(self) -> str: ...

    @abstractmethod
    def _handler(self, match: Match, note: Note) -> Note: ...

    def match(self, text: str) -> Match | None:
        return self.__pattern.match(text)

    def handle(self, text: str, note: Note) -> Note:
        match = self.match(text)
        if match is None:
            return note

        return self._handler(match, note)

    def __resolve_map(self, map: Map | None) -> Map:
        default = self._default_map()

        if map is not None and default is not None:
            default.update(map)

        return default

    def _escaped_keys(self) -> str:
        if self._map is None:
            return ''

        keys = [re.escape(key) for key in self._map]
        return '|'.join(keys)
