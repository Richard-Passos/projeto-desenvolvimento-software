from typing import Protocol

from .root import Shortcut


class Generator(Protocol):
    def generate(self) -> None: ...


# TODO tests
class GenerateShortcut(Shortcut):
    def __init__(self, generator: Generator, *keys: Shortcut.Key) -> None:
        super().__init__(*keys)
        self._generator: Generator = generator

    def name(self) -> str:
        return 'Generate name'

    def image(self) -> str:
        return 'Generate image'

    def execute(self) -> None:
        self._generator.generate()
