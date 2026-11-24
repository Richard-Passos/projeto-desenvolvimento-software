from enum import IntEnum

from model.octave import Octave
from model.volume import Volume
from utils.error import OutOfRangeError


class NoteId(IntEnum):
    C_FLAT = 59
    C = 60
    C_SHARP = 61
    D_FLAT = 61
    D = 62
    D_SHARP = 63
    E_FLAT = 63
    E = 64
    E_SHARP = 65
    F_FLAT = 64
    F = 65
    F_SHARP = 66
    G_FLAT = 66
    G = 67
    G_SHARP = 68
    A_FLAT = 68
    A = 69
    A_SHARP = 70
    B_FLAT = 70
    B = 71
    B_SHARP = 72


class Note:
    MIN_DURATION: int = 0
    MAX_DURATION: int = 7

    def __init__(
        self, id: NoteId, duration: int, volume: Volume, octave: Octave
    ) -> None:
        if not self.in_range(duration):
            raise DurationOutOfRangeError(
                duration, self.MIN_DURATION, self.MAX_DURATION
            )

        self._id = id
        self._duration = duration
        self._volume = volume
        self._octave = octave

    def id(self) -> int:
        return self._id.value

    def duration(self) -> float:
        return 1.0 / 2.0 ** (self._duration - 1)

    def volume(self) -> Volume:
        return self._volume

    def octave(self) -> Octave:
        return self._octave

    def pitch(self) -> int:
        return self._octave.pitch(self.id())

    def with_(
        self,
        *,
        id: NoteId | None = None,
        duration: int | None = None,
        volume: Volume | None = None,
        octave: Octave | None = None,
    ) -> Note:
        return Note(
            id=self._id if id is None else id,
            duration=self._duration if duration is None else duration,
            volume=self._volume if volume is None else volume,
            octave=self._octave if octave is None else octave,
        )

    @classmethod
    def in_range(cls, duration: int) -> bool:
        return cls.MIN_DURATION <= duration <= cls.MAX_DURATION


class DurationOutOfRangeError(OutOfRangeError): ...
