import unittest

from .root import Octave, OctaveOutOfRangeError


# IA Code
class TestOctave(unittest.TestCase):
    def setUp(self) -> None:
        self._value: int = 4
        self._octave: Octave = Octave(self._value)

    def test_accepts_both_limits_as_params(self) -> None:
        self.assertEqual(Octave(Octave.MIN).value(), Octave.MIN)
        self.assertEqual(Octave(Octave.MAX).value(), Octave.MAX)

    def test_rejects_values_outside_the_limits(self) -> None:
        with self.assertRaises(OctaveOutOfRangeError):
            Octave(Octave.MIN - 1)

        with self.assertRaises(OctaveOutOfRangeError):
            Octave(Octave.MAX + 1)

    def test_up_adds_step_and_preserves_original_value(self) -> None:
        self.assertEqual(self._octave.up().value(), self._value + Octave.STEP)
        self.assertEqual(self._octave.value(), self._value)

    def test_down_subtracts_step_and_preserves_original_value(self) -> None:
        self.assertEqual(self._octave.down().value(), self._value - Octave.STEP)
        self.assertEqual(self._octave.value(), self._value)

    def test_up_stops_at_maximum_octave(self) -> None:
        self.assertEqual(Octave(Octave.MAX).up().value(), Octave.MAX)

    def test_down_stops_at_minimum_octave(self) -> None:
        self.assertEqual(Octave(Octave.MIN).down().value(), Octave.MIN)

    def test_pitch_adds_the_note_offset_to_the_octave_base_pitch(self) -> None:
        self.assertEqual(self._octave.pitch(0), 60)
        self.assertEqual(self._octave.pitch(7), 67)


if __name__ == '__main__':
    unittest.main()
