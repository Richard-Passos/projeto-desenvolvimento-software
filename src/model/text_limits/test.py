import unittest

from model.text_limits import TextLimit, TextLimits

# Small limits keep the texts short: 3 lines, 5 characters per line.
SMALL = TextLimits(max_lines=3, max_line_length=5)


class DefaultsTest(unittest.TestCase):
    def test_default_limits_of_the_app(self) -> None:
        limits = TextLimits()

        self.assertEqual(limits.max_lines, 16)
        self.assertEqual(limits.max_line_length, 10_000)


class ExceededTest(unittest.TestCase):
    def test_none_when_the_text_fits(self) -> None:
        cases = {
            'empty': '',
            'one line': 'A',
            'max lines': 'A\nB\nC',
            'max lines with a final break': 'A\nB\nC\n',
            'blank lines': '\n\nA',
            'max characters in a line': 'AAAAA',
            'max lines and characters': 'AAAAA\nAAAAA\nAAAAA',
            'crlf is not part of the line': 'AAAAA\r\nAAAAA\r\n',
        }

        for name, text in cases.items():
            with self.subTest(name):
                self.assertIsNone(SMALL.exceeded(text))

    def test_too_many_lines(self) -> None:
        cases = {
            'one more line': 'A\nB\nC\nD',
            'a line after the final break': 'A\nB\nC\n\n',
            'blank lines count': '\n\n\nA',
        }

        for name, text in cases.items():
            with self.subTest(name):
                self.assertIs(SMALL.exceeded(text), TextLimit.TOO_MANY_LINES)

    def test_line_too_long_in_any_line(self) -> None:
        for text in ('AAAAAA', 'A\nAAAAAA\nB', 'A\nB\nAAAAAA'):
            with self.subTest(text):
                self.assertIs(SMALL.exceeded(text), TextLimit.LINE_TOO_LONG)

    def test_too_many_lines_wins_over_line_too_long(self) -> None:
        text = '\n'.join(['AAAAAA'] * 4)

        self.assertIs(SMALL.exceeded(text), TextLimit.TOO_MANY_LINES)

    def test_uses_its_own_limits(self) -> None:
        text = 'A\nB'

        self.assertIsNone(TextLimits(max_lines=2).exceeded(text))
        self.assertIs(TextLimits(max_lines=1).exceeded(text), TextLimit.TOO_MANY_LINES)


class FitsTest(unittest.TestCase):
    def test_is_true_only_when_nothing_is_exceeded(self) -> None:
        self.assertTrue(SMALL.fits('A\nB'))
        self.assertFalse(SMALL.fits('A\nB\nC\nD'))
        self.assertFalse(SMALL.fits('AAAAAA'))


if __name__ == '__main__':
    unittest.main()
