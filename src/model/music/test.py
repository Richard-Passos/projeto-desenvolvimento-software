import unittest
from unittest.mock import Mock

from model.bpm import Bpm
from model.voice import Voice

from .root import Music


# IA Code
class TestMusic(unittest.TestCase):
    def setUp(self) -> None:
        self._bpm = Mock(spec=Bpm)
        self._voices: list[Voice] = [Mock(spec=Voice), Mock(spec=Voice)]
        self._music = Music(self._bpm, self._voices)

    def test_returns_the_given_bpm_and_voices(self) -> None:
        self.assertIs(self._music.bpm(), self._bpm)
        self.assertEqual(self._music.voices(), self._voices)

    def test_returns_each_voice_by_index(self) -> None:
        self.assertIs(self._music.voice(0), self._voices[0])
        self.assertIs(self._music.voice(1), self._voices[1])

    def test_with_no_changes_creates_a_copy(self) -> None:
        copy = self._music.with_()

        self.assertIsNot(copy, self._music)
        self.assertIs(copy.bpm(), self._bpm)
        self.assertEqual(copy.voices(), self._voices)

    def test_with_changes_creates_a_copy_with_new_values(self) -> None:
        bpm = Mock(spec=Bpm)
        voices = [Mock(spec=Voice)]
        updated = self._music.with_(bpm=bpm, voices=voices)

        self.assertIs(updated.bpm(), bpm)
        self.assertEqual(updated.voices(), voices)
        self.assertIsNot(updated.bpm(), self._bpm)
        self.assertNotEqual(updated.voices(), self._voices)


if __name__ == '__main__':
    unittest.main()
