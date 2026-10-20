from enum import IntEnum

from instrument import Instrument
from octave import Octave
from volume import Volume


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


# TODO tests
class Note:
    def __init__(
        self,
        id: NoteId,
        start: int,
        duration: int,
        octave: Octave,
        volume: Volume,
        instrument: Instrument,
    ) -> None:
        self._id: NoteId = id
        self._start: int = start
        self._duration: int = duration
        self._octave: Octave = octave
        self._volume: Volume = volume
        self._instrument: Instrument = instrument

    def id(self) -> NoteId:
        return self._id

    def start(self) -> int:
        return self._start

    def duration(self) -> int:
        return self._duration

    def octave(self) -> Octave:
        return self._octave

    def volume(self) -> Volume:
        return self._volume

    def instrument(self) -> Instrument:
        return self._instrument
