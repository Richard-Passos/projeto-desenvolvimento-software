from typing import Protocol

from model.path import Path

from .root import Command


# TODO tests
class Exporter(Protocol):
    def export(self, path: Path) -> None: ...


class ExporterCommand(Command):
    def __init__(self, handler: Exporter, path: Path) -> None:
        self._handler = handler
        self._path = path

    def execute(self) -> None:
        self._handler.export(self._path)
