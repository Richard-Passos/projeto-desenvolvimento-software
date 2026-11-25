from collections.abc import Callable
from typing import Protocol

from model.path.text import TextPath
from model.text_file import ReadFailedError


# TODO tests
class View(Protocol):
    def show_error(self, text: str) -> None: ...
    def on_import(self, callback: Callable[[TextPath], str]) -> None: ...


class TextReader(Protocol):
    def read(self, path: TextPath) -> str: ...


class ImportController:
    def __init__(self, view: View, reader: TextReader) -> None:
        self._view = view
        self._reader = reader
        view.on_import(self.load)

    def load(self, path: TextPath) -> str:
        try:
            return self._reader.read(path)
        except ReadFailedError:
            self._view.show_error(
                f'Couldn’t read “{path.name()}”. Try again or choose another file.'
            )

        return ''
