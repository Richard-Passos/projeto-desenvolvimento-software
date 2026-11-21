from collections.abc import Callable
from itertools import cycle

from model.bpm import Bpm
from model.instrument import Instrument
from model.note import NoteId
from model.timeline import Timeline
from model.voice import VoiceControl

from .root import Music
from .timeline import MusicTimeline


# TODO tests
class MusicControl:
    def __init__(self, music: Music) -> None:
        self._index: int = -1
        self._music = music
        self._cycle = cycle(music.voices())
        self._bpms = Timeline[Bpm](music.bpm())
        self._voices = [VoiceControl(voice) for voice in music.voices()]
        self._last_action: Callable[[], None] | None = None

    def timeline(self) -> MusicTimeline:
        voices = [voice.timeline() for voice in self._voices]
        return MusicTimeline(self._bpms, voices)

    def rest(self, duration: int) -> None:
        self.voice_control().rest(duration)

    def redo(self) -> None:
        if self._last_action is None:
            self.rest(1)
        else:
            self._last_action()

    def bpm(self) -> Bpm:
        return self._bpms.get(self.voice_control().time()) or self._music.bpm()

    def voice_control(self) -> VoiceControl:
        return self._voices[self._index]

    def add_voice(self) -> None:
        self._index += 1

        if self._index > len(self._voices):
            self._voices[self._index] = VoiceControl(next(self._cycle))

    def add_bpm(self, bpm: Bpm) -> None:
        self._bpms.set(self.voice_control().time(), bpm)
        self.clear_action()

    def add_note(self, id: NoteId, duration: int) -> None:
        self.voice_control().add_note(id, duration)
        self._last_action = lambda: self.add_note(id, duration)

    def add_instrument(self, id: int) -> None:
        self.voice_control().add_instrument(Instrument(id))
        self.clear_action()

    def increase_bpm(self) -> None:
        self.add_bpm(self.bpm().increase())
        self.clear_action()

    def decrease_bpm(self) -> None:
        self.add_bpm(self.bpm().decrease())
        self.clear_action()

    def double_volume(self) -> None:
        voice = self.voice_control().voice()
        self.voice_control().set_voice(voice.with_(volume=voice.volume().double()))
        self.clear_action()

    def halve_volume(self) -> None:
        voice = self.voice_control().voice()
        self.voice_control().set_voice(voice.with_(volume=voice.volume().halve()))
        self.clear_action()

    def shift_instrument(self, amount: int) -> None:
        instrument_id = self.voice_control().voice().instrument().id() + amount
        self.add_instrument(min(max(instrument_id, Instrument.MIN), Instrument.MAX))
        self.clear_action()

    def up_octave(self) -> None:
        voice = self.voice_control().voice()
        self.voice_control().set_voice(voice.with_(octave=voice.octave().up()))
        self.clear_action()

    def down_octave(self) -> None:
        voice = self.voice_control().voice()
        self.voice_control().set_voice(voice.with_(octave=voice.octave().down()))
        self.clear_action()

    def clear_action(self) -> None:
        self._last_action = None
