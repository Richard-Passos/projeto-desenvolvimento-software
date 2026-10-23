import tempfile
import unittest
from pathlib import Path
from typing import cast
from unittest.mock import Mock, call

from midiutil import MIDIFile

from model.context import ContextTimeline
from model.midi_file import MidiFile
from model.voice import Voice

type Voices = tuple[Mock, ...]
type Contexts = list[tuple[int, Mock]]  # start, mock


# IA Code
class MidiFileTest(unittest.TestCase):
    def setUp(self) -> None:
        self.file = self.midi_file()
        self.directory = tempfile.TemporaryDirectory()
        self.path = str(Path(self.directory.name) / 'song.mid')
        self.addCleanup(self.directory.cleanup)

    def note(
        self,
        start: int = 0,
        duration: int = 1,
        pitch: int = 60,
        volume: int = 100,
        instrument: int = 0,
    ) -> Mock:
        note = Mock()
        note.start.return_value = start
        note.duration.return_value = duration
        note.pitch.return_value = pitch
        note.volume.return_value = volume
        note.instrument.return_value = instrument

        return note

    def voice(self, *notes: Mock) -> Mock:
        voice = Mock()
        voice.notes.return_value = list(notes)
        voice.default_note.return_value = notes[0]

        return voice

    def context(self, bpm: int) -> Mock:
        context = Mock()
        context.bpm.return_value.current.return_value = bpm

        return context

    def midi_file(self) -> Mock:
        file = Mock()
        file.writeFile.side_effect = lambda handle: handle.write(b'midi')

        return file

    def build(self, voices: Voices = (), contexts: Contexts | None = None) -> MidiFile:
        return MidiFile(
            self.path,
            cast(list[Voice], list(voices)),
            cast(ContextTimeline, contexts or []),
            cast(MIDIFile, self.file),
        )

    def test_saves_file(self) -> None:
        self.build()

        self.assertEqual(Path(self.path).read_bytes(), b'midi')
        self.file.writeFile.assert_called_once()

    def test_raises_when_path_does_not_exist(self) -> None:
        self.path = str(Path(self.path) / 'missing' / 'song.mid')

        with self.assertRaises(OSError):
            self.build()

    def test_adds_context_tempos(self) -> None:
        context1, context2 = self.context(bpm=120), self.context(bpm=90)

        self.build(contexts=[(0, context1), (8, context2)])
        self.file.addTempo.assert_has_calls([call(0, 0, 120), call(0, 8, 90)])

    def test_adds_notes_with_correct_values(self) -> None:
        voice = self.voice(self.note(start=3, pitch=64, duration=2, volume=90))

        self.build(voices=(voice,))
        self.file.addNote.assert_called_once_with(
            track=MidiFile.TRACK,
            channel=0,
            pitch=64,
            time=3,
            duration=2,
            volume=90,
        )

    def test_assigns_a_channel_to_each_voice(self) -> None:
        voices = (self.voice(self.note(pitch=60)), self.voice(self.note(pitch=72)))
        self.build(voices=voices)

        channels = [call.kwargs['channel'] for call in self.file.addNote.call_args_list]
        self.assertEqual(channels, [0, 1])

    def test_ignores_voices_after_the_limit(self) -> None:
        voices = tuple(self.voice(self.note(pitch=pitch)) for pitch in range(12))
        self.build(voices=voices)

        self.assertEqual(self.file.addNote.call_count, MidiFile.MAX_VOICES)

    def test_changes_instrument_when_it_changes(self) -> None:
        voice = self.voice(
            self.note(start=0, instrument=0),
            self.note(start=1, instrument=0),
            self.note(start=2, instrument=5),
        )
        self.build((voice,))

        kwargs = [call.kwargs for call in self.file.addProgramChange.call_args_list]
        self.assertEqual(
            kwargs,
            [
                {'tracknum': MidiFile.TRACK, 'channel': 0, 'time': 0, 'program': 0},
                {'tracknum': MidiFile.TRACK, 'channel': 0, 'time': 2, 'program': 5},
            ],
        )


if __name__ == '__main__':
    unittest.main()
