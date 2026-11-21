from enum import Enum, auto

from model.midi_file import MidiFile
from model.player import Player
from utils.error import Error


class PlaybackState(Enum):
    STOPPED = auto()
    PLAYING = auto()
    PAUSED = auto()


# TODO tests
class Playback:
    def __init__(self, file: MidiFile, player: Player) -> None:
        self._file = file
        self._player = player
        self._state: PlaybackState = PlaybackState.STOPPED

        if not player.load(file.path()):
            raise LoadFailedPlaybackError(file.path())

    def play(self) -> None:
        if self.state() is PlaybackState.PLAYING:
            return

        if self.state() is PlaybackState.PAUSED:
            self._player.unpause()
        else:
            self._player.play()

        self._state = PlaybackState.PLAYING

    def pause(self) -> None:
        if self.state() is not PlaybackState.PLAYING:
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
        return self._file.duration()

    def playing(self) -> bool:
        return self.state() is PlaybackState.PLAYING

    def paused(self) -> bool:
        return self.state() is PlaybackState.PAUSED

    def stopped(self) -> bool:
        return self.state() is PlaybackState.PAUSED

    def state(self) -> PlaybackState:
        ended = self._state is PlaybackState.PLAYING and not self._player.busy()
        if ended:
            self._state = PlaybackState.STOPPED

        return self._state


class LoadFailedPlaybackError(Error[str]): ...
