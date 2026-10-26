from typing import Protocol

from .root import Shortcut


class Playable(Protocol):
    def play(self) -> None: ...


class Pausable(Protocol):
    def pause(self) -> None: ...


class Stopable(Protocol):
    def stop(self) -> None: ...


# TODO tests
class PlayShortcut(Shortcut):
    def __init__(self, playback: Playable, *keys: Shortcut.Key) -> None:
        super().__init__(*keys)
        self._playback: Playable = playback

    def name(self) -> str:
        return 'Playback play name'

    def image(self) -> str:
        return 'Playback play image'

    def execute(self) -> None:
        self._playback.play()


class PauseShortcut(Shortcut):
    def __init__(self, playback: Pausable, *keys: Shortcut.Key) -> None:
        super().__init__(*keys)
        self._playback: Pausable = playback

    def name(self) -> str:
        return 'Playback pause name'

    def image(self) -> str:
        return 'Playback pause image'

    def execute(self) -> None:
        self._playback.pause()


class StopShortcut(Shortcut):
    def __init__(self, playback: Stopable, *keys: Shortcut.Key) -> None:
        super().__init__(*keys)
        self._playback: Stopable = playback

    def name(self) -> str:
        return 'Playback stop name'

    def image(self) -> str:
        return 'Playback stop image'

    def execute(self) -> None:
        self._playback.stop()
