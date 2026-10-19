from instrument import Instrument
from note import Note
from octave import Octave
from volume import Volume

from .settings import VoiceSettings


# TODO tests
class Voice:
    def __init__(self, settings: VoiceSettings, notes: list[Note]) -> None:
        self._settings = settings
        self._notes = notes

    def octave(self) -> Octave:
        return self._settings.octave()

    def volume(self) -> Volume:
        return self._settings.volume()

    def instrument(self) -> Instrument:
        return self._settings.instrument()

    def notes(self) -> list[Note]:
        return self._notes
