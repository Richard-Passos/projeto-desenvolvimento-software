from enum import Enum, auto

from model.player import Player


class PlaybackState(Enum):
    STOPPED = auto()
    PLAYING = auto()
    PAUSED = auto()


# TODO tests
class Playback:
    def __init__(self, player: Player, path: str, duration: float) -> None:
        self._player: Player = player
        self._duration: float = duration
        self._state: PlaybackState = PlaybackState.STOPPED

        player.load(path)

    def play(self) -> None:
        if self._current_state() is PlaybackState.PLAYING:
            return

        if self._current_state() is PlaybackState.PAUSED:
            self._player.unpause()
        else:
            self._player.play()

        self._state = PlaybackState.PLAYING

    def pause(self) -> None:
        if self._current_state() is not PlaybackState.PLAYING:
            return

        self._player.pause()
        self._state = PlaybackState.PAUSED

    def stop(self) -> None:
        self._player.stop()
        self._position = 0.0
        self._state = PlaybackState.STOPPED

    def position(self) -> float:
        return self._player.position()

    def duration(self) -> float:
        return self._duration

    def playing(self) -> bool:
        return self._current_state() is PlaybackState.PLAYING

    def paused(self) -> bool:
        return self._current_state() is PlaybackState.PAUSED

    def stopped(self) -> bool:
        return self._current_state() is PlaybackState.PAUSED

    def _current_state(self) -> PlaybackState:
        ended = self._state is PlaybackState.PLAYING and not self._player.busy()
        if ended:
            self._state = PlaybackState.STOPPED

        return self._state
