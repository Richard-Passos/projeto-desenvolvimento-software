from collections.abc import Sequence

from model.command.generator import GeneratorCommand, GeneratorControl

from .root import Shortcut


# TODO tests
class GenerateShortcut(Shortcut[GeneratorControl]):
    def __init__(self, keys: Sequence[Shortcut.Key]) -> None:
        self._keys = keys

    def keys(self) -> Sequence[Shortcut.Key]:
        return self._keys

    def match(self, key: Shortcut.Key) -> GeneratorCommand | None:
        if key in self._keys:
            return GeneratorCommand()

        return None
