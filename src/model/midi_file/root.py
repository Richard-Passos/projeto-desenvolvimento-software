from midiutil import MIDIFile

from model.context import ContextTimeline
from model.note import Note
from model.voice import Voice

type Voices = list[Voice]


class MidiFile:
    TRACK = 0
    MAX_VOICES = 9

    def __init__(
        self,
        path: str,
        voices: Voices,
        contexts: ContextTimeline,
        file: MIDIFile | None = None,
    ) -> None:
        self._path: str = path
        self._file = file or MIDIFile()
        self._duration: int = 0

        self._handle_contexts(contexts)
        self._handle_voices(voices)
        self._save_file()

    def path(self) -> str:
        return self._path

    def duration(self) -> float:
        return self._duration

    def _handle_contexts(self, contexts: ContextTimeline) -> None:
        for start, context in contexts:
            self._file.addTempo(self.TRACK, start, context.bpm().current())

    def _handle_voices(self, voices: Voices) -> None:
        for channel, voice in enumerate(voices[: self.MAX_VOICES]):
            default_note = voice.default_note()
            instrument = default_note.instrument()
            self._add_instrument(channel, voice.default_note())

            for note in voice.notes():
                if note.instrument() != instrument:
                    self._add_instrument(channel, note)
                    instrument = note.instrument()

                self._add_note(channel, note)
                self._duration = max(self._duration, note.end())

    def _add_instrument(self, channel: int, note: Note) -> None:
        self._file.addProgramChange(
            tracknum=self.TRACK,
            channel=channel,
            time=note.start(),
            program=note.instrument(),
        )

    def _add_note(self, channel: int, note: Note) -> None:
        self._file.addNote(
            track=self.TRACK,
            channel=channel,
            pitch=note.pitch(),
            time=note.start(),
            duration=note.duration(),
            volume=note.volume(),
        )

    def _save_file(self) -> None:
        with open(self.path(), 'wb') as file:
            self._file.writeFile(file)
