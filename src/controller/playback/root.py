from collections.abc import Callable

from model.playback import Playback

type View = Callable[[str], None]


class PlaybackController:
    def __init__(self, playback: Playback, view: View = print) -> None:
        self._playback = playback
        self._view: View = view

    def play(self) -> None:
        self._playback.play()
        # TODO uptade playback view
        self._view('Playback State: Playing')

    def pause(self) -> None:
        self._playback.pause()
        # TODO uptade playback view
        self._view('Playback State: Paused')

    def stop(self) -> None:
        self._playback.stop()
        # TODO uptade playback view
        self._view('Playback State: Stopped')
