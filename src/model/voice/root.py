from instrument import Instrument
from note import Note, NoteId
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

    def default_note(self) -> Note:
        return Note(NoteId.C, 0, 0, self.octave(), self.volume(), self.instrument())

    def with_notes(self, notes: list[Note]) -> 'Voice':
        return Voice(self._settings, notes)
