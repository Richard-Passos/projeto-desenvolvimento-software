import unittest

from .root import Bpm, BpmOutOfRangeError


# IA Code
class TestBpm(unittest.TestCase):
    def test_uses_default_value(self) -> None:
        self.assertEqual(Bpm().value(), Bpm.DEFAULT)

    def test_accepts_both_limits_as_params(self) -> None:
        self.assertEqual(Bpm(Bpm.MIN).value(), Bpm.MIN)
        self.assertEqual(Bpm(Bpm.MAX).value(), Bpm.MAX)

    def test_rejects_values_outside_the_limits(self) -> None:
        with self.assertRaises(BpmOutOfRangeError):
            Bpm(Bpm.MIN - 1)

        with self.assertRaises(BpmOutOfRangeError):
            Bpm(Bpm.MAX + 1)

    def test_increase_adds_step_and_preserves_original_value(self) -> None:
        value = 100
        bpm = Bpm(value)
        self.assertEqual(bpm.increase().value(), value + Bpm.STEP)
        self.assertEqual(bpm.value(), value)

    def test_decrease_subtracts_10_and_preserves_original_value(self) -> None:
        value = 100
        bpm = Bpm(value)
        self.assertEqual(bpm.decrease().value(), value - Bpm.STEP)
        self.assertEqual(bpm.value(), value)

    def test_increase_stops_at_limit(self) -> None:
        self.assertEqual(Bpm(Bpm.MAX).increase().value(), Bpm.MAX)

    def test_decrease_stops_at_limit(self) -> None:
        self.assertEqual(Bpm(Bpm.MIN).decrease().value(), Bpm.MIN)


if __name__ == '__main__':
    unittest.main()
