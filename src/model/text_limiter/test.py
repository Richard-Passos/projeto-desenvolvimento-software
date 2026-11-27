import unittest

from .root import NonPositiveColsError, NonPositiveRowsError, TextLimiter


# IA Code
class TestTextLimiter(unittest.TestCase):
    def setUp(self) -> None:
        self._limits = TextLimiter(rows=2, cols=3)

    def test_uses_default_limits(self) -> None:
        limits = TextLimiter()
        self.assertEqual(limits.rows(), TextLimiter.ROWS)
        self.assertEqual(limits.cols(), TextLimiter.COLS)

    def test_uses_custom_limits(self) -> None:
        self.assertEqual(self._limits.rows(), 2)
        self.assertEqual(self._limits.cols(), 3)

    def test_rejects_non_positive_rows(self) -> None:
        with self.assertRaises(NonPositiveRowsError):
            TextLimiter(rows=0)

        with self.assertRaises(NonPositiveRowsError):
            TextLimiter(rows=-1)

    def test_rejects_non_positive_cols(self) -> None:
        with self.assertRaises(NonPositiveColsError):
            TextLimiter(cols=0)

        with self.assertRaises(NonPositiveColsError):
            TextLimiter(cols=-1)

    def test_accepts_empty_text(self) -> None:
        self.assertTrue(self._limits.fits(''))

    def test_accepts_text_at_both_limits(self) -> None:
        self.assertTrue(self._limits.fits('abc\ndef'))

    def test_rejects_text_with_one_extra_line(self) -> None:
        self.assertFalse(self._limits.fits('a\nb\nc'))

    def test_rejects_text_when_only_one_line_is_too_long(self) -> None:
        self.assertFalse(self._limits.fits('abc\ndefg'))


if __name__ == '__main__':
    unittest.main()
