from collections.abc import Sequence

from model.command.exporter import ExporterCommand, ExporterControl
from model.path import Path

from .root import Shortcut


# TODO tests
class ExportShortcut(Shortcut[ExporterControl]):
    def __init__(self, path: Path, keys: Sequence[Shortcut.Key]) -> None:
        self._path = path
        self._keys = keys

    def keys(self) -> Sequence[Shortcut.Key]:
        return self._keys

    def match(self, key: Shortcut.Key) -> ExporterCommand | None:
        if key in self._keys:
            return ExporterCommand(self._path)

        return None
