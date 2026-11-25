from collections.abc import Callable
from typing import Protocol

from model.midi_file import MidiFile
from model.playback import LoadFailedError


# TODO tests
class Playback(Protocol):
    def play(self) -> None: ...

    def pause(self) -> None: ...

    def stop(self) -> None: ...


class View(Protocol):
    def show_error(self, text: str) -> None: ...

    def on_load(self, callback: Callable[[MidiFile], None]) -> None: ...

    def on_play(self, callback: Callable[[], None]) -> None: ...

    def on_pause(self, callback: Callable[[], None]) -> None: ...

    def on_stop(self, callback: Callable[[], None]) -> None: ...


class PlaybackController:
    def __init__(self, view: View, creator: Callable[[MidiFile], Playback]) -> None:
        self._view = view
        self._creator = creator
        self._playback: Playback | None = None

        view.on_load(self.load)
        view.on_play(self.play)
        view.on_pause(self.pause)
        view.on_stop(self.stop)

    def load(self, file: MidiFile) -> None:
        try:
            self._playback = self._creator(file)
        except LoadFailedError:
            self._playback = None
            self._view.show_error(
                f'Não foi possível carregar o arquivo “{file.path()}”. '
                'Tente novamente ou escolha outro arquivo.'
            )

    def play(self) -> None:
        if self._playback:
            self._playback.play()
        else:
            self._no_playback_error()

    def pause(self) -> None:
        if self._playback:
            self._playback.pause()
        else:
            self._no_playback_error()

    def stop(self) -> None:
        if self._playback:
            self._playback.stop()
        else:
            self._no_playback_error()

    def _no_playback_error(self) -> None:
        self._view.show_error(
            'Nenhuma música carregada. Gere uma música para usar os controles de reprodução.'
        )
