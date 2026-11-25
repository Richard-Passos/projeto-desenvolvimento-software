from typing import Protocol

from model.path import Path

from .root import Command


# TODO tests
class ExporterControl(Protocol):
    def export(self, path: Path) -> None: ...


class ExporterCommand(Command[ExporterControl]):
    def __init__(self, path: Path) -> None:
        self._path = path

    def execute(self, handler: ExporterControl) -> None:
        handler.export(self._path)
