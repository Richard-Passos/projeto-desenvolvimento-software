from collections.abc import Sequence

from model.command.playback import (
    Pausable,
    PauseCommand,
    Playable,
    PlayCommand,
    Stopable,
    StopCommand,
)

from .root import Shortcut


# TODO tests
class PlayShortcut(Shortcut[Playable]):
    def __init__(self, keys: Sequence[Shortcut.Key]) -> None:
        self._keys = keys

    def keys(self) -> Sequence[Shortcut.Key]:
        return self._keys

    def match(self, key: Shortcut.Key) -> PlayCommand | None:
        if key in self._keys:
            return PlayCommand()

        return None


class PauseShortcut(Shortcut[Pausable]):
    def __init__(self, keys: Sequence[Shortcut.Key]) -> None:
        self._keys = keys

    def keys(self) -> Sequence[Shortcut.Key]:
        return self._keys

    def match(self, key: Shortcut.Key) -> PauseCommand | None:
        if key in self._keys:
            return PauseCommand()

        return None


class StopShortcut(Shortcut[Stopable]):
    def __init__(self, keys: Sequence[Shortcut.Key]) -> None:
        self._keys = keys

    def keys(self) -> Sequence[Shortcut.Key]:
        return self._keys

    def match(self, key: Shortcut.Key) -> StopCommand | None:
        if key in self._keys:
            return StopCommand()

        return None
