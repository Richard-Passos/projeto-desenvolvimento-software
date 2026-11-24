import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from .root import MidiFile, MidiFileNotFoundError, NonPositiveDurationError


# IA Code
class TestMidiFile(unittest.TestCase):
    def setUp(self) -> None:
        directory = TemporaryDirectory()
        self._path = Path(directory.name) / 'song.mid'
        self._path.touch()
        self.addCleanup(directory.cleanup)

    def test_returns_the_given_path_and_duration(self) -> None:
        duration = 2.5
        path = str(self._path)
        midi_file = MidiFile(path, duration)

        self.assertEqual(midi_file.path(), path)
        self.assertEqual(midi_file.duration(), duration)

    def test_rejects_a_missing_file(self) -> None:
        missing_path = self._path.with_name('missing.mid')

        with self.assertRaises(MidiFileNotFoundError):
            MidiFile(str(missing_path), 1)

    def test_rejects_non_positive_durations(self) -> None:
        path = str(self._path)

        with self.assertRaises(NonPositiveDurationError):
            MidiFile(path, 0.0)

        with self.assertRaises(NonPositiveDurationError):
            MidiFile(path, -1.0)


if __name__ == '__main__':
    unittest.main()
