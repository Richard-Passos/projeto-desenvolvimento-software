from model.instrument import Instrument
from model.note import Note, NoteId
from model.timeline import Timeline
from utils.error import Error

from .root import Voice
from .timeline import VoiceTimeline


# TODO tests
class VoiceControl:
    def __init__(self, voice: Voice) -> None:
        self._time: int = 0
        self._voice = voice
        self._notes = Timeline[Note]()
        self._instruments = Timeline[Instrument](voice.instrument())

    def timeline(self) -> VoiceTimeline:
        return VoiceTimeline(self._notes, self._instruments)

    def voice(self) -> Voice:
        return self._voice

    def time(self) -> int:
        return self._time

    def rest(self, duration: int) -> None:
        if duration <= 0:
            raise NonPositiveDurationVoiceControlError(duration)

        self._time += duration

    def add_note(self, id: NoteId, duration: int) -> None:
        voice = self._voice
        self._notes.set(self.time(), Note(id, duration, voice.volume(), voice.octave()))
        self.rest(duration)

    def add_instrument(self, instrument: Instrument) -> None:
        self._instruments.set(self.time(), instrument)

    def set_voice(self, voice: Voice) -> None:
        self._voice = voice


class NonPositiveDurationVoiceControlError(Error[int]): ...
