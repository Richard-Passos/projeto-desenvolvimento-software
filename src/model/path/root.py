import pathlib
from abc import ABC, abstractmethod

from utils.error import ExpectError


class Path(ABC):
    def __init__(self, path: str) -> None:
        target = pathlib.Path(path)
        if not target.exists():
            raise PathNotFoundError()

        if not target.suffix:
            raise NoExtensionError()

        if target.suffix != self.extension():
            raise InvalidExtensionError(target.suffix, self.extension())

        self._path = target

    def name(self) -> str:
        return self._path.name

    @abstractmethod
    def extension(self) -> str: ...


class PathNotFoundError(Exception): ...


class NoExtensionError(Exception): ...


class InvalidExtensionError(ExpectError[str]): ...
