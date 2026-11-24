import unittest

from .root import Instrument, InstrumentOutOfRangeError


# IA Code
class TestInstrument(unittest.TestCase):
    def test_returns_the_given_id(self) -> None:
        instrument_id = 42
        self.assertEqual(Instrument(instrument_id).id(), instrument_id)

    def test_accepts_both_limits_as_params(self) -> None:
        self.assertEqual(Instrument(Instrument.MIN).id(), Instrument.MIN)
        self.assertEqual(Instrument(Instrument.MAX).id(), Instrument.MAX)

    def test_rejects_ids_outside_the_limits(self) -> None:
        with self.assertRaises(InstrumentOutOfRangeError):
            Instrument(Instrument.MIN - 1)

        with self.assertRaises(InstrumentOutOfRangeError):
            Instrument(Instrument.MAX + 1)


if __name__ == '__main__':
    unittest.main()
