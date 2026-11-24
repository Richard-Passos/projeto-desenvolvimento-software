import unittest
from unittest.mock import Mock

from model.instrument import Instrument
from model.octave import Octave
from model.volume import Volume

from .root import Voice


# IA Code
class TestVoice(unittest.TestCase):
    def setUp(self) -> None:
        self._volume = Mock(spec=Volume)
        self._octave = Mock(spec=Octave)
        self._instrument = Mock(spec=Instrument)
        self._voice = Voice(self._volume, self._octave, self._instrument)

    def test_returns_the_given_params(self) -> None:
        self.assertIs(self._voice.volume(), self._volume)
        self.assertIs(self._voice.octave(), self._octave)
        self.assertIs(self._voice.instrument(), self._instrument)

    def test_with_no_changes_returns_a_copy_with_the_same_values(self) -> None:
        copy = self._voice.with_()

        self.assertIsNot(copy, self._voice)
        self.assertIs(copy.volume(), self._volume)
        self.assertIs(copy.octave(), self._octave)
        self.assertIs(copy.instrument(), self._instrument)

    def test_with_octave_changes_only_the_octave(self) -> None:
        new_octave = Mock(spec=Octave)
        copy = self._voice.with_(octave=new_octave)

        self.assertIs(copy.volume(), self._volume)
        self.assertIs(copy.octave(), new_octave)
        self.assertIs(copy.instrument(), self._instrument)
        self.assertIs(self._voice.octave(), self._octave)
        self.assertIsNot(copy.octave(), self._octave)

    def test_with_all_changes_updates_the_copy_and_preserves_the_original(self) -> None:
        new_volume = Mock(spec=Volume)
        new_octave = Mock(spec=Octave)
        new_instrument = Mock(spec=Instrument)

        copy = self._voice.with_(
            volume=new_volume,
            octave=new_octave,
            instrument=new_instrument,
        )

        self.assertIs(copy.volume(), new_volume)
        self.assertIs(copy.octave(), new_octave)
        self.assertIs(copy.instrument(), new_instrument)

        self.assertIs(self._voice.volume(), self._volume)
        self.assertIs(self._voice.octave(), self._octave)
        self.assertIs(self._voice.instrument(), self._instrument)


if __name__ == '__main__':
    unittest.main()
