from typing import Protocol

from .root import Shortcut


class Exporter(Protocol):
    def export(self) -> None: ...


# TODO tests
class ExportShortcut(Shortcut):
    def __init__(self, exporter: Exporter, *keys: Shortcut.Key) -> None:
        super().__init__(*keys)
        self._exporter: Exporter = exporter

    def name(self) -> str:
        return 'Export name'

    def image(self) -> str:
        return 'Export image'

    def execute(self) -> None:
        self._exporter.export()
