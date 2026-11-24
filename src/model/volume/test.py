import unittest

from .root import Volume, VolumeOutOfRangeError


# IA Code
class TestVolume(unittest.TestCase):
    def setUp(self) -> None:
        self._value: int = 25
        self._volume = Volume(self._value)

    def test_accepts_both_limits(self) -> None:
        self.assertEqual(Volume(Volume.MIN).value(), Volume.MIN)
        self.assertEqual(Volume(Volume.MAX).value(), Volume.MAX)

    def test_rejects_values_outside_the_limits(self) -> None:
        with self.assertRaises(VolumeOutOfRangeError):
            Volume(Volume.MIN - 1)

        with self.assertRaises(VolumeOutOfRangeError):
            Volume(Volume.MAX + 1)

    def test_double_multiplies_by_step_and_preserves_original_value(self) -> None:
        doubled = self._volume.double()
        self.assertEqual(doubled.value(), self._value * Volume.STEP)
        self.assertEqual(self._volume.value(), self._value)

    def test_double_stops_at_maximum_volume(self) -> None:
        volume = Volume(Volume.MAX)
        self.assertEqual(volume.double().value(), Volume.MAX)

    def test_halve_rounds_down_and_preserves_original_value(self) -> None:
        halved = self._volume.halve()
        self.assertEqual(halved.value(), self._value // Volume.STEP)
        self.assertEqual(self._volume.value(), self._value)

    def test_halve_keeps_minimum_volume_at_the_limit(self) -> None:
        volume = Volume(Volume.MIN)
        self.assertEqual(volume.halve().value(), Volume.MIN)


if __name__ == '__main__':
    unittest.main()
