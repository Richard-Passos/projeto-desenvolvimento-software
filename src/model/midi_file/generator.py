import midiutil

from model.bpm import Bpm
from model.instrument import Instrument
from model.music import MusicTimeline
from model.note import Note
from model.path import MidiPath
from utils.error import OutOfRangeError

from .root import MidiFile


# TODO tests
class MidiFileGenerator:
    TRACK: int = 0
    MIN_VOICES: int = 0
    MAX_VOICES: int = 16

    def __init__(self) -> None:
        self._file = midiutil.MIDIFile()
        self._duration: float = 0

    def generate(self, path: MidiPath, music: MusicTimeline) -> MidiFile:
        if not self.MIN_VOICES <= len(music.voices()) <= self.MAX_VOICES:
            raise VoicesOutOfRangeError(
                len(music.voices()), self.MIN_VOICES, self.MAX_VOICES
            )

        for start, bpm in music.bpms():
            self._add_bpm(start, bpm)

        for channel, voice in enumerate(music.voices()):
            for start, note in voice.notes():
                self._add_note(channel, start, note)

            for start, instrument in voice.instruments():
                self._add_instrument(channel, start, instrument)

        self._save(path.name())

        return MidiFile(path, self._duration)

    def _add_bpm(self, start: int, bpm: Bpm) -> None:
        self._file.addTempo(self.TRACK, start, bpm.value())

    def _add_instrument(self, channel: int, start: int, instrument: Instrument) -> None:
        self._file.addProgramChange(
            tracknum=self.TRACK,
            channel=channel,
            time=start,
            program=instrument,
        )

    def _add_note(self, channel: int, start: int, note: Note) -> None:
        self._file.addNote(
            track=self.TRACK,
            channel=channel,
            pitch=note.pitch(),
            time=start,
            duration=note.duration(),
            volume=note.volume(),
        )
        self._duration = start + note.duration()

    def _save(self, path: str) -> None:
        with open(path, 'wb') as file:
            self._file.writeFile(file)


class VoicesOutOfRangeError(OutOfRangeError): ...
