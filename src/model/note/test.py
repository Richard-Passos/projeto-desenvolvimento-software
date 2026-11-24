import unittest
from unittest.mock import Mock

from model.octave import Octave
from model.volume import Volume

from .root import DurationOutOfRangeError, Note, NoteId


# IA Code
class TestNote(unittest.TestCase):
    def setUp(self) -> None:
        self._id = NoteId.C
        self._duration: int = 1
        self._volume = Mock(spec=Volume)
        self._octave = Mock(spec=Octave)
        self._note = Note(NoteId.C, 1, self._volume, self._octave)

    def test_returns_given_params(self) -> None:
        self.assertEqual(self._note.id(), self._id.value)
        self.assertEqual(self._note.duration(), self._duration)
        self.assertIs(self._note.volume(), self._volume)
        self.assertIs(self._note.octave(), self._octave)

    def test_duration_halves_at_each_step(self) -> None:
        expected_durations = (2.0, 1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625)

        for duration, expected in enumerate(expected_durations):
            note = Note(NoteId.C, duration, self._volume, self._octave)
            self.assertEqual(note.duration(), expected)

    def test_rejects_durations_outside_the_limits(self) -> None:
        with self.assertRaises(DurationOutOfRangeError):
            Note(self._id, Note.MIN_DURATION - 1, self._volume, self._octave)

        with self.assertRaises(DurationOutOfRangeError):
            Note(self._id, Note.MAX_DURATION + 1, self._volume, self._octave)

    def test_pitch_uses_the_octave_and_note_id(self) -> None:
        self._octave.pitch.return_value = 72

        self.assertEqual(self._note.pitch(), 72)
        self._octave.pitch.assert_called_once_with(NoteId.C.value)

    def test_with_no_changes_returns_a_copy_with_the_same_values(self) -> None:
        copy = self._note.with_()

        self.assertIsNot(copy, self._note)
        self.assertEqual(copy.id(), self._note.id())
        self.assertEqual(copy.duration(), self._note.duration())
        self.assertIs(copy.volume(), self._note.volume())
        self.assertIs(copy.octave(), self._note.octave())

    def test_with_changes_updates_only_the_copy(self) -> None:
        id = NoteId.D
        volume = Mock(spec=Volume)
        octave = Mock(spec=Octave)
        updated = self._note.with_(id=id, volume=volume, octave=octave)

        self.assertEqual(updated.id(), id.value)
        self.assertIs(updated.volume(), volume)
        self.assertIs(updated.octave(), octave)

        self.assertEqual(self._note.id(), self._id.value)
        self.assertEqual(self._note.duration(), self._duration)
        self.assertIs(self._note.volume(), self._volume)
        self.assertIs(self._note.octave(), self._octave)


if __name__ == '__main__':
    unittest.main()
