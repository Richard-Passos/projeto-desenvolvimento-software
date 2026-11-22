from typing import Protocol

from .root import Command


class ExporterControl(Protocol):
    def export(self, path: str) -> None: ...


class ExporterCommand(Command[ExporterControl]):
    def __init__(self, path: str) -> None:
        self._path = path

    def execute(self, handler: ExporterControl) -> None:
        handler.export(self._path)
