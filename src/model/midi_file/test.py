import unittest
from unittest.mock import Mock

from model.path import MidiPath

from .root import MidiFile, NonPositiveDurationError


# IA Code
class TestMidiFile(unittest.TestCase):
    def setUp(self) -> None:
        self._path = Mock(spec=MidiPath)
        self._path.name.return_value = 'song.midi'

    def test_returns_the_given_path_and_duration(self) -> None:
        duration = 2.5
        midi_file = MidiFile(self._path, duration)

        self.assertEqual(midi_file.path(), self._path.name())
        self.assertEqual(midi_file.duration(), duration)

    def test_rejects_non_positive_durations(self) -> None:
        with self.assertRaises(NonPositiveDurationError):
            MidiFile(self._path, 0.0)

        with self.assertRaises(NonPositiveDurationError):
            MidiFile(self._path, -1.0)


if __name__ == '__main__':
    unittest.main()
